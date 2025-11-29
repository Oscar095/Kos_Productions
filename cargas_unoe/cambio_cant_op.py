import logging
import requests
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import urllib
from eliminar_comp import componente
from cambio_lotes_impre import cant_componente_op
import subprocess

load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")

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

API_URL = os.getenv("API_CAMBIAR_LOTES") #Permite modificar Componentes en OP

def cambiar_componente():

    #subprocess.run(["python", "consulta_sql_bodega019.py"])

    try:
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
                    cc.und und,
                    rp.resultado_siesa
                FROM registro_produccion rp
                    LEFT JOIN maquinas m ON rp.maquina = m.Id
                    LEFT JOIN personal_planta pp ON rp.operario= pp.Id
                    LEFT JOIN centro_costos cc on m.centro_costos_id = cc.Id
                WHERE registro_siesa = 3
            """)
            df = pd.read_sql(query, conn)
            df["resultado_siesa"] = df["resultado_siesa"].astype(str).str.strip()

            query_ops = text("SELECT * FROM op_numeros")
            df_op = pd.read_sql(query_ops, conn)
            df_op["und_medida"] = df_op["und_medida"].astype(str).str.strip()
            df_op["cant_pendiente"] = (df_op["cantidad"] - df_op["cant_consumida"]).where(df_op["cant_consumida"] < df_op["cantidad"], 0)

        if df.empty:
            print("No hay registros pendientes.")
            return

        # 2. Procesar cada registro
        with engine.begin() as conn:
            for _, row in df.iterrows():
                try:
                    filtro = (
                        (df_op["docto"] == row["Docto"]) &
                        (df_op["tipo_inv"] == row["tipo_inv"]) &
                        (df_op["und_medida"] == row["und"])
                    )

                    filtro_rollos = (
                        (df_op["docto"] == row["Docto"]) &
                        (df_op["tipo_inv"] == row["tipo_inv"]) &
                        (df_op["und_medida"] == "KG")
                    )    

                    if df_op.loc[filtro_rollos].empty:
                        print(f"No se encontraron polyboard imreso para Docto {row['Docto']}")
                        continue

                    if df_op.loc[filtro].empty:
                        print(f"No se encontraron resultados para Docto {row['Docto']}")
                        continue

                    print(f"Procesando Docto {row['Docto']}")

                    # Solo construir y enviar payload si la condición es válida
                    if row["resultado_siesa"] == "5-Argument 'Number' is not a valid value.":
                        item = df_op.loc[filtro, "id_item"].values[0]
                        ext1 = df_op.loc[filtro, "ext1"].values[0]
                        ext2 = df_op.loc[filtro, "ext2"].values[0]
                        lote = df_op.loc[filtro_rollos, "lote"].values[0]
                        #cantidad_comp_op = df_op.loc[filtro_rollos, "cantidad"].values[0] #Catidad Original del Componente en la OP
                        cantidad_OP = float(df_op.loc[filtro, "cantidad"].values[0]) #Cantidad original en la OP
                        cantidad_reporte = float(row["Cantidad"]) #Cantidad reportada en el registro
                        cantidad_pendiente = float(df_op.loc[filtro, "cant_pendiente"].values[0]) #Cantidad pendiente en la OP
                        cant_componente_op_req = df_op.loc[filtro_rollos, "cantidad"].values[0]
                        id_comp = componente(row["Docto"], item) #Buscar el item del componente predeterminado
                        cantidad_comp_op = float(cant_componente_op(ext1, ext2, id_comp)) #Cantidad inventario del componente en la OP
                        cantidad_pendiente_comp = float(df_op.loc[filtro_rollos, "cant_pendiente"].values[0]) #Cantidad pendiente del componente en la OP
                        kilos_requeridos = (cant_componente_op_req / cantidad_OP) * cantidad_reporte

                        print(f"Cantidad Componente OP: {cantidad_comp_op}, Cantidad OP: {cantidad_OP}, Cantidad Reporte: {cantidad_reporte}, item_comp: {id_comp}")

                        print(f"Kilos Requeridos: {kilos_requeridos}, Numero OP: {row['Docto']}")

                        if kilos_requeridos > cantidad_comp_op and cantidad_pendiente_comp < cantidad_comp_op:
                            nueva_cant_comp = (cantidad_comp_op * cantidad_OP) / cantidad_reporte
                        else:
                            nueva_cant_comp = cant_componente_op_req

                        payload = {
                            "Movimientos Versión": [
                                {
                                    "F_ACTUALIZA_REG": "1",
                                    "f850_id_tipo_docto_op": "OPK",
                                    "f850_consec_docto_op": int(row["Docto"]),
                                    "f860_id_item_op": int(item),
                                    "f860_referencia_item_op": "",
                                    "f860_codigo_barras_item_op": "",
                                    "f851_id_ext1_detalle_item_op": str(ext1),
                                    "f851_id_ext2_detalle_item_op": str(ext2),
                                    "f860_numero_operacion": 0,
                                    "f860_id_bodega": "026",
                                    "f860_id_item_comp": int(id_comp),
                                    "f860_referencia_item_comp": "",
                                    "f860_codigo_barras_item_comp": "",
                                    "f851_id_ext1_detalle_item_comp": str(ext1),
                                    "f851_id_ext2_detalle_item_comp": str(ext2),
                                    "f860_cant_requerida_base": float(nueva_cant_comp),
                                    "f860_cant_requerida_2": "0",
                                    "f860_notas": "Modificacion Cantidad"
                                }
                            ]
                        }

                        try:
                            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

                            if response.status_code == 200:
                                conn.execute(
                                    text("UPDATE registro_produccion SET registro_siesa = 0 WHERE id = :id"),
                                    {"id": row["id"]}
                                )
                                print(f"Registro ID {row['id']} enviado y actualizado.")
                            else:
                                conn.execute(
                                    text("UPDATE registro_produccion SET registro_siesa = 4 WHERE id = :id"),
                                    {"id": row["id"]}
                                )
                                print(f"Error API para ID {row['id']}: {response.status_code} - {response.text}")

                                # Guarda detalle del error si existe
                                try:
                                    data = response.json()
                                    f_detalle = data.get("detalle", [{}])[0].get("f_detalle", "")
                                    if f_detalle:
                                        conn.execute(
                                            text("UPDATE registro_produccion SET resultado_siesa = :detalle WHERE id = :id"),
                                            {"detalle": f_detalle, "id": row["id"]}
                                        )
                                except Exception:
                                    pass

                        except Exception as e:
                            print(f"Excepción en envío del ID {row['id']}: {e}")
                            continue
                    else:
                        # No cumple la condición: omitir y continuar
                        print(f"Registro ID {row['id']} sin condición válida, se omite.")
                        continue

                except Exception as e:
                    print(f"Error procesando Docto {row.get('Docto')}: {e}")
                    continue

    except Exception as e:
        print(f"Error general en cambiar_componente: {e}")

cambiar_componente()