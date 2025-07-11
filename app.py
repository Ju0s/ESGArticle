from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

KEYWORDS = ['모집', '신청']

def summarize(text):
    # 매우 단순한 요약기 (원한다면 GPT API로 교체 가능)
    return text[:120] + "..."

@app.route('/filter_and_summarize', methods=['POST'])
def filter_and_summarize():
    articles = request.json.get('articles', [])
    result = []

    for item in articles:
        try:
            r = requests.get(item['link'], timeout=3, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, 'html.parser')
            content = soup.get_text()

            if any(kw in content for kw in KEYWORDS):
                result.append({
                    'title': item['title'],
                    'link': item['link'],
                    'summary': summarize(content)
                })
        except:
            continue

    return jsonify(result)

