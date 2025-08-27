import sys

# 出力をUTF-8に強制
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_news():
    url = "https://news.yahoo.co.jp/"
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")

    news_data = []
    for item in soup.select("a"):
        title = item.get_text().strip()
        link = item.get("href")
        if title and link and len(title) > 10:
            news_data.append({"title": title, "url": link})

    df = pd.DataFrame(news_data)
    filename = f"news_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"{len(df)}件のニュースを取得しました。保存ファイル: {filename}")
if __name__ == "__main__":
    scrape_news()

