# ./src/api/federado.py

import numpy as np
import pandas as pd
import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import pickle

from src.api.models import ModeloFederado, MetricasEmpresa, ResultadoAgregado


class ProcesadorFederado:
    """
    Procesador de aprendizaje federado que agrega modelos de múltiples empresas
    sin acceder a sus datos crudos, garantizando privacidad completa.
    """

    def __init__(self):
        """
        Inicializar el procesador federado.
        """
        self.modelos_activos = {}
        self.contribuciones = {}
        self.metricas_agregadas = {}
        self.configuracion_privacidad = {
            "min_contribuciones": 3,  # Mínimo de empresas para agregar
            "ruido_diferencial": True,
            "epsilon": 1.0,  # Parámetro de privacidad diferencial
            "retencion_dias": 90
        }

        # Tipos de modelos soportados
        self.tipos_modelo_soportados = [
            "prediccion_demanda",
            "clasificacion_viajero",
            "optimizacion_precios",
            "deteccion_tendencias",
            "recomendacion_campanas"
        ]

    async def cargar_modelos_existentes(self):
        """
        Cargar modelos agregados existentes al iniciar el sistema.
        """
        directorio_modelos = "data/resultados/modelos"

        if not os.path.exists(directorio_modelos):
            return

        for archivo in os.listdir(directorio_modelos):
            if archivo.endswith('.json'):
                try:
                    with open(os.path.join(directorio_modelos, archivo), 'r') as f:
                        modelo_data = json.load(f)
                        tipo_modelo = modelo_data.get('tipo_modelo')
                        if tipo_modelo:
                            self.modelos_activos[tipo_modelo] = modelo_data
                            print(f"✅ Cargado modelo: {tipo_modelo}")
                except Exception as e:
                    print(f"⚠️ Error cargando modelo {archivo}: {e}")

    def validar_anonimizacion(self, modelo: ModeloFederado) -> bool:
        """
        Validar que el modelo esté correctamente anonimizado.

        Parameters
        ----------
        modelo : ModeloFederado
            Modelo a validar

        Returns
        -------
        bool
            True si el modelo cumple con los requisitos de anonimización
        """
        # Verificar que el hash del giro sea irreversible
        if len(modelo.giro_hash) < 16:
            return False

        # Verificar que no haya identificadores en los parámetros
        parametros_str = json.dumps(modelo.parametros, default=str).lower()
        identificadores_prohibidos = [
            'empresa', 'nombre', 'direccion', 'telefono', 'email',
            'rfc', 'razon_social', 'contacto'
        ]

        for identificador in identificadores_prohibidos:
            if identificador in parametros_str:
                return False

        # Verificar que haya suficientes muestras de entrenamiento
        if modelo.num_muestras_entrenamiento < 50:
            return False

        return True

    def validar_metricas_anonimas(self, metricas: MetricasEmpresa) -> bool:
        """
        Validar que las métricas estén correctamente anonimizadas.

        Parameters
        ----------
        metricas : MetricasEmpresa
            Métricas a validar

        Returns
        -------
        bool
            True si las métricas cumplen con los requisitos
        """
        # Verificar que el hash del giro sea válido
        if len(metricas.giro_hash) < 16:
            return False

        # Verificar que las métricas estén agregadas
        for clave, valor in metricas.metricas_agregadas.items():
            if isinstance(valor, (list, tuple)) and len(valor) < 10:
                return False

        return True

    async def procesar_modelo_anonimo(self, modelo: ModeloFederado, contribucion_id: str):
        """
        Procesar un modelo anónimo y agregarlo al conjunto federado.

        Parameters
        ----------
        modelo : ModeloFederado
            Modelo a procesar
        contribucion_id : str
            ID único de la contribución
        """
        try:
            # Registrar la contribución
            if modelo.tipo_modelo not in self.contribuciones:
                self.contribuciones[modelo.tipo_modelo] = []

            contribucion = {
                "id": contribucion_id,
                "timestamp": modelo.timestamp,
                "giro_hash": modelo.giro_hash,
                "parametros": modelo.parametros,
                "metricas": modelo.metricas_validacion,
                "num_muestras": modelo.num_muestras_entrenamiento
            }

            self.contribuciones[modelo.tipo_modelo].append(contribucion)

            # Si hay suficientes contribuciones, agregar modelo
            if len(self.contribuciones[modelo.tipo_modelo]) >= self.configuracion_privacidad["min_contribuciones"]:
                await self._agregar_modelo(modelo.tipo_modelo)

            # Guardar contribución de forma segura
            await self._guardar_contribucion_segura(contribucion_id, contribucion)

            print(f"✅ Procesada contribución {contribucion_id} para {modelo.tipo_modelo}")

        except Exception as e:
            print(f"❌ Error procesando modelo: {e}")
            raise

    async def _agregar_modelo(self, tipo_modelo: str):
        """
        Agregar múltiples contribuciones en un modelo federado.

        Parameters
        ----------
        tipo_modelo : str
            Tipo de modelo a agregar
        """
        contribuciones = self.contribuciones[tipo_modelo]

        if len(contribuciones) < self.configuracion_privacidad["min_contribuciones"]:
            return

        # Implementar agregación federada según el tipo de modelo
        if tipo_modelo == "prediccion_demanda":
            modelo_agregado = await self._agregar_modelo_prediccion(contribuciones)
        elif tipo_modelo == "clasificacion_viajero":
            modelo_agregado = await self._agregar_modelo_clasificacion(contribuciones)
        else:
            modelo_agregado = await self._agregar_modelo_generico(contribuciones)

        # Aplicar ruido diferencial si está habilitado
        if self.configuracion_privacidad["ruido_diferencial"]:
            modelo_agregado = self._aplicar_ruido_diferencial(modelo_agregado)

        # Guardar modelo agregado
        self.modelos_activos[tipo_modelo] = modelo_agregado
        await self._guardar_modelo_agregado(tipo_modelo, modelo_agregado)

        print(f"🔄 Modelo {tipo_modelo} agregado con {len(contribuciones)} contribuciones")

    async def _agregar_modelo_prediccion(self, contribuciones: List[Dict]) -> Dict:
        """
        Agregar modelos de predicción de demanda usando promedio ponderado.

        Parameters
        ----------
        contribuciones : List[Dict]
            Lista de contribuciones de modelos

        Returns
        -------
        Dict
            Modelo agregado
        """
        # Extraer parámetros de todos los modelos
        todos_parametros = []
        pesos = []

        for contrib in contribuciones:
            parametros = contrib["parametros"]
            peso = contrib["num_muestras"]  # Ponderar por número de muestras

            todos_parametros.append(parametros)
            pesos.append(peso)

        # Normalizar pesos
        pesos = np.array(pesos)
        pesos = pesos / np.sum(pesos)

        # Agregar parámetros usando promedio ponderado
        parametros_agregados = {}

        # Para modelos lineales, promediar coeficientes
        if "coeficientes" in todos_parametros[0]:
            coeficientes = []
            for i, params in enumerate(todos_parametros):
                coeficientes.append(np.array(params["coeficientes"]) * pesos[i])
            parametros_agregados["coeficientes"] = np.sum(coeficientes, axis=0).tolist()

        # Para modelos de ensemble, combinar árboles
        if "arboles" in todos_parametros[0]:
            # Seleccionar subset de árboles de cada contribución
            arboles_agregados = []
            for i, params in enumerate(todos_parametros):
                num_arboles = max(1, int(len(params["arboles"]) * pesos[i]))
                arboles_agregados.extend(params["arboles"][:num_arboles])
            parametros_agregados["arboles"] = arboles_agregados

        # Agregar métricas de validación
        metricas_agregadas = {}
        for metrica in ["mse", "r2", "mae"]:
            valores = [c["metricas"].get(metrica, 0) for c in contribuciones]
            metricas_agregadas[metrica] = float(np.average(valores, weights=pesos))

        return {
            "tipo_modelo": "prediccion_demanda",
            "parametros_agregados": parametros_agregados,
            "num_contribuciones": len(contribuciones),
            "metricas_agregadas": metricas_agregadas,
            "timestamp_agregacion": datetime.now().isoformat(),
            "confianza": self._calcular_confianza(contribuciones),
            "version": "1.0"
        }

    async def _agregar_modelo_clasificacion(self, contribuciones: List[Dict]) -> Dict:
        """
        Agregar modelos de clasificación de viajeros.

        Parameters
        ----------
        contribuciones : List[Dict]
            Lista de contribuciones

        Returns
        -------
        Dict
            Modelo agregado
        """
        # Implementación similar pero para clasificación
        pesos = [c["num_muestras"] for c in contribuciones]
        pesos = np.array(pesos) / np.sum(pesos)

        parametros_agregados = {}

        # Agregar matrices de confusión
        if "matriz_confusion" in contribuciones[0]["parametros"]:
            matrices = []
            for i, contrib in enumerate(contribuciones):
                matriz = np.array(contrib["parametros"]["matriz_confusion"])
                matrices.append(matriz * pesos[i])
            parametros_agregados["matriz_confusion"] = np.sum(matrices, axis=0).tolist()

        # Agregar probabilidades de clase
        if "probabilidades_clase" in contribuciones[0]["parametros"]:
            probs = []
            for i, contrib in enumerate(contribuciones):
                prob = np.array(contrib["parametros"]["probabilidades_clase"])
                probs.append(prob * pesos[i])
            parametros_agregados["probabilidades_clase"] = np.sum(probs, axis=0).tolist()

        metricas_agregadas = {}
        for metrica in ["accuracy", "precision", "recall", "f1"]:
            valores = [c["metricas"].get(metrica, 0) for c in contribuciones]
            metricas_agregadas[metrica] = float(np.average(valores, weights=pesos))

        return {
            "tipo_modelo": "clasificacion_viajero",
            "parametros_agregados": parametros_agregados,
            "num_contribuciones": len(contribuciones),
            "metricas_agregadas": metricas_agregadas,
            "timestamp_agregacion": datetime.now().isoformat(),
            "confianza": self._calcular_confianza(contribuciones),
            "version": "1.0"
        }

    async def _agregar_modelo_generico(self, contribuciones: List[Dict]) -> Dict:
        """
        Agregación genérica para otros tipos de modelos.

        Parameters
        ----------
        contribuciones : List[Dict]
            Lista de contribuciones

        Returns
        -------
        Dict
            Modelo agregado
        """
        pesos = [c["num_muestras"] for c in contribuciones]
        pesos = np.array(pesos) / np.sum(pesos)

        # Agregar parámetros numéricos usando promedio ponderado
        parametros_agregados = {}
        primer_modelo = contribuciones[0]["parametros"]

        for clave, valor in primer_modelo.items():
            if isinstance(valor, (int, float)):
                valores = [c["parametros"].get(clave, 0) for c in contribuciones]
                parametros_agregados[clave] = float(np.average(valores, weights=pesos))
            elif isinstance(valor, list) and all(isinstance(x, (int, float)) for x in valor):
                arrays = []
                for i, contrib in enumerate(contribuciones):
                    arr = np.array(contrib["parametros"].get(clave, []))
                    if len(arr) > 0:
                        arrays.append(arr * pesos[i])
                if arrays:
                    parametros_agregados[clave] = np.sum(arrays, axis=0).tolist()

        # Agregar métricas
        metricas_agregadas = {}
        if contribuciones[0]["metricas"]:
            for metrica in contribuciones[0]["metricas"].keys():
                valores = [c["metricas"].get(metrica, 0) for c in contribuciones]
                metricas_agregadas[metrica] = float(np.average(valores, weights=pesos))

        return {
            "tipo_modelo": "generico",
            "parametros_agregados": parametros_agregados,
            "num_contribuciones": len(contribuciones),
            "metricas_agregadas": metricas_agregadas,
            "timestamp_agregacion": datetime.now().isoformat(),
            "confianza": self._calcular_confianza(contribuciones),
            "version": "1.0"
        }

    def _aplicar_ruido_diferencial(self, modelo: Dict) -> Dict:
        """
        Aplicar ruido diferencial para mayor privacidad.

        Parameters
        ----------
        modelo : Dict
            Modelo a modificar

        Returns
        -------
        Dict
            Modelo con ruido diferencial aplicado
        """
        epsilon = self.configuracion_privacidad["epsilon"]

        # Aplicar ruido Laplaciano a parámetros numéricos
        for clave, valor in modelo["parametros_agregados"].items():
            if isinstance(valor, (int, float)):
                ruido = np.random.laplace(0, 1 / epsilon)
                modelo["parametros_agregados"][clave] = float(valor + ruido)
            elif isinstance(valor, list) and all(isinstance(x, (int, float)) for x in valor):
                ruido = np.random.laplace(0, 1 / epsilon, size=len(valor))
                modelo["parametros_agregados"][clave] = (np.array(valor) + ruido).tolist()

        return modelo

    def _calcular_confianza(self, contribuciones: List[Dict]) -> float:
        """
        Calcular nivel de confianza basado en número y calidad de contribuciones.

        Parameters
        ----------
        contribuciones : List[Dict]
            Lista de contribuciones

        Returns
        -------
        float
            Nivel de confianza entre 0 y 1
        """
        num_contribuciones = len(contribuciones)

        # Confianza base por número de contribuciones
        confianza_base = min(0.9, 0.3 + (num_contribuciones - 3) * 0.1)

        # Ajustar por calidad de métricas
        if contribuciones[0]["metricas"]:
            metricas_promedio = []
            for contrib in contribuciones:
                if "r2" in contrib["metricas"]:
                    metricas_promedio.append(contrib["metricas"]["r2"])
                elif "accuracy" in contrib["metricas"]:
                    metricas_promedio.append(contrib["metricas"]["accuracy"])

            if metricas_promedio:
                calidad_promedio = np.mean(metricas_promedio)
                confianza_base *= calidad_promedio

        return round(confianza_base, 3)

    async def obtener_modelo_agregado(self, tipo_modelo: str) -> Optional[ResultadoAgregado]:
        """
        Obtener el modelo agregado más reciente.

        Parameters
        ----------
        tipo_modelo : str
            Tipo de modelo solicitado

        Returns
        -------
        Optional[ResultadoAgregado]
            Modelo agregado o None si no existe
        """
        if tipo_modelo not in self.modelos_activos:
            return None

        modelo_data = self.modelos_activos[tipo_modelo]

        return ResultadoAgregado(
            tipo_modelo=modelo_data["tipo_modelo"],
            parametros_agregados=modelo_data["parametros_agregados"],
            num_contribuciones=modelo_data["num_contribuciones"],
            metricas_agregadas=modelo_data["metricas_agregadas"],
            timestamp_agregacion=modelo_data["timestamp_agregacion"],
            confianza=modelo_data["confianza"],
            version=modelo_data["version"]
        )

    async def procesar_metricas_anonimas(self, metricas: MetricasEmpresa) -> Dict:
        """
        Procesar métricas anónimas de una empresa.

        Parameters
        ----------
        metricas : MetricasEmpresa
            Métricas a procesar

        Returns
        -------
        Dict
            Resultado del procesamiento
        """
        # Generar ID único para las métricas
        metricas_id = hashlib.sha256(
            f"{metricas.timestamp_envio}_{metricas.giro_hash}".encode()
        ).hexdigest()[:16]

        # Agregar a métricas agregadas
        giro_hash = metricas.giro_hash
        if giro_hash not in self.metricas_agregadas:
            self.metricas_agregadas[giro_hash] = []

        self.metricas_agregadas[giro_hash].append({
            "id": metricas_id,
            "timestamp": metricas.timestamp_envio,
            "metricas": metricas.metricas_agregadas,
            "periodo": f"{metricas.periodo_inicio}_{metricas.periodo_fin}"
        })

        # Guardar métricas de forma segura
        await self._guardar_metricas_seguras(metricas_id, metricas)

        return {
            "id": metricas_id,
            "total_contribuciones": len(self.metricas_agregadas[giro_hash])
        }

    async def generar_predicciones_demanda(
        self,
        giro: str,
        fecha_inicio: str,
        fecha_fin: str,
        parametros_adicionales: Optional[Dict] = None
    ) -> Dict:
        """
        Generar predicciones de demanda usando modelos federados.

        Parameters
        ----------
        giro : str
            Giro turístico
        fecha_inicio : str
            Fecha de inicio
        fecha_fin : str
            Fecha de fin
        parametros_adicionales : Optional[Dict]
            Parámetros adicionales

        Returns
        -------
        Dict
            Predicciones generadas
        """
        # Verificar que hay modelo de predicción disponible
        if "prediccion_demanda" not in self.modelos_activos:
            raise ValueError("No hay modelo de predicción de demanda disponible")

        modelo = self.modelos_activos["prediccion_demanda"]

        # Generar predicciones sintéticas basadas en el modelo agregado
        fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
        predicciones = []

        for fecha in fechas:
            # Aplicar factores estacionales del modelo agregado
            factor_estacional = self._calcular_factor_estacional(fecha, giro)

            # Usar parámetros del modelo agregado
            if "coeficientes" in modelo["parametros_agregados"]:
                coefs = modelo["parametros_agregados"]["coeficientes"]
                prediccion_base = coefs[0] if coefs else 100
            else:
                prediccion_base = 100

            prediccion = prediccion_base * factor_estacional

            predicciones.append({
                "fecha": fecha.strftime('%Y-%m-%d'),
                "prediccion": round(prediccion, 2),
                "confianza": modelo["confianza"]
            })

        return {
            "giro": giro,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "predicciones": predicciones,
            "intervalos_confianza": self._calcular_intervalos_confianza(predicciones),
            "factores_influencia": self._obtener_factores_influencia(giro),
            "timestamp_generacion": datetime.now().isoformat()
        }

    async def calcular_tendencias(self, giro: str, periodo_meses: int) -> Dict:
        """
        Calcular tendencias históricas y proyecciones.

        Parameters
        ----------
        giro : str
            Giro turístico
        periodo_meses : int
            Período en meses

        Returns
        -------
        Dict
            Análisis de tendencias
        """
        # Cargar datos sintéticos para análisis
        try:
            ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
            ventas_giro = ventas_df[ventas_df['giro'] == giro]

            if len(ventas_giro) == 0:
                raise ValueError(f"No hay datos para el giro {giro}")

            # Calcular tendencias
            ventas_giro['fecha'] = pd.to_datetime(ventas_giro['fecha'])
            ventas_mensual = ventas_giro.groupby(ventas_giro['fecha'].dt.to_period('M'))['ingresos_totales'].sum()

            # Calcular tasa de crecimiento
            if len(ventas_mensual) > 1:
                tasa_crecimiento = (ventas_mensual.iloc[-1] / ventas_mensual.iloc[0]) ** (12 / len(ventas_mensual)) - 1
            else:
                tasa_crecimiento = 0

            # Detectar estacionalidad
            estacionalidad = {}
            for mes in range(1, 13):
                datos_mes = ventas_giro[ventas_giro['fecha'].dt.month == mes]['ingresos_totales']
                if len(datos_mes) > 0:
                    estacionalidad[f"mes_{mes}"] = float(datos_mes.mean() / ventas_giro['ingresos_totales'].mean())

            return {
                "giro": giro,
                "periodo_analisis": f"{periodo_meses} meses",
                "tendencia_general": "creciente" if tasa_crecimiento > 0.02 else "estable" if tasa_crecimiento > -0.02 else "decreciente",
                "tasa_crecimiento_anual": round(tasa_crecimiento * 100, 2),
                "estacionalidad": estacionalidad,
                "proyecciones": self._generar_proyecciones(ventas_mensual, 6),
                "confianza_proyeccion": 0.75
            }

        except Exception as e:
            raise ValueError(f"Error calculando tendencias: {e}")

    def _calcular_factor_estacional(self, fecha: pd.Timestamp, giro: str) -> float:
        """Calcular factor estacional para una fecha y giro."""
        mes = fecha.month
        factores = {
            'hotel': {1: 0.7, 2: 0.6, 3: 0.8, 4: 1.2, 5: 1.1, 6: 1.5, 7: 1.8, 8: 1.7, 9: 1.2, 10: 1.0, 11: 0.8, 12: 1.4},
            'restaurante': {1: 0.8, 2: 0.7, 3: 0.9, 4: 1.1, 5: 1.2, 6: 1.3, 7: 1.4, 8: 1.3, 9: 1.2, 10: 1.1, 11: 1.0, 12: 1.5}
        }
        return factores.get(giro, {mes: 1.0 for mes in range(1, 13)})[mes]

    def _calcular_intervalos_confianza(self, predicciones: List[Dict]) -> List[Dict]:
        """Calcular intervalos de confianza para predicciones."""
        intervalos = []
        for pred in predicciones:
            valor = pred["prediccion"]
            margen = valor * 0.15  # 15% de margen
            intervalos.append({
                "fecha": pred["fecha"],
                "limite_inferior": round(valor - margen, 2),
                "limite_superior": round(valor + margen, 2)
            })
        return intervalos

    def _obtener_factores_influencia(self, giro: str) -> Dict[str, float]:
        """Obtener factores que influyen en la predicción."""
        factores_base = {
            "estacionalidad": 0.4,
            "tendencia_historica": 0.3,
            "eventos_especiales": 0.2,
            "factores_economicos": 0.1
        }
        return factores_base

    def _generar_proyecciones(self, datos_historicos: pd.Series, meses_futuro: int) -> List[Dict]:
        """Generar proyecciones futuras."""
        proyecciones = []
        ultimo_valor = datos_historicos.iloc[-1] if len(datos_historicos) > 0 else 1000

        for i in range(1, meses_futuro + 1):
            # Proyección simple con crecimiento lineal
            proyeccion = ultimo_valor * (1 + 0.02 * i)  # 2% crecimiento mensual
            proyecciones.append({
                "mes": i,
                "proyeccion": round(proyeccion, 2),
                "confianza": max(0.5, 0.9 - i * 0.05)  # Confianza decrece con el tiempo
            })

        return proyecciones

    async def _guardar_contribucion_segura(self, contribucion_id: str, contribucion: Dict):
        """Guardar contribución de forma segura."""
        ruta = f"data/resultados/contribuciones/{contribucion_id}.json"
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        # Remover información sensible antes de guardar
        contribucion_segura = {
            "id": contribucion_id,
            "timestamp": contribucion["timestamp"],
            "tipo_modelo": contribucion.get("tipo_modelo", "unknown"),
            "num_parametros": len(contribucion["parametros"]) if "parametros" in contribucion else 0,
            "metricas_validacion": contribucion.get("metricas", {}),
            "num_muestras": contribucion.get("num_muestras", 0)
        }

        with open(ruta, 'w') as f:
            json.dump(contribucion_segura, f, indent=2)

    async def _guardar_modelo_agregado(self, tipo_modelo: str, modelo: Dict):
        """Guardar modelo agregado."""
        ruta = f"data/resultados/modelos/{tipo_modelo}_agregado.json"
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        with open(ruta, 'w') as f:
            json.dump(modelo, f, indent=2)

    async def _guardar_metricas_seguras(self, metricas_id: str, metricas: MetricasEmpresa):
        """Guardar métricas de forma segura."""
        ruta = f"data/resultados/metricas/{metricas_id}.json"
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        metricas_seguras = {
            "id": metricas_id,
            "timestamp": metricas.timestamp_envio,
            "periodo": f"{metricas.periodo_inicio}_{metricas.periodo_fin}",
            "num_metricas": len(metricas.metricas_agregadas),
            "giro_hash": metricas.giro_hash[:8] + "..."  # Solo primeros 8 caracteres
        }

        with open(ruta, 'w') as f:
            json.dump(metricas_seguras, f, indent=2)
