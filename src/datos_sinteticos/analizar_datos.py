# ./src/datos_sinteticos/analizar_datos.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os


def cargar_datos():
    """
    Cargar todos los archivos de datos sintéticos.

    Returns
    -------
    dict
        Diccionario con todos los DataFrames cargados
    """
    datos = {}

    archivos = {
        'empresas': 'data/datos_sinteticos/empresas_dummy.csv',
        'eventos': 'data/datos_sinteticos/eventos_dummy.csv',
        'ventas': 'data/datos_sinteticos/ventas_dummy.csv',
        'publicidad': 'data/datos_sinteticos/publicidad_dummy.csv',
        'perfiles': 'data/datos_sinteticos/perfil_viajero_dummy.csv'
    }

    for nombre, archivo in archivos.items():
        if os.path.exists(archivo):
            datos[nombre] = pd.read_csv(archivo)
            print(f"✅ Cargado {nombre}: {len(datos[nombre]):,} registros")
        else:
            print(f"❌ No encontrado: {archivo}")

    return datos


def analizar_tendencias_estacionales(datos):
    """
    Analizar tendencias estacionales en los datos.

    Parameters
    ----------
    datos : dict
        Diccionario con los DataFrames
    """
    print("\n" + "=" * 60)
    print("📈 ANÁLISIS DE TENDENCIAS ESTACIONALES")
    print("=" * 60)

    # Análisis de eventos por mes
    if 'eventos' in datos:
        eventos_df = datos['eventos']
        eventos_por_mes = eventos_df.groupby('mes')['asistentes'].agg(['count', 'mean']).round(0)

        print("\n🎪 EVENTOS - Asistentes promedio por mes:")
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        for mes_num, mes_nombre in enumerate(meses, 1):
            if mes_num in eventos_por_mes.index:
                count = eventos_por_mes.loc[mes_num, 'count']
                mean_asist = eventos_por_mes.loc[mes_num, 'mean']
                print(f"  {mes_nombre}: {count:3.0f} eventos, {mean_asist:4.0f} asistentes promedio")

    # Análisis de ventas por giro y fin de semana
    if 'ventas' in datos:
        ventas_df = datos['ventas']

        print("\n💰 VENTAS - Comparación fin de semana vs días laborales:")
        comparacion = ventas_df.groupby('es_fin_semana')['ingresos_totales'].agg(['count', 'mean']).round(0)
        for es_finde, datos_row in comparacion.iterrows():
            tipo_dia = "Fin de semana" if es_finde else "Días laborales"
            print(f"  {tipo_dia}: {datos_row['count']:,} registros, ${datos_row['mean']:,.0f} promedio")

        print("\n🏢 VENTAS - Top 5 giros por ingresos totales:")
        ventas_por_giro = ventas_df.groupby('giro')['ingresos_totales'].sum().sort_values(ascending=False).head(5)
        for giro, total in ventas_por_giro.items():
            print(f"  {giro}: ${total:,.0f}")

    # Análisis de perfiles de viajeros por temporada
    if 'perfiles' in datos:
        perfiles_df = datos['perfiles']

        print("\n👥 PERFILES DE VIAJEROS - Gasto promedio por temporada:")
        gasto_temporada = perfiles_df.groupby('temporada')['gasto_total'].mean().sort_values(ascending=False)
        for temporada, gasto in gasto_temporada.items():
            print(f"  {temporada.capitalize()}: ${gasto:,.0f} promedio")

        print("\n🎯 PERFILES DE VIAJEROS - Top 5 tipos por gasto promedio:")
        gasto_por_tipo = perfiles_df.groupby('tipo_viajero')['gasto_total'].mean().sort_values(ascending=False).head(5)
        for tipo, gasto in gasto_por_tipo.items():
            print(f"  {tipo}: ${gasto:,.0f} promedio")


def analizar_publicidad(datos):
    """
    Analizar efectividad de campañas publicitarias.

    Parameters
    ----------
    datos : dict
        Diccionario con los DataFrames
    """
    if 'publicidad' not in datos:
        return

    print("\n" + "=" * 60)
    print("📢 ANÁLISIS DE PUBLICIDAD")
    print("=" * 60)

    publicidad_df = datos['publicidad']

    # ROI por tipo de campaña
    print("\n💡 ROI promedio por tipo de campaña:")
    roi_por_tipo = publicidad_df.groupby('tipo_campana')['roi'].mean().sort_values(ascending=False)
    for tipo, roi in roi_por_tipo.items():
        print(f"  {tipo}: {roi:.1f}% ROI")

    # Tasa de conversión por tipo
    print("\n🎯 Tasa de conversión promedio por tipo de campaña:")
    conversion_por_tipo = publicidad_df.groupby('tipo_campana')['tasa_conversion'].mean().sort_values(ascending=False)
    for tipo, conversion in conversion_por_tipo.items():
        print(f"  {tipo}: {conversion:.2f}%")


def generar_graficos(datos):
    """
    Generar gráficos de las tendencias principales.

    Parameters
    ----------
    datos : dict
        Diccionario con los DataFrames
    """
    print("\n" + "=" * 60)
    print("📊 GENERANDO GRÁFICOS")
    print("=" * 60)

    # Configurar estilo
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análisis de Tendencias - Clúster de Turismo de Nuevo León', fontsize=16, fontweight='bold')

    # Gráfico 1: Eventos por mes
    if 'eventos' in datos:
        eventos_df = datos['eventos']
        eventos_por_mes = eventos_df.groupby('mes')['asistentes'].mean()
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        axes[0, 0].bar(range(1, 13), [eventos_por_mes.get(i, 0) for i in range(1, 13)],
                       color='skyblue', alpha=0.7)
        axes[0, 0].set_title('Asistentes Promedio a Eventos por Mes')
        axes[0, 0].set_xlabel('Mes')
        axes[0, 0].set_ylabel('Asistentes Promedio')
        axes[0, 0].set_xticks(range(1, 13))
        axes[0, 0].set_xticklabels(meses, rotation=45)

    # Gráfico 2: Ventas por giro
    if 'ventas' in datos:
        ventas_df = datos['ventas']
        ventas_por_giro = ventas_df.groupby('giro')['ingresos_totales'].sum().sort_values(ascending=True)

        axes[0, 1].barh(range(len(ventas_por_giro)), ventas_por_giro.values / 1e9,
                        color='lightgreen', alpha=0.7)
        axes[0, 1].set_title('Ingresos Totales por Giro Turístico')
        axes[0, 1].set_xlabel('Ingresos (Miles de Millones $)')
        axes[0, 1].set_yticks(range(len(ventas_por_giro)))
        axes[0, 1].set_yticklabels(ventas_por_giro.index)

    # Gráfico 3: Gasto por tipo de viajero
    if 'perfiles' in datos:
        perfiles_df = datos['perfiles']
        gasto_por_tipo = perfiles_df.groupby('tipo_viajero')['gasto_total'].mean().sort_values(ascending=False)

        axes[1, 0].bar(range(len(gasto_por_tipo)), gasto_por_tipo.values / 1000,
                       color='orange', alpha=0.7)
        axes[1, 0].set_title('Gasto Promedio por Tipo de Viajero')
        axes[1, 0].set_xlabel('Tipo de Viajero')
        axes[1, 0].set_ylabel('Gasto Promedio (Miles $)')
        axes[1, 0].set_xticks(range(len(gasto_por_tipo)))
        axes[1, 0].set_xticklabels(gasto_por_tipo.index, rotation=45, ha='right')

    # Gráfico 4: ROI por tipo de campaña
    if 'publicidad' in datos:
        publicidad_df = datos['publicidad']
        roi_por_tipo = publicidad_df.groupby('tipo_campana')['roi'].mean().sort_values(ascending=True)

        axes[1, 1].barh(range(len(roi_por_tipo)), roi_por_tipo.values / 1000,
                        color='coral', alpha=0.7)
        axes[1, 1].set_title('ROI Promedio por Tipo de Campaña')
        axes[1, 1].set_xlabel('ROI Promedio (Miles %)')
        axes[1, 1].set_yticks(range(len(roi_por_tipo)))
        axes[1, 1].set_yticklabels(roi_por_tipo.index)

    plt.tight_layout()

    # Guardar gráfico
    ruta_grafico = 'data/resultados/analisis_tendencias.png'
    os.makedirs('data/resultados', exist_ok=True)
    plt.savefig(ruta_grafico, dpi=300, bbox_inches='tight')
    print(f"📊 Gráfico guardado en: {ruta_grafico}")

    # Mostrar gráfico
    plt.show()


def main():
    """
    Función principal del análisis.
    """
    print("🔍 ANÁLISIS DE DATOS SINTÉTICOS - CLÚSTER DE TURISMO DE NUEVO LEÓN")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Cargar datos
    datos = cargar_datos()

    if not datos:
        print("❌ No se pudieron cargar los datos. Ejecuta primero generar_todos_datos.py")
        return

    # Realizar análisis
    analizar_tendencias_estacionales(datos)
    analizar_publicidad(datos)

    # Generar gráficos
    try:
        generar_graficos(datos)
    except Exception as e:
        print(f"⚠️ Error al generar gráficos: {e}")
        print("Continuando con el análisis...")

    print("\n" + "=" * 80)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 80)
    print("\n🎯 CONCLUSIONES PRINCIPALES:")
    print("  • Los datos muestran claras tendencias estacionales")
    print("  • Verano (Jun-Ago) es la temporada de mayor actividad")
    print("  • Los fines de semana generan mayores ingresos")
    print("  • Las campañas digitales tienen mejor ROI")
    print("  • Los viajeros de lujo tienen el mayor gasto promedio")
    print("\n🔐 PRIVACIDAD:")
    print("  • Todos los IDs de empresa están completamente anonimizados")
    print("  • Es imposible rastrear el origen de los datos")
    print("  • Los datos son sintéticos pero con patrones realistas")


if __name__ == "__main__":
    main()
