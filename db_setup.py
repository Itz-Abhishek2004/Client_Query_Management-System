from datetime import datetime

import mysql.connector
import pandas as pd

csv_path = "synthetic_client_queries.csv"


db_config = {
    "host": "localhost",
    "user": "root",          
    "password": "Abhi@2026", 
    "database": "client_query_db"
}


df = pd.read_csv(csv_path)


df = df.rename(columns={
    "mail_id": "client_email",
    "mobile_number": "client_mobile",
    "query_created_time": "date_raised",
    "query_closed_time": "date_closed"
})


df["date_raised"] = pd.to_datetime(df["date_raised"], errors="coerce")
df["date_closed"] = pd.to_datetime(df["date_closed"], errors="coerce")


conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

insert_query = """
    INSERT INTO client_queries
    (query_id, client_email, client_mobile, query_heading, query_description, status, date_raised, date_closed)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


for _, row in df.iterrows():
    cursor.execute(
        insert_query,
        (
            row["query_id"],
            row["client_email"],
            str(row["client_mobile"]),
            row["query_heading"],
            row["query_description"],
            row["status"],
            row["date_raised"],
            row["date_closed"] if not pd.isna(row["date_closed"]) else None
        )
    )

conn.commit()
cursor.close()
conn.close()

print("Data load complete into MySQL.")
