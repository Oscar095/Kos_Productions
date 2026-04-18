import requests
import pandas as pd
from sqlalchemy import create_engine, text
import urllib
from dotenv import load_dotenv
import os
import pyodbc
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Cargar variables del archivo .env
load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")
API_OP_NUMEROS = os.getenv("API_OP_NUMEROS")
API_EXISTENCIAS = os.getenv("API_EXISTENCIAS")

params = urllib.parse.quote_plus(
    "DRIVER=ODBC Driver 17 for SQL Server;"
    "SERVER=myappskos.database.windows.net;"
    "DATABASE=kos_apps;"
    "UID=kos;"
    "PWD=Ol38569824*;"
    "TrustServerCertificate=yes;"
    "Encrypt=yes;"
)

engine_str = f"mssql+pyodbc:///?odbc_connect={params}"
engine = create_engine(engine_str)

headers = {
        "ConniKey": CONNI_KEY,
        "ConniToken": CONNI_TOKEN
    }

def fetch_data(base_url):
    """Recorre todas las páginas del API y devuelve un DataFrame completo."""
    all_data = []
    page = 1
    tamPage = 100

    while True:
        # paginated_url = base_url.split("numPag=")[0] + f"numPag={page}|tamPag=100"
        # resp = requests.get(paginated_url, headers=headers, timeout=30)
        # resp.raise_for_status()

        API_URL_BASE = base_url.split("?")[0]
        API_QUERY_PARAMS = base_url.split("?")[1]

        query_params = API_QUERY_PARAMS.replace("numPag=1", f"numPag={page}")
        url = f"{API_URL_BASE}?{query_params}"

        print(f"Consultando página {page}...")

        response = requests.get(url, headers=headers, timeout=30)

        data = response.json()

        # Extrae los datos
        page_data=data["detalle"]["Datos"]

        all_data.extend(page_data)

        total_paginas= data['detalle']['total_páginas']
        pagina= data['detalle']['página_actual']
        
        if not page_data:
            break  # Si no hay datos, termina el bucle
        
        if len(page_data) < tamPage:
            print(f"Última página ({page}) con {len(page_data)} registros.")
            break  # Ya no hay más páginas

        if pagina==total_paginas :
            break

        page += 1
        
    df=pd.DataFrame(all_data)    
    print(f"Total registros descargados: {len(df)}")
    return df


def parse_siesa_date(series):
    return pd.to_datetime(series, format="%Y-%m-%dT%H:%M:%S", errors="coerce")


def main():
    try:
        df_op = fetch_data(API_OP_NUMEROS)
        df_op = df_op.drop("LineaRegistro", axis=1)

        if "f851_fecha_terminacion" in df_op.columns:
            df_op["f851_fecha_terminacion"] = parse_siesa_date(df_op["f851_fecha_terminacion"])

        df_existencias = fetch_data(API_EXISTENCIAS)
        df_existencias = df_existencias.drop("LineaRegistro", axis=1)

        with engine.begin() as conn_dest:
            conn_dest.execute(text("DELETE FROM op_numeros"))
            conn_dest.execute(text("DBCC CHECKIDENT ('op_numeros', RESEED, 0)"))

            conn_dest.execute(text("DELETE FROM existencias"))
            conn_dest.execute(text("DBCC CHECKIDENT ('existencias', RESEED, 0)"))

        df_op.to_sql("op_numeros", con=engine, if_exists='append', index=False, chunksize=500)
        df_existencias.to_sql("existencias", con=engine, if_exists='append', index=False, chunksize=500)

        logging.info("Datos cargados correctamente en Azure SQL: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    except Exception as e:
        logging.error("Error en actualizar-consultas: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    main()
