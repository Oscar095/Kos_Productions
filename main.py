import sys
import os
from fastapi import FastAPI, HTTPException

# Agregar cargas_unoe al path para resolver imports relativos del script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cargas_unoe"))

from cargas_unoe.cargues_api import enviar_datos_a_siesa
import consultas_sql_excel as consultas
import consulta_sql_bodega019 as bodega019

app = FastAPI(title="Kos Productions API")


@app.post("/cargar-siesa")
def cargar_siesa():
    """Envía registros de producción pendientes a SIESA."""
    try:
        enviar_datos_a_siesa()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/actualizar-consultas")
def actualizar_consultas():
    """Sincroniza op_numeros y existencias desde la API SIESA Connekta."""
    try:
        consultas.main()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/actualizar-bodega019")
def actualizar_bodega019():
    """Sincroniza existencias_lote_019 (bodega 019) desde la API SIESA Connekta."""
    try:
        bodega019.main()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
