import sys
import os
from fastapi import FastAPI, BackgroundTasks

# Agregar cargas_unoe al path para resolver imports relativos del script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cargas_unoe"))

from cargas_unoe.cargues_api import enviar_datos_a_siesa
import consultas_sql_excel as consultas
import consulta_sql_bodega019 as bodega019

app = FastAPI(title="Kos Productions API")


@app.post("/cargar-siesa", status_code=202)
def cargar_siesa(background_tasks: BackgroundTasks):
    """Envía registros de producción pendientes a SIESA."""
    background_tasks.add_task(enviar_datos_a_siesa)
    return {"status": "accepted", "message": "Proceso iniciado en background"}


@app.post("/actualizar-consultas", status_code=202)
def actualizar_consultas(background_tasks: BackgroundTasks):
    """Sincroniza op_numeros y existencias desde la API SIESA Connekta."""
    background_tasks.add_task(consultas.main)
    return {"status": "accepted", "message": "Proceso iniciado en background"}


@app.post("/actualizar-bodega019", status_code=202)
def actualizar_bodega019(background_tasks: BackgroundTasks):
    """Sincroniza existencias_lote_019 (bodega 019) desde la API SIESA Connekta."""
    background_tasks.add_task(bodega019.main)
    return {"status": "accepted", "message": "Proceso iniciado en background"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)