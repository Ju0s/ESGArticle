from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

KEYWORDS = ['모집', '신청']

def extract_main_text(soup):
    # 주요 기사 본문 태그들 우선 탐색
    for selector in [
        'article',
        'div#article-view-content-div',
        'div.article_txt',
        'div#news-view-area',
        'section.article_body'
    ]:
        tag = soup.select_one(selector)
        if tag:
            return tag.get_text(separator=' ', strip=True)
    # 실패 시 fallback: 전체 텍스트
    return soup.get_text(separator=' ', strip=True)

def summarize(text):
    for kw in ['모집', '신청']:
        idx = text.find(kw)
        if idx != -1:
            start = max(0, idx - 60)
            end = min(len(text), idx + 60)
            return '...' + text[start:end].strip() + '...'
    return text[:120] + '...'


@app.route('/filter_and_summarize', methods=['POST'])
def filter_and_summarize():
    articles = request.json.get('articles', [])
    result = []

    for item in articles:
        try:
            r = requests.get(item['link'], timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, 'html.parser')

            content = extract_main_text(soup)  # ⬅ 변경된 부분 ✅

            if any(kw in content for kw in ['모집', '신청']):
                summary = summarize(content)
                result.append({
                    'title': item['title'],
                    'link': item['link'],
                    'summary': summary
                })
        except Exception as e:
            print(f"[ERROR] {item['link']} - {e}")
            continue

    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
