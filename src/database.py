import sqlite3
import pandas as pd
from .config import DATA_PATH, DB_PATH

def create_connection():
    return sqlite3.connect(DB_PATH)

def load_csv_to_sqlite():
    df = pd.read_csv(DATA_PATH)
    with create_connection() as conn:
        df.to_sql("sales", conn, if_exists="replace", index=False)
    return len(df)

def query(sql: str) -> pd.DataFrame:
    with create_connection() as conn:
        return pd.read_sql_query(sql, conn)
