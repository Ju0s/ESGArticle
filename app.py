from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

app = Flask(__name__)

KEYWORDS = ["ESG 경영", "ESG 스타트업", "지속가능성", "ESG 지원사업", "ESG 활동", "ESG 모집"]
FILTER_WORDS = ["모집", "신청"]

def summarize(text):
    for word in FILTER_WORDS:
        idx = text.find(word)
        if idx != -1:
            start = max(0, idx - 60)
            end = min(len(text), idx + 60)
            return '...' + text[start:end].strip() + '...'
    return text[:120] + '...'

@app.route("/esg_articles", methods=["GET"])
def fetch_esg_articles():
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y.%m.%d")
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    for keyword in KEYWORDS:
        query = keyword.replace(" ", "+")
        search_url = f"https://search.naver.com/search.naver?where=news&query={query}&pd=2&ds={yesterday_str}&de={yesterday_str}"
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        info_groups = soup.select("div.info_group")

        print(f"\n🔍 [{keyword}] 키워드로 검색된 기사 수: {len(info_groups)}")

        for info_group in info_groups:
            a_tag = info_group.select_one("a.info")
            date_span = info_group.select_one("span.info")

            if not a_tag or not date_span:
                continue

            href = a_tag.get("href")
            date_text = date_span.get_text()

            # 날짜 포맷 확인
            if not re.match(r"\d{4}\.\d{2}\.\d{2}\.", date_text):
                print(f"⛔ [{keyword}] {a_tag.get_text().strip()} → 날짜 정보 없음 (→ {date_text})")
                continue
            if not date_text.startswith(yesterday_str):
                print(f"⚠️ [{keyword}] {a_tag.get_text().strip()} → 어제 날짜 아님 ({date_text})")
                continue

            try:
                article = requests.get(href, headers=headers, timeout=5)
                article_soup = BeautifulSoup(article.text, "html.parser")
                text = article_soup.get_text()

                contains_kw = any(word in text for word in FILTER_WORDS)
                print(f"✅ [{keyword}] {a_tag.get_text().strip()} → 본문 길이: {len(text)} | 모집/신청 포함 여부: {contains_kw}")

                if contains_kw:
                    results.append({
                        "title": a_tag.get_text().strip(),
                        "link": href,
                        "summary": summarize(text)
                    })

            except Exception as e:
                print(f"❌ [{keyword}] {a_tag.get_text().strip()} → 본문 크롤링 실패: {e}")
                continue

    print(f"\n🎯 최종 필터 통과 기사 수: {len(results)}")
    return jsonify(results)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
