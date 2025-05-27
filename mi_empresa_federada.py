#!/usr/bin/env python3
# Script de inicio rápido para ejemplo

from src.cliente.cliente_federado import ClienteFederado


def main():
    """Ejecutar flujo completo para tu empresa."""

    # Configurar cliente federado
    cliente = ClienteFederado(
        empresa_id="1936f244bbdb0f32",
        giro="agencia_viajes",
        api_url="https://federatedstreamapi.onrender.com"
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
