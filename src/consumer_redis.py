import json

import redis
from kafka import KafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

r = redis.Redis(host="localhost", port=6379, db=0)


def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="redis_updater",
        auto_offset_reset="latest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    print("[consumer_redis] Listening for messages...")
    for msg in consumer:
        item = msg.value
        key = f"latest:{item['source'].split('//')[0].split('/')[0]}"
        r.set(key, json.dumps(item))
        print(f"redis - Updated cache for {key}")


if __name__ == "__main__":
    main()
