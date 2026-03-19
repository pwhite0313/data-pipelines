from datetime import datetime, timedelta
from airflow.decorators import dag, task

from src.extract import extract_records
from src.transform import transform_records
from src.load import load_records


@dag(
    dag_id="api_to_csv_local",
    schedule="@daily",
    start_date=datetime(2026, 3, 1),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["etl", "api", "csv"],
)
def api_to_csv_local():

    @task
    def extract():
        return extract_api_data()

    @task
    def transform(raw_data):
        return transform_data(raw_data)

    @task
    def load(clean_data):
        output_path = "/opt/airflow/data/output.csv"
        save_csv(clean_data, output_path)

    raw = extract()
    clean = transform(raw)
    load(clean)


dag = api_to_csv_local()