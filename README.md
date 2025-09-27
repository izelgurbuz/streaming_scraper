# Streaming Scraper + Alerts

This project is basically a mini pipeline that scrapes crypto/news headlines, checks if anything interesting shows up, and then blasts you with alerts on Slack or Gmail. Think of it like a gossip bot for markets, but built with Airflow and a whole crew of supporting services — a bit overkill for headlines, but perfect for practicing with the real tools you’d see in production data systems.

---

### ⚡ Tech Stack (why each piece exists)

| Tool                  | Why it’s here                                                                  |
| --------------------- | ------------------------------------------------------------------------------ |
| **Airflow**           | Orchestrator, runs the DAGs, handles scheduling and branching logic.           |
| **Postgres**          | Metadata DB — stores task history, connections, variables.                     |
| **Redis**             | Lightweight broker/cache for Airflow.                                          |
| **Kafka + Zookeeper** | For practicing with real-time streams (overkill, but useful experience).       |
| **MongoDB**           | Optional schemaless storage for raw scraped data.                              |
| **Slack + Gmail**     | Notification layer. Slack for instant alerts, Gmail via SMTP.                  |
| **Docker Compose**    | Spins up all services locally in isolated containers for easy reproducibility. |

---

### 🚀 Flow in plain English

1. Producer scrapes data

- Scrapes crypto news headlines or uses RSS feeds (e.g., CoinDesk).

- Publishes headlines to Kafka topic.

2. Kafka Consumers

- Consumer #1: Stores structured data in Postgres.

- Consumer #2: Stores raw JSON in MongoDB.

- Consumer #3: Updates Redis cache with latest headlines.

3.Airflow DAG kicks in (every 5 min):

- Task 1 (check_headlines): Pulls latest headlines from Redis.

- Task 2 (branch_decision):

- If matches found: Run Slack + Gmail alerts in parallel.

- If no matches: DAG follows a no-op path and exits.

4. Notifications

- Slack message for instant alert.

- Gmail email summary.

---

### 🛠️ Setup

1. **Clone and enter repo**
   ```bash
   git clone https://github.com/yourusername/streaming_scraper.git
   cd streaming_scraper
   ```

Add .env file (root of project):

```
**Gmail (App Password only, not your real password)**
GMAIL_USER=youremail@gmail.com
GMAIL_PASS=your_16_char_app_password

**Airflow secret key**
AIRFLOW_SECRET_KEY=supersecret
```

2. **Start the stack**

```bash
docker compose up -d
```

This starts:

- Postgres

- Redis

- MongoDB

- Kafka + Zookeeper

- Kafka UI

- Airflow Webserver

- Airflow Scheduler

Initialize Airflow (only first time)

```bash
docker compose run airflow-init
```

3. **Access UIs**

Airflow: `http://localhost:8081`
(admin/admin)

Kafka UI: `http://localhost:8080`

4. **Start the Producer & Consumers**

Before triggering the DAG, you must have streaming data flowing for a meaningful run.
Run each of these in separate terminals from the src/ folder

Terminal 1: start producer

```
python src/producer_rss.py
```

Terminal 2: start Redis consumer

```
python src/consumer_redis.py
```

Terminal 3: start Postgres consumer

```
python src/consumer_postgres.py
```

Terminal 4: start MongoDB consumer (optional)

```
python src/consumer_mongo.py
```

5. **Trigger the DAG**

In Airflow UI → unpause news_alerts → hit “Trigger DAG.”

If matches found → you’ll see Slack/Gmail alerts.

<img width="2088" height="566" alt="Screenshot 2025-09-27 at 19 17 55" src="https://github.com/user-attachments/assets/b5670408-6f36-46d2-97ef-fe3fbb2c3d44" />


### 🐛 What went wrong (aka lessons learned)

Gmail SMTP → ConnectionRefusedError until I realized the scheduler (not just the webserver) needs the SMTP env vars.

Slack → Airflow hates raw webhook URLs. Add the connection on UI or by the command I provided in commands.txt.

Connections disappearing → Postgres had no volume, so every docker compose down wiped it. Fixed by adding a volume to /var/lib/postgresql/data.

Branching logic → Started with ShortCircuitOperator, switched to BranchPythonOperator because it’s cleaner for this case.

### 🎯 Wrap-up

This project is basically a “cloud-native data pipeline in a box”: scrape → process → branch → notify. It’s totally overbuilt for headline alerts, but it gives hands-on practice with the stack you’ll actually encounter in finance/data eng.
