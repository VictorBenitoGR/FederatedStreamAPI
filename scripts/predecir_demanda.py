# ./scripts/predecir_demanda.py

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


def generar_predicciones_demanda(api_url: str, giro: str, fecha_inicio: str,
                                 fecha_fin: str, parametros_adicionales: Optional[Dict] = None) -> Optional[Dict]:
    """
    Generar predicciones de demanda usando la API del clúster.

    Parameters
    ----------
    api_url : str
        URL de la API del clúster
    giro : str
        Giro turístico
    fecha_inicio : str
        Fecha de inicio (YYYY-MM-DD)
    fecha_fin : str
        Fecha de fin (YYYY-MM-DD)
    parametros_adicionales : Optional[Dict]
        Parámetros adicionales para la predicción

    Returns
    -------
    Optional[Dict]
        Predicciones generadas o None si hay error
    """
    try:
        print(f"🔮 Generando predicciones de demanda...")
        print(f"   Giro: {giro}")
        print(f"   Período: {fecha_inicio} a {fecha_fin}")

        payload = {
            "giro": giro,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

        if parametros_adicionales:
            payload.update(parametros_adicionales)

        response = requests.post(
            f"{api_url}/predictions/demand",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error generando predicciones: {response.status_code}")
            print(f"   Detalle: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def mostrar_predicciones(predicciones: Dict, giro: str):
    """
    Mostrar predicciones de forma clara y útil.

    Parameters
    ----------
    predicciones : Dict
        Predicciones generadas
    giro : str
        Giro turístico
    """
    print(f"\n" + "=" * 60)
    print(f"🔮 PREDICCIONES DE DEMANDA - {giro.upper()}")
    print("=" * 60)

    if 'predicciones' not in predicciones:
        print("❌ No se encontraron predicciones en la respuesta")
        return

    preds = predicciones['predicciones']

    print(f"📅 Período: {predicciones.get('fecha_inicio')} a {predicciones.get('fecha_fin')}")
    print(f"📊 Total de predicciones: {len(preds)}")
    print()

    # Mostrar predicciones diarias
    print("📈 PREDICCIONES DIARIAS:")
    print("-" * 40)

    total_predicho = 0
    for pred in preds:
        fecha = pred.get('fecha', 'N/A')
        valor = pred.get('prediccion', 0)
        confianza = pred.get('confianza', 0)

        # Formatear fecha para mejor legibilidad
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            fecha_formateada = fecha_obj.strftime('%a %d/%m')
        except:
            fecha_formateada = fecha

        print(f"  {fecha_formateada}: {valor:8.0f} clientes (confianza: {confianza:.2f})")
        total_predicho += valor

    # Estadísticas resumen
    print(f"\n📊 RESUMEN ESTADÍSTICO:")
    print(f"  Total predicho: {total_predicho:,.0f} clientes")
    print(f"  Promedio diario: {total_predicho/len(preds):,.0f} clientes")

    valores = [p.get('prediccion', 0) for p in preds]
    if valores:
        print(f"  Día más alto: {max(valores):,.0f} clientes")
        print(f"  Día más bajo: {min(valores):,.0f} clientes")
        print(f"  Variabilidad: {(max(valores) - min(valores))/max(valores)*100:.1f}%")

    # Mostrar intervalos de confianza si están disponibles
    if 'intervalos_confianza' in predicciones:
        print(f"\n📊 INTERVALOS DE CONFIANZA:")
        intervalos = predicciones['intervalos_confianza']
        for i, intervalo in enumerate(intervalos[:5]):  # Primeros 5 días
            fecha = intervalo.get('fecha', f'Día {i+1}')
            inf = intervalo.get('limite_inferior', 0)
            sup = intervalo.get('limite_superior', 0)
            print(f"  {fecha}: [{inf:.0f} - {sup:.0f}] clientes")

    # Mostrar factores de influencia
    if 'factores_influencia' in predicciones:
        print(f"\n🎯 FACTORES DE INFLUENCIA:")
        factores = predicciones['factores_influencia']
        for factor, peso in factores.items():
            print(f"  {factor.replace('_', ' ').title()}: {peso:.1%}")


def analizar_tendencias_predicciones(predicciones: Dict) -> Dict:
    """
    Analizar tendencias en las predicciones.

    Parameters
    ----------
    predicciones : Dict
        Predicciones generadas

    Returns
    -------
    Dict
        Análisis de tendencias
    """
    if 'predicciones' not in predicciones:
        return {}

    preds = predicciones['predicciones']
    valores = [p.get('prediccion', 0) for p in preds]
    fechas = [p.get('fecha', '') for p in preds]

    if len(valores) < 2:
        return {}

    # Calcular tendencia general
    primera_mitad = valores[:len(valores) // 2]
    segunda_mitad = valores[len(valores) // 2:]

    promedio_inicial = sum(primera_mitad) / len(primera_mitad)
    promedio_final = sum(segunda_mitad) / len(segunda_mitad)

    cambio_porcentual = (promedio_final - promedio_inicial) / promedio_inicial * 100

    # Identificar días de la semana
    dias_semana = {}
    for i, fecha in enumerate(fechas):
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            dia_semana = fecha_obj.strftime('%A')
            if dia_semana not in dias_semana:
                dias_semana[dia_semana] = []
            dias_semana[dia_semana].append(valores[i])
        except:
            continue

    # Promedios por día de la semana
    promedios_dia = {}
    for dia, vals in dias_semana.items():
        promedios_dia[dia] = sum(vals) / len(vals)

    return {
        "tendencia_general": "creciente" if cambio_porcentual > 5 else "decreciente" if cambio_porcentual < -5 else "estable",
        "cambio_porcentual": cambio_porcentual,
        "promedio_inicial": promedio_inicial,
        "promedio_final": promedio_final,
        "mejor_dia_semana": max(promedios_dia.items(), key=lambda x: x[1]) if promedios_dia else None,
        "peor_dia_semana": min(promedios_dia.items(), key=lambda x: x[1]) if promedios_dia else None,
        "promedios_por_dia": promedios_dia
    }


def generar_recomendaciones_operativas(predicciones: Dict, tendencias: Dict, giro: str) -> List[str]:
    """
    Generar recomendaciones operativas basadas en las predicciones.

    Parameters
    ----------
    predicciones : Dict
        Predicciones generadas
    tendencias : Dict
        Análisis de tendencias
    giro : str
        Giro turístico

    Returns
    -------
    List[str]
        Lista de recomendaciones
    """
    recomendaciones = []

    if not predicciones.get('predicciones'):
        return recomendaciones

    preds = predicciones['predicciones']
    valores = [p.get('prediccion', 0) for p in preds]

    # Recomendaciones basadas en variabilidad
    if valores:
        variabilidad = (max(valores) - min(valores)) / max(valores) * 100

        if variabilidad > 30:
            recomendaciones.append("📊 Alta variabilidad detectada - considera personal flexible o por horas")

        if max(valores) > sum(valores) / len(valores) * 1.5:
            recomendaciones.append("⚡ Días pico identificados - prepara inventario y personal adicional")

    # Recomendaciones basadas en tendencias
    if tendencias.get('tendencia_general') == 'creciente':
        recomendaciones.append("📈 Tendencia creciente - considera expandir capacidad gradualmente")
    elif tendencias.get('tendencia_general') == 'decreciente':
        recomendaciones.append("📉 Tendencia decreciente - optimiza costos y enfócate en retención")

    # Recomendaciones por día de la semana
    if tendencias.get('mejor_dia_semana'):
        mejor_dia, mejor_valor = tendencias['mejor_dia_semana']
        recomendaciones.append(f"🗓️ {mejor_dia} es tu mejor día - maximiza ofertas y promociones")

    if tendencias.get('peor_dia_semana'):
        peor_dia, peor_valor = tendencias['peor_dia_semana']
        recomendaciones.append(f"💡 {peor_dia} es más lento - considera mantenimiento o promociones especiales")

    # Recomendaciones específicas por giro
    if giro == 'hotel':
        recomendaciones.append("🏨 Ajusta tarifas dinámicamente según la demanda predicha")
        recomendaciones.append("🛏️ Optimiza housekeeping según ocupación esperada")
    elif giro == 'restaurante':
        recomendaciones.append("🍽️ Planifica compras de ingredientes según demanda predicha")
        recomendaciones.append("👨‍🍳 Ajusta turnos de cocina y servicio")
    elif giro == 'agencia_viajes':
        recomendaciones.append("✈️ Negocia mejores tarifas con proveedores en días de alta demanda")
        recomendaciones.append("📞 Refuerza call center en períodos pico")

    return recomendaciones


def guardar_predicciones(configuracion: Dict, predicciones: Dict, tendencias: Dict, recomendaciones: List[str]):
    """
    Guardar predicciones y análisis para referencia futura.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    predicciones : Dict
        Predicciones generadas
    tendencias : Dict
        Análisis de tendencias
    recomendaciones : List[str]
        Recomendaciones generadas
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reporte_predicciones = {
        "empresa": {
            "nombre": configuracion['empresa']['nombre'],
            "giro": configuracion['empresa']['giro']
        },
        "timestamp_generacion": datetime.now().isoformat(),
        "predicciones": predicciones,
        "analisis_tendencias": tendencias,
        "recomendaciones_operativas": recomendaciones,
        "resumen": {
            "periodo": f"{predicciones.get('fecha_inicio')} a {predicciones.get('fecha_fin')}",
            "total_dias": len(predicciones.get('predicciones', [])),
            "demanda_total_predicha": sum(p.get('prediccion', 0) for p in predicciones.get('predicciones', [])),
            "demanda_promedio_diaria": sum(p.get('prediccion', 0) for p in predicciones.get('predicciones', [])) / len(predicciones.get('predicciones', [])) if predicciones.get('predicciones') else 0
        }
    }

    # Crear directorio de predicciones
    os.makedirs("predicciones_demanda", exist_ok=True)

    archivo_predicciones = f"predicciones_demanda/prediccion_{timestamp}.json"
    with open(archivo_predicciones, "w") as f:
        json.dump(reporte_predicciones, f, indent=2)

    print(f"\n💾 Predicciones guardadas: {archivo_predicciones}")

    # Crear archivo CSV para análisis en Excel
    if predicciones.get('predicciones'):
        df_predicciones = pd.DataFrame(predicciones['predicciones'])
        archivo_csv = f"predicciones_demanda/prediccion_{timestamp}.csv"
        df_predicciones.to_csv(archivo_csv, index=False)
        print(f"📊 CSV generado: {archivo_csv}")


def main():
    """
    Función principal del script de predicción de demanda.
    """
    parser = argparse.ArgumentParser(description="Generar predicciones de demanda usando modelos federados")
    parser.add_argument("--giro", type=str, help="Giro turístico (opcional, usa el de la configuración si no se especifica)")
    parser.add_argument("--fecha-inicio", type=str, required=True, help="Fecha de inicio (YYYY-MM-DD)")
    parser.add_argument("--fecha-fin", type=str, required=True, help="Fecha de fin (YYYY-MM-DD)")
    parser.add_argument("--parametros", type=str, help="Parámetros adicionales en formato JSON")

    args = parser.parse_args()

    print("🔮 PREDICCIÓN DE DEMANDA - CLÚSTER DE TURISMO NL")
    print("=" * 60)
    print("Generando predicciones usando modelos federados del clúster")
    print("🔒 Basado en conocimiento agregado, preservando privacidad")
    print()

    # Cargar configuración
    configuracion = cargar_configuracion_empresa()
    if not configuracion:
        return False

    # Determinar giro
    giro = args.giro or configuracion['empresa']['giro']

    print(f"✅ Configuración cargada para: {configuracion['empresa']['nombre']}")
    print(f"🏷️ Giro: {giro}")
    print(f"📅 Período: {args.fecha_inicio} a {args.fecha_fin}")

    # Parsear parámetros adicionales
    parametros_adicionales = None
    if args.parametros:
        try:
            parametros_adicionales = json.loads(args.parametros)
        except json.JSONDecodeError:
            print("⚠️ Error parseando parámetros adicionales, ignorando...")

    api_url = configuracion['conexion']['api_url']

    # Generar predicciones
    predicciones = generar_predicciones_demanda(
        api_url, giro, args.fecha_inicio, args.fecha_fin, parametros_adicionales
    )

    if not predicciones:
        print("❌ No se pudieron generar predicciones")
        return False

    # Mostrar predicciones
    mostrar_predicciones(predicciones, giro)

    # Analizar tendencias
    tendencias = analizar_tendencias_predicciones(predicciones)

    if tendencias:
        print(f"\n📈 ANÁLISIS DE TENDENCIAS:")
        print(f"  Tendencia general: {tendencias.get('tendencia_general', 'N/A')}")
        print(f"  Cambio porcentual: {tendencias.get('cambio_porcentual', 0):+.1f}%")

        if tendencias.get('mejor_dia_semana'):
            mejor_dia, mejor_valor = tendencias['mejor_dia_semana']
            print(f"  Mejor día: {mejor_dia} ({mejor_valor:.0f} clientes promedio)")

    # Generar recomendaciones
    recomendaciones = generar_recomendaciones_operativas(predicciones, tendencias, giro)

    if recomendaciones:
        print(f"\n💡 RECOMENDACIONES OPERATIVAS:")
        for i, rec in enumerate(recomendaciones, 1):
            print(f"  {i}. {rec}")

    # Guardar resultados
    guardar_predicciones(configuracion, predicciones, tendencias, recomendaciones)

    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"  1. Implementa las recomendaciones operativas")
    print(f"  2. Monitorea la precisión de las predicciones")
    print(f"  3. Ajusta tu planificación según las tendencias")
    print(f"  4. Genera nuevas predicciones regularmente")

    return True


if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            print(f"\n🎉 ¡Predicciones generadas exitosamente!")
        else:
            print(f"\n💥 No se pudieron generar las predicciones")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
