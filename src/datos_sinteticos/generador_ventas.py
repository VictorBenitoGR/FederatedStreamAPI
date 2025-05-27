# ./src/datos_sinteticos/generador_ventas.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


class GeneradorVentas:
    """
    Generador de datos sintéticos de ventas por giro turístico.

    Simula ventas con patrones realistas:
    - Hoteles: picos en vacaciones y fines de semana
    - Restaurantes: mayor actividad en fines de semana
    - Agencias de viajes: muy estacional (vacaciones)
    - Otros giros: patrones específicos por tipo
    """

    def __init__(self, empresas_df, fecha_inicio='2020-01-01', fecha_fin='2025-12-31', seed=42):
        """
        Inicializar el generador de ventas.

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

    def _calcular_factor_estacional_giro(self, fecha, giro):
        """
        Calcular factor estacional específico por giro.

        Parameters
        ----------
        fecha : datetime
            Fecha de la venta
        giro : str
            Giro turístico de la empresa

        Returns
        -------
        float
            Factor multiplicador estacional
        """
        mes = fecha.month
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo

        # Factores base por mes para cada giro
        factores_por_giro = {
            'hotel': {
                1: 0.7, 2: 0.6, 3: 0.8, 4: 1.2, 5: 1.1, 6: 1.5,
                7: 1.8, 8: 1.7, 9: 1.2, 10: 1.0, 11: 0.8, 12: 1.4
            },
            'restaurante': {
                1: 0.8, 2: 0.7, 3: 0.9, 4: 1.1, 5: 1.2, 6: 1.3,
                7: 1.4, 8: 1.3, 9: 1.2, 10: 1.1, 11: 1.0, 12: 1.5
            },
            'agencia_viajes': {
                1: 0.5, 2: 0.4, 3: 0.7, 4: 1.3, 5: 1.4, 6: 1.8,
                7: 2.0, 8: 1.9, 9: 1.1, 10: 0.8, 11: 0.6, 12: 1.6
            },
            'transporte': {
                1: 0.7, 2: 0.6, 3: 0.8, 4: 1.2, 5: 1.3, 6: 1.6,
                7: 1.8, 8: 1.7, 9: 1.2, 10: 1.0, 11: 0.8, 12: 1.3
            },
            'atraccion_turistica': {
                1: 0.6, 2: 0.5, 3: 0.8, 4: 1.1, 5: 1.3, 6: 1.7,
                7: 1.9, 8: 1.8, 9: 1.3, 10: 1.1, 11: 0.7, 12: 1.2
            }
        }

        # Factor base por mes
        if giro in factores_por_giro:
            factor_base = factores_por_giro[giro][mes]
        else:
            # Factor genérico para otros giros
            factor_base = {
                1: 0.8, 2: 0.7, 3: 0.9, 4: 1.1, 5: 1.2, 6: 1.4,
                7: 1.5, 8: 1.4, 9: 1.2, 10: 1.1, 11: 0.9, 12: 1.3
            }[mes]

        # Factor de fin de semana específico por giro
        if dia_semana >= 5:  # Sábado o domingo
            if giro == 'restaurante':
                factor_base *= 1.8  # Restaurantes muy activos en fines de semana
            elif giro == 'hotel':
                factor_base *= 1.4  # Hoteles moderadamente más activos
            elif giro == 'agencia_viajes':
                factor_base *= 1.1  # Agencias poco afectadas por fin de semana
            else:
                factor_base *= 1.3  # Factor genérico

        # Factor de crecimiento anual (1.5% anual)
        años_desde_2020 = fecha.year - 2020
        factor_crecimiento = 1 + (años_desde_2020 * 0.015)

        return factor_base * factor_crecimiento

    def _generar_ventas_empresa(self, empresa_row):
        """
        Generar ventas para una empresa específica.

        Parameters
        ----------
        empresa_row : pd.Series
            Fila con datos de la empresa

        Returns
        -------
        list
            Lista de ventas generadas
        """
        ventas = []
        empresa_id = empresa_row['empresa_id']
        giro = empresa_row['giro']
        capacidad_base = empresa_row['capacidad_base']
        precio_base = empresa_row['precio_promedio_base']

        # Generar ventas diarias
        fecha_actual = self.fecha_inicio

        while fecha_actual <= self.fecha_fin:
            factor_estacional = self._calcular_factor_estacional_giro(fecha_actual, giro)

            # Probabilidad de tener ventas (varía por giro)
            prob_base = {
                'hotel': 0.85,
                'restaurante': 0.90,
                'agencia_viajes': 0.60,
                'evento': 0.40,  # Ya manejado en generador_eventos
                'transporte': 0.70,
                'atraccion_turistica': 0.75
            }.get(giro, 0.65)

            probabilidad_venta = min(prob_base * (factor_estacional * 0.3 + 0.7), 0.95)

            if np.random.random() < probabilidad_venta:
                # Calcular número de transacciones/clientes
                if giro == 'hotel':
                    # Habitaciones ocupadas
                    clientes = int(capacidad_base * np.random.uniform(0.2, 0.9) * factor_estacional)
                    clientes = max(1, min(clientes, capacidad_base))
                elif giro == 'restaurante':
                    # Comensales por día
                    clientes = int(capacidad_base * np.random.uniform(0.3, 1.2) * factor_estacional)
                    clientes = max(1, clientes)
                else:
                    # Clientes/servicios generales
                    clientes = int(capacidad_base * np.random.uniform(0.1, 0.8) * factor_estacional)
                    clientes = max(1, clientes)

                # Calcular precio promedio con variación
                precio_promedio = precio_base * np.random.uniform(0.8, 1.3) * (factor_estacional * 0.4 + 0.6)

                # Calcular ingresos totales
                ingresos_totales = clientes * precio_promedio

                venta = {
                    'empresa_id': empresa_id,
                    'fecha': fecha_actual.strftime('%Y-%m-%d'),
                    'giro': giro,
                    'numero_clientes': clientes,
                    'precio_promedio': round(precio_promedio, 2),
                    'ingresos_totales': round(ingresos_totales, 2),
                    'factor_estacional': round(factor_estacional, 3),
                    'dia_semana': fecha_actual.strftime('%A'),
                    'mes': fecha_actual.month,
                    'año': fecha_actual.year,
                    'es_fin_semana': fecha_actual.weekday() >= 5
                }

                ventas.append(venta)

            # Avanzar un día
            fecha_actual += timedelta(days=1)

        return ventas

    def generar_todas_ventas(self):
        """
        Generar ventas para todas las empresas.

        Returns
        -------
        pd.DataFrame
            DataFrame con todas las ventas generadas
        """
        todas_ventas = []

        print(f"💰 Generando ventas para {len(self.empresas_df)} empresas...")

        for idx, empresa in self.empresas_df.iterrows():
            # Saltar empresas de eventos (ya manejadas en generador_eventos)
            if empresa['giro'] != 'evento':
                ventas_empresa = self._generar_ventas_empresa(empresa)
                todas_ventas.extend(ventas_empresa)

            if (idx + 1) % 10 == 0:
                print(f"  Procesadas {idx + 1}/{len(self.empresas_df)} empresas")

        df_ventas = pd.DataFrame(todas_ventas)

        if len(df_ventas) > 0:
            # Ordenar por fecha
            df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha'])
            df_ventas = df_ventas.sort_values(['fecha', 'empresa_id']).reset_index(drop=True)
            df_ventas['fecha'] = df_ventas['fecha'].dt.strftime('%Y-%m-%d')

        return df_ventas

    def guardar_ventas(self, ruta_archivo='data/datos_sinteticos/ventas_dummy.csv'):
        """
        Generar y guardar las ventas en un archivo CSV.

        Parameters
        ----------
        ruta_archivo : str, default='data/datos_sinteticos/ventas_dummy.csv'
            Ruta donde guardar el archivo

        Returns
        -------
        pd.DataFrame
            DataFrame con las ventas generadas
        """
        df_ventas = self.generar_todas_ventas()

        if len(df_ventas) > 0:
            df_ventas.to_csv(ruta_archivo, index=False)
            print(f"✅ Generadas {len(df_ventas)} ventas guardadas en {ruta_archivo}")

            # Estadísticas generales
            print(f"\n📊 Estadísticas de ventas:")
            print(f"  Total registros: {len(df_ventas):,}")
            print(f"  Período: {df_ventas['fecha'].min()} a {df_ventas['fecha'].max()}")
            print(f"  Ingresos totales: ${df_ventas['ingresos_totales'].sum():,.0f}")
            print(f"  Ingreso promedio por transacción: ${df_ventas['ingresos_totales'].mean():.0f}")

            # Estadísticas por giro
            print(f"\n🏢 Ventas por giro:")
            ventas_por_giro = df_ventas.groupby('giro').agg({
                'ingresos_totales': ['count', 'sum', 'mean'],
                'numero_clientes': 'sum'
            }).round(0)

            for giro in ventas_por_giro.index:
                count = ventas_por_giro.loc[giro, ('ingresos_totales', 'count')]
                total = ventas_por_giro.loc[giro, ('ingresos_totales', 'sum')]
                promedio = ventas_por_giro.loc[giro, ('ingresos_totales', 'mean')]
                clientes = ventas_por_giro.loc[giro, ('numero_clientes', 'sum')]
                print(f"  {giro}: {count:,.0f} registros, ${total:,.0f} total, ${promedio:,.0f} promedio, {clientes:,.0f} clientes")

            # Comparación fin de semana vs días laborales
            print(f"\n📅 Comparación fin de semana vs días laborales:")
            comparacion = df_ventas.groupby('es_fin_semana')['ingresos_totales'].agg(['count', 'mean']).round(0)
            for es_finde, datos in comparacion.iterrows():
                tipo_dia = "Fin de semana" if es_finde else "Días laborales"
                print(f"  {tipo_dia}: {datos['count']:,.0f} registros, ${datos['mean']:,.0f} promedio")
        else:
            print("⚠️ No se generaron ventas")

        return df_ventas


if __name__ == "__main__":
    # Cargar empresas dummy
    try:
        empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')

        # Generar ventas
        generador = GeneradorVentas(empresas_df)
        ventas_df = generador.guardar_ventas()

    except FileNotFoundError:
        print("❌ Error: Primero ejecuta generador_empresas.py para crear las empresas dummy")
