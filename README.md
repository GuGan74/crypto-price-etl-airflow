# 🚀 CryptoPulse Trading Dashboard (formerly Crypto Price ETL Pipeline)

## 📌 Project Overview
CryptoPulse is a live crypto price dashboard built on top of an automated **ETL (Extract, Transform, Load) pipeline**. It collects live cryptocurrency prices from the CoinGecko API, stores them in a Postgres database, and serves them via a FastAPI backend to a sleek React trading dashboard.

The pipeline is orchestrated using **Apache Airflow**, containerized using **Docker**, and scheduled to run every 15 minutes. The frontend provides real-time charting and trading signals (Buy/Sell/Hold) based on simple moving average (SMA) crossovers.

---

## 🏗️ Architecture

**1. Data Pipeline (Airflow ETL):**
   - **Extract:** Fetches live price data for BTC, ETH, SOL, BNB, XRP from CoinGecko.
   - **Transform:** Cleans and restructures the JSON data into tabular format.
   - **Load:** Loads the data into a **PostgreSQL database** (with a fallback to SQLite for local development without Docker).

**2. Backend API (FastAPI):**
   - Connects to Postgres and provides REST endpoints for latest prices, historical data, and trading signals.

**3. Frontend Dashboard (React + Vite):**
   - Polls the API every 30 seconds to update charts and trading signals.
   - Features a clean, dark-mode trading aesthetic.

**Flow:** Airflow ETL ➡️ Postgres ➡️ FastAPI ➡️ React Dashboard

---

## 🧰 Tech Stack

| Category | Tools |
|--------|------|
| Orchestration | Apache Airflow 2.10 |
| Backend API | FastAPI, Python |
| Frontend | React, Vite, Recharts, Tailwind/Vanilla CSS |
| Database | PostgreSQL (Primary), SQLite (Fallback) |
| Containerization | Docker, Docker Compose |
| Data Processing | Pandas |

---

## 📁 Project Structure

```text
crypto-price-etl-airflow/
├── api/                  # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/            # React + Vite frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── dags/                 # Airflow DAGs
│   └── crypto_dag.py
├── seed_data.py          # Script to generate dummy historical data
├── docker-compose.yml    # Orchestrates Postgres, Airflow, API, and Dashboard
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run the Project

### 1️⃣ Prerequisites
Ensure the following are installed:
- Docker
- Docker Compose
- Git

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/GuGan74/crypto-price-etl-airflow.git
cd crypto-price-etl-airflow
```

### 3️⃣ Start the Stack Using Docker
Bring up Airflow, Postgres, the FastAPI backend, and the React Dashboard:
```bash
docker-compose up -d --build
```

### 4️⃣ Access the Services

- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Airflow Web UI:** [http://localhost:8080](http://localhost:8080) (Username: `airflow` / Password: `airflow`)

### 5️⃣ Seed the Database (Optional but recommended)
To see charts and signals immediately without waiting for the 15-minute DAG cycles, you can seed the database with historical data:
```bash
python seed_data.py
# Note: You may need to install pandas and sqlalchemy locally, or run this script inside the API container.
```

### 6️⃣ Run the DAG
In the Airflow Web UI, enable the DAG `crypto_etl_pipeline`. It will run every 15 minutes automatically, keeping your dashboard updated!

---
👤 Author

Gugan
Computer Science Engineering Student
Aspiring Data Engineer / Data Analyst
