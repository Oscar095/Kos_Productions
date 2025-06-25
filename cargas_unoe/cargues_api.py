import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import urllib
from datetime import datetime
import pyodbc
import os
import logging

# Configurar logging
logging.basicConfig(
    filename="envio_siesa.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Cargar variables del archivo .env
load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")

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

headers = {
        "ConniKey": CONNI_KEY,
        "ConniToken": CONNI_TOKEN
    }

API_URL = os.getenv("API_CARGUES_SIESA") #Falta cambiar la URL

def enviar_datos_a_siesa():
    # try:
        # 1. Leer registros pendientes
        with engine.connect() as conn:
            query = text("""
                SELECT
                    rp.Id id,
                    rp.numero_op Docto,
                    rp.fecha Fecha,
                    rp.produccion Cantidad,
                    m.nombre Maquina,
                    pp.nombre_operario operario,
                    cc.centro 'Centro de Trabajo',
                    cc.tipo_inv tipo_inv,
                    cc.und und
                FROM registro_produccion rp
                    LEFT JOIN maquinas m ON rp.maquina = m.Id
                    LEFT JOIN personal_planta pp ON rp.operario= pp.Id
                    LEFT JOIN centro_costos cc on m.centro_costos_id = cc.Id
                WHERE registro_siesa = 0
            """)
            df = pd.read_sql(query, conn)

            query_ops =text("""
                    SELECT *    
                    FROM op_numeros           
            """)
            df_op = pd.read_sql(query_ops,conn)
            df_op["und_medida"] = df_op["und_medida"].astype(str).str.strip()

        if df.empty:
            logging.info("No hay registros pendientes.")
            return

        # 2. Procesar cada registro
        with engine.begin() as conn:  # begin => commit automático
            for _, row in df.iterrows():

                try:

                    filtro = (
                    (df_op["docto"] == row["Docto"]) &
                    (df_op["tipo_inv"] == row["tipo_inv"]) &
                    (df_op["und_medida"] == row["und"])
                    )

                    if df_op.loc[filtro].empty:
                        print(f"No se encontraron resultados para Docto {row['Docto']}")
                        continue  # Salta a la siguiente fila

                    item=df_op.loc[filtro,"item"].values[0]
                    lote=df_op.loc[filtro,"lote"].values[0]
                    ext1=df_op.loc[filtro,"ext1"].values[0]
                    ext2=df_op.loc[filtro,"ext2"].values[0]
                    bodega=df_op.loc[filtro,"bodega"].values[0]
                except Exception as e:
                    print(f"No se encontraron resultados {row['Docto']} : {e}")
                    continue

                payload = {
                    #Documento
                        "f350_id_tipo_docto": "EPP",
                        "f350_consec_docto": 1,
                        "f350_fecha": row["Fecha"].strftime('%Y%m%d') if isinstance(row["Fecha"], datetime) else row["Fecha"],
                        "f350_notas": row["operario"]+" "+row["Maquina"],
                    #Movimiento
                        "f470_id_tipo_docto": "OPK",
                        "f470_consec_docto": 1,
                        "f470_nro_registro": 1,
                        "f850_consec_docto": row["Docto"],
                        "f470_id_item": item,
                        "f470_referencia_item": "",
                        "f470_codigo_barras": "",
                        "f470_id_ext1_detalle": ext1,
                        "f470_id_ext2_detalle": ext2,
                        "f470_id_bodega": bodega,
                        "f470_id_lote": lote,
                        "f470_cant_base_entrega": row["Cantidad"]
                        }
                
                print(payload)

                # try:
                #     response = requests.post(API_URL, json=payload, headers=headers)

                #     if response.status_code == 200:
                #         # Marcar registro como enviado
                #         conn.execute(
                #             text("UPDATE registros_produccion SET registros_siesa = 1 WHERE id = :id"),
                #             {"id": row["id"]}
                #         )
                #         logging.info(f"Registro ID {row['id']} enviado y actualizado.")
                #     else:
                #         logging.error(f"Error API para ID {row['id']}: {response.status_code} - {response.text}")

                # except Exception as e:
                #     logging.exception(f"Excepción en envío del ID {row['id']}: {e}")

    # except Exception as e:
    #     print("error")
    #     logging.exception("Error general al ejecutar el proceso.")

if __name__ == "__main__":
    enviar_datos_a_siesa()

