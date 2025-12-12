"""
Robust crypto_etl_pipeline DAG.
Uses AIRFLOW_HOME/data if present, otherwise falls back to ~/airflow/data.
This version logs errors and avoids hard-coded absolute paths.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import json
import pandas as pd
import sqlite3
import os
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Data folder: prefer AIRFLOW_HOME/data, then ~/airflow/data, then ./data
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", os.path.expanduser("~/airflow"))
DATA_DIR = os.path.join(AIRFLOW_HOME, "data")
os.makedirs(DATA_DIR, exist_ok=True)

RAW_PATH = os.path.join(DATA_DIR, "crypto_data.json")
CSV_PATH = os.path.join(DATA_DIR, "crypto_transformed.csv")
DB_PATH = os.path.join(DATA_DIR, "crypto_data.db")

def extract_crypto_prices(**context):
    """Fetch prices for bitcoin and ethereum from CoinGecko and save JSON."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd,inr"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        with open(RAW_PATH, "w") as f:
            json.dump(data, f)
        logger.info("Extracted data saved to %s", RAW_PATH)
    except Exception as e:
        logger.exception("Failed to extract crypto prices: %s", e)
        # Re-raise so Airflow marks the task as failed
        raise

def transform_crypto_data(**context):
    """Read raw JSON and write transformed CSV records."""
    try:
        with open(RAW_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error("Raw file not found: %s", RAW_PATH)
        raise
    except Exception as e:
        logger.exception("Error reading raw JSON: %s", e)
        raise

    try:
        records = []
        timestamp = datetime.now().isoformat()
        for coin, prices in data.items():
            # prices is e.g. {"usd": 123.45, "inr": 10000}
            for currency, value in prices.items():
                records.append({
                    "coin": coin,
                    "currency": currency,
                    "price": value,
                    "timestamp": timestamp
                })
        df = pd.DataFrame(records)
        df.to_csv(CSV_PATH, index=False)
        logger.info("Transformed CSV saved to %s", CSV_PATH)
    except Exception as e:
        logger.exception("Failed to transform data: %s", e)
        raise

def load_to_sqlite(**context):
    """Load CSV into SQLite table crypto_prices (append)."""
    try:
        df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        logger.error("Transformed CSV not found: %s", CSV_PATH)
        raise
    except Exception as e:
        logger.exception("Error reading CSV: %s", e)
        raise

    try:
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("crypto_prices", conn, if_exists="append", index=False)
        conn.close()
        logger.info("Loaded %d rows into SQLite: %s", len(df), DB_PATH)
    except Exception as e:
        logger.exception("Failed to load into SQLite: %s", e)
        raise

# DAG configuration
default_args = {
    "owner": "gugan",
    "start_date": datetime(2023, 1, 1),
}

with DAG(
    dag_id="crypto_etl_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["crypto"]
) as dag:

    t1 = PythonOperator(
        task_id="extract_crypto_data",
        python_callable=extract_crypto_prices,
        provide_context=True,
    )

    t2 = PythonOperator(
        task_id="transform_crypto_data",
        python_callable=transform_crypto_data,
        provide_context=True,
    )

    t3 = PythonOperator(
        task_id="load_to_sqlite",
        python_callable=load_to_sqlite,
        provide_context=True,
    )

    t1 >> t2 >> t3

