import pandas as pd
import psycopg2
from environment import DB_PASS, DB_HOST


def load_all_data():
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password=DB_PASS,
        host=DB_HOST,
    )
    all_data = pd.read_sql(
        "SELECT * FROM weatherstation.records WHERE station_name = 'CBHOME'",
        conn,
    )

    all_data["year"] = all_data["inserted_at"].dt.year
    all_data["month"] = all_data["inserted_at"].dt.month

    return all_data
