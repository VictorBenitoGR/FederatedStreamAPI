# ./scripts/test_endpoints_render.py

import requests
import json
import sys
from datetime import datetime

# URL base de tu API en Render
API_BASE = "https://federatedstreamapi.onrender.com"


def test_endpoint(endpoint, descripcion):
    """
    Probar un endpoint específico.

    Parameters
    ----------
    endpoint : str
        Endpoint a probar
    descripcion : str
        Descripción del endpoint
    """
    print(f"\n📡 Probando: {descripcion}")
    print(f"🔗 URL: {API_BASE}{endpoint}")

    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=30)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito - Código: {response.status_code}")

            # Mostrar información básica del response
            if isinstance(data, dict):
                if 'metadata' in data:
                    print(f"📊 Última actualización: {data['metadata'].get('ultima_actualizacion', 'N/A')}")

                # Mostrar algunas métricas clave según el endpoint
                if 'cluster_stats' in data:
                    print(f"📈 Total giros: {data['cluster_stats']['total_giros']}")
                    print(f"📈 Total registros: {data['cluster_stats']['total_registros']:,}")

                if 'economia' in data:
                    ingresos = data['economia']['ingresos_totales']
                    print(f"💰 Ingresos totales: ${ingresos:,.0f}")

                if 'tendencias_mensuales' in data:
                    print(f"📅 Meses analizados: {len(data['tendencias_mensuales'])}")

                if 'estadisticas_por_giro' in data:
                    print(f"🏷️ Giros analizados: {len(data['estadisticas_por_giro'])}")

                if 'perfiles_viajeros' in data:
                    print(f"👥 Perfiles de viajeros: {len(data['perfiles_viajeros'])}")

                if 'resumen_eventos' in data:
                    eventos = data['resumen_eventos']['total_eventos']
                    print(f"🎪 Total eventos: {eventos:,}")

            print(f"📦 Tamaño respuesta: {len(response.content)} bytes")

        else:
            print(f"❌ Error - Código: {response.status_code}")
            print(f"📝 Mensaje: {response.text[:200]}...")

    except requests.exceptions.Timeout:
        print(f"⏰ Timeout - El endpoint tardó más de 30 segundos")
    except requests.exceptions.ConnectionError:
        print(f"🔌 Error de conexión - No se pudo conectar al servidor")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de request: {str(e)}")
    except json.JSONDecodeError:
        print(f"❌ Error decodificando JSON")
    except Exception as e:
        print(f"💥 Error inesperado: {str(e)}")


def main():
    """
    Probar todos los endpoints públicos de la API.
    """
    print("🧪 PROBANDO ENDPOINTS DE LA API EN RENDER")
    print("=" * 60)
    print(f"🌐 Base URL: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()

    # Lista de endpoints a probar
    endpoints = [
        ("/", "Endpoint raíz"),
        ("/health", "Health check"),
        ("/public/cluster/overview", "Resumen del clúster"),
        ("/public/cluster/tendencias-estacionales", "Tendencias estacionales"),
        ("/public/giros/estadisticas", "Estadísticas por giro"),
        ("/public/eventos/resumen", "Resumen de eventos"),
        ("/public/viajeros/perfiles", "Perfiles de viajeros"),
        ("/public/export/all", "Exportar todos los datos")
    ]

    resultados = {"exitosos": 0, "fallidos": 0}

    for endpoint, descripcion in endpoints:
        try:
            test_endpoint(endpoint, descripcion)
            resultados["exitosos"] += 1
        except Exception as e:
            print(f"💥 Error probando {endpoint}: {e}")
            resultados["fallidos"] += 1

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Endpoints exitosos: {resultados['exitosos']}")
    print(f"❌ Endpoints fallidos: {resultados['fallidos']}")
    print(f"📈 Tasa de éxito: {(resultados['exitosos'] / len(endpoints) * 100):.1f}%")

    if resultados["exitosos"] == len(endpoints):
        print("\n🎉 ¡Todos los endpoints funcionan correctamente!")
        print("🚀 Tu API está lista para usar en aplicaciones Next.js")
    else:
        print(f"\n⚠️ Algunos endpoints tienen problemas")
        print("🔧 Revisa los logs del servidor en Render")

    print(f"\n📋 PARA USAR EN NEXT.JS:")
    print(f"   NEXT_PUBLIC_API_URL={API_BASE}")
    print(f"   NEXT_PUBLIC_USE_STATIC_DATA=false")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n⏹️ Pruebas canceladas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
