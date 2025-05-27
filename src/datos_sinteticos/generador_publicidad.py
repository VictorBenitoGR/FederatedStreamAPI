# ./src/datos_sinteticos/generador_publicidad.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


class GeneradorPublicidad:
    """
    Generador de datos sintéticos de campañas publicitarias.

    Simula campañas con patrones realistas:
    - Mejor conversión en meses específicos según el giro
    - Variación por tipo de campaña (digital, tradicional)
    - Estacionalidad en efectividad
    - Diferentes presupuestos y alcances
    """

    def __init__(self, empresas_df, fecha_inicio='2020-01-01', fecha_fin='2025-12-31', seed=42):
        """
        Inicializar el generador de publicidad.

        Parameters
        ----------
        empresas_df : pd.DataFrame
            DataFrame con las empresas dummy
        fecha_inicio : str, default='2020-01-01'
            Fecha de inicio para generar datos
        fecha_fin : str, default='2025-12-31'
            Fecha de fin para generar datos
        seed : int, default=42
            Semilla para reproducibilidad
        """
        self.empresas_df = empresas_df
        self.fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        self.fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

        # Tipos de campañas publicitarias
        self.tipos_campana = [
            'google_ads', 'facebook_ads', 'instagram_ads', 'radio_local',
            'periodico_local', 'vallas_publicitarias', 'email_marketing',
            'influencer_marketing', 'tv_local', 'folletos_turisticos'
        ]

        # Distribución de tipos de campaña
        self.distribucion_campanas = {
            'google_ads': 0.25,
            'facebook_ads': 0.20,
            'instagram_ads': 0.15,
            'email_marketing': 0.12,
            'radio_local': 0.08,
            'influencer_marketing': 0.07,
            'periodico_local': 0.05,
            'vallas_publicitarias': 0.04,
            'tv_local': 0.03,
            'folletos_turisticos': 0.01
        }

    def _calcular_factor_conversion_estacional(self, fecha, giro, tipo_campana):
        """
        Calcular factor de conversión estacional.

        Parameters
        ----------
        fecha : datetime
            Fecha de la campaña
        giro : str
            Giro turístico de la empresa
        tipo_campana : str
            Tipo de campaña publicitaria

        Returns
        -------
        float
            Factor multiplicador de conversión
        """
        mes = fecha.month

        # Factores base de conversión por mes y giro
        factores_conversion = {
            'hotel': {
                1: 0.6, 2: 0.5, 3: 0.8, 4: 1.3, 5: 1.2, 6: 1.6,
                7: 1.8, 8: 1.7, 9: 1.1, 10: 0.9, 11: 0.7, 12: 1.4
            },
            'restaurante': {
                1: 0.7, 2: 0.6, 3: 0.8, 4: 1.0, 5: 1.1, 6: 1.2,
                7: 1.3, 8: 1.2, 9: 1.1, 10: 1.0, 11: 0.9, 12: 1.4
            },
            'agencia_viajes': {
                1: 0.4, 2: 0.3, 3: 0.6, 4: 1.4, 5: 1.6, 6: 1.9,
                7: 2.0, 8: 1.8, 9: 1.0, 10: 0.7, 11: 0.5, 12: 1.5
            },
            'evento': {
                1: 0.5, 2: 0.4, 3: 0.7, 4: 1.2, 5: 1.4, 6: 1.7,
                7: 1.9, 8: 1.8, 9: 1.3, 10: 1.0, 11: 0.6, 12: 1.3
            }
        }

        # Factor base por giro
        if giro in factores_conversion:
            factor_base = factores_conversion[giro][mes]
        else:
            # Factor genérico
            factor_base = {
                1: 0.6, 2: 0.5, 3: 0.7, 4: 1.1, 5: 1.2, 6: 1.4,
                7: 1.5, 8: 1.4, 9: 1.1, 10: 0.9, 11: 0.7, 12: 1.2
            }[mes]

        # Factor por tipo de campaña (digital vs tradicional)
        if tipo_campana in ['google_ads', 'facebook_ads', 'instagram_ads', 'email_marketing']:
            factor_base *= 1.2  # Campañas digitales más efectivas
        elif tipo_campana in ['influencer_marketing']:
            factor_base *= 1.4  # Influencers muy efectivos en turismo
        elif tipo_campana in ['radio_local', 'tv_local']:
            factor_base *= 0.8  # Medios tradicionales menos efectivos

        # Factor de mejora anual (aprendizaje en marketing digital)
        años_desde_2020 = fecha.year - 2020
        factor_mejora = 1 + (años_desde_2020 * 0.03)  # 3% mejora anual

        return factor_base * factor_mejora

    def _generar_campanas_empresa(self, empresa_row):
        """
        Generar campañas publicitarias para una empresa específica.

        Parameters
        ----------
        empresa_row : pd.Series
            Fila con datos de la empresa

        Returns
        -------
        list
            Lista de campañas generadas
        """
        campanas = []
        empresa_id = empresa_row['empresa_id']
        giro = empresa_row['giro']
        capacidad_base = empresa_row['capacidad_base']
        precio_base = empresa_row['precio_promedio_base']

        # Generar campañas mensuales (aproximadamente)
        fecha_actual = self.fecha_inicio

        while fecha_actual <= self.fecha_fin:
            # Probabilidad de lanzar campaña (más alta en temporadas altas)
            mes = fecha_actual.month
            prob_base = 0.4  # 40% probabilidad base mensual

            # Aumentar probabilidad en meses de alta temporada
            if mes in [6, 7, 8, 12]:  # Verano y diciembre
                prob_base = 0.7
            elif mes in [4, 5, 9]:  # Meses medios
                prob_base = 0.5

            if np.random.random() < prob_base:
                # Seleccionar tipo de campaña
                tipos = list(self.distribucion_campanas.keys())
                probabilidades = list(self.distribucion_campanas.values())
                tipo_campana = np.random.choice(tipos, p=probabilidades)

                # Calcular presupuesto basado en el giro y tipo de campaña
                if tipo_campana in ['google_ads', 'facebook_ads', 'instagram_ads']:
                    presupuesto_base = precio_base * capacidad_base * 0.05  # 5% de ingresos potenciales
                elif tipo_campana in ['tv_local', 'radio_local']:
                    presupuesto_base = precio_base * capacidad_base * 0.08  # Más caro
                else:
                    presupuesto_base = precio_base * capacidad_base * 0.03  # Más barato

                presupuesto = presupuesto_base * np.random.uniform(0.5, 2.0)

                # Calcular alcance basado en presupuesto y tipo
                if tipo_campana in ['google_ads', 'facebook_ads', 'instagram_ads']:
                    alcance = int(presupuesto * np.random.uniform(8, 15))  # Mejor alcance digital
                elif tipo_campana in ['tv_local', 'radio_local']:
                    alcance = int(presupuesto * np.random.uniform(20, 40))  # Mucho alcance tradicional
                else:
                    alcance = int(presupuesto * np.random.uniform(5, 12))

                # Calcular factor de conversión
                factor_conversion = self._calcular_factor_conversion_estacional(fecha_actual, giro, tipo_campana)

                # Calcular conversiones (clicks, llamadas, visitas, etc.)
                tasa_conversion_base = {
                    'google_ads': 0.03,
                    'facebook_ads': 0.025,
                    'instagram_ads': 0.02,
                    'email_marketing': 0.05,
                    'influencer_marketing': 0.04,
                    'radio_local': 0.008,
                    'tv_local': 0.006,
                    'periodico_local': 0.01,
                    'vallas_publicitarias': 0.005,
                    'folletos_turisticos': 0.015
                }.get(tipo_campana, 0.02)

                tasa_conversion = tasa_conversion_base * factor_conversion
                conversiones = int(alcance * tasa_conversion)

                # Calcular ventas generadas (no todas las conversiones se vuelven ventas)
                tasa_venta = np.random.uniform(0.15, 0.4)  # 15-40% de conversiones se vuelven ventas
                ventas_generadas = int(conversiones * tasa_venta)

                # Calcular ROI
                ingresos_generados = ventas_generadas * precio_base * np.random.uniform(0.8, 1.2)
                roi = (ingresos_generados - presupuesto) / presupuesto if presupuesto > 0 else 0

                campana = {
                    'empresa_id': empresa_id,
                    'fecha_inicio': fecha_actual.strftime('%Y-%m-%d'),
                    'giro': giro,
                    'tipo_campana': tipo_campana,
                    'presupuesto': round(presupuesto, 2),
                    'alcance': alcance,
                    'conversiones': conversiones,
                    'tasa_conversion': round(tasa_conversion * 100, 3),  # En porcentaje
                    'ventas_generadas': ventas_generadas,
                    'ingresos_generados': round(ingresos_generados, 2),
                    'roi': round(roi * 100, 2),  # En porcentaje
                    'factor_estacional': round(factor_conversion, 3),
                    'mes': fecha_actual.month,
                    'año': fecha_actual.year
                }

                campanas.append(campana)

            # Avanzar aproximadamente un mes
            dias_siguiente = np.random.randint(25, 35)
            fecha_actual += timedelta(days=dias_siguiente)

        return campanas

    def generar_todas_campanas(self):
        """
        Generar campañas para todas las empresas.

        Returns
        -------
        pd.DataFrame
            DataFrame con todas las campañas generadas
        """
        todas_campanas = []

        print(f"📢 Generando campañas publicitarias para {len(self.empresas_df)} empresas...")

        for idx, empresa in self.empresas_df.iterrows():
            campanas_empresa = self._generar_campanas_empresa(empresa)
            todas_campanas.extend(campanas_empresa)

            if (idx + 1) % 10 == 0:
                print(f"  Procesadas {idx + 1}/{len(self.empresas_df)} empresas")

        df_campanas = pd.DataFrame(todas_campanas)

        if len(df_campanas) > 0:
            # Ordenar por fecha
            df_campanas['fecha_inicio'] = pd.to_datetime(df_campanas['fecha_inicio'])
            df_campanas = df_campanas.sort_values(['fecha_inicio', 'empresa_id']).reset_index(drop=True)
            df_campanas['fecha_inicio'] = df_campanas['fecha_inicio'].dt.strftime('%Y-%m-%d')

        return df_campanas

    def guardar_campanas(self, ruta_archivo='data/datos_sinteticos/publicidad_dummy.csv'):
        """
        Generar y guardar las campañas en un archivo CSV.

        Parameters
        ----------
        ruta_archivo : str, default='data/datos_sinteticos/publicidad_dummy.csv'
            Ruta donde guardar el archivo

        Returns
        -------
        pd.DataFrame
            DataFrame con las campañas generadas
        """
        df_campanas = self.generar_todas_campanas()

        if len(df_campanas) > 0:
            df_campanas.to_csv(ruta_archivo, index=False)
            print(f"✅ Generadas {len(df_campanas)} campañas publicitarias guardadas en {ruta_archivo}")

            # Estadísticas generales
            print(f"\n📊 Estadísticas de campañas publicitarias:")
            print(f"  Total campañas: {len(df_campanas):,}")
            print(f"  Período: {df_campanas['fecha_inicio'].min()} a {df_campanas['fecha_inicio'].max()}")
            print(f"  Presupuesto total: ${df_campanas['presupuesto'].sum():,.0f}")
            print(f"  Ingresos generados: ${df_campanas['ingresos_generados'].sum():,.0f}")
            print(f"  ROI promedio: {df_campanas['roi'].mean():.1f}%")
            print(f"  Tasa conversión promedio: {df_campanas['tasa_conversion'].mean():.2f}%")

            # Estadísticas por tipo de campaña
            print(f"\n📱 Rendimiento por tipo de campaña:")
            stats_tipo = df_campanas.groupby('tipo_campana').agg({
                'presupuesto': ['count', 'sum', 'mean'],
                'tasa_conversion': 'mean',
                'roi': 'mean',
                'alcance': 'sum'
            }).round(2)

            for tipo in stats_tipo.index:
                count = stats_tipo.loc[tipo, ('presupuesto', 'count')]
                presupuesto_total = stats_tipo.loc[tipo, ('presupuesto', 'sum')]
                conversion = stats_tipo.loc[tipo, ('tasa_conversion', 'mean')]
                roi = stats_tipo.loc[tipo, ('roi', 'mean')]
                alcance = stats_tipo.loc[tipo, ('alcance', 'sum')]
                print(f"  {tipo}: {count} campañas, ${presupuesto_total:,.0f} total, {conversion:.2f}% conversión, {roi:.1f}% ROI, {alcance:,.0f} alcance")

            # Estadísticas por giro
            print(f"\n🏢 ROI promedio por giro:")
            roi_por_giro = df_campanas.groupby('giro')['roi'].mean().sort_values(ascending=False)
            for giro, roi in roi_por_giro.items():
                print(f"  {giro}: {roi:.1f}% ROI promedio")
        else:
            print("⚠️ No se generaron campañas publicitarias")

        return df_campanas


if __name__ == "__main__":
    # Cargar empresas dummy
    try:
        empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')

        # Generar campañas publicitarias
        generador = GeneradorPublicidad(empresas_df)
        campanas_df = generador.guardar_campanas()

    except FileNotFoundError:
        print("❌ Error: Primero ejecuta generador_empresas.py para crear las empresas dummy")
