from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check_keyword():
    data = request.json
    url = data.get("url")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        text = soup.get_text(separator=' ', strip=True)
        contains_keyword = "모집" in text

        return jsonify({"url": url, "contains": contains_keyword})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
