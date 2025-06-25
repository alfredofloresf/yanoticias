import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

sources = {
    "Primicias": "https://www.primicias.ec/feed/",
    "Teleamazonas": "https://www.teleamazonas.com/feed/",
    "Expreso": "https://www.expreso.ec/rss/feed.xml"
}

today = datetime.now().strftime("%d %b %Y")
output_news = []

for source_name, rss_url in sources.items():
    try:
        res = requests.get(rss_url, timeout=10)
        soup = BeautifulSoup(res.content, "xml")
        items = soup.find_all("item")
        for item in items:
            pub_date = item.pubDate.text if item.pubDate else ""
            if today in pub_date:
                title = item.title.text
                link = item.link.text
                time_str = datetime.strptime(pub_date[:-6], "%a, %d %b %Y %H:%M:%S").strftime("%H:%M")
                output_news.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "time": time_str
                })
    except Exception as e:
        print(f"Error fetching from {source_name}: {e}")

output_news.sort(key=lambda x: x["time"], reverse=True)

html_parts = ["""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>YaNoticias – Noticias del Día</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f4f4f4;
      color: #333;
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
    }
    img {
      max-width: 180px;
      display: block;
      margin: 0 auto 20px;
    }
    .news-item {
      display: flex;
      align-items: flex-start;
      margin-bottom: 15px;
      border-bottom: 1px solid #ddd;
      padding-bottom: 10px;
    }
    .news-time {
      width: 60px;
      font-size: 12px;
      color: gray;
      margin-right: 10px;
      flex-shrink: 0;
    }
    .news-content a {
      font-size: 16px;
      font-weight: bold;
      color: #007acc;
      text-decoration: none;
    }
    .news-content a:hover {
      text-decoration: underline;
    }
    .news-source {
      font-size: 12px;
      color: gray;
    }
  </style>
</head>
<body>
  <img src="logo.png" alt="YaNoticias">
"""]

for item in output_news:
    html_parts.append(f'''
    <div class="news-item">
      <div class="news-time">{item['time']}</div>
      <div class="news-content">
        <a href="{item['link']}" target="_blank">{item['title']}</a>
        <div class="news-source">{item['source']}</div>
      </div>
    </div>''')

html_parts.append("</body></html>")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
with open(output_dir / "index.html", "w", encoding="utf-8") as f:
    f.write("".join(html_parts))

print("✔ YaNoticias page generated: output/index.html")
