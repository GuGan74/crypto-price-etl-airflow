# 🚀 Automated Crypto Price ETL Pipeline using Apache Airflow & Docker

## 📌 Project Overview
This project implements an **end-to-end ETL (Extract, Transform, Load) pipeline** to automatically collect live cryptocurrency prices, transform the data into a structured format, and store it in a database for analysis.

The pipeline is orchestrated using **Apache Airflow**, containerized using **Docker**, and scheduled to run on a daily basis.

This project demonstrates **real-world Data Engineering concepts**, including workflow orchestration, task dependencies, scheduling, API integration, and containerized deployment.

---

## 🏗️ Architecture

**ETL Flow:**

1. **Extract**
   - Fetches live cryptocurrency price data from a public API
   - Saves raw data as JSON

2. **Transform**
   - Cleans and restructures the raw JSON data
   - Converts it into a CSV format

3. **Load**
   - Loads the transformed data into a **SQLite database**

**Orchestration**
- Apache Airflow manages task execution and dependencies
- Docker ensures a consistent and reproducible runtime environment

---

## 🧰 Tech Stack

| Category | Tools |
|--------|------|
| Orchestration | Apache Airflow 2.10 |
| Containerization | Docker, Docker Compose |
| Programming Language | Python |
| Data Processing | Pandas |
| Database | SQLite |
| API | Public Cryptocurrency API |

---

## 📁 Project Structure

crypto-price-etl-airflow/
├── dags/
│ └── crypto_dag.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore



> Runtime-generated folders such as `data/`, `airflow-webserver/`, `airflow-scheduler/` are excluded from Git.

---

## ⚙️ DAG Details

- **DAG Name:** `crypto_etl_pipeline`
- **Schedule:** `@daily`
- **Executor:** LocalExecutor
- **Tasks:**
  1. `extract_crypto_data`
  2. `transform_crypto_data`
  3. `load_to_sqlite`

Each task runs sequentially and depends on the successful completion of the previous task.

---

## ▶️ How to Run the Project

### 1️⃣ Prerequisites
Ensure the following are installed:
- Docker
- Docker Compose
- Git

---

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/GuGan74/crypto-price-etl-airflow.git
cd crypto-price-etl-airflow
```
---
###3️⃣ Start Airflow Using Docker
docker-compose up -d

---
###4️⃣ Access Airflow Web UI

http://localhost:8080

##Login Credentials:
**Username: airflow
Password: airflow
**
----
###5️⃣ Run the DAG

Enable the DAG crypto_etl_pipeline

Trigger it manually or wait for the scheduled run

---
###📊 Output Files

After a successful DAG execution, the following files are generated:

| File                     | Description                              |
| ------------------------ | ---------------------------------------- |
| `crypto_data.json`       | Raw extracted API data                   |
| `crypto_transformed.csv` | Cleaned and structured data              |
| `crypto_data.db`         | SQLite database containing crypto prices |


----
###Key Learnings

Building ETL pipelines using Apache Airflow

Writing production-ready DAGs

Managing task dependencies and retries

Dockerizing data pipelines

Handling Airflow database initialization

Debugging Airflow scheduler and webserver issues

---
👤 Author

Gugan
Computer Science Engineering Student
Aspiring Data Engineer / Data Analyst
