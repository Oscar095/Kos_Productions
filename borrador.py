import requests
import json

url = "https://servicios.siesacloud.com/api/siesa/v3/conectoresimportarestandar?idCompania=7501&idDocumento=142951&nombreDocumento=API_v1_Inventarios_Comercial_DocumentoInv"

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
      "f350_fecha": "20250705",
      "f350_id_tercero": "",
      "f350_id_clase_docto": "67",
      "f350_ind_estado": "0",
      "f350_ind_impresion": "0",
      "f350_notas": "",
      "f450_id_concepto": "607",
      "f450_id_bodega_salida": "019",
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
      "f470_id_bodega": "019",
      "f470_id_ubicacion_aux": "",
      "f470_id_lote": "01370",
      "f470_id_concepto": "607",
      "f470_id_motivo": "04",
      "f470_id_co_movto": "001",
      "f470_id_ccosto_movto": "",
      "f470_id_proyecto": "",
      "f470_id_unidad_medida": "KG",
      "f470_cant_base": "4",
      "f470_cant_2": "",
      "f470_costo_prom_uni": "0",
      "f470_notas": "",
      "f470_desc_varible": "",
      "F_DESC_ITEM": "",
      "F_ID_UM_INVENTARIO": "",
      "f470_id_ubicacion_aux_ent": "",
      "f470_id_lote_ent": "01370",
      "f470_id_item": "33807",
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
headers = {
  'ConniKey': '2151a36b5f98858457784a4d3eb88788',
  'ConniToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6Ijk5MjIxZDE1LTkwZjItNDVjNi1iZDc5LTczMGIxNTVkMDA1NiIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcHJpbWFyeXNpZCI6IjhkOTEyMDEwLTFkMGEtNDE1MS1hNmEyLTA2NmFjNzM4ODMyYSJ9.7epvbp5HCSlwTNJvRtFXCi1ToxeK9oQXnm2Bg-gGAQw',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)