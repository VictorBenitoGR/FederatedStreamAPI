# ./scripts/benchmark_anonimo.py

import os
import json
import sys
import requests
import argparse
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def cargar_configuracion_empresa() -> Optional[Dict]:
    """
    Cargar configuración de la empresa desde archivo.

    Returns
    -------
    Optional[Dict]
        Configuración de la empresa o None si no existe
    """
    try:
        with open("config/empresa.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró configuración de empresa")
        print("   Ejecuta primero: python scripts/configurar_empresa.py")
        return None
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return None


def obtener_metricas_cluster(api_url: str) -> Optional[Dict]:
    """
    Obtener métricas generales del clúster.

    Parameters
    ----------
    api_url : str
        URL de la API del clúster

    Returns
    -------
    Optional[Dict]
        Métricas del clúster o None si hay error
    """
    try:
        response = requests.get(f"{api_url}/metrics/general", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error obteniendo métricas del clúster: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def obtener_metricas_giro(api_url: str, giro: str) -> Optional[Dict]:
    """
    Obtener métricas específicas del giro.

    Parameters
    ----------
    api_url : str
        URL de la API del clúster
    giro : str
        Giro turístico

    Returns
    -------
    Optional[Dict]
        Métricas del giro o None si hay error
    """
    try:
        response = requests.get(f"{api_url}/metrics/by-sector/{giro}", timeout=30)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"⚠️ No hay datos suficientes para el giro {giro}")
            return None
        else:
            print(f"❌ Error obteniendo métricas del giro: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def cargar_metricas_empresa() -> Optional[Dict]:
    """
    Cargar las métricas más recientes de la empresa.

    Returns
    -------
    Optional[Dict]
        Métricas de la empresa o None si no existen
    """
    try:
        # Buscar el archivo de métricas más reciente
        directorio_resultados = "resultados_entrenamiento"
        if not os.path.exists(directorio_resultados):
            print("❌ No se encontraron resultados de entrenamiento")
            print("   Ejecuta primero: python scripts/entrenar_y_enviar.py")
            return None

        archivos_metricas = [f for f in os.listdir(directorio_resultados) if f.startswith('metricas_')]

        if not archivos_metricas:
            print("❌ No se encontraron archivos de métricas")
            return None

        # Tomar el archivo más reciente
        archivo_mas_reciente = sorted(archivos_metricas)[-1]
        ruta_metricas = os.path.join(directorio_resultados, archivo_mas_reciente)

        with open(ruta_metricas, 'r') as f:
            return json.load(f)

    except Exception as e:
        print(f"❌ Error cargando métricas de la empresa: {e}")
        return None


def calcular_benchmarks(metricas_empresa: Dict, metricas_giro: Dict, metricas_cluster: Dict) -> Dict:
    """
    Calcular benchmarks comparando empresa vs giro vs clúster.

    Parameters
    ----------
    metricas_empresa : Dict
        Métricas de la empresa
    metricas_giro : Dict
        Métricas del giro
    metricas_cluster : Dict
        Métricas del clúster completo

    Returns
    -------
    Dict
        Análisis de benchmarking
    """
    benchmarks = {
        "comparacion_giro": {},
        "comparacion_cluster": {},
        "posicion_relativa": {},
        "areas_mejora": [],
        "fortalezas": []
    }

    # Extraer métricas de la empresa
    empresa_metricas = metricas_empresa.get('metricas_agregadas', {})

    # Comparación con el giro
    if 'metricas_economicas' in metricas_giro:
        giro_economicas = metricas_giro['metricas_economicas']

        # Ingresos promedio diario
        empresa_ingresos = empresa_metricas.get('ingresos_promedio_diario', 0)
        giro_ingresos = giro_economicas.get('ingresos_promedio_diario', 0)

        if giro_ingresos > 0:
            ratio_ingresos = empresa_ingresos / giro_ingresos
            benchmarks['comparacion_giro']['ingresos_ratio'] = ratio_ingresos
            benchmarks['comparacion_giro']['ingresos_vs_giro'] = f"{ratio_ingresos:.2f}x"

            if ratio_ingresos > 1.2:
                benchmarks['fortalezas'].append("Ingresos superiores al promedio del giro")
            elif ratio_ingresos < 0.8:
                benchmarks['areas_mejora'].append("Ingresos por debajo del promedio del giro")

        # Clientes promedio diario
        empresa_clientes = empresa_metricas.get('clientes_promedio_diario', 0)
        giro_clientes = giro_economicas.get('clientes_promedio_diario', 0)

        if giro_clientes > 0:
            ratio_clientes = empresa_clientes / giro_clientes
            benchmarks['comparacion_giro']['clientes_ratio'] = ratio_clientes
            benchmarks['comparacion_giro']['clientes_vs_giro'] = f"{ratio_clientes:.2f}x"

            if ratio_clientes > 1.2:
                benchmarks['fortalezas'].append("Volumen de clientes superior al giro")
            elif ratio_clientes < 0.8:
                benchmarks['areas_mejora'].append("Volumen de clientes por debajo del giro")

        # Precio promedio
        empresa_precio = empresa_metricas.get('precio_promedio', 0)
        giro_precio = giro_economicas.get('precio_promedio', 0)

        if giro_precio > 0:
            ratio_precio = empresa_precio / giro_precio
            benchmarks['comparacion_giro']['precio_ratio'] = ratio_precio
            benchmarks['comparacion_giro']['precio_vs_giro'] = f"{ratio_precio:.2f}x"

            if ratio_precio > 1.1:
                benchmarks['fortalezas'].append("Precios premium vs el giro")
            elif ratio_precio < 0.9:
                benchmarks['areas_mejora'].append("Precios por debajo del promedio del giro")

    # Comparación con el clúster completo
    if 'metricas_economicas' in metricas_cluster:
        cluster_economicas = metricas_cluster['metricas_economicas']

        # Ticket promedio vs clúster
        empresa_ticket = empresa_metricas.get('ingresos_promedio_diario', 0) / max(empresa_metricas.get('clientes_promedio_diario', 1), 1)
        cluster_ticket = cluster_economicas.get('ticket_promedio_cluster', 0)

        if cluster_ticket > 0:
            ratio_ticket = empresa_ticket / cluster_ticket
            benchmarks['comparacion_cluster']['ticket_ratio'] = ratio_ticket
            benchmarks['comparacion_cluster']['ticket_vs_cluster'] = f"{ratio_ticket:.2f}x"

    # Calcular posición relativa
    ratios = []
    if 'ingresos_ratio' in benchmarks['comparacion_giro']:
        ratios.append(benchmarks['comparacion_giro']['ingresos_ratio'])
    if 'clientes_ratio' in benchmarks['comparacion_giro']:
        ratios.append(benchmarks['comparacion_giro']['clientes_ratio'])
    if 'precio_ratio' in benchmarks['comparacion_giro']:
        ratios.append(benchmarks['comparacion_giro']['precio_ratio'])

    if ratios:
        promedio_ratios = sum(ratios) / len(ratios)
        if promedio_ratios > 1.2:
            benchmarks['posicion_relativa']['categoria'] = "Líder del giro"
            benchmarks['posicion_relativa']['descripcion'] = "Tu empresa supera significativamente el promedio"
        elif promedio_ratios > 1.0:
            benchmarks['posicion_relativa']['categoria'] = "Por encima del promedio"
            benchmarks['posicion_relativa']['descripcion'] = "Tu empresa está por encima del promedio del giro"
        elif promedio_ratios > 0.8:
            benchmarks['posicion_relativa']['categoria'] = "En el promedio"
            benchmarks['posicion_relativa']['descripcion'] = "Tu empresa está cerca del promedio del giro"
        else:
            benchmarks['posicion_relativa']['categoria'] = "Por debajo del promedio"
            benchmarks['posicion_relativa']['descripcion'] = "Hay oportunidades de mejora significativas"

    return benchmarks


def mostrar_benchmarks(benchmarks: Dict, giro: str, nombre_empresa: str):
    """
    Mostrar resultados del benchmarking de forma clara.

    Parameters
    ----------
    benchmarks : Dict
        Resultados del benchmarking
    giro : str
        Giro de la empresa
    nombre_empresa : str
        Nombre de la empresa
    """
    print(f"\n" + "=" * 60)
    print(f"📊 BENCHMARKING ANÓNIMO - {nombre_empresa.upper()}")
    print("=" * 60)
    print(f"🏷️ Giro: {giro}")
    print(f"🔒 Comparación completamente anónima")
    print()

    # Posición relativa
    if 'posicion_relativa' in benchmarks and benchmarks['posicion_relativa']:
        pos = benchmarks['posicion_relativa']
        categoria = pos.get('categoria', 'N/A')
        descripcion = pos.get('descripcion', '')

        # Emoji según la categoría
        emoji = "🏆" if "Líder" in categoria else "📈" if "encima" in categoria else "📊" if "promedio" in categoria else "📉"

        print(f"🎯 POSICIÓN RELATIVA EN EL GIRO:")
        print(f"  {emoji} {categoria}")
        print(f"  {descripcion}")
        print()

    # Comparación con el giro
    if 'comparacion_giro' in benchmarks and benchmarks['comparacion_giro']:
        comp_giro = benchmarks['comparacion_giro']

        print(f"📊 COMPARACIÓN CON EL GIRO {giro.upper()}:")
        print("-" * 40)

        if 'ingresos_vs_giro' in comp_giro:
            ratio = comp_giro['ingresos_ratio']
            emoji = "🟢" if ratio > 1.1 else "🟡" if ratio > 0.9 else "🔴"
            print(f"  {emoji} Ingresos vs giro: {comp_giro['ingresos_vs_giro']}")

        if 'clientes_vs_giro' in comp_giro:
            ratio = comp_giro['clientes_ratio']
            emoji = "🟢" if ratio > 1.1 else "🟡" if ratio > 0.9 else "🔴"
            print(f"  {emoji} Clientes vs giro: {comp_giro['clientes_vs_giro']}")

        if 'precio_vs_giro' in comp_giro:
            ratio = comp_giro['precio_ratio']
            emoji = "🟢" if ratio > 1.05 else "🟡" if ratio > 0.95 else "🔴"
            print(f"  {emoji} Precios vs giro: {comp_giro['precio_vs_giro']}")

        print()

    # Comparación con el clúster
    if 'comparacion_cluster' in benchmarks and benchmarks['comparacion_cluster']:
        comp_cluster = benchmarks['comparacion_cluster']

        print(f"🌐 COMPARACIÓN CON EL CLÚSTER COMPLETO:")
        print("-" * 40)

        if 'ticket_vs_cluster' in comp_cluster:
            ratio = comp_cluster['ticket_ratio']
            emoji = "🟢" if ratio > 1.1 else "🟡" if ratio > 0.9 else "🔴"
            print(f"  {emoji} Ticket promedio vs clúster: {comp_cluster['ticket_vs_cluster']}")

        print()

    # Fortalezas
    if benchmarks.get('fortalezas'):
        print(f"💪 FORTALEZAS IDENTIFICADAS:")
        for i, fortaleza in enumerate(benchmarks['fortalezas'], 1):
            print(f"  {i}. {fortaleza}")
        print()

    # Áreas de mejora
    if benchmarks.get('areas_mejora'):
        print(f"🎯 ÁREAS DE MEJORA:")
        for i, area in enumerate(benchmarks['areas_mejora'], 1):
            print(f"  {i}. {area}")
        print()


def generar_recomendaciones_benchmark(benchmarks: Dict, giro: str) -> List[str]:
    """
    Generar recomendaciones basadas en el benchmarking.

    Parameters
    ----------
    benchmarks : Dict
        Resultados del benchmarking
    giro : str
        Giro de la empresa

    Returns
    -------
    List[str]
        Lista de recomendaciones
    """
    recomendaciones = []

    # Recomendaciones basadas en posición relativa
    if 'posicion_relativa' in benchmarks:
        categoria = benchmarks['posicion_relativa'].get('categoria', '')

        if "Líder" in categoria:
            recomendaciones.append("🏆 Mantén tu liderazgo y considera compartir mejores prácticas")
            recomendaciones.append("📈 Explora oportunidades de expansión o diversificación")
        elif "Por debajo" in categoria:
            recomendaciones.append("🎯 Enfócate en mejorar las métricas clave identificadas")
            recomendaciones.append("📚 Estudia las mejores prácticas del giro")

    # Recomendaciones específicas por métrica
    if 'comparacion_giro' in benchmarks:
        comp = benchmarks['comparacion_giro']

        if comp.get('ingresos_ratio', 1) < 0.9:
            recomendaciones.append("💰 Revisa tu estrategia de precios y mix de productos")
            recomendaciones.append("📊 Analiza los canales de venta más efectivos del giro")

        if comp.get('clientes_ratio', 1) < 0.9:
            recomendaciones.append("👥 Mejora tu estrategia de marketing y captación")
            recomendaciones.append("🎯 Optimiza la experiencia del cliente para aumentar retención")

        if comp.get('precio_ratio', 1) < 0.95:
            recomendaciones.append("💎 Considera mejorar la propuesta de valor para justificar precios premium")
            recomendaciones.append("🏷️ Evalúa si tus precios están alineados con el mercado")

    # Recomendaciones específicas por giro
    if giro == 'hotel':
        recomendaciones.append("🏨 Optimiza tu revenue management basado en patrones del giro")
        recomendaciones.append("⭐ Mejora tu rating online para competir efectivamente")
    elif giro == 'restaurante':
        recomendaciones.append("🍽️ Analiza tu menú y precios vs la competencia del giro")
        recomendaciones.append("📱 Considera delivery y marketing digital")
    elif giro == 'agencia_viajes':
        recomendaciones.append("✈️ Especialízate en nichos rentables del mercado")
        recomendaciones.append("🤝 Mejora las alianzas con proveedores")

    return recomendaciones


def guardar_reporte_benchmark(configuracion: Dict, benchmarks: Dict, recomendaciones: List[str]):
    """
    Guardar reporte de benchmarking para referencia futura.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    benchmarks : Dict
        Resultados del benchmarking
    recomendaciones : List[str]
        Recomendaciones generadas
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reporte = {
        "empresa": {
            "nombre": configuracion['empresa']['nombre'],
            "giro": configuracion['empresa']['giro']
        },
        "timestamp_benchmark": datetime.now().isoformat(),
        "resultados_benchmark": benchmarks,
        "recomendaciones": recomendaciones,
        "resumen_ejecutivo": {
            "posicion_relativa": benchmarks.get('posicion_relativa', {}).get('categoria', 'N/A'),
            "num_fortalezas": len(benchmarks.get('fortalezas', [])),
            "num_areas_mejora": len(benchmarks.get('areas_mejora', [])),
            "num_recomendaciones": len(recomendaciones)
        }
    }

    # Crear directorio de benchmarks
    os.makedirs("benchmarks_anonimos", exist_ok=True)

    archivo_benchmark = f"benchmarks_anonimos/benchmark_{timestamp}.json"
    with open(archivo_benchmark, "w") as f:
        json.dump(reporte, f, indent=2)

    print(f"\n💾 Reporte de benchmark guardado: {archivo_benchmark}")


def main():
    """
    Función principal del script de benchmarking anónimo.
    """
    parser = argparse.ArgumentParser(description="Realizar benchmarking anónimo vs el giro y clúster")
    parser.add_argument("--mi-giro", type=str, help="Tu giro turístico (opcional, usa el de la configuración si no se especifica)")

    args = parser.parse_args()

    print("📊 BENCHMARKING ANÓNIMO - CLÚSTER DE TURISMO NL")
    print("=" * 60)
    print("Comparando tu rendimiento con el promedio del sector")
    print("🔒 Comparación completamente anónima - nadie puede identificarte")
    print()

    # Cargar configuración
    configuracion = cargar_configuracion_empresa()
    if not configuracion:
        return False

    giro = args.mi_giro or configuracion['empresa']['giro']
    nombre_empresa = configuracion['empresa']['nombre']
    api_url = configuracion['conexion']['api_url']

    print(f"✅ Configuración cargada para: {nombre_empresa}")
    print(f"🏷️ Giro: {giro}")
    print()

    # Cargar métricas de la empresa
    print("📊 Cargando tus métricas...")
    metricas_empresa = cargar_metricas_empresa()
    if not metricas_empresa:
        return False

    # Obtener métricas del clúster
    print("🌐 Obteniendo métricas del clúster...")
    metricas_cluster = obtener_metricas_cluster(api_url)
    if not metricas_cluster:
        print("⚠️ No se pudieron obtener métricas del clúster")
        return False

    # Obtener métricas del giro
    print(f"🏷️ Obteniendo métricas del giro {giro}...")
    metricas_giro = obtener_metricas_giro(api_url, giro)
    if not metricas_giro:
        print(f"⚠️ No se pudieron obtener métricas del giro {giro}")
        return False

    # Calcular benchmarks
    print("🔍 Calculando benchmarks...")
    benchmarks = calcular_benchmarks(metricas_empresa, metricas_giro, metricas_cluster)

    # Mostrar resultados
    mostrar_benchmarks(benchmarks, giro, nombre_empresa)

    # Generar recomendaciones
    recomendaciones = generar_recomendaciones_benchmark(benchmarks, giro)

    if recomendaciones:
        print(f"💡 RECOMENDACIONES ESTRATÉGICAS:")
        for i, rec in enumerate(recomendaciones, 1):
            print(f"  {i}. {rec}")
        print()

    # Guardar reporte
    guardar_reporte_benchmark(configuracion, benchmarks, recomendaciones)

    print(f"🎯 PRÓXIMOS PASOS:")
    print(f"  1. Implementa las recomendaciones prioritarias")
    print(f"  2. Monitorea tu progreso mensualmente")
    print(f"  3. Compara con benchmarks históricos")
    print(f"  4. Ajusta estrategias según resultados")

    return True


if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            print(f"\n🎉 ¡Benchmarking completado exitosamente!")
            print(f"📊 Usa estos insights para mejorar tu posición competitiva")
        else:
            print(f"\n💥 El benchmarking no se pudo completar")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Benchmarking cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
