# ./scripts/analizar_tendencias.py

import os
import json
import sys
import requests
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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


def obtener_tendencias_giro(api_url: str, giro: str) -> Optional[Dict]:
    """
    Obtener tendencias específicas del giro.

    Parameters
    ----------
    api_url : str
        URL de la API del clúster
    giro : str
        Giro turístico

    Returns
    -------
    Optional[Dict]
        Tendencias del giro o None si hay error
    """
    try:
        print(f"📈 Obteniendo tendencias para giro: {giro}")
        response = requests.get(f"{api_url}/predictions/trends/{giro}", timeout=30)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"⚠️ No hay datos suficientes para analizar tendencias del giro {giro}")
            return None
        else:
            print(f"❌ Error obteniendo tendencias: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def analizar_estacionalidad(tendencias: Dict) -> Dict:
    """
    Analizar patrones estacionales en las tendencias.

    Parameters
    ----------
    tendencias : Dict
        Datos de tendencias del giro

    Returns
    -------
    Dict
        Análisis de estacionalidad
    """
    analisis = {
        "temporada_alta": {},
        "temporada_baja": {},
        "patrones_mensuales": {},
        "patrones_semanales": {},
        "oportunidades": []
    }

    if 'datos_historicos' in tendencias:
        datos = tendencias['datos_historicos']

        # Analizar por meses
        ingresos_por_mes = {}
        for registro in datos:
            fecha = registro.get('fecha', '')
            ingresos = registro.get('ingresos', 0)

            try:
                mes = datetime.strptime(fecha, '%Y-%m-%d').month
                if mes not in ingresos_por_mes:
                    ingresos_por_mes[mes] = []
                ingresos_por_mes[mes].append(ingresos)
            except:
                continue

        # Calcular promedios mensuales
        promedios_mensuales = {}
        for mes, valores in ingresos_por_mes.items():
            promedios_mensuales[mes] = sum(valores) / len(valores)

        if promedios_mensuales:
            # Identificar temporada alta y baja
            mes_mayor = max(promedios_mensuales.items(), key=lambda x: x[1])
            mes_menor = min(promedios_mensuales.items(), key=lambda x: x[1])

            meses_nombres = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }

            analisis['temporada_alta'] = {
                "mes": meses_nombres.get(mes_mayor[0], mes_mayor[0]),
                "ingresos_promedio": mes_mayor[1],
                "factor": mes_mayor[1] / sum(promedios_mensuales.values()) * len(promedios_mensuales)
            }

            analisis['temporada_baja'] = {
                "mes": meses_nombres.get(mes_menor[0], mes_menor[0]),
                "ingresos_promedio": mes_menor[1],
                "factor": mes_menor[1] / sum(promedios_mensuales.values()) * len(promedios_mensuales)
            }

            analisis['patrones_mensuales'] = {
                meses_nombres.get(mes, mes): valor for mes, valor in promedios_mensuales.items()
            }

    # Identificar oportunidades
    if analisis['temporada_alta'] and analisis['temporada_baja']:
        factor_alta = analisis['temporada_alta']['factor']
        factor_baja = analisis['temporada_baja']['factor']

        if factor_alta > 1.3:
            analisis['oportunidades'].append(f"Maximiza capacidad en {analisis['temporada_alta']['mes']}")

        if factor_baja < 0.7:
            analisis['oportunidades'].append(f"Implementa promociones especiales en {analisis['temporada_baja']['mes']}")

        if factor_alta / factor_baja > 2:
            analisis['oportunidades'].append("Alta variabilidad estacional - considera estrategias de diversificación")

    return analisis


def mostrar_analisis_tendencias(tendencias: Dict, estacionalidad: Dict, giro: str):
    """
    Mostrar análisis de tendencias de forma clara.

    Parameters
    ----------
    tendencias : Dict
        Datos de tendencias
    estacionalidad : Dict
        Análisis de estacionalidad
    giro : str
        Giro turístico
    """
    print(f"\n" + "=" * 60)
    print(f"📈 ANÁLISIS DE TENDENCIAS - {giro.upper()}")
    print("=" * 60)

    # Tendencias generales
    if 'tendencia_general' in tendencias:
        tendencia = tendencias['tendencia_general']

        print("🎯 TENDENCIA GENERAL:")
        print(f"  Dirección: {tendencia.get('direccion', 'N/A')}")
        print(f"  Crecimiento anual: {tendencia.get('crecimiento_anual', 0):+.1f}%")
        print(f"  Confianza: {tendencia.get('confianza', 0):.1%}")
        print()

    # Estacionalidad
    if estacionalidad.get('temporada_alta'):
        alta = estacionalidad['temporada_alta']
        print("🌟 TEMPORADA ALTA:")
        print(f"  Mes pico: {alta['mes']}")
        print(f"  Factor: {alta['factor']:.2f}x el promedio")
        print(f"  Ingresos promedio: ${alta['ingresos_promedio']:,.0f}")
        print()

    if estacionalidad.get('temporada_baja'):
        baja = estacionalidad['temporada_baja']
        print("📉 TEMPORADA BAJA:")
        print(f"  Mes más bajo: {baja['mes']}")
        print(f"  Factor: {baja['factor']:.2f}x el promedio")
        print(f"  Ingresos promedio: ${baja['ingresos_promedio']:,.0f}")
        print()

    # Patrones mensuales
    if estacionalidad.get('patrones_mensuales'):
        print("📅 PATRONES MENSUALES:")
        patrones = estacionalidad['patrones_mensuales']
        for mes, valor in patrones.items():
            print(f"  {mes}: ${valor:,.0f}")
        print()

    # Factores de influencia
    if 'factores_influencia' in tendencias:
        print("🎯 FACTORES DE INFLUENCIA:")
        factores = tendencias['factores_influencia']
        for factor, impacto in factores.items():
            print(f"  {factor.replace('_', ' ').title()}: {impacto:.1%}")
        print()


def generar_recomendaciones_tendencias(tendencias: Dict, estacionalidad: Dict, giro: str) -> List[str]:
    """
    Generar recomendaciones basadas en el análisis de tendencias.

    Parameters
    ----------
    tendencias : Dict
        Datos de tendencias
    estacionalidad : Dict
        Análisis de estacionalidad
    giro : str
        Giro turístico

    Returns
    -------
    List[str]
        Lista de recomendaciones
    """
    recomendaciones = []

    # Recomendaciones basadas en tendencia general
    if 'tendencia_general' in tendencias:
        direccion = tendencias['tendencia_general'].get('direccion', '')
        crecimiento = tendencias['tendencia_general'].get('crecimiento_anual', 0)

        if direccion == 'creciente' and crecimiento > 5:
            recomendaciones.append("📈 Tendencia positiva fuerte - considera expandir operaciones")
        elif direccion == 'decreciente' and crecimiento < -5:
            recomendaciones.append("📉 Tendencia negativa - enfócate en eficiencia y retención")
        elif abs(crecimiento) < 2:
            recomendaciones.append("📊 Mercado estable - busca diferenciación competitiva")

    # Recomendaciones basadas en estacionalidad
    if estacionalidad.get('temporada_alta'):
        alta = estacionalidad['temporada_alta']
        if alta['factor'] > 1.5:
            recomendaciones.append(f"🌟 Prepárate para {alta['mes']} - aumenta inventario y personal")

    if estacionalidad.get('temporada_baja'):
        baja = estacionalidad['temporada_baja']
        if baja['factor'] < 0.6:
            recomendaciones.append(f"💡 Aprovecha {baja['mes']} para mantenimiento y capacitación")

    # Oportunidades identificadas
    if estacionalidad.get('oportunidades'):
        recomendaciones.extend(estacionalidad['oportunidades'])

    # Recomendaciones específicas por giro
    if giro == 'hotel':
        recomendaciones.append("🏨 Implementa revenue management dinámico basado en estacionalidad")
        recomendaciones.append("📱 Ajusta estrategias de marketing digital según temporadas")
    elif giro == 'restaurante':
        recomendaciones.append("🍽️ Adapta menú y horarios según patrones estacionales")
        recomendaciones.append("🎉 Crea eventos especiales en temporadas bajas")
    elif giro == 'agencia_viajes':
        recomendaciones.append("✈️ Desarrolla paquetes específicos para cada temporada")
        recomendaciones.append("🎯 Segmenta marketing según patrones de viaje")

    return recomendaciones


def crear_visualizaciones(tendencias: Dict, estacionalidad: Dict, giro: str):
    """
    Crear visualizaciones de las tendencias.

    Parameters
    ----------
    tendencias : Dict
        Datos de tendencias
    estacionalidad : Dict
        Análisis de estacionalidad
    giro : str
        Giro turístico
    """
    try:
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Análisis de Tendencias - {giro.title()}', fontsize=16, fontweight='bold')

        # Gráfico 1: Patrones mensuales
        if estacionalidad.get('patrones_mensuales'):
            patrones = estacionalidad['patrones_mensuales']
            meses = list(patrones.keys())
            valores = list(patrones.values())

            axes[0, 0].bar(meses, valores, color='skyblue', alpha=0.7)
            axes[0, 0].set_title('Ingresos Promedio por Mes')
            axes[0, 0].set_ylabel('Ingresos ($)')
            axes[0, 0].tick_params(axis='x', rotation=45)

        # Gráfico 2: Tendencia temporal (simulada)
        if 'datos_historicos' in tendencias:
            datos = tendencias['datos_historicos'][:50]  # Primeros 50 registros
            fechas = [datetime.strptime(d['fecha'], '%Y-%m-%d') for d in datos if 'fecha' in d]
            ingresos = [d['ingresos'] for d in datos if 'ingresos' in d]

            if fechas and ingresos:
                axes[0, 1].plot(fechas, ingresos, color='green', alpha=0.7)
                axes[0, 1].set_title('Tendencia Temporal')
                axes[0, 1].set_ylabel('Ingresos ($)')
                axes[0, 1].tick_params(axis='x', rotation=45)

        # Gráfico 3: Factores de influencia
        if 'factores_influencia' in tendencias:
            factores = tendencias['factores_influencia']
            nombres = [f.replace('_', ' ').title() for f in factores.keys()]
            valores = list(factores.values())

            axes[1, 0].pie(valores, labels=nombres, autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title('Factores de Influencia')

        # Gráfico 4: Comparación temporadas
        if estacionalidad.get('temporada_alta') and estacionalidad.get('temporada_baja'):
            alta = estacionalidad['temporada_alta']
            baja = estacionalidad['temporada_baja']

            temporadas = ['Temporada Alta', 'Temporada Baja']
            valores = [alta['ingresos_promedio'], baja['ingresos_promedio']]
            colores = ['gold', 'lightcoral']

            axes[1, 1].bar(temporadas, valores, color=colores, alpha=0.7)
            axes[1, 1].set_title('Comparación de Temporadas')
            axes[1, 1].set_ylabel('Ingresos Promedio ($)')

        plt.tight_layout()

        # Guardar gráfico
        os.makedirs("analisis_tendencias", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_grafico = f"analisis_tendencias/tendencias_{giro}_{timestamp}.png"
        plt.savefig(archivo_grafico, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"📊 Gráficos guardados: {archivo_grafico}")

    except Exception as e:
        print(f"⚠️ No se pudieron crear visualizaciones: {e}")


def guardar_analisis_tendencias(configuracion: Dict, tendencias: Dict, estacionalidad: Dict, recomendaciones: List[str]):
    """
    Guardar análisis de tendencias para referencia futura.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    tendencias : Dict
        Datos de tendencias
    estacionalidad : Dict
        Análisis de estacionalidad
    recomendaciones : List[str]
        Recomendaciones generadas
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reporte = {
        "empresa": {
            "nombre": configuracion['empresa']['nombre'],
            "giro": configuracion['empresa']['giro']
        },
        "timestamp_analisis": datetime.now().isoformat(),
        "tendencias_giro": tendencias,
        "analisis_estacionalidad": estacionalidad,
        "recomendaciones_estrategicas": recomendaciones,
        "resumen_ejecutivo": {
            "tendencia_general": tendencias.get('tendencia_general', {}).get('direccion', 'N/A'),
            "crecimiento_anual": tendencias.get('tendencia_general', {}).get('crecimiento_anual', 0),
            "temporada_alta": estacionalidad.get('temporada_alta', {}).get('mes', 'N/A'),
            "temporada_baja": estacionalidad.get('temporada_baja', {}).get('mes', 'N/A'),
            "num_oportunidades": len(estacionalidad.get('oportunidades', [])),
            "num_recomendaciones": len(recomendaciones)
        }
    }

    # Crear directorio de análisis
    os.makedirs("analisis_tendencias", exist_ok=True)

    archivo_analisis = f"analisis_tendencias/analisis_{timestamp}.json"
    with open(archivo_analisis, "w") as f:
        json.dump(reporte, f, indent=2)

    print(f"\n💾 Análisis guardado: {archivo_analisis}")


def main():
    """
    Función principal del script de análisis de tendencias.
    """
    parser = argparse.ArgumentParser(description="Analizar tendencias estacionales y oportunidades del mercado")
    parser.add_argument("--giro", type=str, help="Giro turístico (opcional, usa el de la configuración si no se especifica)")

    args = parser.parse_args()

    print("📈 ANÁLISIS DE TENDENCIAS - CLÚSTER DE TURISMO NL")
    print("=" * 60)
    print("Analizando tendencias estacionales y oportunidades del mercado")
    print("🔒 Basado en datos agregados del clúster, preservando privacidad")
    print()

    # Cargar configuración
    configuracion = cargar_configuracion_empresa()
    if not configuracion:
        return False

    # Determinar giro
    giro = args.giro or configuracion['empresa']['giro']

    print(f"✅ Configuración cargada para: {configuracion['empresa']['nombre']}")
    print(f"🏷️ Giro: {giro}")

    api_url = configuracion['conexion']['api_url']

    # Obtener tendencias del giro
    tendencias = obtener_tendencias_giro(api_url, giro)
    if not tendencias:
        print("❌ No se pudieron obtener tendencias")
        return False

    # Analizar estacionalidad
    print("🔍 Analizando patrones estacionales...")
    estacionalidad = analizar_estacionalidad(tendencias)

    # Mostrar análisis
    mostrar_analisis_tendencias(tendencias, estacionalidad, giro)

    # Mostrar oportunidades
    if estacionalidad.get('oportunidades'):
        print("💡 OPORTUNIDADES IDENTIFICADAS:")
        for i, oportunidad in enumerate(estacionalidad['oportunidades'], 1):
            print(f"  {i}. {oportunidad}")
        print()

    # Generar recomendaciones
    recomendaciones = generar_recomendaciones_tendencias(tendencias, estacionalidad, giro)

    if recomendaciones:
        print("🎯 RECOMENDACIONES ESTRATÉGICAS:")
        for i, rec in enumerate(recomendaciones, 1):
            print(f"  {i}. {rec}")
        print()

    # Crear visualizaciones
    print("📊 Generando visualizaciones...")
    crear_visualizaciones(tendencias, estacionalidad, giro)

    # Guardar análisis
    guardar_analisis_tendencias(configuracion, tendencias, estacionalidad, recomendaciones)

    print(f"🎯 PRÓXIMOS PASOS:")
    print(f"  1. Implementa las recomendaciones estratégicas")
    print(f"  2. Planifica operaciones según estacionalidad")
    print(f"  3. Monitorea cambios en las tendencias")
    print(f"  4. Actualiza análisis trimestralmente")

    return True


if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            print(f"\n🎉 ¡Análisis de tendencias completado exitosamente!")
        else:
            print(f"\n💥 No se pudo completar el análisis")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Análisis cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
