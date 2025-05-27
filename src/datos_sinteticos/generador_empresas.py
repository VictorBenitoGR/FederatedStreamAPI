# ./src/datos_sinteticos/generador_empresas.py

import pandas as pd
import numpy as np
import hashlib
import uuid
from datetime import datetime, timedelta
import random


class GeneradorEmpresas:
    """
    Generador de empresas dummy para el Clúster de Turismo de Nuevo León.

    Esta clase crea empresas sintéticas con diferentes giros turísticos,
    asegurando la anonimización completa de los identificadores.
    """

    def __init__(self, num_empresas=100, seed=42):
        """
        Inicializar el generador de empresas.

        Parameters
        ----------
        num_empresas : int, default=100
            Número de empresas dummy a generar
        seed : int, default=42
            Semilla para reproducibilidad de los datos
        """
        self.num_empresas = num_empresas
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

        # Giros turísticos disponibles
        self.giros_turisticos = [
            'hotel', 'restaurante', 'agencia_viajes', 'evento',
            'transporte', 'atraccion_turistica', 'spa_wellness',
            'tour_operador', 'renta_vehiculos', 'comercio_souvenirs'
        ]

        # Distribución de empresas por giro (más realista)
        self.distribucion_giros = {
            'hotel': 0.20,
            'restaurante': 0.25,
            'agencia_viajes': 0.15,
            'evento': 0.10,
            'transporte': 0.08,
            'atraccion_turistica': 0.07,
            'spa_wellness': 0.05,
            'tour_operador': 0.04,
            'renta_vehiculos': 0.03,
            'comercio_souvenirs': 0.03
        }

    def _generar_id_anonimo(self, indice):
        """
        Generar un ID completamente anónimo e irreversible.

        Parameters
        ----------
        indice : int
            Índice de la empresa

        Returns
        -------
        str
            ID anónimo hasheado
        """
        # Crear un UUID único y hashearlo para anonimización completa
        uuid_empresa = str(uuid.uuid4())
        timestamp = str(datetime.now().timestamp())
        salt = f"cluster_turismo_nl_{indice}_{timestamp}"

        # Hash SHA-256 para anonimización irreversible
        hash_input = f"{uuid_empresa}_{salt}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()[:16]

    def _asignar_giro(self):
        """
        Asignar un giro turístico basado en la distribución realista.

        Returns
        -------
        str
            Giro turístico asignado
        """
        giros = list(self.distribucion_giros.keys())
        probabilidades = list(self.distribucion_giros.values())
        return np.random.choice(giros, p=probabilidades)

    def _generar_caracteristicas_empresa(self, giro):
        """
        Generar características específicas según el giro de la empresa.

        Parameters
        ----------
        giro : str
            Giro turístico de la empresa

        Returns
        -------
        dict
            Características de la empresa
        """
        caracteristicas = {
            'capacidad_base': 0,
            'precio_promedio_base': 0,
            'estacionalidad_factor': 1.0,
            'weekend_factor': 1.0
        }

        if giro == 'hotel':
            caracteristicas['capacidad_base'] = np.random.randint(20, 200)
            caracteristicas['precio_promedio_base'] = np.random.uniform(800, 3500)
            caracteristicas['estacionalidad_factor'] = 1.4  # Mayor demanda en vacaciones
            caracteristicas['weekend_factor'] = 1.2

        elif giro == 'restaurante':
            caracteristicas['capacidad_base'] = np.random.randint(30, 150)
            caracteristicas['precio_promedio_base'] = np.random.uniform(200, 800)
            caracteristicas['estacionalidad_factor'] = 1.2
            caracteristicas['weekend_factor'] = 1.6  # Mucho mayor en fines de semana

        elif giro == 'agencia_viajes':
            caracteristicas['capacidad_base'] = np.random.randint(50, 500)  # Clientes por mes
            caracteristicas['precio_promedio_base'] = np.random.uniform(2000, 15000)
            caracteristicas['estacionalidad_factor'] = 1.8  # Muy estacional
            caracteristicas['weekend_factor'] = 1.1

        elif giro == 'evento':
            caracteristicas['capacidad_base'] = np.random.randint(100, 2000)
            caracteristicas['precio_promedio_base'] = np.random.uniform(300, 1500)
            caracteristicas['estacionalidad_factor'] = 1.5  # Más eventos en verano
            caracteristicas['weekend_factor'] = 1.3

        else:  # Otros giros
            caracteristicas['capacidad_base'] = np.random.randint(20, 300)
            caracteristicas['precio_promedio_base'] = np.random.uniform(150, 2000)
            caracteristicas['estacionalidad_factor'] = np.random.uniform(1.1, 1.4)
            caracteristicas['weekend_factor'] = np.random.uniform(1.0, 1.3)

        return caracteristicas

    def generar_empresas(self):
        """
        Generar el conjunto completo de empresas dummy.

        Returns
        -------
        pd.DataFrame
            DataFrame con las empresas generadas
        """
        empresas = []

        for i in range(self.num_empresas):
            # ID completamente anónimo
            empresa_id = self._generar_id_anonimo(i)

            # Asignar giro
            giro = self._asignar_giro()

            # Generar características
            caracteristicas = self._generar_caracteristicas_empresa(giro)

            empresa = {
                'empresa_id': empresa_id,
                'giro': giro,
                'capacidad_base': caracteristicas['capacidad_base'],
                'precio_promedio_base': caracteristicas['precio_promedio_base'],
                'estacionalidad_factor': caracteristicas['estacionalidad_factor'],
                'weekend_factor': caracteristicas['weekend_factor'],
                'fecha_creacion': datetime.now().isoformat()
            }

            empresas.append(empresa)

        return pd.DataFrame(empresas)

    def guardar_empresas(self, ruta_archivo='data/datos_sinteticos/empresas_dummy.csv'):
        """
        Generar y guardar las empresas en un archivo CSV.

        Parameters
        ----------
        ruta_archivo : str, default='data/datos_sinteticos/empresas_dummy.csv'
            Ruta donde guardar el archivo

        Returns
        -------
        pd.DataFrame
            DataFrame con las empresas generadas
        """
        df_empresas = self.generar_empresas()
        df_empresas.to_csv(ruta_archivo, index=False)
        print(f"✅ Generadas {len(df_empresas)} empresas dummy guardadas en {ruta_archivo}")

        # Mostrar estadísticas
        print("\n📊 Distribución por giro:")
        distribucion = df_empresas['giro'].value_counts()
        for giro, cantidad in distribucion.items():
            print(f"  {giro}: {cantidad} empresas ({cantidad/len(df_empresas)*100:.1f}%)")

        return df_empresas


if __name__ == "__main__":
    # Generar empresas dummy
    generador = GeneradorEmpresas(num_empresas=100)
    empresas_df = generador.guardar_empresas()
