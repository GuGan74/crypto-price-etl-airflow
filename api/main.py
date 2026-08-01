from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sqlalchemy import create_engine
import sqlite3
import os

app = FastAPI(title="CryptoPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection paths/URLs
PG_CONN_STR = "postgresql+psycopg2://airflow:airflow@postgres/airflow"
SQLITE_DB_PATH = "/opt/airflow/data/crypto_data.db"

def get_df_from_db(query: str, params=None):
    try:
        engine = create_engine(PG_CONN_STR)
        with engine.connect() as conn:
            return pd.read_sql(query, conn, params=params)
    except Exception as e:
        print(f"Postgres failed: {e}. Trying SQLite.")
        if os.path.exists(SQLITE_DB_PATH):
            conn = sqlite3.connect(SQLITE_DB_PATH)
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            return df
        else:
            # For local testing when SQLite isn't in /opt/airflow/data
            local_sqlite = "../data/crypto_data.db"
            if os.path.exists(local_sqlite):
                conn = sqlite3.connect(local_sqlite)
                df = pd.read_sql(query, conn, params=params)
                conn.close()
                return df
            raise Exception("Database connection failed for both Postgres and SQLite")

@app.get("/prices/latest")
def get_latest_prices():
    query = """
    SELECT * FROM crypto_prices
    WHERE timestamp = (SELECT MAX(timestamp) FROM crypto_prices)
    """
    try:
        df = get_df_from_db(query)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prices/history")
def get_price_history(coin: str, hours: int = 24):
    query = """
    SELECT * FROM crypto_prices
    WHERE coin = %(coin)s
    ORDER BY timestamp DESC
    """
    # SQLite uses ?, Postgres via sqlalchemy uses %(name)s.
    # To handle both simply with pandas read_sql, we'll fetch all for the coin and limit/filter in python.
    # We could write separate queries but this is easier for MVP
    try:
        df = get_df_from_db(f"SELECT * FROM crypto_prices WHERE coin = '{coin}' ORDER BY timestamp DESC")
        if df.empty:
            return []
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = df['timestamp'].max() - pd.Timedelta(hours=hours)
        df_filtered = df[df['timestamp'] >= cutoff]
        df_filtered = df_filtered.sort_values(by='timestamp')
        return df_filtered.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/{coin}")
def get_signals(coin: str):
    try:
        df = get_df_from_db(f"SELECT * FROM crypto_prices WHERE coin = '{coin}' ORDER BY timestamp ASC")
        if df.empty or len(df) < 20:
            return {"signal": "hold"}
            
        df['price'] = df['price'].astype(float)
        
        # Compute Simple Moving Averages (5-period and 20-period)
        df['sma_5'] = df['price'].rolling(window=5).mean()
        df['sma_20'] = df['price'].rolling(window=20).mean()
        
        latest = df.iloc[-1]
        
        if pd.isna(latest['sma_5']) or pd.isna(latest['sma_20']):
             return {"signal": "hold"}
             
        if latest['sma_5'] > latest['sma_20']:
            return {"signal": "buy"}
        elif latest['sma_5'] < latest['sma_20']:
            return {"signal": "sell"}
        else:
            return {"signal": "hold"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
