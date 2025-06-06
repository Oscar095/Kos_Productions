import requests
import pandas as pd
from sqlalchemy import create_engine, text
import urllib
from dotenv import load_dotenv
import os
import pyodbc


# Cargar variables del archivo .env
load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")
API_OP_NUMEROS = os.getenv("API_OP_NUMEROS")
API_EXISTENCIAS = os.getenv("API_EXISTENCIAS")


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


def fetch_data(base_url: str) -> pd.DataFrame:
    """Recorre todas las páginas del API y devuelve un DataFrame completo."""
    all_data = []
    page = 1
    headers = {
        "connekta-key": os.getenv("CONNI_KEY"),
        "Authorization": f"Bearer {os.getenv('CONNI_TOKEN')}"
    }

    while True:
        paginated_url = base_url.split("numPag=")[0] + f"numPag={page}|tamPag=100"
        resp = requests.get(paginated_url, headers=headers, timeout=30)
        resp.raise_for_status()

        # Extrae los datos
        page_data = resp.json().get("Datos", []) 
        if not page_data:
            break  # Si no hay datos, termina el bucle

        all_data.extend(page_data)
        
        if len(page_data) < 100:
            break  # Ya no hay más páginas

        page += 1

    return pd.DataFrame(all_data)



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
