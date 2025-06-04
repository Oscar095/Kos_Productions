import requests
import pandas as pd
from sqlalchemy import create_engine, text
import urllib

# API endpoints to fetch data from AWS service
API_OP_NUMEROS = "https://example.com/api/op-numeros"
API_EXISTENCIAS = "https://example.com/api/existencias"

params = urllib.parse.quote_plus(
    "DRIVER=ODBC Driver 18 for SQL Server;"
    "SERVER=myappskos.database.windows.net;"
    "DATABASE=kos_apps;"
    "UID=kos;"
    "PWD=Ol38569824*;"
    "TrustServerCertificate=yes;"
    "Encrypt=yes;"
)

engine_str = f"mssql+pyodbc:///?odbc_connect={params}"
engine = create_engine(engine_str)


def fetch_data(url: str) -> pd.DataFrame:
    """Request data from the given API endpoint and return a DataFrame."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pd.DataFrame(resp.json())


def main() -> None:
    df_op = fetch_data(API_OP_NUMEROS)
    df_existencias = fetch_data(API_EXISTENCIAS)

    with engine.begin() as conn_dest:
        conn_dest.execute(text("DELETE FROM op_numeros"))
        conn_dest.execute(text("DELETE FROM existencias"))

    df_op.to_sql("op_numeros", con=engine, if_exists='append', index=False, chunksize=500)
    df_existencias.to_sql("existencias", con=engine, if_exists='append', index=False, chunksize=500)

    print("Datos cargados correctamente en Azure SQL.")


if __name__ == "__main__":
    main()
