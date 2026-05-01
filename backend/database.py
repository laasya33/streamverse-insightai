import sqlite3
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "streamverse.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

TABLES = [
    "movies", "viewers", "watch_activity",
    "reviews", "marketing_spend", "regional_performance"
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    for table in TABLES:
        csv_path = os.path.join(DATA_DIR, f"{table}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df.to_sql(table, conn, if_exists="replace", index=False)
            logger.info(f"Loaded {len(df)} rows into table '{table}'")
        else:
            logger.warning(f"CSV not found: {csv_path}")
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def run_query(sql: str, params: tuple = ()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
        conn.close()
        return {"columns": columns, "rows": [dict(r) for r in rows]}
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise ValueError(f"SQL error: {str(e)}")

def get_schema():
    conn = get_connection()
    schema = {}
    for table in TABLES:
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            cols = cursor.fetchall()
            schema[table] = [{"name": c[1], "type": c[2]} for c in cols]
        except:
            pass
    conn.close()
    return schema
