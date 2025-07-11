from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/check', methods=['POST'])
def check_article():
    data = request.get_json(force=True)
    url = data.get('url')

    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 본문 텍스트 추출
        paragraphs = soup.find_all('p')
        full_text = ' '.join(p.get_text() for p in paragraphs)

        # 키워드 포함 여부 확인
        keywords = ['모집', '신청']
        contains = any(kw in full_text for kw in keywords)

        return jsonify({'contains': contains})

    except Exception as e:
        return jsonify({'contains': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
