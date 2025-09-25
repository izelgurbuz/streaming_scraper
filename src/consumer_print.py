import json

from kafka import KafkaConsumer

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC


def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        # If you have 2 consumers in the same group:
        # - Kafka splits the messages between them (load balancing)
        # If you have consumers in different groups:
        # - Each group gets its own copy of every message
        group_id="printer",
        # what to do if there’s no saved bookmark
        auto_offset_reset="latest",
        value_deserializer=lambda d: json.loads((d.decode("utf-8"))),
        # True = Kafka automatically saves your progress every few seconds - simple but less control
        # False = You must manually commit offsets in codes
        enable_auto_commit=True,
    )
    print(f"consumer - listening on topic '{KAFKA_TOPIC}'")
    for msg in consumer:
        item = msg.value
        print(f"- {item.get('title')}  | {item.get('link')}")


if __name__ == "__main__":
    main()
