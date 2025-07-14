from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

KEYWORDS = ['모집', '신청']

def summarize(text):
    return text[:120] + '...' if len(text) > 120 else text

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
    app.run(debug=True)
