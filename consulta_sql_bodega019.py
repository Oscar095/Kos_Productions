import requests
import pandas as pd
from sqlalchemy import create_engine, text
import urllib
from dotenv import load_dotenv
import os
import pyodbc
from datetime import datetime

# Cargar variables del archivo .env
load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")
API_EXISTENCIAS_019 = os.getenv("API_EXISTENCIAS_019")

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


def main():
    df = fetch_data(API_EXISTENCIAS_019)
    df = df.drop("LineaRegistro",axis=1)  

    with engine.begin() as conn_dest:
    # Eliminar los datos de ambas tablas
        conn_dest.execute(text("DELETE FROM existencias_lote_019"))
        conn_dest.execute(text("DBCC CHECKIDENT ('existencias_lote_019', RESEED, 0)"))

    df.to_sql("existencias_lote_019", con=engine, if_exists='append', index=False, chunksize=500)

    print("Datos cargados correctamente en Azure SQL: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
