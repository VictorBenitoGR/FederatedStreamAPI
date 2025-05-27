# ./scripts/generar_datos_publicos.py

import os
import json
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def generar_resumen_cluster() -> Dict[str, Any]:
    """
    Generar resumen general del clúster.

    Returns
    -------
    Dict[str, Any]
        Resumen del clúster
    """
    try:
        # Cargar métricas generales más recientes
        archivo_metricas = "data/resultados/metricas_generales_latest.json"

        if not os.path.exists(archivo_metricas):
            print("⚠️ Archivo de métricas no encontrado, generando datos básicos...")
            return generar_datos_basicos_cluster()

        with open(archivo_metricas, 'r', encoding='utf-8') as f:
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
        print(f"❌ Error generando resumen del clúster: {e}")
        return generar_datos_basicos_cluster()


def generar_datos_basicos_cluster() -> Dict[str, Any]:
    """
    Generar datos básicos del clúster desde archivos sintéticos.

    Returns
    -------
    Dict[str, Any]
        Datos básicos del clúster
    """
    try:
        # Cargar datos sintéticos
        ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
        eventos_df = pd.read_csv('data/datos_sinteticos/eventos_dummy.csv')
        perfiles_df = pd.read_csv('data/datos_sinteticos/perfil_viajero_dummy.csv')
        empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')

        return {
            "cluster_stats": {
                "total_giros": len(empresas_df['giro'].unique()),
                "periodo_datos": {"inicio": "2020-01-01", "fin": "2025-12-31"},
                "total_registros": len(ventas_df)
            },
            "economia": {
                "ingresos_totales": round(ventas_df['ingresos_totales'].sum()),
                "ingreso_promedio_diario": round(ventas_df['ingresos_totales'].mean()),
                "clientes_totales": ventas_df['numero_clientes'].sum(),
                "ticket_promedio": round(ventas_df['precio_promedio'].mean())
            },
            "eventos": {
                "total_eventos": len(eventos_df),
                "asistentes_totales": eventos_df['asistentes'].sum(),
                "asistentes_promedio": round(eventos_df['asistentes'].mean()),
                "ocupacion_promedio": round(eventos_df['ocupacion'].mean(), 1)
            },
            "viajeros": {
                "perfiles_analizados": len(perfiles_df),
                "gasto_promedio": round(perfiles_df['gasto_total'].mean()),
                "estancia_promedio": round(perfiles_df['duracion_estancia'].mean(), 1),
                "tipos_viajero": len(perfiles_df['tipo_viajero'].unique())
            },
            "metadata": {
                "ultima_actualizacion": datetime.now().isoformat(),
                "nivel_privacidad": "datos_completamente_anonimos",
                "empresas_identificables": False
            }
        }

    except Exception as e:
        print(f"❌ Error generando datos básicos: {e}")
        return {}


def generar_tendencias_estacionales() -> Dict[str, Any]:
    """
    Generar tendencias estacionales del clúster.

    Returns
    -------
    Dict[str, Any]
        Tendencias estacionales
    """
    try:
        ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
        ventas_df['fecha'] = pd.to_datetime(ventas_df['fecha'])
        ventas_df['mes'] = ventas_df['fecha'].dt.month

        # Calcular factor estacional por mes
        ingresos_por_mes = ventas_df.groupby('mes')['ingresos_totales'].mean()
        promedio_general = ingresos_por_mes.mean()
        factores_estacionales = (ingresos_por_mes / promedio_general).to_dict()

        # Formatear para visualización
        meses_nombres = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }

        tendencias_formateadas = []
        for mes, factor in factores_estacionales.items():
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
                "periodo_analisis": {"inicio": "2020-01-01", "fin": "2025-12-31"},
                "ultima_actualizacion": datetime.now().isoformat()
            }
        }

    except Exception as e:
        print(f"❌ Error generando tendencias estacionales: {e}")
        return {}


def generar_estadisticas_giros() -> Dict[str, Any]:
    """
    Generar estadísticas por giro turístico.

    Returns
    -------
    Dict[str, Any]
        Estadísticas por giro
    """
    try:
        # Cargar datos sintéticos
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
        print(f"❌ Error generando estadísticas por giro: {e}")
        return {}


def generar_resumen_eventos() -> Dict[str, Any]:
    """
    Generar resumen de eventos del clúster.

    Returns
    -------
    Dict[str, Any]
        Resumen de eventos
    """
    try:
        eventos_df = pd.read_csv('data/datos_sinteticos/eventos_dummy.csv')

        # Calcular estadísticas agregadas
        resumen = {
            "total_eventos": len(eventos_df),
            "asistentes_totales": int(eventos_df['asistentes'].sum()),
            "asistentes_promedio": round(eventos_df['asistentes'].mean()),
            "ocupacion_promedio": round(eventos_df['ocupacion'].mean(), 1),
            "capacidad_total": int(eventos_df['capacidad'].sum()),
            "tipos_evento": int(eventos_df['tipo_evento'].nunique()),
            "eventos_por_tipo": eventos_df['tipo_evento'].value_counts().to_dict(),
            "tendencia_asistencia": {
                "maximo": int(eventos_df['asistentes'].max()),
                "minimo": int(eventos_df['asistentes'].min()),
                "mediana": int(eventos_df['asistentes'].median())
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
        print(f"❌ Error generando resumen de eventos: {e}")
        return {}


def generar_perfiles_viajeros() -> Dict[str, Any]:
    """
    Generar análisis de perfiles de viajeros.

    Returns
    -------
    Dict[str, Any]
        Perfiles de viajeros
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
        print(f"❌ Error generando perfiles de viajeros: {e}")
        return {}


def generar_archivos_estaticos():
    """
    Generar todos los archivos JSON estáticos para deploy.
    """
    print("📊 GENERANDO DATOS PÚBLICOS PARA DEPLOY")
    print("=" * 60)
    print("Creando archivos JSON estáticos para tu aplicación Next.js")
    print()

    # Crear directorio de salida
    directorio_salida = "public_data"
    os.makedirs(directorio_salida, exist_ok=True)

    # Generar cada conjunto de datos
    datasets = {
        "cluster_overview.json": generar_resumen_cluster,
        "tendencias_estacionales.json": generar_tendencias_estacionales,
        "estadisticas_giros.json": generar_estadisticas_giros,
        "resumen_eventos.json": generar_resumen_eventos,
        "perfiles_viajeros.json": generar_perfiles_viajeros
    }

    archivos_generados = []
    datos_completos = {}

    for archivo, funcion in datasets.items():
        print(f"📄 Generando {archivo}...")
        try:
            datos = funcion()
            if datos:
                # Guardar archivo individual
                ruta_archivo = os.path.join(directorio_salida, archivo)
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)

                archivos_generados.append(archivo)
                datos_completos[archivo.replace('.json', '')] = datos
                print(f"✅ {archivo} generado exitosamente")
            else:
                print(f"⚠️ {archivo} no se pudo generar")
        except Exception as e:
            print(f"❌ Error generando {archivo}: {e}")

    # Generar archivo consolidado
    if datos_completos:
        print(f"\n📦 Generando archivo consolidado...")
        datos_completos["metadata_export"] = {
            "timestamp_export": datetime.now().isoformat(),
            "version_api": "1.0.0",
            "nivel_privacidad": "datos_publicos_anonimos",
            "uso_recomendado": "dashboards_y_visualizaciones",
            "archivos_incluidos": list(datos_completos.keys())
        }

        archivo_consolidado = os.path.join(directorio_salida, "all_data.json")
        with open(archivo_consolidado, 'w', encoding='utf-8') as f:
            json.dump(datos_completos, f, indent=2, ensure_ascii=False)

        archivos_generados.append("all_data.json")
        print(f"✅ all_data.json generado exitosamente")

    # Generar archivo de configuración para Next.js
    config_nextjs = {
        "api_endpoints": {
            "base_url": "https://federatedstreamapi.onrender.com",
            "endpoints": {
                "cluster_overview": "/public/cluster/overview",
                "tendencias_estacionales": "/public/cluster/tendencias-estacionales",
                "estadisticas_giros": "/public/giros/estadisticas",
                "resumen_eventos": "/public/eventos/resumen",
                "perfiles_viajeros": "/public/viajeros/perfiles",
                "export_all": "/public/export/all"
            }
        },
        "archivos_estaticos": {
            "directorio": "./public_data/",
            "archivos": archivos_generados
        },
        "configuracion_cors": {
            "allowed_origins": ["*"],
            "allowed_methods": ["GET"],
            "cache_control": "public, max-age=3600"
        }
    }

    archivo_config = os.path.join(directorio_salida, "nextjs_config.json")
    with open(archivo_config, 'w', encoding='utf-8') as f:
        json.dump(config_nextjs, f, indent=2, ensure_ascii=False)

    # Mostrar resumen
    print(f"\n" + "=" * 60)
    print(f"✅ GENERACIÓN COMPLETADA")
    print(f"=" * 60)
    print(f"📁 Directorio: {directorio_salida}/")
    print(f"📄 Archivos generados: {len(archivos_generados)}")

    for archivo in archivos_generados:
        ruta_completa = os.path.join(directorio_salida, archivo)
        tamaño = os.path.getsize(ruta_completa) / 1024  # KB
        print(f"   ✅ {archivo} ({tamaño:.1f} KB)")

    print(f"\n🚀 PARA USAR EN NEXT.JS:")
    print(f"1. Copia la carpeta '{directorio_salida}/' a tu proyecto Next.js")
    print(f"2. Usa los archivos JSON como datos estáticos")
    print(f"3. O consume los endpoints de la API directamente")
    print(f"4. Configura CORS según nextjs_config.json")

    print(f"\n📡 ENDPOINTS DE API DISPONIBLES:")
    for endpoint, url in config_nextjs["api_endpoints"]["endpoints"].items():
        print(f"   GET {url}")

    return archivos_generados


def main():
    """
    Función principal del generador de datos públicos.
    """
    try:
        archivos = generar_archivos_estaticos()
        if archivos:
            print(f"\n🎉 ¡Datos públicos generados exitosamente!")
            print(f"📊 Listos para usar en tu aplicación Next.js")
        else:
            print(f"\n💥 No se pudieron generar los datos")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Generación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
