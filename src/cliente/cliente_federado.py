# ./src/cliente/cliente_federado.py

import pandas as pd
import numpy as np
import requests
import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import pickle


class ClienteFederado:
    """
    Cliente federado que simula una empresa del clúster turístico.

    Este cliente:
    1. Carga sus datos locales (sintéticos)
    2. Entrena modelos localmente
    3. Anonimiza completamente los parámetros del modelo
    4. Envía solo parámetros agregados a la API federada
    5. Nunca comparte datos crudos
    """

    def __init__(self, empresa_id: str, giro: str, api_url: str = "http://localhost:8000"):
        """
        Inicializar cliente federado para una empresa.

        Parameters
        ----------
        empresa_id : str
            ID de la empresa (será anonimizado)
        giro : str
            Giro turístico de la empresa
        api_url : str
            URL de la API federada
        """
        self.empresa_id = empresa_id
        self.giro = giro
        self.api_url = api_url

        # Generar hash irreversible del giro para anonimización
        self.giro_hash = self._generar_hash_anonimo(f"{giro}_{empresa_id}")

        # Configuración de privacidad
        self.configuracion_privacidad = {
            "min_muestras_entrenamiento": 100,
            "ruido_local": True,
            "agregacion_local": True,
            "validacion_anonimizacion": True
        }

        # Datos locales (cargados de forma segura)
        self.datos_locales = None
        self.modelos_entrenados = {}
        self.ruta_datos = None  # Ruta personalizada para datos de empresa

        print(f"🏢 Cliente federado inicializado")
        print(f"   Giro: {giro}")
        print(f"   Hash anónimo: {self.giro_hash}")
        print(f"   API: {api_url}")

    def _generar_hash_anonimo(self, texto: str) -> str:
        """
        Generar hash completamente anónimo e irreversible.

        Parameters
        ----------
        texto : str
            Texto a hashear

        Returns
        -------
        str
            Hash anónimo
        """
        # Usar múltiples capas de hash con salt único
        salt = f"cluster_turismo_nl_{datetime.now().timestamp()}"
        hash_input = f"{texto}_{salt}".encode('utf-8')

        # Hash SHA-256 con múltiples iteraciones
        hash_resultado = hashlib.sha256(hash_input).hexdigest()
        for _ in range(1000):  # 1000 iteraciones para mayor seguridad
            hash_resultado = hashlib.sha256(hash_resultado.encode()).hexdigest()

        return hash_resultado[:32]  # Primeros 32 caracteres

    def cargar_datos_locales(self):
        """
        Cargar datos locales de la empresa de forma segura.

        En un escenario real, estos datos nunca saldrían de la empresa.
        """
        try:
            # Si hay ruta personalizada, usar datos de la empresa
            if self.ruta_datos:
                return self._cargar_datos_empresa()

            # Cargar datos sintéticos filtrados por empresa (modo demo)
            ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
            eventos_df = pd.read_csv('data/datos_sinteticos/eventos_dummy.csv')

            # Filtrar datos de esta empresa específica
            datos_empresa = ventas_df[ventas_df['empresa_id'] == self.empresa_id].copy()

            if len(datos_empresa) == 0:
                print(f"⚠️ No se encontraron datos para la empresa {self.empresa_id}")
                return False

            # Preparar datos para entrenamiento
            datos_empresa['fecha'] = pd.to_datetime(datos_empresa['fecha'])
            datos_empresa['mes'] = datos_empresa['fecha'].dt.month
            datos_empresa['dia_semana'] = datos_empresa['fecha'].dt.dayofweek
            datos_empresa['es_fin_semana'] = datos_empresa['es_fin_semana'].astype(int)

            self.datos_locales = datos_empresa

            print(f"✅ Datos locales cargados: {len(datos_empresa)} registros")
            print(f"   Período: {datos_empresa['fecha'].min()} a {datos_empresa['fecha'].max()}")
            print(f"   Ingresos totales: ${datos_empresa['ingresos_totales'].sum():,.0f}")

            return True

        except Exception as e:
            print(f"❌ Error cargando datos locales: {e}")
            return False

    def _cargar_datos_empresa(self):
        """
        Cargar datos reales de la empresa desde archivos CSV.

        Returns
        -------
        bool
            True si se cargaron exitosamente
        """
        try:
            # Buscar archivos CSV en la ruta de datos
            archivos_csv = []
            for archivo in os.listdir(self.ruta_datos):
                if archivo.endswith('.csv'):
                    archivos_csv.append(os.path.join(self.ruta_datos, archivo))

            if not archivos_csv:
                print(f"❌ No se encontraron archivos CSV en: {self.ruta_datos}")
                return False

            # Cargar y combinar todos los archivos CSV
            datos_combinados = []
            for archivo in archivos_csv:
                df = pd.read_csv(archivo)
                datos_combinados.append(df)

            # Combinar todos los DataFrames
            datos_empresa = pd.concat(datos_combinados, ignore_index=True)

            # Preparar datos para entrenamiento
            datos_empresa['fecha'] = pd.to_datetime(datos_empresa['fecha'])
            datos_empresa['mes'] = datos_empresa['fecha'].dt.month
            datos_empresa['dia_semana'] = datos_empresa['fecha'].dt.dayofweek

            # Crear columna es_fin_semana si no existe
            if 'es_fin_semana' not in datos_empresa.columns:
                datos_empresa['es_fin_semana'] = (datos_empresa['dia_semana'] >= 5).astype(int)

            # Crear factor estacional si no existe
            if 'factor_estacional' not in datos_empresa.columns:
                # Factor estacional simple basado en el mes
                factores_mes = {1: 0.8, 2: 0.7, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.3,
                                7: 1.5, 8: 1.4, 9: 1.1, 10: 1.0, 11: 0.9, 12: 1.2}
                datos_empresa['factor_estacional'] = datos_empresa['mes'].map(factores_mes)

            # Mapear columnas según el giro
            if self.giro == 'hotel':
                # Para hoteles, usar ocupacion como proxy de numero_clientes si no existe
                if 'numero_clientes' not in datos_empresa.columns and 'ocupacion' in datos_empresa.columns:
                    # Estimar clientes basado en ocupación (asumiendo capacidad promedio)
                    datos_empresa['numero_clientes'] = (datos_empresa['ocupacion'] * 0.6).round().astype(int)

            # Verificar columnas requeridas
            columnas_requeridas = ['fecha', 'ingresos', 'numero_clientes']
            for col in columnas_requeridas:
                if col not in datos_empresa.columns:
                    print(f"❌ Columna requerida '{col}' no encontrada en los datos")
                    return False

            self.datos_locales = datos_empresa

            print(f"✅ Datos de empresa cargados: {len(datos_empresa)} registros")
            print(f"   Período: {datos_empresa['fecha'].min()} a {datos_empresa['fecha'].max()}")
            print(f"   Ingresos totales: ${datos_empresa['ingresos'].sum():,.0f}")
            print(f"   Archivos procesados: {len(archivos_csv)}")

            return True

        except Exception as e:
            print(f"❌ Error cargando datos de empresa: {e}")
            return False

    def entrenar_modelo_prediccion_demanda(self) -> Dict:
        """
        Entrenar modelo de predicción de demanda localmente.

        Returns
        -------
        Dict
            Parámetros del modelo entrenado (anonimizados)
        """
        if self.datos_locales is None:
            raise ValueError("Primero debe cargar los datos locales")

        print("🤖 Entrenando modelo de predicción de demanda...")

        # Preparar características para el modelo
        caracteristicas = ['mes', 'dia_semana', 'es_fin_semana', 'factor_estacional']
        objetivo = 'numero_clientes'

        # Verificar que tenemos suficientes datos
        if len(self.datos_locales) < self.configuracion_privacidad["min_muestras_entrenamiento"]:
            raise ValueError(f"Datos insuficientes para entrenamiento seguro (mínimo {self.configuracion_privacidad['min_muestras_entrenamiento']})")

        # Preparar datos
        X = self.datos_locales[caracteristicas].copy()
        y = self.datos_locales[objetivo].copy()

        # Dividir en entrenamiento y validación
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Entrenar modelo Random Forest
        modelo_rf = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        modelo_rf.fit(X_train, y_train)

        # Validar modelo
        y_pred = modelo_rf.predict(X_test)
        metricas_validacion = {
            "mse": float(mean_squared_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
            "mae": float(mean_absolute_error(y_test, y_pred))
        }

        # Extraer parámetros del modelo de forma anonimizada
        parametros_anonimizados = self._extraer_parametros_anonimos_rf(modelo_rf)

        # Aplicar ruido local si está habilitado
        if self.configuracion_privacidad["ruido_local"]:
            parametros_anonimizados = self._aplicar_ruido_local(parametros_anonimizados)

        modelo_federado = {
            "tipo_modelo": "prediccion_demanda",
            "parametros": parametros_anonimizados,
            "giro_hash": self.giro_hash,
            "timestamp": datetime.now().isoformat(),
            "metricas_validacion": metricas_validacion,
            "version_algoritmo": "1.0",
            "num_muestras_entrenamiento": len(X_train)
        }

        # Guardar modelo localmente
        self.modelos_entrenados["prediccion_demanda"] = modelo_federado

        print(f"✅ Modelo entrenado exitosamente")
        print(f"   R² Score: {metricas_validacion['r2']:.3f}")
        print(f"   MAE: {metricas_validacion['mae']:.2f}")
        print(f"   Muestras entrenamiento: {len(X_train)}")

        return modelo_federado

    def entrenar_modelo_clasificacion_viajero(self) -> Dict:
        """
        Entrenar modelo de clasificación de tipo de viajero.

        Returns
        -------
        Dict
            Parámetros del modelo entrenado (anonimizados)
        """
        print("🎯 Entrenando modelo de clasificación de viajero...")

        try:
            # Cargar datos de perfiles de viajeros
            perfiles_df = pd.read_csv('data/datos_sinteticos/perfil_viajero_dummy.csv')

            # Simular datos locales de la empresa (agregados)
            # En realidad, cada empresa tendría sus propios datos de clientes
            datos_simulados = perfiles_df.sample(
                min(500, len(perfiles_df)),
                random_state=hash(self.empresa_id) % 1000
            ).copy()

            # Preparar características
            caracteristicas = ['edad', 'tamaño_grupo', 'duracion_estancia', 'gasto_total']
            objetivo = 'tipo_viajero'

            X = datos_simulados[caracteristicas].copy()
            y = datos_simulados[objetivo].copy()

            # Codificar variables categóricas
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)

            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42
            )

            # Entrenar modelo
            from sklearn.ensemble import RandomForestClassifier
            modelo_clf = RandomForestClassifier(
                n_estimators=30,
                max_depth=8,
                random_state=42
            )
            modelo_clf.fit(X_train, y_train)

            # Validar
            y_pred = modelo_clf.predict(X_test)
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

            metricas_validacion = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred, average='weighted')),
                "recall": float(recall_score(y_test, y_pred, average='weighted')),
                "f1": float(f1_score(y_test, y_pred, average='weighted'))
            }

            # Extraer parámetros anonimizados
            parametros_anonimizados = self._extraer_parametros_anonimos_clf(modelo_clf, le)

            modelo_federado = {
                "tipo_modelo": "clasificacion_viajero",
                "parametros": parametros_anonimizados,
                "giro_hash": self.giro_hash,
                "timestamp": datetime.now().isoformat(),
                "metricas_validacion": metricas_validacion,
                "version_algoritmo": "1.0",
                "num_muestras_entrenamiento": len(X_train)
            }

            self.modelos_entrenados["clasificacion_viajero"] = modelo_federado

            print(f"✅ Modelo de clasificación entrenado")
            print(f"   Accuracy: {metricas_validacion['accuracy']:.3f}")
            print(f"   F1-Score: {metricas_validacion['f1']:.3f}")

            return modelo_federado

        except Exception as e:
            print(f"❌ Error entrenando modelo de clasificación: {e}")
            return {}

    def _extraer_parametros_anonimos_rf(self, modelo_rf: RandomForestRegressor) -> Dict:
        """
        Extraer parámetros del Random Forest de forma anónima.

        Parameters
        ----------
        modelo_rf : RandomForestRegressor
            Modelo entrenado

        Returns
        -------
        Dict
            Parámetros anonimizados
        """
        # Extraer información agregada de los árboles
        importancias = modelo_rf.feature_importances_.tolist()

        # Extraer estadísticas agregadas de los árboles (sin estructura completa)
        profundidades = [arbol.tree_.max_depth for arbol in modelo_rf.estimators_]
        num_nodos = [arbol.tree_.node_count for arbol in modelo_rf.estimators_]

        # Parámetros agregados (no revelan datos individuales)
        parametros = {
            "importancias_caracteristicas": importancias,
            "profundidad_promedio": float(np.mean(profundidades)),
            "profundidad_std": float(np.std(profundidades)),
            "nodos_promedio": float(np.mean(num_nodos)),
            "nodos_std": float(np.std(num_nodos)),
            "num_arboles": len(modelo_rf.estimators_),
            "parametros_modelo": {
                "max_depth": modelo_rf.max_depth,
                "n_estimators": modelo_rf.n_estimators,
                "min_samples_split": modelo_rf.min_samples_split,
                "min_samples_leaf": modelo_rf.min_samples_leaf
            }
        }

        return parametros

    def _extraer_parametros_anonimos_clf(self, modelo_clf, label_encoder) -> Dict:
        """
        Extraer parámetros del clasificador de forma anónima.

        Parameters
        ----------
        modelo_clf : RandomForestClassifier
            Modelo entrenado
        label_encoder : LabelEncoder
            Codificador de etiquetas

        Returns
        -------
        Dict
            Parámetros anonimizados
        """
        # Importancias de características
        importancias = modelo_clf.feature_importances_.tolist()

        # Probabilidades de clase agregadas
        clases = label_encoder.classes_
        num_clases = len(clases)

        # Estadísticas agregadas
        profundidades = [arbol.tree_.max_depth for arbol in modelo_clf.estimators_]

        parametros = {
            "importancias_caracteristicas": importancias,
            "num_clases": num_clases,
            "profundidad_promedio": float(np.mean(profundidades)),
            "num_arboles": len(modelo_clf.estimators_),
            "parametros_modelo": {
                "max_depth": modelo_clf.max_depth,
                "n_estimators": modelo_clf.n_estimators
            }
        }

        return parametros

    def _aplicar_ruido_local(self, parametros: Dict) -> Dict:
        """
        Aplicar ruido local para mayor privacidad.

        Parameters
        ----------
        parametros : Dict
            Parámetros originales

        Returns
        -------
        Dict
            Parámetros con ruido aplicado
        """
        parametros_con_ruido = parametros.copy()

        # Aplicar ruido gaussiano a valores numéricos
        for clave, valor in parametros.items():
            if isinstance(valor, (int, float)):
                ruido = np.random.normal(0, abs(valor) * 0.01)  # 1% de ruido
                parametros_con_ruido[clave] = float(valor + ruido)
            elif isinstance(valor, list) and all(isinstance(x, (int, float)) for x in valor):
                ruido = np.random.normal(0, np.std(valor) * 0.01, len(valor))
                parametros_con_ruido[clave] = (np.array(valor) + ruido).tolist()

        return parametros_con_ruido

    def generar_metricas_agregadas(self, periodo_dias: int = 30) -> Dict:
        """
        Generar métricas agregadas de la empresa.

        Parameters
        ----------
        periodo_dias : int
            Período en días para agregar métricas

        Returns
        -------
        Dict
            Métricas agregadas anonimizadas
        """
        if self.datos_locales is None:
            raise ValueError("Primero debe cargar los datos locales")

        print(f"📊 Generando métricas agregadas para {periodo_dias} días...")

        # Filtrar datos del período
        fecha_fin = self.datos_locales['fecha'].max()
        fecha_inicio = fecha_fin - timedelta(days=periodo_dias)

        datos_periodo = self.datos_locales[
            (self.datos_locales['fecha'] >= fecha_inicio) &
            (self.datos_locales['fecha'] <= fecha_fin)
        ].copy()

        if len(datos_periodo) < 10:
            raise ValueError("Datos insuficientes para generar métricas agregadas")

        # Calcular métricas agregadas (sin revelar transacciones individuales)
        metricas_agregadas = {
            "ingresos_promedio_diario": float(datos_periodo['ingresos_totales'].mean()),
            "ingresos_mediana_diaria": float(datos_periodo['ingresos_totales'].median()),
            "clientes_promedio_diario": float(datos_periodo['numero_clientes'].mean()),
            "precio_promedio": float(datos_periodo['precio_promedio'].mean()),
            "dias_con_ventas": int(len(datos_periodo)),
            "variabilidad_ingresos": float(datos_periodo['ingresos_totales'].std()),
            "percentil_75_ingresos": float(datos_periodo['ingresos_totales'].quantile(0.75)),
            "percentil_25_ingresos": float(datos_periodo['ingresos_totales'].quantile(0.25))
        }

        # Aplicar agregación adicional para mayor privacidad
        if self.configuracion_privacidad["agregacion_local"]:
            # Redondear valores para reducir precisión
            for clave, valor in metricas_agregadas.items():
                if isinstance(valor, float):
                    metricas_agregadas[clave] = round(valor, 0)  # Sin decimales

        metricas_empresa = {
            "giro_hash": self.giro_hash,
            "periodo_inicio": fecha_inicio.strftime('%Y-%m-%d'),
            "periodo_fin": fecha_fin.strftime('%Y-%m-%d'),
            "metricas_agregadas": metricas_agregadas,
            "timestamp_envio": datetime.now().isoformat(),
            "ingresos_promedio_diario": metricas_agregadas["ingresos_promedio_diario"],
            "clientes_promedio_diario": metricas_agregadas["clientes_promedio_diario"],
            "precio_promedio": metricas_agregadas["precio_promedio"]
        }

        print(f"✅ Métricas agregadas generadas")
        print(f"   Período: {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")
        print(f"   Ingresos promedio diario: ${metricas_agregadas['ingresos_promedio_diario']:,.0f}")
        print(f"   Clientes promedio diario: {metricas_agregadas['clientes_promedio_diario']:.0f}")

        return metricas_empresa

    def enviar_modelo_a_api(self, tipo_modelo: str) -> bool:
        """
        Enviar modelo entrenado a la API federada.

        Parameters
        ----------
        tipo_modelo : str
            Tipo de modelo a enviar

        Returns
        -------
        bool
            True si el envío fue exitoso
        """
        if tipo_modelo not in self.modelos_entrenados:
            print(f"❌ Modelo {tipo_modelo} no encontrado. Primero debe entrenarlo.")
            return False

        modelo = self.modelos_entrenados[tipo_modelo]

        # Validar anonimización antes del envío
        if self.configuracion_privacidad["validacion_anonimizacion"]:
            if not self._validar_anonimizacion_modelo(modelo):
                print("❌ El modelo no pasó la validación de anonimización")
                return False

        try:
            print(f"📤 Enviando modelo {tipo_modelo} a la API federada...")

            response = requests.post(
                f"{self.api_url}/federated/submit-model",
                json=modelo,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                resultado = response.json()
                print(f"✅ Modelo enviado exitosamente")
                print(f"   ID contribución: {resultado.get('contribucion_id')}")
                print(f"   Status: {resultado.get('status')}")
                return True
            else:
                print(f"❌ Error enviando modelo: {response.status_code}")
                print(f"   Detalle: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def enviar_metricas_a_api(self, metricas: Dict) -> bool:
        """
        Enviar métricas agregadas a la API federada.

        Parameters
        ----------
        metricas : Dict
            Métricas a enviar

        Returns
        -------
        bool
            True si el envío fue exitoso
        """
        try:
            print("📤 Enviando métricas agregadas a la API federada...")

            response = requests.post(
                f"{self.api_url}/federated/submit-metrics",
                json=metricas,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                resultado = response.json()
                print(f"✅ Métricas enviadas exitosamente")
                print(f"   ID métricas: {resultado.get('metricas_id')}")
                print(f"   Total contribuciones: {resultado.get('contribuciones_totales')}")
                return True
            else:
                print(f"❌ Error enviando métricas: {response.status_code}")
                print(f"   Detalle: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def consultar_modelo_agregado(self, tipo_modelo: str) -> Optional[Dict]:
        """
        Consultar modelo agregado desde la API.

        Parameters
        ----------
        tipo_modelo : str
            Tipo de modelo a consultar

        Returns
        -------
        Optional[Dict]
            Modelo agregado o None si no está disponible
        """
        try:
            print(f"📥 Consultando modelo agregado: {tipo_modelo}")

            response = requests.get(
                f"{self.api_url}/federated/get-aggregated/{tipo_modelo}",
                timeout=30
            )

            if response.status_code == 200:
                modelo_agregado = response.json()
                print(f"✅ Modelo agregado obtenido")
                print(f"   Contribuciones: {modelo_agregado.get('num_contribuciones')}")
                print(f"   Confianza: {modelo_agregado.get('confianza')}")
                print(f"   Versión: {modelo_agregado.get('version')}")
                return modelo_agregado
            elif response.status_code == 404:
                print(f"⚠️ Modelo {tipo_modelo} no disponible aún")
                return None
            else:
                print(f"❌ Error consultando modelo: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def _validar_anonimizacion_modelo(self, modelo: Dict) -> bool:
        """
        Validar que el modelo esté correctamente anonimizado.

        Parameters
        ----------
        modelo : Dict
            Modelo a validar

        Returns
        -------
        bool
            True si el modelo está correctamente anonimizado
        """
        # Verificar que no haya identificadores en los parámetros
        parametros_str = json.dumps(modelo["parametros"], default=str).lower()

        identificadores_prohibidos = [
            self.empresa_id.lower(),
            'empresa', 'nombre', 'direccion', 'telefono', 'email'
        ]

        for identificador in identificadores_prohibidos:
            if identificador in parametros_str:
                print(f"⚠️ Identificador prohibido encontrado: {identificador}")
                return False

        # Verificar que el hash del giro sea correcto
        if modelo["giro_hash"] != self.giro_hash:
            print("⚠️ Hash del giro no coincide")
            return False

        # Verificar que haya suficientes muestras
        if modelo["num_muestras_entrenamiento"] < self.configuracion_privacidad["min_muestras_entrenamiento"]:
            print("⚠️ Insuficientes muestras de entrenamiento")
            return False

        return True

    def ejecutar_flujo_completo(self):
        """
        Ejecutar el flujo completo del cliente federado.

        1. Cargar datos locales
        2. Entrenar modelos
        3. Generar métricas
        4. Enviar todo a la API
        5. Consultar resultados agregados
        """
        print("🚀 Iniciando flujo completo del cliente federado")
        print("=" * 60)

        # 1. Cargar datos locales
        if not self.cargar_datos_locales():
            print("❌ No se pudieron cargar los datos locales")
            return False

        # 2. Entrenar modelos
        try:
            modelo_prediccion = self.entrenar_modelo_prediccion_demanda()
            modelo_clasificacion = self.entrenar_modelo_clasificacion_viajero()
        except Exception as e:
            print(f"❌ Error entrenando modelos: {e}")
            return False

        # 3. Generar métricas agregadas
        try:
            metricas = self.generar_metricas_agregadas()
        except Exception as e:
            print(f"❌ Error generando métricas: {e}")
            return False

        # 4. Enviar a la API (simular que la API está disponible)
        print("\n📡 Simulando envío a API federada...")
        print("   (En producción, aquí se enviarían los datos a la API real)")

        # Guardar resultados localmente para demostración
        self._guardar_resultados_locales(modelo_prediccion, modelo_clasificacion, metricas)

        print("\n✅ Flujo completo ejecutado exitosamente")
        return True

    def _guardar_resultados_locales(self, modelo_prediccion: Dict, modelo_clasificacion: Dict, metricas: Dict):
        """
        Guardar resultados localmente para demostración.

        Parameters
        ----------
        modelo_prediccion : Dict
            Modelo de predicción entrenado
        modelo_clasificacion : Dict
            Modelo de clasificación entrenado
        metricas : Dict
            Métricas agregadas
        """
        # Crear directorio para resultados del cliente
        directorio_cliente = f"data/resultados/cliente_{self.giro_hash[:8]}"
        os.makedirs(directorio_cliente, exist_ok=True)

        # Guardar modelos
        with open(f"{directorio_cliente}/modelo_prediccion.json", 'w') as f:
            json.dump(modelo_prediccion, f, indent=2)

        with open(f"{directorio_cliente}/modelo_clasificacion.json", 'w') as f:
            json.dump(modelo_clasificacion, f, indent=2)

        # Guardar métricas
        with open(f"{directorio_cliente}/metricas_agregadas.json", 'w') as f:
            json.dump(metricas, f, indent=2)

        # Crear resumen
        resumen = {
            "empresa_hash": self.giro_hash[:8] + "...",
            "giro": self.giro,
            "timestamp": datetime.now().isoformat(),
            "modelos_entrenados": ["prediccion_demanda", "clasificacion_viajero"],
            "metricas_generadas": True,
            "datos_anonimizados": True,
            "privacidad_garantizada": True
        }

        with open(f"{directorio_cliente}/resumen_contribucion.json", 'w') as f:
            json.dump(resumen, f, indent=2)

        print(f"💾 Resultados guardados en: {directorio_cliente}")


if __name__ == "__main__":
    # Ejemplo de uso del cliente federado

    # Cargar una empresa de ejemplo
    try:
        empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')
        empresa_ejemplo = empresas_df.iloc[0]

        # Crear cliente federado
        cliente = ClienteFederado(
            empresa_id=empresa_ejemplo['empresa_id'],
            giro=empresa_ejemplo['giro'],
            api_url="http://localhost:8000"
        )

        # Ejecutar flujo completo
        cliente.ejecutar_flujo_completo()

    except FileNotFoundError:
        print("❌ Error: Primero ejecuta generador_empresas.py para crear las empresas dummy")
