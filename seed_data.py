import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
import os
from sqlalchemy import create_engine

PG_CONN_STR = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
SQLITE_DB_PATH = "data/crypto_data.db"
COINS = ["bitcoin", "ethereum", "solana", "binancecoin", "ripple"]
CURRENCIES = ["usd", "inr"]

def generate_dummy_data():
    records = []
    now = datetime.utcnow()
    # Generate data for the last 3 days, every 15 mins
    timestamps = [now - timedelta(minutes=15 * i) for i in range(288)] # 288 * 15 mins = 3 days
    
    # Base prices to simulate somewhat realistic data
    base_prices = {
        "bitcoin": 60000,
        "ethereum": 3000,
        "solana": 150,
        "binancecoin": 600,
        "ripple": 0.5
    }
    
    for ts in timestamps:
        for coin in COINS:
            # Random walk for price
            base_prices[coin] = base_prices[coin] * (1 + random.uniform(-0.005, 0.005))
            for currency in CURRENCIES:
                price = base_prices[coin]
                if currency == "inr":
                    price *= 83.5 # dummy conversion rate
                
                records.append({
                    "coin": coin,
                    "currency": currency,
                    "price": round(price, 2),
                    "timestamp": ts.isoformat()
                })
    
    return pd.DataFrame(records)

def seed_database():
    df = generate_dummy_data()
    print(f"Generated {len(df)} records.")
    
    # Try Postgres first
    try:
        engine = create_engine(PG_CONN_STR)
        with engine.connect() as conn:
            pass
        print("Connected to Postgres successfully.")
        df.to_sql("crypto_prices", engine, if_exists="append", index=False)
        print("Data seeded to Postgres.")
        return
    except Exception as e:
        print(f"Postgres connection failed: {e}. Trying SQLite.")
    
    # Fallback to SQLite
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    df.to_sql("crypto_prices", conn, if_exists="append", index=False)
    conn.close()
    print("Data seeded to SQLite.")

if __name__ == "__main__":
    seed_database()
