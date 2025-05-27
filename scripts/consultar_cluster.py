# ./scripts/consultar_cluster.py

import os
import json
import sys
import requests
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


def consultar_metricas_generales(api_url: str) -> Optional[Dict]:
    """
    Consultar métricas generales del clúster.

    Parameters
    ----------
    api_url : str
        URL de la API del clúster

    Returns
    -------
    Optional[Dict]
        Métricas generales o None si hay error
    """
    try:
        print("📊 Consultando métricas generales del clúster...")
        response = requests.get(f"{api_url}/metrics/general", timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error consultando métricas: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("   Verifica que la API esté funcionando")
        return None


def consultar_metricas_por_giro(api_url: str, giro: str) -> Optional[Dict]:
    """
    Consultar métricas específicas de un giro.

    Parameters
    ----------
    api_url : str
        URL de la API del clúster
    giro : str
        Giro turístico a consultar

    Returns
    -------
    Optional[Dict]
        Métricas del giro o None si hay error
    """
    try:
        print(f"🏷️ Consultando métricas para giro: {giro}")
        response = requests.get(f"{api_url}/metrics/by-sector/{giro}", timeout=30)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"⚠️ No hay datos suficientes para el giro {giro}")
            return None
        else:
            print(f"❌ Error consultando giro: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def consultar_modelos_agregados(api_url: str) -> Dict[str, Optional[Dict]]:
    """
    Consultar modelos agregados disponibles.

    Parameters
    ----------
    api_url : str
        URL de la API del clúster

    Returns
    -------
    Dict[str, Optional[Dict]]
        Diccionario con modelos disponibles
    """
    modelos = {}
    tipos_modelo = ["prediccion_demanda", "clasificacion_viajero"]

    for tipo in tipos_modelo:
        try:
            print(f"🤖 Consultando modelo: {tipo}")
            response = requests.get(f"{api_url}/federated/get-aggregated/{tipo}", timeout=30)

            if response.status_code == 200:
                modelos[tipo] = response.json()
                print(f"✅ Modelo {tipo} disponible")
            elif response.status_code == 404:
                print(f"⚠️ Modelo {tipo} no disponible aún")
                modelos[tipo] = None
            else:
                print(f"❌ Error consultando {tipo}: {response.status_code}")
                modelos[tipo] = None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión para {tipo}: {e}")
            modelos[tipo] = None

    return modelos


def mostrar_metricas_generales(metricas: Dict):
    """
    Mostrar métricas generales del clúster de forma clara.

    Parameters
    ----------
    metricas : Dict
        Métricas generales del clúster
    """
    print("\n" + "=" * 60)
    print("📊 MÉTRICAS GENERALES DEL CLÚSTER")
    print("=" * 60)

    if 'metricas_economicas' in metricas:
        economicas = metricas['metricas_economicas']

        print("💰 INDICADORES ECONÓMICOS:")
        print(f"  Ingresos totales del clúster: ${economicas.get('ingresos_totales_cluster', 0):,.0f}")
        print(f"  Ingreso promedio diario: ${economicas.get('ingreso_promedio_diario', 0):,.0f}")
        print(f"  Clientes totales atendidos: {economicas.get('clientes_totales_atendidos', 0):,}")
        print(f"  Ticket promedio del clúster: ${economicas.get('ticket_promedio_cluster', 0):,.0f}")

    if 'metricas_eventos' in metricas:
        eventos = metricas['metricas_eventos']

        print("\n🎪 INDICADORES DE EVENTOS:")
        print(f"  Total de eventos realizados: {eventos.get('total_eventos_realizados', 0):,}")
        print(f"  Asistentes totales: {eventos.get('asistentes_totales', 0):,}")
        print(f"  Asistentes promedio por evento: {eventos.get('asistentes_promedio_evento', 0):.0f}")
        print(f"  Ocupación promedio: {eventos.get('ocupacion_promedio_eventos', 0):.1f}%")

    if 'perfil_viajeros' in metricas:
        viajeros = metricas['perfil_viajeros']

        print("\n👥 PERFIL DE VIAJEROS:")
        print(f"  Total de perfiles analizados: {viajeros.get('total_perfiles_analizados', 0):,}")
        print(f"  Gasto promedio por viajero: ${viajeros.get('gasto_promedio_viajero', 0):,.0f}")
        print(f"  Estancia promedio: {viajeros.get('estancia_promedio_dias', 0):.1f} días")
        print(f"  Tipos de viajero: {viajeros.get('tipos_viajero_representados', 0)}")


def mostrar_metricas_giro(metricas: Dict, giro: str):
    """
    Mostrar métricas específicas de un giro.

    Parameters
    ----------
    metricas : Dict
        Métricas del giro
    giro : str
        Nombre del giro
    """
    print(f"\n" + "=" * 60)
    print(f"🏷️ MÉTRICAS DEL GIRO: {giro.upper()}")
    print("=" * 60)

    if 'metricas_economicas' in metricas:
        economicas = metricas['metricas_economicas']

        print("💰 RENDIMIENTO ECONÓMICO:")
        print(f"  Ingresos totales: ${economicas.get('ingresos_totales', 0):,.0f}")
        print(f"  Ingresos promedio diario: ${economicas.get('ingresos_promedio_diario', 0):,.0f}")
        print(f"  Clientes totales: {economicas.get('clientes_totales', 0):,}")
        print(f"  Clientes promedio diario: {economicas.get('clientes_promedio_diario', 0):.0f}")
        print(f"  Precio promedio: ${economicas.get('precio_promedio', 0):,.0f}")

    if 'patrones_temporales' in metricas:
        patrones = metricas['patrones_temporales']

        print("\n📅 PATRONES TEMPORALES:")
        if 'mejor_mes' in patrones:
            mejor_mes = patrones['mejor_mes']
            print(f"  Mejor mes: {mejor_mes.get('mes', 'N/A')} (${mejor_mes.get('ingresos', 0):,.0f})")

        if 'mejor_dia_semana' in patrones:
            mejor_dia = patrones['mejor_dia_semana']
            print(f"  Mejor período: {mejor_dia.get('tipo', 'N/A')} (factor: {mejor_dia.get('factor', 1):.2f}x)")

    if 'comparacion_cluster' in metricas:
        comparacion = metricas['comparacion_cluster']

        print("\n📊 COMPARACIÓN CON EL CLÚSTER:")
        print(f"  Participación en ingresos: {comparacion.get('participacion_ingresos', 0):.2f}%")
        print(f"  Participación en clientes: {comparacion.get('participacion_clientes', 0):.2f}%")


def mostrar_modelos_disponibles(modelos: Dict[str, Optional[Dict]]):
    """
    Mostrar información sobre modelos agregados disponibles.

    Parameters
    ----------
    modelos : Dict[str, Optional[Dict]]
        Diccionario con modelos disponibles
    """
    print(f"\n" + "=" * 60)
    print("🤖 MODELOS AGREGADOS DISPONIBLES")
    print("=" * 60)

    for tipo_modelo, modelo in modelos.items():
        print(f"\n📈 {tipo_modelo.replace('_', ' ').title()}:")

        if modelo:
            print(f"  ✅ Disponible")
            print(f"  Contribuciones: {modelo.get('num_contribuciones', 0)} empresas")
            print(f"  Confianza: {modelo.get('confianza', 0):.3f}")
            print(f"  Última actualización: {modelo.get('timestamp_agregacion', 'N/A')}")

            if 'metricas_agregadas' in modelo:
                metricas = modelo['metricas_agregadas']
                print(f"  Métricas:")
                for metrica, valor in metricas.items():
                    if isinstance(valor, float):
                        print(f"    {metrica}: {valor:.3f}")
                    else:
                        print(f"    {metrica}: {valor}")
        else:
            print(f"  ❌ No disponible")
            print(f"  Se necesitan más contribuciones de empresas")


def generar_recomendaciones(configuracion: Dict, metricas_generales: Optional[Dict],
                            metricas_giro: Optional[Dict], modelos: Dict[str, Optional[Dict]]):
    """
    Generar recomendaciones personalizadas para la empresa.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    metricas_generales : Optional[Dict]
        Métricas generales del clúster
    metricas_giro : Optional[Dict]
        Métricas del giro de la empresa
    modelos : Dict[str, Optional[Dict]]
        Modelos disponibles
    """
    print(f"\n" + "=" * 60)
    print("💡 RECOMENDACIONES PERSONALIZADAS")
    print("=" * 60)

    giro = configuracion['empresa']['giro']
    nombre = configuracion['empresa']['nombre']

    print(f"🏢 Para: {nombre} ({giro})")
    print()

    recomendaciones = []

    # Recomendaciones basadas en métricas del giro
    if metricas_giro and 'patrones_temporales' in metricas_giro:
        patrones = metricas_giro['patrones_temporales']

        if 'mejor_mes' in patrones:
            mes = patrones['mejor_mes'].get('mes', 0)
            if mes:
                recomendaciones.append(f"📅 Optimiza tu operación para el mes {mes} (mejor rendimiento del giro)")

        if 'mejor_dia_semana' in patrones:
            tipo_dia = patrones['mejor_dia_semana'].get('tipo', '')
            factor = patrones['mejor_dia_semana'].get('factor', 1)
            if factor > 1.2:
                recomendaciones.append(f"📈 Enfócate en {tipo_dia} (rendimiento {factor:.1f}x superior)")

    # Recomendaciones basadas en modelos disponibles
    if modelos.get('prediccion_demanda'):
        recomendaciones.append("🔮 Usa el modelo de predicción para planificar inventario y personal")

    if modelos.get('clasificacion_viajero'):
        recomendaciones.append("👥 Aplica el modelo de clasificación para personalizar ofertas")

    # Recomendaciones basadas en comparación con el clúster
    if metricas_giro and 'comparacion_cluster' in metricas_giro:
        participacion = metricas_giro['comparacion_cluster'].get('participacion_ingresos', 0)
        if participacion < 1.0:  # Menos del 1% del clúster
            recomendaciones.append("📊 Considera estrategias de crecimiento basadas en mejores prácticas del clúster")

    # Mostrar recomendaciones
    if recomendaciones:
        for i, rec in enumerate(recomendaciones, 1):
            print(f"{i}. {rec}")
    else:
        print("📊 Continúa participando en el clúster para obtener más insights")

    # Próximos pasos
    print(f"\n🎯 PRÓXIMOS PASOS SUGERIDOS:")
    print(f"1. Ejecuta predicciones específicas: python scripts/predecir_demanda.py")
    print(f"2. Haz benchmarking detallado: python scripts/benchmark_anonimo.py")
    print(f"3. Analiza tendencias estacionales: python scripts/analizar_tendencias.py")
    print(f"4. Vuelve a entrenar modelos: python scripts/entrenar_y_enviar.py")


def guardar_reporte_consulta(configuracion: Dict, metricas_generales: Optional[Dict],
                             metricas_giro: Optional[Dict], modelos: Dict[str, Optional[Dict]]):
    """
    Guardar reporte de la consulta para referencia futura.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    metricas_generales : Optional[Dict]
        Métricas generales
    metricas_giro : Optional[Dict]
        Métricas del giro
    modelos : Dict[str, Optional[Dict]]
        Modelos disponibles
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    reporte = {
        "empresa": {
            "nombre": configuracion['empresa']['nombre'],
            "giro": configuracion['empresa']['giro'],
            "id": configuracion['empresa']['id']
        },
        "timestamp_consulta": datetime.now().isoformat(),
        "metricas_generales": metricas_generales,
        "metricas_giro": metricas_giro,
        "modelos_disponibles": {
            tipo: modelo is not None for tipo, modelo in modelos.items()
        },
        "resumen_modelos": {
            tipo: {
                "disponible": modelo is not None,
                "contribuciones": modelo.get('num_contribuciones', 0) if modelo else 0,
                "confianza": modelo.get('confianza', 0) if modelo else 0
            } for tipo, modelo in modelos.items()
        }
    }

    # Crear directorio de reportes
    os.makedirs("reportes_cluster", exist_ok=True)

    archivo_reporte = f"reportes_cluster/consulta_{timestamp}.json"
    with open(archivo_reporte, "w") as f:
        json.dump(reporte, f, indent=2)

    print(f"\n💾 Reporte guardado: {archivo_reporte}")


def main():
    """
    Función principal del script de consulta del clúster.
    """
    print("📊 CONSULTA DEL CLÚSTER - TURISMO NL")
    print("=" * 60)
    print("Consultando resultados agregados del clúster para tu empresa")
    print("🔒 Solo recibes información agregada, nunca datos individuales")
    print()

    # Cargar configuración
    configuracion = cargar_configuracion_empresa()
    if not configuracion:
        return False

    print(f"✅ Configuración cargada para: {configuracion['empresa']['nombre']}")
    print(f"🏷️ Giro: {configuracion['empresa']['giro']}")

    api_url = configuracion['conexion']['api_url']
    giro = configuracion['empresa']['giro']

    # Consultar métricas generales
    metricas_generales = consultar_metricas_generales(api_url)
    if metricas_generales:
        mostrar_metricas_generales(metricas_generales)

    # Consultar métricas del giro específico
    metricas_giro = consultar_metricas_por_giro(api_url, giro)
    if metricas_giro:
        mostrar_metricas_giro(metricas_giro, giro)

    # Consultar modelos agregados
    modelos = consultar_modelos_agregados(api_url)
    mostrar_modelos_disponibles(modelos)

    # Generar recomendaciones
    generar_recomendaciones(configuracion, metricas_generales, metricas_giro, modelos)

    # Guardar reporte
    guardar_reporte_consulta(configuracion, metricas_generales, metricas_giro, modelos)

    return True


if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            print(f"\n🎉 ¡Consulta completada exitosamente!")
            print(f"📊 Usa esta información para tomar mejores decisiones de negocio")
        else:
            print(f"\n💥 La consulta no se pudo completar")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Consulta cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
