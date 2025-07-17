import requests
import pandas as pd
from dotenv import load_dotenv
import os
import datetime
import json

load_dotenv()

CONNI_KEY = os.getenv("CONNI_KEY")
CONNI_TOKEN = os.getenv("CONNI_TOKEN")
API_CAMBIAR_LOTES =os.getenv("API_CAMBIAR_LOTES")
API_COMPONENTES_OP = os.getenv("API_COMPONENTES_OP")
API_TPK = os.getenv("API_TPK")

headers = {
        "ConniKey": CONNI_KEY,
        "ConniToken": CONNI_TOKEN,
        'Content-Type': 'application/json'
    }

def tpk(cant, lote, item_comp, bodega_comp):
    
    fecha = datetime.datetime.now()

    payload = json.dumps({
    "Inicial": [
        {
        "F_CIA": "1"
        }
    ],
    "Documentos": [
        {
        "F_CIA": "1",
        "F_CONSEC_AUTO_REG": "1",
        "f350_id_co": "001",
        "f350_id_tipo_docto": "TPK",
        "f350_consec_docto": "1",
        "f350_fecha": str(fecha.strftime('%Y%m%d')),
        "f350_id_tercero": "",
        "f350_id_clase_docto": "67",
        "f350_ind_estado": "1",
        "f350_ind_impresion": "0",
        "f350_notas": "",
        "f450_id_concepto": "607",
        "f450_id_bodega_salida": str(bodega_comp),
        "f450_id_bodega_entrada": "029",
        "f450_docto_alterno": "",
        "f350_id_co_base": "001",
        "f350_id_tipo_docto_base": "",
        "f350_consec_docto_base": "",
        "f462_id_vehiculo": "",
        "f462_id_tercero_transp": "",
        "f462_id_sucursal_transp": "",
        "f462_id_tercero_conductor": "",
        "f462_nombre_conductor": "",
        "f462_identif_conductor": "",
        "f462_numero_guia": "",
        "f462_cajas": "",
        "f462_peso": "",
        "f462_volumen": "",
        "f462_valor_seguros": "",
        "f462_notas": ""
        }
    ],
    "Movimientos": [
        {
        "F_CIA": "1",
        "f470_id_co": "001",
        "f470_id_tipo_docto": "TPK",
        "f470_consec_docto": "1",
        "f470_nro_registro": "1",
        "f470_id_bodega": str(bodega_comp),
        "f470_id_ubicacion_aux": "",
        "f470_id_lote": str(lote),
        "f470_id_concepto": "607",
        "f470_id_motivo": "04",
        "f470_id_co_movto": "001",
        "f470_id_ccosto_movto": "",
        "f470_id_proyecto": "",
        "f470_id_unidad_medida": "KG",
        "f470_cant_base": float(cant),
        "f470_cant_2": "",
        "f470_costo_prom_uni": "0",
        "f470_notas": "",
        "f470_desc_varible": "",
        "F_DESC_ITEM": "",
        "F_ID_UM_INVENTARIO": "",
        "f470_id_ubicacion_aux_ent": "",
        "f470_id_lote_ent": str(lote),
        "f470_id_item": int(item_comp),
        "f470_referencia_item": "",
        "f470_codigo_barras": "",
        "f470_id_ext1_detalle": "",
        "f470_id_ext2_detalle": "",
        "f470_id_un_movto": "01"
        }
    ],
    "Final": [
        {
        "F_CIA": "1"
        }
    ]
    })

    try:
        response = requests.request("POST", API_TPK, headers=headers, data=payload)

        if response.status_code == 200:
            print("Lote Transferido Correctamente")
        else:
            print(f"Error API: {response.status_code} - {response.text}")
        

    except Exception as e:
        print(f"Excepción en envío del ID: {e}")

def componente(docto, item): #Extraer Item Componente
        
        API_URL_BASE = API_COMPONENTES_OP.split("?")[0]
        API_QUERY_PARAMS = API_COMPONENTES_OP.split("?")[1]

        query_params = API_QUERY_PARAMS.replace("{docto}", str(docto))
        url = f"{API_URL_BASE}?{query_params}"

        response = requests.get(url, headers=headers, timeout=30)

        data = response.json()
        page_data=data["detalle"]["Datos"]

        # Extrae los datos
        
        df=pd.DataFrame(page_data)

        item_componente=df.loc[item==df["item_padre"],"item_comp"].values[0]

        return item_componente

def eliminar_lote(item_padre,ext1,ext2,docto,item_componente):
    
    payload= {

        "Movimientos Versión": [
            {
            "F_ACTUALIZA_REG": "3",
            "f850_id_tipo_docto_op": "OPK",
            "f850_consec_docto_op": int(docto),
            "f860_id_item_op": int(item_padre),
            "f860_referencia_item_op": "",
            "f860_codigo_barras_item_op": "",
            "f851_id_ext1_detalle_item_op": str(ext1),
            "f851_id_ext2_detalle_item_op": str(ext2),
            "f860_numero_operacion": "0",
            "f860_id_bodega": "026",
            "f860_id_item_comp": int(item_componente),
            "f860_referencia_item_comp": "",
            "f860_codigo_barras_item_comp": "",
            "f851_id_ext1_detalle_item_comp": "",
            "f851_id_ext2_detalle_item_comp": "",
            "f860_cant_requerida_base": "0",
            "f860_cant_requerida_2": "0",
            "f860_notas": ""
            }
        ]  
            }

    try:
        response = requests.post(API_CAMBIAR_LOTES, json=payload, headers=headers)

        if response.status_code == 200:
            print("Lote anterior eliminado correctamente")
        else:
            print(f"Error API: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Excepción en envío del ID: {e}")