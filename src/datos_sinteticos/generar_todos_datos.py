# ./src/datos_sinteticos/generar_todos_datos.py

from src.datos_sinteticos.generador_perfil_viajero import GeneradorPerfilViajero
from src.datos_sinteticos.generador_publicidad import GeneradorPublicidad
from src.datos_sinteticos.generador_ventas import GeneradorVentas
from src.datos_sinteticos.generador_eventos import GeneradorEventos
from src.datos_sinteticos.generador_empresas import GeneradorEmpresas
import os
import sys
import time
from datetime import datetime

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def crear_directorios():
    """
    Crear directorios necesarios si no existen.
    """
    directorios = [
        'data',
        'data/datos_sinteticos',
        'data/resultados'
    ]

    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            print(f"📁 Creado directorio: {directorio}")


def generar_todos_los_datos():
    """
    Ejecutar todos los generadores de datos sintéticos.

    Este script genera datos sintéticos para el prototipo del Clúster de Turismo
    de Nuevo León, incluyendo empresas, eventos, ventas, publicidad y perfiles
    de viajeros con tendencias estacionales realistas.
    """
    print("🚀 Iniciando generación de datos sintéticos para el Clúster de Turismo de Nuevo León")
    print("=" * 80)

    inicio_total = time.time()

    # Crear directorios necesarios
    crear_directorios()

    try:
        # 1. Generar empresas dummy (base para todo lo demás)
        print("\n1️⃣ GENERANDO EMPRESAS DUMMY")
        print("-" * 40)
        inicio = time.time()

        generador_empresas = GeneradorEmpresas(num_empresas=100, seed=42)
        empresas_df = generador_empresas.guardar_empresas()

        tiempo_empresas = time.time() - inicio
        print(f"⏱️ Tiempo: {tiempo_empresas:.2f} segundos")

        # 2. Generar eventos
        print("\n2️⃣ GENERANDO DATOS DE EVENTOS")
        print("-" * 40)
        inicio = time.time()

        generador_eventos = GeneradorEventos(empresas_df, seed=42)
        eventos_df = generador_eventos.guardar_eventos()

        tiempo_eventos = time.time() - inicio
        print(f"⏱️ Tiempo: {tiempo_eventos:.2f} segundos")

        # 3. Generar ventas por giro
        print("\n3️⃣ GENERANDO DATOS DE VENTAS POR GIRO")
        print("-" * 40)
        inicio = time.time()

        generador_ventas = GeneradorVentas(empresas_df, seed=42)
        ventas_df = generador_ventas.guardar_ventas()

        tiempo_ventas = time.time() - inicio
        print(f"⏱️ Tiempo: {tiempo_ventas:.2f} segundos")

        # 4. Generar campañas publicitarias
        print("\n4️⃣ GENERANDO DATOS DE PUBLICIDAD")
        print("-" * 40)
        inicio = time.time()

        generador_publicidad = GeneradorPublicidad(empresas_df, seed=42)
        publicidad_df = generador_publicidad.guardar_campanas()

        tiempo_publicidad = time.time() - inicio
        print(f"⏱️ Tiempo: {tiempo_publicidad:.2f} segundos")

        # 5. Generar perfiles de viajeros
        print("\n5️⃣ GENERANDO PERFILES DE VIAJEROS")
        print("-" * 40)
        inicio = time.time()

        generador_perfiles = GeneradorPerfilViajero(empresas_df, seed=42)
        perfiles_df = generador_perfiles.guardar_perfiles(num_registros=5000)

        tiempo_perfiles = time.time() - inicio
        print(f"⏱️ Tiempo: {tiempo_perfiles:.2f} segundos")

        # Resumen final
        tiempo_total = time.time() - inicio_total

        print("\n" + "=" * 80)
        print("✅ GENERACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)

        print(f"\n📊 RESUMEN DE DATOS GENERADOS:")
        print(f"  🏢 Empresas: {len(empresas_df)} registros")
        print(f"  🎪 Eventos: {len(eventos_df)} registros")
        print(f"  💰 Ventas: {len(ventas_df)} registros")
        print(f"  📢 Campañas publicitarias: {len(publicidad_df)} registros")
        print(f"  👥 Perfiles de viajeros: {len(perfiles_df)} registros")

        total_registros = len(empresas_df) + len(eventos_df) + len(ventas_df) + len(publicidad_df) + len(perfiles_df)
        print(f"\n📈 TOTAL DE REGISTROS: {total_registros:,}")

        print(f"\n⏱️ TIEMPOS DE EJECUCIÓN:")
        print(f"  Empresas: {tiempo_empresas:.2f}s")
        print(f"  Eventos: {tiempo_eventos:.2f}s")
        print(f"  Ventas: {tiempo_ventas:.2f}s")
        print(f"  Publicidad: {tiempo_publicidad:.2f}s")
        print(f"  Perfiles: {tiempo_perfiles:.2f}s")
        print(f"  TOTAL: {tiempo_total:.2f}s")

        print(f"\n📁 ARCHIVOS GENERADOS:")
        archivos = [
            'data/datos_sinteticos/empresas_dummy.csv',
            'data/datos_sinteticos/eventos_dummy.csv',
            'data/datos_sinteticos/ventas_dummy.csv',
            'data/datos_sinteticos/publicidad_dummy.csv',
            'data/datos_sinteticos/perfil_viajero_dummy.csv'
        ]

        for archivo in archivos:
            if os.path.exists(archivo):
                tamaño = os.path.getsize(archivo) / 1024  # KB
                print(f"  ✅ {archivo} ({tamaño:.1f} KB)")
            else:
                print(f"  ❌ {archivo} (no encontrado)")

        print(f"\n🎯 CARACTERÍSTICAS DE LOS DATOS:")
        print(f"  📅 Período: 2020-01-01 a 2025-12-31")
        print(f"  🌍 Ubicación: Nuevo León, México")
        print(f"  🔒 Anonimización: IDs completamente irreversibles")
        print(f"  📈 Tendencias: Estacionalidad, crecimiento anual, patrones de fin de semana")
        print(f"  🎲 Reproducibilidad: Seed fijo (42) para resultados consistentes")

        print(f"\n🔐 PRIVACIDAD Y ANONIMIZACIÓN:")
        print(f"  ✅ IDs de empresa hasheados con SHA-256")
        print(f"  ✅ Sin metadatos que permitan rastreo")
        print(f"  ✅ Datos completamente sintéticos")
        print(f"  ✅ Imposible inferir empresa real")

        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"  1. Revisar los datos generados en ./data/datos_sinteticos/")
        print(f"  2. Desarrollar la API FastAPI para CRUD y métricas")
        print(f"  3. Implementar algoritmos de aprendizaje federado")
        print(f"  4. Crear endpoints para analítica agregada")
        print(f"  5. Configurar anonimización para datos en ./data/resultados/")

    except Exception as e:
        print(f"\n❌ ERROR durante la generación: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print(f"Ejecutando desde: {os.getcwd()}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    exito = generar_todos_los_datos()

    if exito:
        print(f"\n🎉 ¡Generación de datos completada exitosamente!")
        sys.exit(0)
    else:
        print(f"\n💥 Error en la generación de datos")
        sys.exit(1)
