from datetime import datetime, timedelta
from airflow.decorators import dag, task

from src.extract import extract_records
from src.transform import transform_records
from src.load import load_records
from postgres.load_to_postgres import load_weather_csv_to_raw_table
from src.logging_config import setup_logging


@dag(
    dag_id="api_to_csv_local",
    schedule="@daily",
    start_date=datetime(2026, 3, 1),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["etl", "api", "csv", "postgres"],
)
def api_to_csv_local():

    @task
    def extract():
        setup_logging()
        return extract_records()

    @task
    def transform(raw_data):
        setup_logging()
        return transform_records(raw_data)

    @task
    def load(clean_data):
        setup_logging()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/opt/airflow/data/raw/output_{timestamp}.csv"
        load_records(clean_data, output_path)
        return output_path

    @task
    def load_raw_table(file_path: str):
        setup_logging()
        context = get_current_context()
        dag_run_id = context["dag_run"].run_id if context.get("dag_run") else None
        return load_weather_csv_to_raw_table(
            file_path=file_path,
            dag_run_id=dag_run_id,
            skip_if_loaded=True,
        )

    raw = extract()
    clean = transform(raw)
    load(clean)
    load_raw_table(file_path)


dag = api_to_csv_local()