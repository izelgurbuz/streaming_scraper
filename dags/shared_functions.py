import json

import redis

REDIS_HOST = "redis"
REDIS_PORT = 6379
KEY_PATTERN = "latest:*"


def check_redis_for_alerts():
    """
    Pull headlines from Redis and return those mentioning Bitcoin or Ethereum.
    """
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    matching = []
    for key in r.keys(KEY_PATTERN):
        latest_data = json.loads(r.get(key))
        title = latest_data.get("title", "")
        if (
            "bitcoin" in title.lower()
            or "ethereum" in title.lower()
            or "stock" in title.lower()
        ):
            matching.append(latest_data)
    return matching
