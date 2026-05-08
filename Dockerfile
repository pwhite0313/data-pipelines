FROM apache/airflow:2.8.1

USER airflow
COPY requirements-airflow.txt .
RUN pip install --no-cache-dir -r requirements-airflow.txt
