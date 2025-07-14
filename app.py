from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

KEYWORDS = ['모집', '신청']

def summarize(text):
    import re

    # 1. 문장 구분 기준: 마침표, 줄바꿈, 물음표, 느낌표 등
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)

    # 2. 키워드 포함 문장 찾기
    for kw in ['모집', '신청']:
        for s in sentences:
            if kw in s and len(s.strip()) > 20:
                return s.strip()

    # 3. fallback: 본문 앞 120자
    return text[:120] + '...'

@app.route('/filter_and_summarize', methods=['POST'])
def filter_and_summarize():
    articles = request.json.get('articles', [])
    result = []

    for item in articles:
        try:
            r = requests.get(item['link'], timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, 'html.parser')
            content = soup.get_text(separator=' ', strip=True)

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
