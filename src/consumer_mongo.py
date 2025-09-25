import json

from kafka import KafkaConsumer
from pymongo import MongoClient

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

client = MongoClient("mongodb://localhost:27017")
db = client.streamdb
collection = db.news


def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="mongo_saver",
        auto_offset_reset="latest",
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    print("mongo - Listening for messages...")

    for msg in consumer:
        doc = msg.value
        collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
        print(f"mongo - Saved: {doc['title']}")


if __name__ == "__main__":
    main()
