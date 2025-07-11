import requests
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import urllib
from eliminar_comp import componente, eliminar_lote
import datetime

load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")
API_EXISTENCIAS_019 = os.getenv("API_EXISTENCIAS_019")
API_CAMBIAR_LOTES = os.getenv("API_CAMBIAR_LOTES")
CREAR_LOTES = os.getenv("CREAR_LOTES")

headers = {
        "ConniKey": CONNI_KEY,
        "ConniToken": CONNI_TOKEN
    }

def lote(id_lote): #Encontrar Lote de OP a buscar

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
        df_existencias_lote = pd.read_sql(query, conn) # Tabla de inventarios de rollos

    df_existencias_lote["lote"]=df_existencias_lote["lote"].astype(str).str.strip()
    item = df_existencias_lote.loc[df_existencias_lote["lote"]==id_lote,"id_item"].values[0]

    return item

def lote_bodega(id_lote): #Encontrar Lote de OP a buscar

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
        df_existencias_lote = pd.read_sql(query, conn) # Tabla de inventarios de rollos

    df_existencias_lote["lote"]=df_existencias_lote["lote"].astype(str).str.strip()
    item_lote_comp_bodega = df_existencias_lote.loc[df_existencias_lote["lote"]==id_lote,"bodega"].values[0]

    if item_lote_comp_bodega == 1 :
        item_lote_comp_bodega = "019"
    elif item_lote_comp_bodega == 5:
        item_lote_comp_bodega = "026"
    else:
        item_lote_comp_bodega = "026"

    return item_lote_comp_bodega


def crear_lote(lote_com,item_padre,ext1, ext2):
    
    fecha = datetime.datetime.now()

    payload = {
        "Versión": [
            {
            "f403_id": str(lote_com),
            "f403_id_item": int(item_padre),
            "f403_id_ext1_detalle": str(ext1),
            "f403_id_ext2_detalle": str(ext2),
            "f403_fecha_creacion": str(fecha.strftime('%Y%m%d')),
            "f403_fecha_vcto": str(fecha.strftime('%Y%m%d'))
            }
        ]
        }
    
    try:
        response = requests.post(CREAR_LOTES, json=payload, headers=headers)

        if response.status_code == 200:
            print("Lote creado item padre") #Cargar el nuevo item del lote
        else:
            print(f"Error API: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Excepción en envío del ID: {e}")


def cambiar_lotes(lote_rollo,ext1,ext2,cant,docto,item_padre):
    
    item=lote(lote_rollo) #Item del lote agregado desde registro produccion
    item_compo_delete=componente(docto,item_padre) #Buscar el item del componente predeterminado


    payload= {

        "Movimientos Versión": [
            {
            "F_ACTUALIZA_REG": "0",
            "f850_id_tipo_docto_op": "OPK",
            "f850_consec_docto_op": int(docto),
            "f860_id_item_op": int(item_padre),
            "f860_referencia_item_op": "",
            "f860_codigo_barras_item_op": "",
            "f851_id_ext1_detalle_item_op": str(ext1),
            "f851_id_ext2_detalle_item_op": str(ext2),
            "f860_numero_operacion": "0",
            "f860_id_bodega": "029",
            "f860_id_item_comp": int(item),
            "f860_referencia_item_comp": "",
            "f860_codigo_barras_item_comp": "",
            "f851_id_ext1_detalle_item_comp": "",
            "f851_id_ext2_detalle_item_comp": "",
            "f860_cant_requerida_base": int(cant),
            "f860_cant_requerida_2": "0",
            "f860_notas": ""
            }
        ]  
            }

    try:
        response = requests.post(API_CAMBIAR_LOTES, json=payload, headers=headers)

        if response.status_code == 200:
            print("Lote cambiado correctamente") #Cargar el nuevo item del lote
            eliminar_lote (item_padre,ext1,ext2,docto,item_compo_delete) #Eliminar el item predeterminado de la OP
        else:
            print(f"Error API: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Excepción en envío del ID: {e}")

