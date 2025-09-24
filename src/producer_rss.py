import hashlib
import json
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, RSS_FEEDS, USER_AGENT


def make_id(title: str, link: str) -> str:
    return hashlib.sha1(f"{title}|{link}".encode("utf-8")).hexdigest()


def fetch_feed(url: str):
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "xml")
    for item in soup.find_all("item"):
        title = (item.title.text or "").strip()
        link = (item.link.text or "").strip()
        pubDate = (item.pubDate.text or "").strip()

        yield {
            "id": make_id(title, link),
            "source": url,
            "title": title,
            "link": link,
            "pubDate": pubDate,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }


def main():
    # Kafka producer object which is responsible for sending messages into Kafka
    producer = KafkaProducer(
        # think like front desk
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        # how to convert messages into bytes
        value_serializer=lambda d: json.dumps(d).encode("utf-8"),
        # Wait 50 milliseconds for more messages to come in before sending them out
        linger_ms=50,
        # leader and followers (all brokers) have to acknowledge
        acks="all",
    )
    # de-dup in memory (same news comes again)
    seen = set()
    print(f"publishing to toips {KAFKA_TOPIC}")

    while True:
        new_count = 0
        for feed in RSS_FEEDS:
            try:
                for item in fetch_feed(feed):
                    if item["id"] in seen:
                        continue
                    producer.send(KAFKA_TOPIC, item)
                    seen.add(item["id"])
                    new_count += 1
            except Exception as e:
                print(f"feed error: {feed} : {e}")
        if new_count:
            print(f"producer published {new_count} new items")
        time.sleep(15)  # being polite with RSS


if __name__ == "__main__":
    main()
