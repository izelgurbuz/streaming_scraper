import json

import psycopg2
from kafka import KafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

DB_CONFIG = {
    "host": "localhost",
    "port": 5555,
    "dbname": "streamdb",
    "user": "app",
    "password": "app",
}


def save_to_postgres(item):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO news_history (headline_id, title, link, pub_date, source, ingested_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (headline_id) DO NOTHING;
        """,
            (
                item["id"],
                item["title"],
                item["link"],
                item["pubDate"],
                item["source"],
                item["ingested_at"],
            ),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="postgres_saver",
        auto_offset_reset="latest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    print("postgres - Listening for messages...")
    for msg in consumer:
        save_to_postgres(msg.value)
        print(f"postgres - Saved: {msg.value['title']}")


if __name__ == "__main__":
    main()
