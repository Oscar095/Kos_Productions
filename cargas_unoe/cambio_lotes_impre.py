import requests
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import urllib

load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")
API_EXISTENCIAS_019 = os.getenv("API_EXISTENCIAS_019")
API_CAMBIAR_LOTES =os.getenv("API_CAMBIAR_LOTES")

headers = {
        "ConniKey": CONNI_KEY,
        "ConniToken": CONNI_TOKEN
    }

def lote(id_lote): #Encontrar Lote de OP a buscar
    
    # df["lote"] = df["lote"].astype(str).str.strip()
    # lote_item=df["lote"].values[0]

    #Conexion a la base de datos
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

    with engine.connect() as conn:
        query = text("""
            SELECT *                
            FROM existencias_lote_019
        """)
        df_existencias_lote = pd.read_sql(query, conn) # Tabla de inventarios

    df_existencias_lote["lote"]=df_existencias_lote["lote"].astype(str).str.strip()
    item = df_existencias_lote.loc[df_existencias_lote["lote"]==id_lote,"id_item"].values[0]

    return item


def cambiar_lotes(lote_rollo):
    
    item=lote(lote_rollo)
    print(item)

    # payload= {
    #     "id_item": int(item)
    # }

    # try:
    #     response = requests.post(API_CAMBIAR_LOTES, json=payload, headers=headers)

    #     if response.status_code == 200:
    #         print("Lote cambiado correctamente")
    #     else:
    #         print(f"Error API: {response.status_code} - {response.text}")

    # except Exception as e:
    #     print(f"Excepción en envío del ID: {e}")


