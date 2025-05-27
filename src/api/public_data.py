from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import pandas as pd

# Router para datos públicos
router = APIRouter(prefix="/public", tags=["Datos Públicos"])


@router.get("/cluster/overview")
async def obtener_resumen_cluster():
    """
    Obtener resumen general del clúster para visualización pública.

    Datos completamente agregados y anónimos, ideales para dashboards.
    """
    try:
        # Cargar métricas generales más recientes
        archivo_metricas = "data/resultados/metricas_generales_latest.json"

        if not os.path.exists(archivo_metricas):
            raise HTTPException(
                status_code=404,
                detail="Métricas del clúster no disponibles"
            )

        with open(archivo_metricas, 'r') as f:
            metricas = json.load(f)

        # Formatear para consumo público
        resumen = {
            "cluster_stats": {
                "total_giros": metricas["resumen_cluster"]["total_giros_representados"],
                "periodo_datos": metricas["resumen_cluster"]["periodo_datos"],
                "total_registros": metricas["resumen_cluster"]["total_registros_agregados"]
            },
            "economia": {
                "ingresos_totales": round(metricas["metricas_economicas"]["ingresos_totales_cluster"]),
                "ingreso_promedio_diario": round(metricas["metricas_economicas"]["ingreso_promedio_diario"]),
                "clientes_totales": metricas["metricas_economicas"]["clientes_totales_atendidos"],
                "ticket_promedio": round(metricas["metricas_economicas"]["ticket_promedio_cluster"])
            },
            "eventos": {
                "total_eventos": metricas["metricas_eventos"]["total_eventos_realizados"],
                "asistentes_totales": metricas["metricas_eventos"]["asistentes_totales"],
                "asistentes_promedio": round(metricas["metricas_eventos"]["asistentes_promedio_evento"]),
                "ocupacion_promedio": round(metricas["metricas_eventos"]["ocupacion_promedio_eventos"], 1)
            },
            "viajeros": {
                "perfiles_analizados": metricas["perfil_viajeros"]["total_perfiles_analizados"],
                "gasto_promedio": round(metricas["perfil_viajeros"]["gasto_promedio_viajero"]),
                "estancia_promedio": round(metricas["perfil_viajeros"]["estancia_promedio_dias"], 1),
                "tipos_viajero": metricas["perfil_viajeros"]["tipos_viajero_representados"]
            },
            "metadata": {
                "ultima_actualizacion": metricas["timestamp_calculo"],
                "nivel_privacidad": "datos_completamente_anonimos",
                "empresas_identificables": False
            }
        }

        return resumen

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}")


@router.get("/cluster/tendencias-estacionales")
async def obtener_tendencias_estacionales():
    """
    Obtener tendencias estacionales agregadas del clúster.

    Perfecto para gráficos de estacionalidad en el dashboard.
    """
    try:
        archivo_metricas = "data/resultados/metricas_generales_latest.json"

        with open(archivo_metricas, 'r') as f:
            metricas = json.load(f)

        tendencias = metricas["tendencias_estacionales"]

        # Formatear para visualización
        meses_nombres = {
            "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril",
            "5": "Mayo", "6": "Junio", "7": "Julio", "8": "Agosto",
            "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
        }

        tendencias_formateadas = []
        for mes, factor in tendencias.items():
            tendencias_formateadas.append({
                "mes": meses_nombres[mes],
                "mes_numero": int(mes),
                "factor_estacional": round(factor, 3),
                "porcentaje_vs_promedio": round((factor - 1) * 100, 1)
            })

        # Ordenar por mes
        tendencias_formateadas.sort(key=lambda x: x["mes_numero"])

        return {
            "tendencias_mensuales": tendencias_formateadas,
            "temporada_alta": max(tendencias_formateadas, key=lambda x: x["factor_estacional"]),
            "temporada_baja": min(tendencias_formateadas, key=lambda x: x["factor_estacional"]),
            "metadata": {
                "periodo_analisis": metricas["resumen_cluster"]["periodo_datos"],
                "ultima_actualizacion": metricas["timestamp_calculo"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo tendencias: {str(e)}")


@router.get("/giros/estadisticas")
async def obtener_estadisticas_giros():
    """
    Obtener estadísticas agregadas por giro turístico.

    Datos anónimos para comparación entre sectores.
    """
    try:
        # Cargar datos sintéticos para análisis por giro
        ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
        empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')

        # Agregar información de giro
        datos_con_giro = ventas_df.merge(empresas_df[['empresa_id', 'giro']], on='empresa_id')

        # Calcular estadísticas por giro
        stats_por_giro = []

        for giro in datos_con_giro['giro'].unique():
            datos_giro = datos_con_giro[datos_con_giro['giro'] == giro]

            stats = {
                "giro": giro,
                "empresas_participantes": len(datos_giro['empresa_id'].unique()),
                "ingresos_totales": round(datos_giro['ingresos_totales'].sum()),
                "ingresos_promedio": round(datos_giro['ingresos_totales'].mean()),
                "clientes_totales": datos_giro['numero_clientes'].sum(),
                "clientes_promedio": round(datos_giro['numero_clientes'].mean()),
                "precio_promedio": round(datos_giro['precio_promedio'].mean()),
                "registros_totales": len(datos_giro)
            }

            stats_por_giro.append(stats)

        # Ordenar por ingresos totales
        stats_por_giro.sort(key=lambda x: x["ingresos_totales"], reverse=True)

        return {
            "estadisticas_por_giro": stats_por_giro,
            "resumen": {
                "total_giros": len(stats_por_giro),
                "giro_lider": stats_por_giro[0]["giro"] if stats_por_giro else None,
                "ingresos_cluster": sum(s["ingresos_totales"] for s in stats_por_giro)
            },
            "metadata": {
                "datos_anonimizados": True,
                "nivel_agregacion": "por_giro",
                "ultima_actualizacion": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas por giro: {str(e)}")


@router.get("/eventos/resumen")
async def obtener_resumen_eventos():
    """
    Obtener resumen agregado de eventos del clúster.
    """
    try:
        eventos_df = pd.read_csv('data/datos_sinteticos/eventos_dummy.csv')

        # Calcular estadísticas agregadas
        resumen = {
            "total_eventos": len(eventos_df),
            "asistentes_totales": eventos_df['asistentes'].sum(),
            "asistentes_promedio": round(eventos_df['asistentes'].mean()),
            "ocupacion_promedio": round(eventos_df['ocupacion'].mean(), 1),
            "capacidad_total": eventos_df['capacidad'].sum(),
            "tipos_evento": eventos_df['tipo_evento'].nunique(),
            "eventos_por_tipo": eventos_df['tipo_evento'].value_counts().to_dict(),
            "tendencia_asistencia": {
                "maximo": eventos_df['asistentes'].max(),
                "minimo": eventos_df['asistentes'].min(),
                "mediana": eventos_df['asistentes'].median()
            }
        }

        return {
            "resumen_eventos": resumen,
            "metadata": {
                "datos_anonimizados": True,
                "empresas_no_identificables": True,
                "ultima_actualizacion": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen de eventos: {str(e)}")


@router.get("/viajeros/perfiles")
async def obtener_perfiles_viajeros():
    """
    Obtener análisis agregado de perfiles de viajeros.
    """
    try:
        perfiles_df = pd.read_csv('data/datos_sinteticos/perfil_viajero_dummy.csv')

        # Análisis por tipo de viajero
        analisis_tipos = []
        for tipo in perfiles_df['tipo_viajero'].unique():
            datos_tipo = perfiles_df[perfiles_df['tipo_viajero'] == tipo]

            analisis = {
                "tipo_viajero": tipo,
                "cantidad": len(datos_tipo),
                "porcentaje": round(len(datos_tipo) / len(perfiles_df) * 100, 1),
                "gasto_promedio": round(datos_tipo['gasto_total'].mean()),
                "edad_promedio": round(datos_tipo['edad'].mean()),
                "estancia_promedio": round(datos_tipo['duracion_estancia'].mean(), 1),
                "grupo_promedio": round(datos_tipo['tamaño_grupo'].mean(), 1)
            }

            analisis_tipos.append(analisis)

        # Ordenar por gasto promedio
        analisis_tipos.sort(key=lambda x: x["gasto_promedio"], reverse=True)

        return {
            "perfiles_viajeros": analisis_tipos,
            "estadisticas_generales": {
                "total_perfiles": len(perfiles_df),
                "gasto_promedio_general": round(perfiles_df['gasto_total'].mean()),
                "edad_promedio_general": round(perfiles_df['edad'].mean()),
                "estancia_promedio_general": round(perfiles_df['duracion_estancia'].mean(), 1),
                "tipos_viajero_unicos": len(analisis_tipos)
            },
            "metadata": {
                "datos_completamente_anonimos": True,
                "sin_informacion_personal": True,
                "ultima_actualizacion": datetime.now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo perfiles de viajeros: {str(e)}")


@router.get("/export/all")
async def exportar_todos_los_datos():
    """
    Exportar todos los datos públicos en un solo endpoint.

    Ideal para generar archivos estáticos para deploy.
    """
    try:
        # Obtener todos los datos
        resumen_cluster = await obtener_resumen_cluster()
        tendencias = await obtener_tendencias_estacionales()
        stats_giros = await obtener_estadisticas_giros()
        resumen_eventos = await obtener_resumen_eventos()
        perfiles_viajeros = await obtener_perfiles_viajeros()

        export_completo = {
            "cluster_overview": resumen_cluster,
            "tendencias_estacionales": tendencias,
            "estadisticas_giros": stats_giros,
            "resumen_eventos": resumen_eventos,
            "perfiles_viajeros": perfiles_viajeros,
            "metadata_export": {
                "timestamp_export": datetime.now().isoformat(),
                "version_api": "1.0.0",
                "nivel_privacidad": "datos_publicos_anonimos",
                "uso_recomendado": "dashboards_y_visualizaciones"
            }
        }

        return export_completo

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando datos: {str(e)}")
