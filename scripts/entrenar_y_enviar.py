# ./scripts/entrenar_y_enviar.py

from src.cliente.cliente_federado import ClienteFederado
import os
import json
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

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


def validar_datos_empresa(configuracion: Dict) -> bool:
    """
    Validar que los datos de la empresa estén disponibles.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa

    Returns
    -------
    bool
        True si los datos están disponibles
    """
    ruta_datos = configuracion["datos"]["ruta_local"]

    if not os.path.exists(ruta_datos):
        print(f"❌ Directorio de datos no encontrado: {ruta_datos}")
        print("   Crea el directorio y coloca tus archivos de datos")
        return False

    # Buscar archivos de datos
    archivos_datos = []
    for archivo in os.listdir(ruta_datos):
        if archivo.endswith(('.csv', '.json', '.xlsx')):
            archivos_datos.append(archivo)

    if not archivos_datos:
        print(f"❌ No se encontraron archivos de datos en: {ruta_datos}")
        print("   Formatos soportados: CSV, JSON, XLSX")
        return False

    print(f"✅ Archivos de datos encontrados: {len(archivos_datos)}")
    for archivo in archivos_datos:
        print(f"   📄 {archivo}")

    return True


def entrenar_modelos_empresa(configuracion: Dict) -> bool:
    """
    Entrenar modelos de ML con los datos de la empresa.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa

    Returns
    -------
    bool
        True si el entrenamiento fue exitoso
    """
    print("🤖 ENTRENAMIENTO DE MODELOS")
    print("=" * 60)
    print("Entrenando modelos de machine learning con tus datos locales...")
    print("🔒 Tus datos NUNCA salen de tu empresa")
    print()

    # Crear cliente federado
    empresa_info = configuracion["empresa"]
    conexion_info = configuracion["conexion"]

    cliente = ClienteFederado(
        empresa_id=empresa_info["id"],
        giro=empresa_info["giro"],
        api_url=conexion_info["api_url"]
    )

    # Configurar ruta de datos de la empresa
    cliente.ruta_datos = configuracion["datos"]["ruta_local"]

    try:
        # Cargar datos locales
        print("📊 Cargando datos locales...")
        if not cliente.cargar_datos_locales():
            print("❌ Error cargando datos locales")
            print("   Verifica que tus datos estén en el formato correcto")
            return False

        # Entrenar modelos según configuración
        modelos_entrenados = []
        tipos_habilitados = configuracion["modelos"]["tipos_habilitados"]

        if "prediccion_demanda" in tipos_habilitados:
            print("\n🎯 Entrenando modelo de predicción de demanda...")
            try:
                modelo = cliente.entrenar_modelo_prediccion_demanda()
                modelos_entrenados.append(("prediccion_demanda", modelo))
                print("✅ Modelo de predicción entrenado exitosamente")
            except Exception as e:
                print(f"⚠️ Error entrenando predicción: {e}")

        if "clasificacion_viajero" in tipos_habilitados:
            print("\n👥 Entrenando modelo de clasificación de viajeros...")
            try:
                modelo = cliente.entrenar_modelo_clasificacion_viajero()
                modelos_entrenados.append(("clasificacion_viajero", modelo))
                print("✅ Modelo de clasificación entrenado exitosamente")
            except Exception as e:
                print(f"⚠️ Error entrenando clasificación: {e}")

        # Generar métricas agregadas
        print("\n📈 Generando métricas agregadas...")
        try:
            metricas = cliente.generar_metricas_agregadas()
            print("✅ Métricas agregadas generadas exitosamente")
        except Exception as e:
            print(f"⚠️ Error generando métricas: {e}")
            metricas = None

        # Guardar resultados localmente
        guardar_resultados_entrenamiento(configuracion, modelos_entrenados, metricas)

        # Enviar a la API si está configurado
        if configuracion["modelos"].get("auto_envio", False):
            return enviar_modelos_a_cluster(cliente, modelos_entrenados, metricas)
        else:
            print("\n📤 Para enviar los modelos al clúster, ejecuta:")
            print("   python scripts/enviar_al_cluster.py")
            return True

    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        return False


def guardar_resultados_entrenamiento(configuracion: Dict, modelos: list, metricas: Optional[Dict]):
    """
    Guardar resultados del entrenamiento localmente.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    modelos : list
        Lista de modelos entrenados
    metricas : Optional[Dict]
        Métricas agregadas
    """
    # Crear directorio de resultados
    directorio_resultados = "resultados_entrenamiento"
    os.makedirs(directorio_resultados, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Guardar modelos
    for tipo_modelo, modelo in modelos:
        archivo_modelo = f"{directorio_resultados}/{tipo_modelo}_{timestamp}.json"
        with open(archivo_modelo, "w") as f:
            json.dump(modelo, f, indent=2)
        print(f"💾 Modelo guardado: {archivo_modelo}")

    # Guardar métricas
    if metricas:
        archivo_metricas = f"{directorio_resultados}/metricas_{timestamp}.json"
        with open(archivo_metricas, "w") as f:
            json.dump(metricas, f, indent=2)
        print(f"💾 Métricas guardadas: {archivo_metricas}")

    # Crear resumen
    resumen = {
        "empresa": configuracion["empresa"]["nombre"],
        "giro": configuracion["empresa"]["giro"],
        "timestamp_entrenamiento": datetime.now().isoformat(),
        "modelos_entrenados": [tipo for tipo, _ in modelos],
        "metricas_generadas": metricas is not None,
        "archivos_generados": len(modelos) + (1 if metricas else 0)
    }

    archivo_resumen = f"{directorio_resultados}/resumen_{timestamp}.json"
    with open(archivo_resumen, "w") as f:
        json.dump(resumen, f, indent=2)

    print(f"📋 Resumen guardado: {archivo_resumen}")


def enviar_modelos_a_cluster(cliente: ClienteFederado, modelos: list, metricas: Optional[Dict]) -> bool:
    """
    Enviar modelos entrenados al clúster federado.

    Parameters
    ----------
    cliente : ClienteFederado
        Cliente federado configurado
    modelos : list
        Lista de modelos entrenados
    metricas : Optional[Dict]
        Métricas agregadas

    Returns
    -------
    bool
        True si el envío fue exitoso
    """
    print("\n📤 ENVÍO AL CLÚSTER FEDERADO")
    print("=" * 60)
    print("Enviando modelos anonimizados al clúster...")
    print("🔒 Solo se envían parámetros agregados, nunca datos crudos")
    print()

    envios_exitosos = 0

    # Enviar modelos
    for tipo_modelo, modelo in modelos:
        print(f"📤 Enviando modelo: {tipo_modelo}")
        if cliente.enviar_modelo_a_api(tipo_modelo):
            envios_exitosos += 1
        else:
            print(f"❌ Error enviando {tipo_modelo}")

    # Enviar métricas
    if metricas:
        print("📤 Enviando métricas agregadas...")
        if cliente.enviar_metricas_a_api(metricas):
            envios_exitosos += 1
        else:
            print("❌ Error enviando métricas")

    total_envios = len(modelos) + (1 if metricas else 0)

    if envios_exitosos == total_envios:
        print(f"\n✅ Todos los envíos completados exitosamente ({envios_exitosos}/{total_envios})")
        print("🎉 ¡Tu empresa ya está contribuyendo al clúster federado!")
        return True
    else:
        print(f"\n⚠️ Envíos parcialmente exitosos ({envios_exitosos}/{total_envios})")
        print("   Algunos modelos no se pudieron enviar")
        return False


def mostrar_resumen_final(configuracion: Dict, exito_entrenamiento: bool, exito_envio: bool):
    """
    Mostrar resumen final del proceso.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    exito_entrenamiento : bool
        Si el entrenamiento fue exitoso
    exito_envio : bool
        Si el envío fue exitoso
    """
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL")
    print("=" * 60)

    print(f"🏢 Empresa: {configuracion['empresa']['nombre']}")
    print(f"🏷️ Giro: {configuracion['empresa']['giro']}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n📊 RESULTADOS:")
    print(f"  Entrenamiento: {'✅ Exitoso' if exito_entrenamiento else '❌ Falló'}")

    if configuracion["modelos"].get("auto_envio", False):
        print(f"  Envío al clúster: {'✅ Exitoso' if exito_envio else '❌ Falló'}")
    else:
        print(f"  Envío al clúster: ⏸️ Pendiente (auto_envio deshabilitado)")

    print(f"\n🎯 PRÓXIMOS PASOS:")
    if exito_entrenamiento and not configuracion["modelos"].get("auto_envio", False):
        print(f"  1. Revisar resultados en: resultados_entrenamiento/")
        print(f"  2. Enviar al clúster: python scripts/enviar_al_cluster.py")
        print(f"  3. Consultar resultados: python scripts/consultar_cluster.py")
    elif exito_entrenamiento and exito_envio:
        print(f"  1. Consultar resultados del clúster: python scripts/consultar_cluster.py")
        print(f"  2. Generar predicciones: python scripts/predecir_demanda.py")
        print(f"  3. Hacer benchmarking: python scripts/benchmark_anonimo.py")
    else:
        print(f"  1. Revisar errores en el log")
        print(f"  2. Verificar formato de datos")
        print(f"  3. Contactar soporte: soporte@cluster-turismo-nl.com")


def main():
    """
    Función principal del script de entrenamiento y envío.
    """
    print("🤖 ENTRENAMIENTO Y ENVÍO - CLÚSTER DE TURISMO NL")
    print("=" * 60)
    print("Este script entrenará modelos con tus datos y los enviará al clúster")
    print("🔒 Garantizando privacidad completa en todo el proceso")
    print()

    # Cargar configuración
    configuracion = cargar_configuracion_empresa()
    if not configuracion:
        return False

    print(f"✅ Configuración cargada para: {configuracion['empresa']['nombre']}")

    # Validar datos
    if not validar_datos_empresa(configuracion):
        return False

    # Entrenar modelos
    exito_entrenamiento = entrenar_modelos_empresa(configuracion)

    # Enviar si está configurado
    exito_envio = False
    if exito_entrenamiento and configuracion["modelos"].get("auto_envio", False):
        # El envío ya se hizo en entrenar_modelos_empresa
        exito_envio = True

    # Mostrar resumen
    mostrar_resumen_final(configuracion, exito_entrenamiento, exito_envio)

    return exito_entrenamiento


if __name__ == "__main__":
    try:
        exito = main()
        if exito:
            print(f"\n🎉 ¡Proceso completado exitosamente!")
        else:
            print(f"\n💥 El proceso no se pudo completar")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
