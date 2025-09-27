from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator  # Needed for "do nothing"
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from shared_functions import check_redis_for_alerts  # if in separate file

REDIS_HOST = "redis"
REDIS_PORT = 6379
KEY_PATTERN = "latest:*"

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}


def choose_path(**context):
    # ti object is your hook into XComs
    # TaskInstance object for the currently running task
    # xcom_pull() : fetches a value that was pushed by another task
    matches = context["ti"].xcom_pull(task_ids="check_headlines")
    if matches and len(matches) > 0:
        print(f"Found {len(matches)} relevant headlines.")
        return ["send_slack_alert", "send_email_summary"]
    return "no_alert_path"


with DAG(
    dag_id="news_alerts",
    default_args=default_args,
    schedule_interval="*/5 * * * *",  # every 5 minutes
    start_date=datetime(2025, 9, 25),
    catchup=False,
) as dag:
    check_task = PythonOperator(
        task_id="check_headlines",
        python_callable=check_redis_for_alerts,
    )
    branch_task = BranchPythonOperator(
        task_id="branch_decision",
        python_callable=choose_path,
        provide_context=True,
    )

    slack_alert = SlackWebhookOperator(
        task_id="send_slack_alert",
        message=":rotating_light: Bitcoin or Ethereum mentioned in latest headlines!",
        slack_webhook_conn_id="slack_default",
    )

    send_email = EmailOperator(
        task_id="send_email_summary",
        to="izelgurbuz@gmail.com",
        subject="Crypto News Alert",
        html_content="<h3>Check Slack for detailed alerts.</h3>",
    )

    no_alert_path = EmptyOperator(task_id="no_alert_path")

    # DAG Flow
    check_task >> branch_task
    branch_task >> [slack_alert, send_email]
    branch_task >> no_alert_path
