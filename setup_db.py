import pandas as pd
import sqlite3

# Load CSV
df = pd.read_csv("data/sales_data.csv")

# Connect to SQLite
conn = sqlite3.connect("database.db")

# Write table
df.to_sql("sales", conn, if_exists="replace", index=False)

conn.close()

print("✅ Database created successfully")
