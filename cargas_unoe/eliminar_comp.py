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



def eliminar_lote(item,ext1,ext2,docto):
    
    payload= {

        "Movimientos Versión": [
            {
            "F_ACTUALIZA_REG": "3",
            "f850_id_tipo_docto_op": "OPK",
            "f850_consec_docto_op": docto,
            "f860_id_item_op": item,
            "f860_referencia_item_op": "",
            "f860_codigo_barras_item_op": "",
            "f851_id_ext1_detalle_item_op": ext1,
            "f851_id_ext2_detalle_item_op": ext2,
            "f860_numero_operacion": "0",
            "f860_id_bodega": "026",
            "f860_id_item_comp": "****",
            "f860_referencia_item_comp": "",
            "f860_codigo_barras_item_comp": "",
            "f851_id_ext1_detalle_item_comp": "",
            "f851_id_ext2_detalle_item_comp": "",
            "f860_cant_requerida_base": "",
            "f860_cant_requerida_2": "0",
            "f860_notas": ""
            }
        ]  
            }

    try:
        response = requests.post(API_CAMBIAR_LOTES, json=payload, headers=headers)

        if response.status_code == 200:
            print("Lote cambiado correctamente")
        else:
            print(f"Error API: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Excepción en envío del ID: {e}")


