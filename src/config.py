KAFKA_BOOTSTRAP_SERVERS = "localhost:29092"
KAFKA_TOPIC = "news_rss"

# You can add more feeds later
RSS_FEEDS = [
    "https://finance.yahoo.com/rss/topstories",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
]
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/118.0 Safari/537.36"
)
