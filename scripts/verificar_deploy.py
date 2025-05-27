# ./scripts/verificar_deploy.py

import os
import sys
import importlib.util


def verificar_estructura_proyecto():
    """
    Verificar que la estructura del proyecto sea correcta para el deploy.
    """
    print("🔍 VERIFICANDO ESTRUCTURA DEL PROYECTO")
    print("=" * 50)

    archivos_requeridos = [
        "requirements.txt",
        "render.yaml",
        "start.py",
        "src/api/main.py",
        "src/api/models.py",
        "src/api/federado.py",
        "src/api/storage.py",
        "src/api/public_data.py"
    ]

    directorios_requeridos = [
        "src",
        "src/api",
        "data",
        "data/datos_sinteticos"
    ]

    # Verificar archivos
    print("\n📄 Verificando archivos requeridos:")
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)

    # Verificar directorios
    print("\n📁 Verificando directorios requeridos:")
    directorios_faltantes = []
    for directorio in directorios_requeridos:
        if os.path.exists(directorio):
            print(f"✅ {directorio}/")
        else:
            print(f"❌ {directorio}/ - FALTANTE")
            directorios_faltantes.append(directorio)

    return len(archivos_faltantes) == 0 and len(directorios_faltantes) == 0


def verificar_importaciones():
    """
    Verificar que las importaciones funcionen correctamente.
    """
    print("\n🔗 VERIFICANDO IMPORTACIONES")
    print("=" * 50)

    try:
        # Agregar el directorio raíz al path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Intentar importar la aplicación principal
        print("📦 Importando aplicación principal...")
        from src.api.main import app
        print("✅ src.api.main:app importado correctamente")

        # Verificar que sea una aplicación FastAPI
        if hasattr(app, 'openapi'):
            print("✅ Es una aplicación FastAPI válida")
        else:
            print("❌ No es una aplicación FastAPI válida")
            return False

        # Verificar endpoints públicos
        print("📡 Verificando endpoints públicos...")
        routes = [route.path for route in app.routes]
        endpoints_publicos = [
            "/public/cluster/overview",
            "/public/cluster/tendencias-estacionales",
            "/public/giros/estadisticas",
            "/public/eventos/resumen",
            "/public/viajeros/perfiles",
            "/public/export/all"
        ]

        for endpoint in endpoints_publicos:
            if any(endpoint in route for route in routes):
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - NO ENCONTRADO")

        return True

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def verificar_dependencias():
    """
    Verificar que todas las dependencias estén instaladas.
    """
    print("\n📦 VERIFICANDO DEPENDENCIAS")
    print("=" * 50)

    dependencias_criticas = [
        "fastapi",
        "uvicorn",
        "pandas",
        "numpy",
        "requests",
        "pydantic"
    ]

    dependencias_faltantes = []

    for dep in dependencias_criticas:
        try:
            spec = importlib.util.find_spec(dep)
            if spec is not None:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep} - NO INSTALADO")
                dependencias_faltantes.append(dep)
        except Exception as e:
            print(f"❌ {dep} - ERROR: {e}")
            dependencias_faltantes.append(dep)

    return len(dependencias_faltantes) == 0


def verificar_datos_sinteticos():
    """
    Verificar que los datos sintéticos existan.
    """
    print("\n📊 VERIFICANDO DATOS SINTÉTICOS")
    print("=" * 50)

    archivos_datos = [
        "data/datos_sinteticos/ventas_dummy.csv",
        "data/datos_sinteticos/eventos_dummy.csv",
        "data/datos_sinteticos/perfil_viajero_dummy.csv",
        "data/datos_sinteticos/empresas_dummy.csv"
    ]

    datos_faltantes = []

    for archivo in archivos_datos:
        if os.path.exists(archivo):
            # Verificar que no esté vacío
            size = os.path.getsize(archivo)
            if size > 0:
                print(f"✅ {archivo} ({size:,} bytes)")
            else:
                print(f"⚠️ {archivo} - VACÍO")
                datos_faltantes.append(archivo)
        else:
            print(f"❌ {archivo} - FALTANTE")
            datos_faltantes.append(archivo)

    return len(datos_faltantes) == 0


def main():
    """
    Ejecutar todas las verificaciones.
    """
    print("🚀 VERIFICACIÓN PRE-DEPLOY PARA RENDER")
    print("=" * 60)
    print("Verificando que todo esté listo para el deploy...")
    print()

    verificaciones = [
        ("Estructura del proyecto", verificar_estructura_proyecto),
        ("Importaciones", verificar_importaciones),
        ("Dependencias", verificar_dependencias),
        ("Datos sintéticos", verificar_datos_sinteticos)
    ]

    resultados = []

    for nombre, funcion in verificaciones:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"💥 Error en {nombre}: {e}")
            resultados.append((nombre, False))

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIONES")
    print("=" * 60)

    exitosas = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado} - {nombre}")

    print(f"\n📈 Resultado: {exitosas}/{total} verificaciones exitosas")

    if exitosas == total:
        print("\n🎉 ¡TODO LISTO PARA EL DEPLOY!")
        print("🚀 Puedes proceder con el deploy en Render")
        print("\n📋 COMANDOS PARA RENDER:")
        print("   Build Command: pip install -r requirements.txt")
        print("   Start Command: python start.py")
    else:
        print(f"\n⚠️ HAY PROBLEMAS QUE RESOLVER")
        print("🔧 Corrige los errores antes de hacer deploy")

        if not verificar_datos_sinteticos():
            print("\n💡 Para generar datos sintéticos:")
            print("   python src/datos_sinteticos/generar_todos_datos.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n⏹️ Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
