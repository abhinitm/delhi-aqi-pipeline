from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="delhi_aqi_pipeline",
    schedule="@hourly",
    start_date=datetime(2026, 10, 1),
    catchup=False,
    default_args={"retries": 2},
) as dag:

    load = BashOperator(
        task_id="load_aqi",
        bash_command="python /opt/airflow/src/load_aqi.py",
    )

    check = BashOperator(
        task_id="check_quality",
        bash_command="python /opt/airflow/src/check_quality.py",
    )

    load >> check