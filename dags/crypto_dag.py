from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import json
import pandas as pd
import sqlite3
import os

DATA_DIR = "/opt/airflow/data"
JSON_PATH = f"{DATA_DIR}/crypto_data.json"
CSV_PATH = f"{DATA_DIR}/crypto_transformed.csv"
DB_PATH = f"{DATA_DIR}/crypto_data.db"

def extract_crypto_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd,inr"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    with open(JSON_PATH, "w") as f:
        json.dump(response.json(), f)

def transform_crypto_data():
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    records = []
    timestamp = datetime.utcnow().isoformat()

    for coin, prices in data.items():
        for currency, price in prices.items():
            records.append({
                "coin": coin,
                "currency": currency,
                "price": price,
                "timestamp": timestamp
            })

    df = pd.DataFrame(records)
    df.to_csv(CSV_PATH, index=False)

def load_to_sqlite():
    df = pd.read_csv(CSV_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("crypto_prices", conn, if_exists="append", index=False)
    conn.close()

default_args = {
    "owner": "gugan",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

with DAG(
    dag_id="crypto_etl_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["crypto"],
) as dag:

    extract = PythonOperator(
        task_id="extract_crypto_data",
        python_callable=extract_crypto_data,
    )

    transform = PythonOperator(
        task_id="transform_crypto_data",
        python_callable=transform_crypto_data,
    )

    load = PythonOperator(
        task_id="load_to_sqlite",
        python_callable=load_to_sqlite,
    )

    extract >> transform >> load

