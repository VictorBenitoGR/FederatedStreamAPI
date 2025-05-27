import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import sqlite3
from pathlib import Path

from src.api.models import ConsultaMetricas


class AlmacenResultados:
    """
    Sistema de almacenamiento seguro para resultados agregados.

    Maneja el almacenamiento de métricas, modelos y resultados de forma
    que garantiza la privacidad y permite consultas eficientes.
    """

    def __init__(self, directorio_base: str = "data/resultados"):
        """
        Inicializar el almacén de resultados.

        Parameters
        ----------
        directorio_base : str
            Directorio base para almacenar resultados
        """
        self.directorio_base = Path(directorio_base)
        self.directorio_base.mkdir(parents=True, exist_ok=True)

        # Crear subdirectorios
        (self.directorio_base / "metricas").mkdir(exist_ok=True)
        (self.directorio_base / "modelos").mkdir(exist_ok=True)
        (self.directorio_base / "contribuciones").mkdir(exist_ok=True)
        (self.directorio_base / "predicciones").mkdir(exist_ok=True)
        (self.directorio_base / "exportaciones").mkdir(exist_ok=True)

        # Inicializar base de datos SQLite para consultas rápidas
        self.db_path = self.directorio_base / "metricas_agregadas.db"
        self._inicializar_db()

    def _inicializar_db(self):
        """
        Inicializar la base de datos SQLite para métricas agregadas.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabla para métricas agregadas por giro
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metricas_giro (
                    id TEXT PRIMARY KEY,
                    giro_hash TEXT NOT NULL,
                    fecha DATE NOT NULL,
                    ingresos_promedio REAL,
                    clientes_promedio REAL,
                    ocupacion_promedio REAL,
                    precio_promedio REAL,
                    num_contribuciones INTEGER,
                    timestamp_agregacion TEXT
                )
            """)

            # Tabla para métricas generales del clúster
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metricas_generales (
                    id TEXT PRIMARY KEY,
                    fecha DATE NOT NULL,
                    total_ingresos REAL,
                    total_clientes INTEGER,
                    ocupacion_promedio_cluster REAL,
                    num_empresas_activas INTEGER,
                    timestamp_calculo TEXT
                )
            """)

            # Tabla para consultas realizadas (auditoría)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_consultas (
                    id TEXT PRIMARY KEY,
                    tipo_consulta TEXT NOT NULL,
                    parametros_hash TEXT,
                    timestamp_consulta TEXT,
                    resultado_hash TEXT
                )
            """)

            # Índices para consultas eficientes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metricas_giro_fecha ON metricas_giro(fecha)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metricas_giro_hash ON metricas_giro(giro_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metricas_generales_fecha ON metricas_generales(fecha)")

            conn.commit()

    async def guardar_metadatos_contribucion(self, contribucion_id: str, metadatos: Dict):
        """
        Guardar metadatos de una contribución (sin datos sensibles).

        Parameters
        ----------
        contribucion_id : str
            ID único de la contribución
        metadatos : Dict
            Metadatos a guardar
        """
        ruta = self.directorio_base / "contribuciones" / f"{contribucion_id}_meta.json"

        metadatos_seguros = {
            "id": contribucion_id,
            "timestamp": metadatos.get("timestamp"),
            "tipo_modelo": metadatos.get("tipo_modelo"),
            "giro_hash_parcial": metadatos.get("giro_anonimizado", "")[:8] + "...",
            "metricas_validacion": metadatos.get("metricas_validacion", {}),
            "num_parametros": len(metadatos.get("parametros", {})) if "parametros" in metadatos else 0
        }

        with open(ruta, 'w') as f:
            json.dump(metadatos_seguros, f, indent=2)

    async def registrar_consulta_modelo(self, tipo_modelo: str):
        """
        Registrar una consulta de modelo para auditoría.

        Parameters
        ----------
        tipo_modelo : str
            Tipo de modelo consultado
        """
        consulta_id = hashlib.sha256(
            f"{datetime.now().isoformat()}_{tipo_modelo}".encode()
        ).hexdigest()[:16]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO log_consultas 
                (id, tipo_consulta, parametros_hash, timestamp_consulta, resultado_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (
                consulta_id,
                "modelo_agregado",
                hashlib.sha256(tipo_modelo.encode()).hexdigest()[:16],
                datetime.now().isoformat(),
                "modelo_entregado"
            ))
            conn.commit()

    async def obtener_metricas_generales(self) -> Dict:
        """
        Obtener métricas generales agregadas del clúster.

        Returns
        -------
        Dict
            Métricas generales del clúster
        """
        try:
            # Cargar datos sintéticos para calcular métricas agregadas
            ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
            eventos_df = pd.read_csv('data/datos_sinteticos/eventos_dummy.csv')
            perfiles_df = pd.read_csv('data/datos_sinteticos/perfil_viajero_dummy.csv')

            # Calcular métricas agregadas (sin revelar datos individuales)
            metricas = {
                "resumen_cluster": {
                    "total_giros_representados": len(ventas_df['giro'].unique()),
                    "periodo_datos": {
                        "inicio": ventas_df['fecha'].min(),
                        "fin": ventas_df['fecha'].max()
                    },
                    "total_registros_agregados": len(ventas_df) + len(eventos_df) + len(perfiles_df)
                },
                "metricas_economicas": {
                    "ingresos_totales_cluster": float(ventas_df['ingresos_totales'].sum()),
                    "ingreso_promedio_diario": float(ventas_df['ingresos_totales'].mean()),
                    "clientes_totales_atendidos": int(ventas_df['numero_clientes'].sum()),
                    "ticket_promedio_cluster": float(ventas_df['ingresos_totales'].sum() / ventas_df['numero_clientes'].sum())
                },
                "metricas_eventos": {
                    "total_eventos_realizados": len(eventos_df),
                    "asistentes_totales": int(eventos_df['asistentes'].sum()),
                    "asistentes_promedio_evento": float(eventos_df['asistentes'].mean()),
                    "ocupacion_promedio_eventos": float(eventos_df['ocupacion_porcentaje'].mean())
                },
                "perfil_viajeros": {
                    "total_perfiles_analizados": len(perfiles_df),
                    "gasto_promedio_viajero": float(perfiles_df['gasto_total'].mean()),
                    "estancia_promedio_dias": float(perfiles_df['duracion_estancia'].mean()),
                    "tipos_viajero_representados": len(perfiles_df['tipo_viajero'].unique())
                },
                "tendencias_estacionales": self._calcular_tendencias_estacionales(ventas_df),
                "timestamp_calculo": datetime.now().isoformat(),
                "nivel_agregacion": "cluster_completo",
                "privacidad": {
                    "datos_anonimizados": True,
                    "nivel_agregacion": "alto",
                    "empresas_individuales_no_identificables": True
                }
            }

            # Guardar métricas calculadas
            await self._guardar_metricas_generales(metricas)

            return metricas

        except Exception as e:
            # En caso de error, devolver métricas básicas
            return {
                "error": "No se pudieron calcular métricas completas",
                "metricas_basicas": {
                    "timestamp": datetime.now().isoformat(),
                    "status": "datos_no_disponibles"
                }
            }

    async def obtener_metricas_por_giro(self, giro: str) -> Optional[Dict]:
        """
        Obtener métricas agregadas por giro turístico.

        Parameters
        ----------
        giro : str
            Giro turístico

        Returns
        -------
        Optional[Dict]
            Métricas del giro o None si no hay datos suficientes
        """
        try:
            ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
            ventas_giro = ventas_df[ventas_df['giro'] == giro]

            if len(ventas_giro) < 10:  # Mínimo de registros para agregar
                return None

            # Calcular métricas agregadas por giro
            metricas_giro = {
                "giro": giro,
                "periodo_analisis": {
                    "inicio": ventas_giro['fecha'].min(),
                    "fin": ventas_giro['fecha'].max()
                },
                "metricas_economicas": {
                    "ingresos_totales": float(ventas_giro['ingresos_totales'].sum()),
                    "ingresos_promedio_diario": float(ventas_giro['ingresos_totales'].mean()),
                    "clientes_totales": int(ventas_giro['numero_clientes'].sum()),
                    "clientes_promedio_diario": float(ventas_giro['numero_clientes'].mean()),
                    "precio_promedio": float(ventas_giro['precio_promedio'].mean())
                },
                "patrones_temporales": {
                    "mejor_mes": self._obtener_mejor_mes(ventas_giro),
                    "mejor_dia_semana": self._obtener_mejor_dia_semana(ventas_giro),
                    "estacionalidad": self._calcular_estacionalidad_giro(ventas_giro)
                },
                "comparacion_cluster": {
                    "participacion_ingresos": float(ventas_giro['ingresos_totales'].sum() / ventas_df['ingresos_totales'].sum() * 100),
                    "participacion_clientes": float(ventas_giro['numero_clientes'].sum() / ventas_df['numero_clientes'].sum() * 100)
                },
                "num_registros_agregados": len(ventas_giro),
                "timestamp_calculo": datetime.now().isoformat()
            }

            return metricas_giro

        except Exception as e:
            return None

    async def consultar_metricas_personalizadas(self, consulta: ConsultaMetricas) -> Dict:
        """
        Realizar consultas personalizadas sobre métricas agregadas.

        Parameters
        ----------
        consulta : ConsultaMetricas
            Parámetros de la consulta

        Returns
        -------
        Dict
            Resultados de la consulta
        """
        try:
            # Cargar datos base
            ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')
            ventas_df['fecha'] = pd.to_datetime(ventas_df['fecha'])

            # Aplicar filtros
            datos_filtrados = ventas_df.copy()

            if consulta.giros:
                datos_filtrados = datos_filtrados[datos_filtrados['giro'].isin(consulta.giros)]

            if consulta.fecha_inicio:
                fecha_inicio = pd.to_datetime(consulta.fecha_inicio)
                datos_filtrados = datos_filtrados[datos_filtrados['fecha'] >= fecha_inicio]

            if consulta.fecha_fin:
                fecha_fin = pd.to_datetime(consulta.fecha_fin)
                datos_filtrados = datos_filtrados[datos_filtrados['fecha'] <= fecha_fin]

            # Agregar datos según el nivel solicitado
            if consulta.nivel_agregacion == "diario":
                agrupacion = datos_filtrados.groupby(['fecha', 'giro'])
            elif consulta.nivel_agregacion == "semanal":
                datos_filtrados['semana'] = datos_filtrados['fecha'].dt.isocalendar().week
                agrupacion = datos_filtrados.groupby(['semana', 'giro'])
            else:  # mensual
                datos_filtrados['mes'] = datos_filtrados['fecha'].dt.to_period('M')
                agrupacion = datos_filtrados.groupby(['mes', 'giro'])

            # Calcular métricas agregadas
            resultados_agregados = agrupacion.agg({
                'ingresos_totales': ['sum', 'mean', 'count'],
                'numero_clientes': ['sum', 'mean'],
                'precio_promedio': 'mean'
            }).round(2)

            # Convertir a formato JSON serializable
            resultados = {
                "parametros_consulta": {
                    "giros": consulta.giros,
                    "fecha_inicio": consulta.fecha_inicio,
                    "fecha_fin": consulta.fecha_fin,
                    "nivel_agregacion": consulta.nivel_agregacion
                },
                "resultados": resultados_agregados.to_dict(),
                "resumen": {
                    "total_registros": len(datos_filtrados),
                    "giros_incluidos": list(datos_filtrados['giro'].unique()),
                    "periodo_real": {
                        "inicio": datos_filtrados['fecha'].min().strftime('%Y-%m-%d'),
                        "fin": datos_filtrados['fecha'].max().strftime('%Y-%m-%d')
                    }
                },
                "timestamp_consulta": datetime.now().isoformat()
            }

            # Incluir tendencias si se solicita
            if consulta.incluir_tendencias:
                resultados["tendencias"] = self._calcular_tendencias_personalizadas(datos_filtrados)

            # Registrar consulta para auditoría
            await self._registrar_consulta_personalizada(consulta, resultados)

            return resultados

        except Exception as e:
            return {
                "error": f"Error en consulta personalizada: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def guardar_prediccion(self, prediccion: Dict):
        """
        Guardar una predicción generada.

        Parameters
        ----------
        prediccion : Dict
            Predicción a guardar
        """
        prediccion_id = hashlib.sha256(
            f"{prediccion.get('timestamp_generacion', '')}_{prediccion.get('giro', '')}".encode()
        ).hexdigest()[:16]

        ruta = self.directorio_base / "predicciones" / f"prediccion_{prediccion_id}.json"

        with open(ruta, 'w') as f:
            json.dump(prediccion, f, indent=2)

    async def obtener_estadisticas_sistema(self) -> Dict:
        """
        Obtener estadísticas del sistema federado.

        Returns
        -------
        Dict
            Estadísticas del sistema
        """
        # Contar archivos en cada directorio
        num_contribuciones = len(list((self.directorio_base / "contribuciones").glob("*.json")))
        num_modelos = len(list((self.directorio_base / "modelos").glob("*.json")))
        num_predicciones = len(list((self.directorio_base / "predicciones").glob("*.json")))

        # Estadísticas de la base de datos
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM log_consultas")
            num_consultas = cursor.fetchone()[0]

        return {
            "sistema": {
                "total_contribuciones": num_contribuciones,
                "modelos_agregados": num_modelos,
                "predicciones_generadas": num_predicciones,
                "consultas_realizadas": num_consultas
            },
            "almacenamiento": {
                "directorio_base": str(self.directorio_base),
                "size_db_mb": os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            },
            "timestamp": datetime.now().isoformat()
        }

    async def exportar_resultados_anonimos(self, formato: str = "json") -> str:
        """
        Exportar resultados agregados para análisis externo.

        Parameters
        ----------
        formato : str
            Formato de exportación ('json' o 'csv')

        Returns
        -------
        str
            Ruta del archivo exportado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if formato == "json":
            archivo_exportacion = self.directorio_base / "exportaciones" / f"resultados_agregados_{timestamp}.json"

            # Recopilar todos los resultados agregados
            resultados_exportacion = {
                "metadatos": {
                    "timestamp_exportacion": datetime.now().isoformat(),
                    "tipo_exportacion": "resultados_agregados",
                    "nivel_privacidad": "alto",
                    "datos_anonimizados": True
                },
                "metricas_generales": await self.obtener_metricas_generales(),
                "estadisticas_sistema": await self.obtener_estadisticas_sistema()
            }

            with open(archivo_exportacion, 'w') as f:
                json.dump(resultados_exportacion, f, indent=2)

        elif formato == "csv":
            archivo_exportacion = self.directorio_base / "exportaciones" / f"metricas_agregadas_{timestamp}.csv"

            # Exportar métricas en formato CSV
            try:
                ventas_df = pd.read_csv('data/datos_sinteticos/ventas_dummy.csv')

                # Crear resumen agregado por giro y mes
                ventas_df['fecha'] = pd.to_datetime(ventas_df['fecha'])
                ventas_df['mes'] = ventas_df['fecha'].dt.to_period('M')

                resumen_agregado = ventas_df.groupby(['giro', 'mes']).agg({
                    'ingresos_totales': ['sum', 'mean', 'count'],
                    'numero_clientes': ['sum', 'mean'],
                    'precio_promedio': 'mean'
                }).round(2)

                resumen_agregado.to_csv(archivo_exportacion)

            except Exception as e:
                # Crear CSV básico en caso de error
                datos_basicos = pd.DataFrame({
                    'timestamp': [datetime.now().isoformat()],
                    'tipo': ['exportacion_agregada'],
                    'error': [str(e)]
                })
                datos_basicos.to_csv(archivo_exportacion, index=False)

        return str(archivo_exportacion)

    def _calcular_tendencias_estacionales(self, ventas_df: pd.DataFrame) -> Dict:
        """Calcular tendencias estacionales del clúster."""
        ventas_df['fecha'] = pd.to_datetime(ventas_df['fecha'])
        ventas_df['mes'] = ventas_df['fecha'].dt.month

        tendencias_mensuales = ventas_df.groupby('mes')['ingresos_totales'].mean()
        promedio_anual = tendencias_mensuales.mean()

        return {
            mes: float(valor / promedio_anual)
            for mes, valor in tendencias_mensuales.items()
        }

    def _obtener_mejor_mes(self, ventas_giro: pd.DataFrame) -> Dict:
        """Obtener el mejor mes para un giro."""
        ventas_giro['mes'] = pd.to_datetime(ventas_giro['fecha']).dt.month
        ingresos_por_mes = ventas_giro.groupby('mes')['ingresos_totales'].sum()
        mejor_mes = ingresos_por_mes.idxmax()

        return {
            "mes": int(mejor_mes),
            "ingresos": float(ingresos_por_mes.max())
        }

    def _obtener_mejor_dia_semana(self, ventas_giro: pd.DataFrame) -> Dict:
        """Obtener el mejor día de la semana para un giro."""
        ingresos_por_finde = ventas_giro.groupby('es_fin_semana')['ingresos_totales'].mean()

        if True in ingresos_por_finde.index and False in ingresos_por_finde.index:
            if ingresos_por_finde[True] > ingresos_por_finde[False]:
                return {"tipo": "fin_de_semana", "factor": float(ingresos_por_finde[True] / ingresos_por_finde[False])}
            else:
                return {"tipo": "dias_laborales", "factor": float(ingresos_por_finde[False] / ingresos_por_finde[True])}

        return {"tipo": "sin_diferencia", "factor": 1.0}

    def _calcular_estacionalidad_giro(self, ventas_giro: pd.DataFrame) -> Dict:
        """Calcular estacionalidad específica de un giro."""
        ventas_giro['mes'] = pd.to_datetime(ventas_giro['fecha']).dt.month
        ingresos_por_mes = ventas_giro.groupby('mes')['ingresos_totales'].mean()
        promedio = ingresos_por_mes.mean()

        return {
            f"mes_{mes}": float(valor / promedio)
            for mes, valor in ingresos_por_mes.items()
        }

    def _calcular_tendencias_personalizadas(self, datos: pd.DataFrame) -> Dict:
        """Calcular tendencias para consulta personalizada."""
        if len(datos) < 2:
            return {"error": "Datos insuficientes para calcular tendencias"}

        # Tendencia temporal simple
        datos_ordenados = datos.sort_values('fecha')
        primer_mes = datos_ordenados['ingresos_totales'].head(len(datos_ordenados) // 3).mean()
        ultimo_mes = datos_ordenados['ingresos_totales'].tail(len(datos_ordenados) // 3).mean()

        if primer_mes > 0:
            crecimiento = (ultimo_mes - primer_mes) / primer_mes * 100
        else:
            crecimiento = 0

        return {
            "crecimiento_porcentual": round(crecimiento, 2),
            "tendencia": "creciente" if crecimiento > 5 else "decreciente" if crecimiento < -5 else "estable"
        }

    async def _guardar_metricas_generales(self, metricas: Dict):
        """Guardar métricas generales en archivo."""
        ruta = self.directorio_base / "metricas_generales_latest.json"
        with open(ruta, 'w') as f:
            json.dump(metricas, f, indent=2)

    async def _registrar_consulta_personalizada(self, consulta: ConsultaMetricas, resultados: Dict):
        """Registrar consulta personalizada para auditoría."""
        consulta_id = hashlib.sha256(
            f"{datetime.now().isoformat()}_{str(consulta.dict())}".encode()
        ).hexdigest()[:16]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO log_consultas 
                (id, tipo_consulta, parametros_hash, timestamp_consulta, resultado_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (
                consulta_id,
                "consulta_personalizada",
                hashlib.sha256(str(consulta.dict()).encode()).hexdigest()[:16],
                datetime.now().isoformat(),
                hashlib.sha256(str(resultados).encode()).hexdigest()[:16]
            ))
            conn.commit()
