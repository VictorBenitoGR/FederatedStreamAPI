# ./src/datos_sinteticos/generador_perfil_viajero.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


class GeneradorPerfilViajero:
    """
    Generador de datos sintéticos de perfil del viajero.

    Simula perfiles de viajeros con patrones realistas:
    - Diferentes tipos de viajeros (familiar, negocios, aventura, etc.)
    - Gasto promedio que varía por temporada
    - Preferencias por actividades según el perfil
    - Duración de estancia variable
    """

    def __init__(self, empresas_df, fecha_inicio='2020-01-01', fecha_fin='2025-12-31', seed=42):
        """
        Inicializar el generador de perfil del viajero.

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

        # Tipos de viajeros
        self.tipos_viajero = [
            'familiar', 'negocios', 'aventura', 'cultural', 'romantico',
            'mochilero', 'lujo', 'gastronomico', 'wellness', 'deportivo'
        ]

        # Distribución de tipos de viajero
        self.distribucion_viajeros = {
            'familiar': 0.30,
            'negocios': 0.20,
            'aventura': 0.15,
            'cultural': 0.10,
            'romantico': 0.08,
            'gastronomico': 0.06,
            'mochilero': 0.04,
            'lujo': 0.03,
            'wellness': 0.02,
            'deportivo': 0.02
        }

        # Rangos de edad por tipo de viajero
        self.rangos_edad = {
            'familiar': (25, 45),
            'negocios': (28, 55),
            'aventura': (20, 40),
            'cultural': (30, 65),
            'romantico': (22, 50),
            'gastronomico': (25, 60),
            'mochilero': (18, 30),
            'lujo': (35, 70),
            'wellness': (30, 55),
            'deportivo': (20, 45)
        }

    def _calcular_factor_gasto_estacional(self, fecha, tipo_viajero):
        """
        Calcular factor de gasto estacional por tipo de viajero.

        Parameters
        ----------
        fecha : datetime
            Fecha del viaje
        tipo_viajero : str
            Tipo de viajero

        Returns
        -------
        float
            Factor multiplicador de gasto
        """
        mes = fecha.month

        # Factores de gasto por mes y tipo de viajero
        factores_gasto = {
            'familiar': {
                1: 0.8, 2: 0.7, 3: 0.9, 4: 1.2, 5: 1.1, 6: 1.5,
                7: 1.8, 8: 1.7, 9: 1.0, 10: 0.9, 11: 0.8, 12: 1.4
            },
            'negocios': {
                1: 1.0, 2: 1.1, 3: 1.2, 4: 1.1, 5: 1.0, 6: 0.9,
                7: 0.8, 8: 0.7, 9: 1.2, 10: 1.3, 11: 1.2, 12: 0.9
            },
            'aventura': {
                1: 0.6, 2: 0.5, 3: 0.8, 4: 1.1, 5: 1.3, 6: 1.6,
                7: 1.8, 8: 1.7, 9: 1.4, 10: 1.2, 11: 0.7, 12: 0.8
            },
            'cultural': {
                1: 0.8, 2: 0.7, 3: 1.0, 4: 1.2, 5: 1.1, 6: 1.3,
                7: 1.4, 8: 1.3, 9: 1.2, 10: 1.1, 11: 1.0, 12: 1.1
            },
            'romantico': {
                1: 0.7, 2: 1.5, 3: 0.9, 4: 1.0, 5: 1.2, 6: 1.3,
                7: 1.4, 8: 1.3, 9: 1.0, 10: 0.9, 11: 0.8, 12: 1.6
            },
            'lujo': {
                1: 1.2, 2: 1.0, 3: 1.1, 4: 1.3, 5: 1.2, 6: 1.4,
                7: 1.6, 8: 1.5, 9: 1.2, 10: 1.1, 11: 1.0, 12: 1.8
            }
        }

        # Factor base por tipo
        if tipo_viajero in factores_gasto:
            factor_base = factores_gasto[tipo_viajero][mes]
        else:
            # Factor genérico
            factor_base = {
                1: 0.8, 2: 0.7, 3: 0.9, 4: 1.1, 5: 1.2, 6: 1.4,
                7: 1.5, 8: 1.4, 9: 1.1, 10: 1.0, 11: 0.9, 12: 1.3
            }[mes]

        # Factor de crecimiento anual (inflación + mejora económica)
        años_desde_2020 = fecha.year - 2020
        factor_crecimiento = 1 + (años_desde_2020 * 0.025)  # 2.5% anual

        return factor_base * factor_crecimiento

    def _generar_gasto_base_por_tipo(self, tipo_viajero):
        """
        Generar gasto base diario según el tipo de viajero.

        Parameters
        ----------
        tipo_viajero : str
            Tipo de viajero

        Returns
        -------
        float
            Gasto base diario en pesos
        """
        gastos_base = {
            'familiar': np.random.uniform(1500, 3500),
            'negocios': np.random.uniform(2500, 5000),
            'aventura': np.random.uniform(800, 2000),
            'cultural': np.random.uniform(1200, 2800),
            'romantico': np.random.uniform(2000, 4500),
            'gastronomico': np.random.uniform(1800, 4000),
            'mochilero': np.random.uniform(400, 1200),
            'lujo': np.random.uniform(5000, 15000),
            'wellness': np.random.uniform(2500, 6000),
            'deportivo': np.random.uniform(1000, 2500)
        }

        return gastos_base.get(tipo_viajero, np.random.uniform(1000, 3000))

    def _generar_duracion_estancia(self, tipo_viajero):
        """
        Generar duración de estancia según el tipo de viajero.

        Parameters
        ----------
        tipo_viajero : str
            Tipo de viajero

        Returns
        -------
        int
            Días de estancia
        """
        duraciones = {
            'familiar': np.random.randint(3, 8),
            'negocios': np.random.randint(1, 4),
            'aventura': np.random.randint(5, 15),
            'cultural': np.random.randint(3, 10),
            'romantico': np.random.randint(2, 6),
            'gastronomico': np.random.randint(2, 5),
            'mochilero': np.random.randint(7, 21),
            'lujo': np.random.randint(3, 10),
            'wellness': np.random.randint(3, 7),
            'deportivo': np.random.randint(2, 8)
        }

        return duraciones.get(tipo_viajero, np.random.randint(2, 7))

    def _generar_actividades_preferidas(self, tipo_viajero):
        """
        Generar actividades preferidas según el tipo de viajero.

        Parameters
        ----------
        tipo_viajero : str
            Tipo de viajero

        Returns
        -------
        list
            Lista de actividades preferidas
        """
        actividades_por_tipo = {
            'familiar': ['parques_tematicos', 'museos', 'playas', 'restaurantes_familiares'],
            'negocios': ['hoteles_ejecutivos', 'centros_convenciones', 'restaurantes_formales'],
            'aventura': ['deportes_extremos', 'senderismo', 'tours_naturaleza'],
            'cultural': ['museos', 'sitios_historicos', 'tours_culturales', 'teatros'],
            'romantico': ['hoteles_boutique', 'restaurantes_romanticos', 'spas'],
            'gastronomico': ['restaurantes_gourmet', 'tours_gastronomicos', 'mercados_locales'],
            'mochilero': ['hostales', 'transporte_publico', 'comida_local'],
            'lujo': ['hoteles_lujo', 'restaurantes_exclusivos', 'spas_premium'],
            'wellness': ['spas', 'yoga', 'retiros_wellness'],
            'deportivo': ['actividades_deportivas', 'gimnasios', 'competencias']
        }

        return actividades_por_tipo.get(tipo_viajero, ['actividades_generales'])

    def generar_perfiles_viajeros(self, num_registros=5000):
        """
        Generar registros de perfiles de viajeros.

        Parameters
        ----------
        num_registros : int, default=5000
            Número de registros a generar

        Returns
        -------
        pd.DataFrame
            DataFrame con perfiles de viajeros
        """
        perfiles = []

        print(f"👥 Generando {num_registros} perfiles de viajeros...")

        for i in range(num_registros):
            # Generar fecha aleatoria
            dias_total = (self.fecha_fin - self.fecha_inicio).days
            fecha_llegada = self.fecha_inicio + timedelta(days=np.random.randint(0, dias_total))

            # Seleccionar tipo de viajero
            tipos = list(self.distribucion_viajeros.keys())
            probabilidades = list(self.distribucion_viajeros.values())
            tipo_viajero = np.random.choice(tipos, p=probabilidades)

            # Generar características del viajero
            edad_min, edad_max = self.rangos_edad[tipo_viajero]
            edad = np.random.randint(edad_min, edad_max + 1)

            # Generar grupo de viaje
            if tipo_viajero == 'familiar':
                tamaño_grupo = np.random.randint(3, 6)
            elif tipo_viajero == 'negocios':
                tamaño_grupo = 1 if np.random.random() < 0.7 else np.random.randint(2, 4)
            elif tipo_viajero == 'romantico':
                tamaño_grupo = 2
            elif tipo_viajero == 'mochilero':
                tamaño_grupo = 1 if np.random.random() < 0.6 else np.random.randint(2, 4)
            else:
                tamaño_grupo = np.random.randint(1, 5)

            # Calcular duración y gastos
            duracion_estancia = self._generar_duracion_estancia(tipo_viajero)
            gasto_base_diario = self._generar_gasto_base_por_tipo(tipo_viajero)
            factor_estacional = self._calcular_factor_gasto_estacional(fecha_llegada, tipo_viajero)

            gasto_diario_ajustado = gasto_base_diario * factor_estacional * tamaño_grupo
            gasto_total = gasto_diario_ajustado * duracion_estancia

            # Distribución del gasto por categorías
            if tipo_viajero == 'gastronomico':
                pct_alimentacion = np.random.uniform(0.4, 0.6)
            elif tipo_viajero == 'lujo':
                pct_alimentacion = np.random.uniform(0.25, 0.35)
            else:
                pct_alimentacion = np.random.uniform(0.25, 0.4)

            if tipo_viajero in ['negocios', 'lujo']:
                pct_hospedaje = np.random.uniform(0.4, 0.6)
            elif tipo_viajero == 'mochilero':
                pct_hospedaje = np.random.uniform(0.15, 0.25)
            else:
                pct_hospedaje = np.random.uniform(0.3, 0.45)

            pct_actividades = 1 - pct_alimentacion - pct_hospedaje

            gasto_alimentacion = gasto_total * pct_alimentacion
            gasto_hospedaje = gasto_total * pct_hospedaje
            gasto_actividades = gasto_total * pct_actividades

            # Generar actividades preferidas
            actividades = self._generar_actividades_preferidas(tipo_viajero)

            perfil = {
                'viajero_id': f"viajero_{i+1:06d}",
                'fecha_llegada': fecha_llegada.strftime('%Y-%m-%d'),
                'tipo_viajero': tipo_viajero,
                'edad': edad,
                'tamaño_grupo': tamaño_grupo,
                'duracion_estancia': duracion_estancia,
                'gasto_total': round(gasto_total, 2),
                'gasto_diario_promedio': round(gasto_diario_ajustado, 2),
                'gasto_alimentacion': round(gasto_alimentacion, 2),
                'gasto_hospedaje': round(gasto_hospedaje, 2),
                'gasto_actividades': round(gasto_actividades, 2),
                'actividades_preferidas': ','.join(actividades),
                'factor_estacional': round(factor_estacional, 3),
                'mes': fecha_llegada.month,
                'año': fecha_llegada.year,
                'temporada': self._clasificar_temporada(fecha_llegada.month)
            }

            perfiles.append(perfil)

            if (i + 1) % 1000 == 0:
                print(f"  Generados {i + 1}/{num_registros} perfiles")

        return pd.DataFrame(perfiles)

    def _clasificar_temporada(self, mes):
        """
        Clasificar temporada según el mes.

        Parameters
        ----------
        mes : int
            Número del mes

        Returns
        -------
        str
            Temporada clasificada
        """
        if mes in [12, 1, 2]:
            return 'invierno'
        elif mes in [3, 4, 5]:
            return 'primavera'
        elif mes in [6, 7, 8]:
            return 'verano'
        else:
            return 'otoño'

    def guardar_perfiles(self, ruta_archivo='data/datos_sinteticos/perfil_viajero_dummy.csv', num_registros=5000):
        """
        Generar y guardar los perfiles de viajeros en un archivo CSV.

        Parameters
        ----------
        ruta_archivo : str, default='data/datos_sinteticos/perfil_viajero_dummy.csv'
            Ruta donde guardar el archivo
        num_registros : int, default=5000
            Número de registros a generar

        Returns
        -------
        pd.DataFrame
            DataFrame con los perfiles generados
        """
        df_perfiles = self.generar_perfiles_viajeros(num_registros)

        if len(df_perfiles) > 0:
            df_perfiles.to_csv(ruta_archivo, index=False)
            print(f"✅ Generados {len(df_perfiles)} perfiles de viajeros guardados en {ruta_archivo}")

            # Estadísticas generales
            print(f"\n📊 Estadísticas de perfiles de viajeros:")
            print(f"  Total perfiles: {len(df_perfiles):,}")
            print(f"  Período: {df_perfiles['fecha_llegada'].min()} a {df_perfiles['fecha_llegada'].max()}")
            print(f"  Gasto total acumulado: ${df_perfiles['gasto_total'].sum():,.0f}")
            print(f"  Gasto promedio por viajero: ${df_perfiles['gasto_total'].mean():.0f}")
            print(f"  Duración promedio de estancia: {df_perfiles['duracion_estancia'].mean():.1f} días")

            # Estadísticas por tipo de viajero
            print(f"\n👥 Estadísticas por tipo de viajero:")
            stats_tipo = df_perfiles.groupby('tipo_viajero').agg({
                'gasto_total': ['count', 'mean', 'sum'],
                'duracion_estancia': 'mean',
                'tamaño_grupo': 'mean'
            }).round(1)

            for tipo in stats_tipo.index:
                count = stats_tipo.loc[tipo, ('gasto_total', 'count')]
                gasto_promedio = stats_tipo.loc[tipo, ('gasto_total', 'mean')]
                gasto_total = stats_tipo.loc[tipo, ('gasto_total', 'sum')]
                duracion = stats_tipo.loc[tipo, ('duracion_estancia', 'mean')]
                grupo = stats_tipo.loc[tipo, ('tamaño_grupo', 'mean')]
                print(f"  {tipo}: {count} viajeros, ${gasto_promedio:,.0f} promedio, {duracion:.1f} días, {grupo:.1f} personas/grupo")

            # Estadísticas por temporada
            print(f"\n🌤️ Gasto promedio por temporada:")
            gasto_temporada = df_perfiles.groupby('temporada')['gasto_total'].mean().sort_values(ascending=False)
            for temporada, gasto in gasto_temporada.items():
                print(f"  {temporada}: ${gasto:,.0f} promedio")
        else:
            print("⚠️ No se generaron perfiles de viajeros")

        return df_perfiles


if __name__ == "__main__":
    # Cargar empresas dummy (aunque no se usen directamente, mantener consistencia)
    try:
        empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')

        # Generar perfiles de viajeros
        generador = GeneradorPerfilViajero(empresas_df)
        perfiles_df = generador.guardar_perfiles(num_registros=5000)

    except FileNotFoundError:
        print("❌ Error: Primero ejecuta generador_empresas.py para crear las empresas dummy")
