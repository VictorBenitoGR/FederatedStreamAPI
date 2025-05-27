# ./src/datos_sinteticos/generador_eventos.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import math


class GeneradorEventos:
    """
    Generador de datos sintéticos de eventos con tendencias estacionales.

    Simula eventos turísticos con patrones realistas:
    - Más asistentes en verano (junio-agosto)
    - Picos en vacaciones (diciembre, semana santa)
    - Mayor actividad en fines de semana
    - Crecimiento año tras año
    """

    def __init__(self, empresas_df, fecha_inicio='2020-01-01', fecha_fin='2025-12-31', seed=42):
        """
        Inicializar el generador de eventos.

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

        # Filtrar solo empresas de eventos
        self.empresas_eventos = empresas_df[empresas_df['giro'] == 'evento'].copy()

    def _calcular_factor_estacional(self, fecha):
        """
        Calcular factor estacional basado en la fecha.

        Parameters
        ----------
        fecha : datetime
            Fecha del evento

        Returns
        -------
        float
            Factor multiplicador estacional (0.5 - 2.0)
        """
        mes = fecha.month

        # Factores estacionales por mes (más alto en verano y vacaciones)
        factores_mensuales = {
            1: 0.8,   # Enero - post navidad
            2: 0.7,   # Febrero - temporada baja
            3: 0.9,   # Marzo - inicio primavera
            4: 1.1,   # Abril - semana santa
            5: 1.2,   # Mayo - buen clima
            6: 1.6,   # Junio - inicio verano
            7: 1.8,   # Julio - pico verano
            8: 1.7,   # Agosto - verano
            9: 1.3,   # Septiembre - regreso actividades
            10: 1.1,  # Octubre - otoño
            11: 0.9,  # Noviembre - pre invierno
            12: 1.4   # Diciembre - fiestas navideñas
        }

        factor_base = factores_mensuales[mes]

        # Factor adicional para fines de semana
        if fecha.weekday() >= 5:  # Sábado o domingo
            factor_base *= 1.3

        # Factor de crecimiento anual (2% anual)
        años_desde_2020 = fecha.year - 2020
        factor_crecimiento = 1 + (años_desde_2020 * 0.02)

        return factor_base * factor_crecimiento

    def _generar_eventos_empresa(self, empresa_row):
        """
        Generar eventos para una empresa específica.

        Parameters
        ----------
        empresa_row : pd.Series
            Fila con datos de la empresa

        Returns
        -------
        list
            Lista de eventos generados
        """
        eventos = []
        empresa_id = empresa_row['empresa_id']
        capacidad_base = empresa_row['capacidad_base']
        precio_base = empresa_row['precio_promedio_base']

        # Generar eventos a lo largo del período
        fecha_actual = self.fecha_inicio

        while fecha_actual <= self.fecha_fin:
            # Probabilidad de tener evento (más alta en temporadas altas)
            factor_estacional = self._calcular_factor_estacional(fecha_actual)
            probabilidad_evento = min(0.15 * factor_estacional, 0.8)

            if np.random.random() < probabilidad_evento:
                # Calcular asistentes basado en capacidad y factores estacionales
                asistentes_base = capacidad_base * np.random.uniform(0.3, 0.9)
                asistentes = int(asistentes_base * factor_estacional)
                asistentes = max(10, min(asistentes, capacidad_base))  # Límites realistas

                # Calcular precio con variación estacional
                precio_evento = precio_base * np.random.uniform(0.8, 1.2) * (factor_estacional * 0.5 + 0.5)

                # Calcular ingresos totales
                ingresos_totales = asistentes * precio_evento

                evento = {
                    'empresa_id': empresa_id,
                    'fecha': fecha_actual.strftime('%Y-%m-%d'),
                    'asistentes': asistentes,
                    'capacidad_maxima': capacidad_base,
                    'precio_entrada': round(precio_evento, 2),
                    'ingresos_totales': round(ingresos_totales, 2),
                    'ocupacion_porcentaje': round((asistentes / capacidad_base) * 100, 1),
                    'factor_estacional': round(factor_estacional, 3),
                    'dia_semana': fecha_actual.strftime('%A'),
                    'mes': fecha_actual.month,
                    'año': fecha_actual.year
                }

                eventos.append(evento)

            # Avanzar fecha (eventos pueden ser cada 1-7 días)
            dias_siguiente = np.random.randint(1, 8)
            fecha_actual += timedelta(days=dias_siguiente)

        return eventos

    def generar_todos_eventos(self):
        """
        Generar eventos para todas las empresas de eventos.

        Returns
        -------
        pd.DataFrame
            DataFrame con todos los eventos generados
        """
        todos_eventos = []

        print(f"🎪 Generando eventos para {len(self.empresas_eventos)} empresas...")

        for idx, empresa in self.empresas_eventos.iterrows():
            eventos_empresa = self._generar_eventos_empresa(empresa)
            todos_eventos.extend(eventos_empresa)

            if (idx + 1) % 5 == 0:
                print(f"  Procesadas {idx + 1}/{len(self.empresas_eventos)} empresas")

        df_eventos = pd.DataFrame(todos_eventos)

        if len(df_eventos) > 0:
            # Ordenar por fecha
            df_eventos['fecha'] = pd.to_datetime(df_eventos['fecha'])
            df_eventos = df_eventos.sort_values('fecha').reset_index(drop=True)
            df_eventos['fecha'] = df_eventos['fecha'].dt.strftime('%Y-%m-%d')

        return df_eventos

    def guardar_eventos(self, ruta_archivo='data/datos_sinteticos/eventos_dummy.csv'):
        """
        Generar y guardar los eventos en un archivo CSV.

        Parameters
        ----------
        ruta_archivo : str, default='data/datos_sinteticos/eventos_dummy.csv'
            Ruta donde guardar el archivo

        Returns
        -------
        pd.DataFrame
            DataFrame con los eventos generados
        """
        df_eventos = self.generar_todos_eventos()

        if len(df_eventos) > 0:
            df_eventos.to_csv(ruta_archivo, index=False)
            print(f"✅ Generados {len(df_eventos)} eventos guardados en {ruta_archivo}")

            # Estadísticas
            print(f"\n📊 Estadísticas de eventos:")
            print(f"  Total eventos: {len(df_eventos):,}")
            print(f"  Período: {df_eventos['fecha'].min()} a {df_eventos['fecha'].max()}")
            print(f"  Asistentes promedio: {df_eventos['asistentes'].mean():.0f}")
            print(f"  Ocupación promedio: {df_eventos['ocupacion_porcentaje'].mean():.1f}%")
            print(f"  Ingresos totales: ${df_eventos['ingresos_totales'].sum():,.0f}")

            # Estadísticas por mes
            eventos_por_mes = df_eventos.groupby('mes')['asistentes'].agg(['count', 'mean']).round(0)
            print(f"\n📅 Eventos y asistentes promedio por mes:")
            meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                     'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            for mes_num, mes_nombre in enumerate(meses, 1):
                if mes_num in eventos_por_mes.index:
                    count = eventos_por_mes.loc[mes_num, 'count']
                    mean_asist = eventos_por_mes.loc[mes_num, 'mean']
                    print(f"  {mes_nombre}: {count} eventos, {mean_asist:.0f} asistentes promedio")
        else:
            print("⚠️ No se generaron eventos (no hay empresas de eventos)")

        return df_eventos


if __name__ == "__main__":
    # Cargar empresas dummy
    try:
        empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')

        # Generar eventos
        generador = GeneradorEventos(empresas_df)
        eventos_df = generador.guardar_eventos()

    except FileNotFoundError:
        print("❌ Error: Primero ejecuta generador_empresas.py para crear las empresas dummy")
