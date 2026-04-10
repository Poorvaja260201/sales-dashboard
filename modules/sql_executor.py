import sqlite3
import pandas as pd

def run_sql(query):
    conn = sqlite3.connect("database.db")

    df = pd.read_sql(query, conn)

    conn.close()

    return df
