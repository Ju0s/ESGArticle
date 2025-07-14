from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

KEYWORDS = ['모집', '신청']

def extract_main_text(soup):
    for selector in [
        'div#article-view-content',
        'div.article_txt',
        'article',
        'section.article_body',
        'div#news-view-area',
        'div#content',
        'div.view_cont',
        'div.article'
    ]:
        tag = soup.select_one(selector)
        if tag:
            return tag.get_text(separator=' ', strip=True)
    return soup.get_text(separator=' ', strip=True)

def summarize(text):
    for kw in KEYWORDS:
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
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile; rv:109.0) Gecko/20100101 Firefox/119.0"
            }
            r = requests.get(item['link'], timeout=5, headers=headers)

            # 🔍 debug.html로 저장해서 확인 (선택 사항)
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(r.text)
                
            soup = BeautifulSoup(r.text, 'html.parser')

            content = extract_main_text(soup)
            content = re.sub(r'\s+', ' ', content)  # 🔧 공백/개행 정리

            if any(kw in content for kw in KEYWORDS):
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
