# Automated Crypto Price ETL Pipeline using Apache Airflow & SQLite

This project automates the extraction, transformation, and loading (ETL) of live cryptocurrency prices (Bitcoin & Ethereum) using Apache Airflow.  
It fetches data from the CoinGecko API, transforms it using Pandas, stores it in SQLite, and schedules the pipeline to run daily.

---

## Features

- Automated ETL with Airflow DAG
- Extract live crypto prices (BTC, ETH)
- Transform JSON → CSV (clean tabular format)
- Load into SQLite for historical storage
- Daily scheduling using Airflow
- Ready for visualization (Power BI, Tableau, Streamlit)

---

## Project Structure
crypto-price-etl-airflow/
│
├── dags/
│ └── crypto_dag.py
│
├── data/
│ ├── crypto_data.json
│ ├── crypto_transformed.csv
│ └── crypto_data.db
│
├── README.md
└── requirements.txt


---

## Installation

### 1. Create Virtual Environment

python3 -m venv airflow-venv
source airflow-venv/bin/activate
pip install -r requirements.txt


### 2. Initialize Airflow
airflow db init


### 3. Start Services

airflow scheduler
airflow webserver --port 8080


### 4. Trigger the DAG from Airflow UI  
Open: http://localhost:8080  
Enable and trigger: `crypto_etl_pipeline`

---

## Output Files

| File | Description |
|------|-------------|
| `crypto_data.json` | Raw API response |
| `crypto_transformed.csv` | Cleaned transformed data |
| `crypto_data.db` | SQLite database storing prices |

---

## Requirements



---

## Future Enhancements
- Add more cryptocurrencies
- Dockerize Airflow setup
- Add alerts (Telegram/Email)
- Build a Streamlit dashboard
- Visualize with Power BI

---

Created By: **Gugan S**
