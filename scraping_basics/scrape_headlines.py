import requests
from bs4 import BeautifulSoup

# RSS  URL
RSS_URL = "https://finance.yahoo.com/rss/topstories"

#  add headers to pretend you're a browser
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

response = requests.get(RSS_URL, headers=headers)
if response.status_code != 200:
    print(f"Failed to fetch RSS feed! Status code: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "xml")

items = soup.find_all("item")

print("Latest RSS Headlines:")
print("=" * 40)

for idx, item in enumerate(items[:10], start=1):
    title = item.title.text
    link = item.link.text
    pub_date = item.pubDate.text

    print(f"{idx}. {title}")
    print(f"   Published: {pub_date}")
    print(f"   Link: {link}\n")
