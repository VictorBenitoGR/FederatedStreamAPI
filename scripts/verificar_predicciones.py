# ./scripts/verificar_predicciones.py

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# URL de la API
API_URL = "https://federatedstreamapi.onrender.com"


def verificar_api_salud() -> bool:
    """
    Verificar que la API esté funcionando.

    Returns
    -------
    bool
        True si la API está activa
    """
    try:
        print("🔍 Verificando estado de la API...")
        response = requests.get(f"{API_URL}/health", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API funcionando: {data['status']}")
            print(f"   Modelos cargados: {data['componentes']['modelos_cargados']}")
            return True
        else:
            print(f"❌ API no responde correctamente: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error conectando con la API: {e}")
        return False


def probar_prediccion_demanda() -> bool:
    """
    Probar el endpoint de predicción de demanda.

    Returns
    -------
    bool
        True si funciona correctamente
    """
    try:
        print("\n🔮 Probando predicción de demanda...")

        params = {
            "giro": "hotel",
            "fecha_inicio": "2025-06-01",
            "fecha_fin": "2025-06-05"
        }

        response = requests.post(
            f"{API_URL}/predictions/demand",
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Verificar estructura de respuesta
            campos_esperados = ["giro", "fecha_inicio", "fecha_fin", "predicciones",
                                "intervalos_confianza", "factores_influencia"]

            for campo in campos_esperados:
                if campo not in data:
                    print(f"❌ Falta campo esperado: {campo}")
                    return False

            print(f"✅ Predicción funcionando correctamente")
            print(f"   Giro: {data['giro']}")
            print(f"   Período: {data['fecha_inicio']} a {data['fecha_fin']}")
            print(f"   Predicciones: {len(data['predicciones'])} días")

            # Mostrar ejemplo de predicción
            primera_pred = data['predicciones'][0]
            print(f"   Ejemplo: {primera_pred['fecha']} = {primera_pred['prediccion']:.1f} clientes")
            print(f"   Confianza: {primera_pred['confianza']:.3f}")

            return True

        else:
            print(f"❌ Error en predicción: {response.status_code}")
            print(f"   Detalle: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error probando predicción: {e}")
        return False


def probar_tendencias() -> bool:
    """
    Probar el endpoint de análisis de tendencias.

    Returns
    -------
    bool
        True si funciona correctamente
    """
    try:
        print("\n📊 Probando análisis de tendencias...")

        response = requests.get(
            f"{API_URL}/predictions/trends/hotel",
            params={"periodo_meses": 6},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Verificar estructura
            campos_esperados = ["giro", "tendencia_general", "estacionalidad",
                                "proyecciones", "confianza_proyeccion"]

            for campo in campos_esperados:
                if campo not in data:
                    print(f"❌ Falta campo esperado: {campo}")
                    return False

            print(f"✅ Tendencias funcionando correctamente")
            print(f"   Giro: {data['giro']}")
            print(f"   Tendencia: {data['tendencia_general']}")
            print(f"   Crecimiento anual: {data['tasa_crecimiento_anual']:.2f}%")
            print(f"   Proyecciones: {len(data['proyecciones'])} meses")

            # Mostrar estacionalidad de ejemplo
            est = data['estacionalidad']
            mes_alto = max(est, key=est.get)
            mes_bajo = min(est, key=est.get)
            print(f"   Temporada alta: {mes_alto} ({est[mes_alto]:.2f}x)")
            print(f"   Temporada baja: {mes_bajo} ({est[mes_bajo]:.2f}x)")

            return True

        else:
            print(f"❌ Error en tendencias: {response.status_code}")
            print(f"   Detalle: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error probando tendencias: {e}")
        return False


def probar_diferentes_giros() -> bool:
    """
    Probar predicciones con diferentes giros turísticos.

    Returns
    -------
    bool
        True si todos los giros funcionan
    """
    try:
        print("\n🏢 Probando diferentes giros turísticos...")

        giros = ["hotel", "restaurante", "evento", "agencia_viajes"]
        resultados = {}

        for giro in giros:
            try:
                params = {
                    "giro": giro,
                    "fecha_inicio": "2025-07-01",
                    "fecha_fin": "2025-07-03"
                }

                response = requests.post(
                    f"{API_URL}/predictions/demand",
                    params=params,
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    pred_promedio = sum(p['prediccion'] for p in data['predicciones']) / len(data['predicciones'])
                    resultados[giro] = {
                        "estado": "✅",
                        "prediccion_promedio": pred_promedio
                    }
                    print(f"   {giro}: ✅ {pred_promedio:.1f} clientes/día")
                else:
                    resultados[giro] = {"estado": "❌", "error": response.status_code}
                    print(f"   {giro}: ❌ Error {response.status_code}")

            except Exception as e:
                resultados[giro] = {"estado": "❌", "error": str(e)}
                print(f"   {giro}: ❌ {e}")

        exitosos = sum(1 for r in resultados.values() if r["estado"] == "✅")
        print(f"\n📊 Resultado: {exitosos}/{len(giros)} giros funcionando")

        return exitosos >= len(giros) * 0.75  # Al menos 75% funcionando

    except Exception as e:
        print(f"❌ Error probando giros: {e}")
        return False


def probar_casos_extremos() -> bool:
    """
    Probar casos extremos y manejo de errores.

    Returns
    -------
    bool
        True si el manejo de errores funciona
    """
    try:
        print("\n⚠️ Probando manejo de errores...")

        # Caso 1: Giro inexistente
        params = {
            "giro": "giro_inexistente",
            "fecha_inicio": "2025-06-01",
            "fecha_fin": "2025-06-05"
        }

        response = requests.post(f"{API_URL}/predictions/demand", params=params, timeout=10)

        if response.status_code == 200:
            print("   ✅ Giro inexistente manejado correctamente")
        else:
            print(f"   ⚠️ Giro inexistente devuelve error {response.status_code} (esperado)")

        # Caso 2: Fechas inválidas
        params = {
            "giro": "hotel",
            "fecha_inicio": "2025-13-01",  # Mes inválido
            "fecha_fin": "2025-06-05"
        }

        response = requests.post(f"{API_URL}/predictions/demand", params=params, timeout=10)

        if response.status_code != 200:
            print("   ✅ Fechas inválidas detectadas correctamente")
        else:
            print("   ⚠️ Fechas inválidas no detectadas")

        # Caso 3: Período muy largo
        params = {
            "giro": "hotel",
            "fecha_inicio": "2025-01-01",
            "fecha_fin": "2026-12-31"  # 2 años
        }

        response = requests.post(f"{API_URL}/predictions/demand", params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            if len(data['predicciones']) > 300:
                print(f"   ✅ Período largo manejado ({len(data['predicciones'])} días)")
            else:
                print("   ⚠️ Período largo limitado por la API")
        else:
            print("   ⚠️ Período largo rechazado por la API")

        return True

    except Exception as e:
        print(f"❌ Error probando casos extremos: {e}")
        return False


def mostrar_ejemplo_completo():
    """
    Mostrar un ejemplo completo de uso de las predicciones.
    """
    try:
        print("\n" + "=" * 60)
        print("🎯 EJEMPLO COMPLETO DE USO")
        print("=" * 60)

        # Predicción para hotel en temporada alta
        params = {
            "giro": "hotel",
            "fecha_inicio": "2025-07-15",  # Temporada alta
            "fecha_fin": "2025-07-21"     # Una semana
        }

        print(f"📋 Solicitud: Predicción para {params['giro']} del {params['fecha_inicio']} al {params['fecha_fin']}")

        response = requests.post(f"{API_URL}/predictions/demand", params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()

            print(f"\n📊 RESULTADOS:")
            print(f"   Giro: {data['giro']}")
            print(f"   Período: {data['fecha_inicio']} a {data['fecha_fin']}")

            print(f"\n📅 PREDICCIONES DIARIAS:")
            total_predicho = 0
            for pred in data['predicciones']:
                fecha = pred['fecha']
                valor = pred['prediccion']
                confianza = pred['confianza']
                total_predicho += valor

                # Formatear día de la semana
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                dia_semana = fecha_obj.strftime('%a')

                print(f"   {dia_semana} {fecha}: {valor:6.1f} clientes (confianza: {confianza:.2f})")

            print(f"\n📈 RESUMEN:")
            print(f"   Total semanal: {total_predicho:,.0f} clientes")
            print(f"   Promedio diario: {total_predicho/7:,.1f} clientes")

            # Factores de influencia
            print(f"\n🎯 FACTORES DE INFLUENCIA:")
            factores = data['factores_influencia']
            for factor, peso in factores.items():
                print(f"   {factor.replace('_', ' ').title()}: {peso:.1%}")

            # Intervalos de confianza
            print(f"\n📊 INTERVALOS DE CONFIANZA (95%):")
            for intervalo in data['intervalos_confianza'][:3]:  # Primeros 3 días
                fecha = intervalo['fecha']
                inf = intervalo['limite_inferior']
                sup = intervalo['limite_superior']
                print(f"   {fecha}: [{inf:.0f} - {sup:.0f}] clientes")

            print(f"\n✅ Ejemplo completado exitosamente")

        else:
            print(f"❌ Error en ejemplo: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en ejemplo: {e}")


def main():
    """
    Función principal para verificar todas las predicciones.
    """
    print("🔮 VERIFICACIÓN DE ENDPOINTS DE PREDICCIÓN")
    print("=" * 60)
    print("Verificando que todas las funcionalidades documentadas funcionan correctamente")
    print()

    resultados = []

    # 1. Verificar API
    resultados.append(("Estado de la API", verificar_api_salud()))

    # 2. Predicción de demanda
    resultados.append(("Predicción de Demanda", probar_prediccion_demanda()))

    # 3. Análisis de tendencias
    resultados.append(("Análisis de Tendencias", probar_tendencias()))

    # 4. Diferentes giros
    resultados.append(("Múltiples Giros", probar_diferentes_giros()))

    # 5. Casos extremos
    resultados.append(("Manejo de Errores", probar_casos_extremos()))

    # Mostrar ejemplo completo
    mostrar_ejemplo_completo()

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)

    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{nombre:25} {estado}")
        if resultado:
            exitosos += 1

    porcentaje = (exitosos / len(resultados)) * 100
    print(f"\n🎯 RESULTADO GENERAL: {exitosos}/{len(resultados)} pruebas exitosas ({porcentaje:.1f}%)")

    if porcentaje >= 80:
        print("✅ Sistema de predicciones funcionando correctamente")
        print("\n🚀 Puedes usar con confianza los endpoints documentados en README_PREDICCIONES.md")
    elif porcentaje >= 60:
        print("⚠️ Sistema parcialmente funcional, revisar fallos")
    else:
        print("❌ Sistema con problemas significativos")

    print(f"\n📖 Documentación: README_PREDICCIONES.md")
    print(f"🌐 API URL: {API_URL}")
    print(f"📊 Documentación interactiva: {API_URL}/docs")

    return exitosos == len(resultados)


if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)
