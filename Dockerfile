FROM apache/airflow:2.9.2

USER airflow
COPY requirements-airflow.txt .
RUN pip install --no-cache-dir -r requirements-airflow.txt
