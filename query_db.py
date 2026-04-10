import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")

query = """
SELECT Country, SUM(Revenue) as total_revenue
FROM sales
GROUP BY Country
ORDER BY total_revenue DESC
"""

df = pd.read_sql(query, conn)

print(df)

conn.close()
