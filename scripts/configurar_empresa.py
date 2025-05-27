# ./scripts/configurar_empresa.py

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List


def configurar_empresa():
    """
    Script interactivo para configurar una empresa en el sistema federado.

    Guía a la empresa a través del proceso de configuración inicial,
    creando los archivos necesarios para participar en el clúster.
    """
    print("🏢 CONFIGURACIÓN DE EMPRESA - CLÚSTER DE TURISMO NL")
    print("=" * 60)
    print("Este asistente te ayudará a configurar tu empresa para participar")
    print("en el sistema de analítica federada del clúster turístico.")
    print()

    # Recopilar información de la empresa
    print("📋 INFORMACIÓN DE TU EMPRESA")
    print("-" * 30)

    nombre_empresa = input("Nombre de tu empresa: ").strip()
    if not nombre_empresa:
        print("❌ El nombre de la empresa es obligatorio")
        return False

    # Seleccionar giro turístico
    giros_disponibles = [
        "hotel", "restaurante", "agencia_viajes", "transporte",
        "evento", "spa_wellness", "tour_operador", "renta_autos",
        "entretenimiento", "comercio_turistico"
    ]

    print(f"\n🏷️ GIRO TURÍSTICO")
    print("Selecciona el giro principal de tu empresa:")
    for i, giro in enumerate(giros_disponibles, 1):
        print(f"  {i}. {giro.replace('_', ' ').title()}")

    while True:
        try:
            seleccion = int(input("\nSelecciona el número de tu giro: "))
            if 1 <= seleccion <= len(giros_disponibles):
                giro_empresa = giros_disponibles[seleccion - 1]
                break
            else:
                print("❌ Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("❌ Por favor ingresa un número válido.")

    # Configuración de datos
    print(f"\n📊 CONFIGURACIÓN DE DATOS")
    print("-" * 30)

    ruta_datos = input("Ruta a tus archivos de datos (opcional): ").strip()
    if not ruta_datos:
        ruta_datos = "data/mi_empresa/"

    # Configuración de API
    print(f"\n🌐 CONFIGURACIÓN DE CONEXIÓN")
    print("-" * 30)

    api_url = input("URL de la API del clúster (presiona Enter para usar la predeterminada): ").strip()
    if not api_url:
        api_url = "https://api.cluster-turismo-nl.com"

    # Generar configuración
    configuracion = generar_configuracion_empresa(
        nombre_empresa, giro_empresa, ruta_datos, api_url
    )

    # Guardar configuración
    if guardar_configuracion(configuracion):
        mostrar_resumen_configuracion(configuracion)
        mostrar_proximos_pasos()
        return True
    else:
        print("❌ Error guardando la configuración")
        return False


def generar_configuracion_empresa(nombre: str, giro: str, ruta_datos: str, api_url: str) -> Dict:
    """
    Generar configuración completa de la empresa.

    Parameters
    ----------
    nombre : str
        Nombre de la empresa
    giro : str
        Giro turístico
    ruta_datos : str
        Ruta a los datos de la empresa
    api_url : str
        URL de la API del clúster

    Returns
    -------
    Dict
        Configuración completa de la empresa
    """
    # Generar ID único y anónimo para la empresa
    timestamp = datetime.now().isoformat()
    empresa_id = hashlib.sha256(f"{nombre}_{timestamp}".encode()).hexdigest()[:16]

    configuracion = {
        "empresa": {
            "id": empresa_id,
            "nombre": nombre,
            "giro": giro,
            "fecha_configuracion": timestamp
        },
        "datos": {
            "ruta_local": ruta_datos,
            "formatos_soportados": ["csv", "json", "xlsx"],
            "campos_requeridos": obtener_campos_requeridos(giro)
        },
        "conexion": {
            "api_url": api_url,
            "timeout": 30,
            "reintentos": 3
        },
        "privacidad": {
            "anonimizacion_activa": True,
            "ruido_local": True,
            "validacion_automatica": True,
            "min_muestras_entrenamiento": 100
        },
        "modelos": {
            "tipos_habilitados": ["prediccion_demanda", "clasificacion_viajero"],
            "frecuencia_entrenamiento": "semanal",
            "auto_envio": False
        }
    }

    return configuracion


def obtener_campos_requeridos(giro: str) -> List[str]:
    """
    Obtener campos de datos requeridos según el giro.

    Parameters
    ----------
    giro : str
        Giro turístico de la empresa

    Returns
    -------
    List[str]
        Lista de campos requeridos
    """
    campos_base = ["fecha", "ingresos", "numero_clientes"]

    campos_especificos = {
        "hotel": ["ocupacion", "tarifa_promedio", "noches_estancia"],
        "restaurante": ["numero_mesas", "ticket_promedio", "tipo_comida"],
        "agencia_viajes": ["destinos", "tipo_paquete", "duracion_viaje"],
        "transporte": ["tipo_vehiculo", "distancia", "pasajeros"],
        "evento": ["tipo_evento", "capacidad", "asistentes"],
        "spa_wellness": ["tipo_servicio", "duracion_servicio", "satisfaccion"]
    }

    return campos_base + campos_especificos.get(giro, [])


def guardar_configuracion(configuracion: Dict) -> bool:
    """
    Guardar configuración en archivo local.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa

    Returns
    -------
    bool
        True si se guardó exitosamente
    """
    try:
        # Crear directorio de configuración
        os.makedirs("config", exist_ok=True)

        # Guardar configuración principal
        with open("config/empresa.json", "w", encoding='utf-8') as f:
            json.dump(configuracion, f, indent=2, ensure_ascii=False)

        # Crear archivo de ejemplo de datos
        crear_archivo_ejemplo_datos(configuracion)

        # Crear script de inicio rápido
        crear_script_inicio_rapido(configuracion)

        return True

    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False


def crear_archivo_ejemplo_datos(configuracion: Dict):
    """
    Crear archivo de ejemplo con el formato de datos esperado.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    """
    giro = configuracion["empresa"]["giro"]
    campos = configuracion["datos"]["campos_requeridos"]

    # Crear directorio de datos
    ruta_datos = configuracion["datos"]["ruta_local"]
    os.makedirs(ruta_datos, exist_ok=True)

    # Crear archivo CSV de ejemplo
    ejemplo_csv = f"{ruta_datos}/ejemplo_datos.csv"

    with open(ejemplo_csv, "w", encoding='utf-8') as f:
        # Escribir encabezados
        f.write(",".join(campos) + "\n")

        # Escribir filas de ejemplo
        if giro == "hotel":
            f.write("2025-01-01,15000,45,85,2500,2.3\n")
            f.write("2025-01-02,18000,52,92,2800,2.1\n")
        elif giro == "restaurante":
            f.write("2025-01-01,8500,120,25,450,italiana\n")
            f.write("2025-01-02,9200,135,25,480,italiana\n")
        else:
            # Ejemplo genérico
            f.write("2025-01-01,10000,50\n")
            f.write("2025-01-02,12000,60\n")


def crear_script_inicio_rapido(configuracion: Dict):
    """
    Crear script personalizado de inicio rápido.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    """
    empresa_id = configuracion["empresa"]["id"]
    giro = configuracion["empresa"]["giro"]

    script_content = f'''#!/usr/bin/env python3
# Script de inicio rápido para {configuracion["empresa"]["nombre"]}

from src.cliente.cliente_federado import ClienteFederado

def main():
    """Ejecutar flujo completo para tu empresa."""
    
    # Configurar cliente federado
    cliente = ClienteFederado(
        empresa_id="{empresa_id}",
        giro="{giro}",
        api_url="{configuracion["conexion"]["api_url"]}"
    )
    
    print("🚀 Iniciando proceso federado para tu empresa...")
    
    # Ejecutar flujo completo
    exito = cliente.ejecutar_flujo_completo()
    
    if exito:
        print("✅ ¡Proceso completado exitosamente!")
        print("📊 Revisa los resultados en data/resultados/")
    else:
        print("❌ Hubo un error en el proceso")

if __name__ == "__main__":
    main()
'''

    with open("mi_empresa_federada.py", "w", encoding='utf-8') as f:
        f.write(script_content)

    # Hacer ejecutable en sistemas Unix
    try:
        os.chmod("mi_empresa_federada.py", 0o755)
    except:
        pass


def mostrar_resumen_configuracion(configuracion: Dict):
    """
    Mostrar resumen de la configuración creada.

    Parameters
    ----------
    configuracion : Dict
        Configuración de la empresa
    """
    print(f"\n✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print(f"🏢 Empresa: {configuracion['empresa']['nombre']}")
    print(f"🏷️ Giro: {configuracion['empresa']['giro']}")
    print(f"🆔 ID Anónimo: {configuracion['empresa']['id']}")
    print(f"📁 Datos: {configuracion['datos']['ruta_local']}")
    print(f"🌐 API: {configuracion['conexion']['api_url']}")
    print(f"🔒 Privacidad: Activada")

    print(f"\n📁 ARCHIVOS CREADOS:")
    print(f"  ✅ config/empresa.json - Configuración principal")
    print(f"  ✅ {configuracion['datos']['ruta_local']}/ejemplo_datos.csv - Formato de datos")
    print(f"  ✅ mi_empresa_federada.py - Script de inicio rápido")


def mostrar_proximos_pasos():
    """
    Mostrar los próximos pasos para la empresa.
    """
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"  1. Coloca tus datos en el formato del archivo ejemplo")
    print(f"  2. Ejecuta: python scripts/entrenar_y_enviar.py")
    print(f"  3. Consulta resultados: python scripts/consultar_cluster.py")
    print(f"  4. O usa el script rápido: python mi_empresa_federada.py")

    print(f"\n📚 DOCUMENTACIÓN:")
    print(f"  📖 Guía completa: docs.cluster-turismo-nl.com")
    print(f"  📞 Soporte: soporte@cluster-turismo-nl.com")
    print(f"  🔒 Privacidad: Tus datos NUNCA salen de tu empresa")


if __name__ == "__main__":
    try:
        exito = configurar_empresa()
        if exito:
            print(f"\n🎉 ¡Bienvenido al Clúster de Turismo de Nuevo León!")
        else:
            print(f"\n💥 La configuración no se pudo completar")
    except KeyboardInterrupt:
        print(f"\n⏹️ Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
