# ./src/api/main.py

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import hashlib
import json
import os
from datetime import datetime, timedelta
import uuid

from src.api.models import (
    ModeloFederado, ResultadoAgregado, MetricasEmpresa,
    DatosAnonimizados, ConsultaMetricas
)
from src.api.federado import ProcesadorFederado
from src.api.storage import AlmacenResultados
from src.api.public_data import router as public_router

# Configuración de la aplicación
app = FastAPI(
    title="Clúster de Turismo NL - API Federada",
    description="Sistema de analítica y aprendizaje federado para empresas turísticas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
procesador_federado = ProcesadorFederado()
almacen = AlmacenResultados()

# Incluir routers
app.include_router(public_router)


@app.on_event("startup")
async def startup_event():
    """
    Inicializar la aplicación al arrancar.
    """
    print("🚀 Iniciando API del Clúster de Turismo de Nuevo León")
    print("🔒 Sistema de analítica federada con privacidad garantizada")

    # Crear directorios necesarios
    os.makedirs("data/resultados", exist_ok=True)
    os.makedirs("data/resultados/modelos", exist_ok=True)
    os.makedirs("data/resultados/metricas", exist_ok=True)

    # Cargar modelos existentes si los hay
    await procesador_federado.cargar_modelos_existentes()

    print("✅ API iniciada correctamente")


@app.get("/")
async def root():
    """
    Endpoint raíz con información del sistema.
    """
    return {
        "mensaje": "API del Clúster de Turismo de Nuevo León",
        "version": "1.0.0",
        "descripcion": "Sistema de analítica federada con privacidad garantizada",
        "timestamp": datetime.now().isoformat(),
        "endpoints_principales": [
            "/federated/submit-model",
            "/federated/get-aggregated",
            "/metrics/general",
            "/metrics/by-sector"
        ]
    }


@app.get("/health")
async def health_check():
    """
    Verificar el estado de salud del sistema.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "componentes": {
            "procesador_federado": "activo",
            "almacen_resultados": "activo",
            "modelos_cargados": len(procesador_federado.modelos_activos)
        }
    }

# === ENDPOINTS DE APRENDIZAJE FEDERADO ===


@app.post("/federated/submit-model")
async def enviar_modelo_federado(
    modelo: ModeloFederado,
    background_tasks: BackgroundTasks
):
    """
    Recibir un modelo entrenado localmente por una empresa.

    Los datos nunca salen de la empresa, solo se envían los parámetros
    del modelo entrenado de forma completamente anonimizada.
    """
    try:
        # Validar que el modelo esté correctamente anonimizado
        if not procesador_federado.validar_anonimizacion(modelo):
            raise HTTPException(
                status_code=400,
                detail="El modelo no cumple con los requisitos de anonimización"
            )

        # Generar ID único para esta contribución
        contribucion_id = hashlib.sha256(
            f"{modelo.timestamp}_{uuid.uuid4()}".encode()
        ).hexdigest()[:16]

        # Procesar el modelo en segundo plano
        background_tasks.add_task(
            procesador_federado.procesar_modelo_anonimo,
            modelo,
            contribucion_id
        )

        # Guardar metadatos (sin información identificable)
        await almacen.guardar_metadatos_contribucion(contribucion_id, {
            "timestamp": modelo.timestamp,
            "tipo_modelo": modelo.tipo_modelo,
            "giro_anonimizado": modelo.giro_hash,
            "metricas_validacion": modelo.metricas_validacion
        })

        return {
            "status": "recibido",
            "contribucion_id": contribucion_id,
            "mensaje": "Modelo recibido y procesándose de forma segura",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando modelo: {str(e)}")


@app.get("/federated/get-aggregated/{tipo_modelo}")
async def obtener_modelo_agregado(tipo_modelo: str) -> ResultadoAgregado:
    """
    Obtener el modelo agregado más reciente para un tipo específico.

    Este modelo es el resultado de combinar múltiples contribuciones
    sin revelar información de empresas individuales.
    """
    try:
        resultado = await procesador_federado.obtener_modelo_agregado(tipo_modelo)

        if not resultado:
            raise HTTPException(
                status_code=404,
                detail=f"No hay modelo agregado disponible para {tipo_modelo}"
            )

        # Guardar consulta para auditoría (sin datos sensibles)
        await almacen.registrar_consulta_modelo(tipo_modelo)

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo modelo: {str(e)}")


@app.post("/federated/submit-metrics")
async def enviar_metricas_anonimas(metricas: MetricasEmpresa):
    """
    Recibir métricas agregadas de una empresa de forma anónima.

    Las métricas están pre-agregadas y anonimizadas localmente.
    """
    try:
        # Validar anonimización de métricas
        if not procesador_federado.validar_metricas_anonimas(metricas):
            raise HTTPException(
                status_code=400,
                detail="Las métricas no cumplen con los requisitos de anonimización"
            )

        # Procesar métricas
        resultado = await procesador_federado.procesar_metricas_anonimas(metricas)

        return {
            "status": "procesado",
            "metricas_id": resultado["id"],
            "contribuciones_totales": resultado["total_contribuciones"],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando métricas: {str(e)}")

# === ENDPOINTS DE CONSULTA DE MÉTRICAS ===


@app.get("/metrics/general")
async def obtener_metricas_generales():
    """
    Obtener métricas generales agregadas del clúster.

    Todas las métricas están completamente anonimizadas.
    """
    try:
        metricas = await almacen.obtener_metricas_generales()
        return metricas

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")


@app.get("/metrics/by-sector/{giro}")
async def obtener_metricas_por_giro(giro: str):
    """
    Obtener métricas agregadas por giro turístico.

    Solo se muestran datos agregados, nunca individuales.
    """
    try:
        metricas = await almacen.obtener_metricas_por_giro(giro)

        if not metricas:
            raise HTTPException(
                status_code=404,
                detail=f"No hay datos suficientes para el giro {giro}"
            )

        return metricas

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")


@app.post("/metrics/query")
async def consultar_metricas_personalizadas(consulta: ConsultaMetricas):
    """
    Realizar consultas personalizadas sobre métricas agregadas.

    Permite filtros por período, giro, tipo de métrica, etc.
    """
    try:
        resultados = await almacen.consultar_metricas_personalizadas(consulta)
        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en consulta: {str(e)}")

# === ENDPOINTS DE PREDICCIONES ===


@app.post("/predictions/demand")
async def predecir_demanda(
    giro: str,
    fecha_inicio: str,
    fecha_fin: str,
    parametros_adicionales: Optional[Dict[str, Any]] = None
):
    """
    Generar predicciones de demanda usando modelos federados.

    Las predicciones se basan en patrones agregados del clúster.
    """
    try:
        predicciones = await procesador_federado.generar_predicciones_demanda(
            giro, fecha_inicio, fecha_fin, parametros_adicionales
        )

        # Guardar predicción para análisis posterior
        await almacen.guardar_prediccion(predicciones)

        return predicciones

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando predicciones: {str(e)}")


@app.get("/predictions/trends/{giro}")
async def obtener_tendencias(giro: str, periodo_meses: int = 12):
    """
    Obtener tendencias históricas y proyecciones para un giro.
    """
    try:
        tendencias = await procesador_federado.calcular_tendencias(giro, periodo_meses)
        return tendencias

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando tendencias: {str(e)}")

# === ENDPOINTS DE ADMINISTRACIÓN ===


@app.get("/admin/stats")
async def estadisticas_sistema():
    """
    Obtener estadísticas del sistema (solo metadatos, sin datos sensibles).
    """
    try:
        stats = await almacen.obtener_estadisticas_sistema()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.post("/admin/export-results")
async def exportar_resultados(formato: str = "json"):
    """
    Exportar resultados agregados para análisis externo.

    Solo se exportan datos completamente anonimizados.
    """
    try:
        if formato not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Formato debe ser 'json' o 'csv'")

        archivo_exportado = await almacen.exportar_resultados_anonimos(formato)

        return {
            "status": "exportado",
            "archivo": archivo_exportado,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
