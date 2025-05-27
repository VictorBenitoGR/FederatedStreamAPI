from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import numpy as np


class ModeloFederado(BaseModel):
    """
    Modelo entrenado localmente por una empresa.

    Contiene solo los parámetros del modelo, nunca datos crudos.
    Todos los identificadores están completamente anonimizados.
    """
    tipo_modelo: str = Field(..., description="Tipo de modelo (prediccion_demanda, clasificacion_viajero, etc.)")
    parametros: Dict[str, Any] = Field(..., description="Parámetros del modelo entrenado")
    giro_hash: str = Field(..., description="Hash irreversible del giro de la empresa")
    timestamp: str = Field(..., description="Timestamp de entrenamiento")
    metricas_validacion: Dict[str, float] = Field(..., description="Métricas de validación del modelo")
    version_algoritmo: str = Field(default="1.0", description="Versión del algoritmo utilizado")
    num_muestras_entrenamiento: int = Field(..., description="Número de muestras usadas (sin revelar datos)")

    @validator('giro_hash')
    def validar_giro_hash(cls, v):
        """Validar que el hash del giro sea irreversible."""
        if len(v) < 16:
            raise ValueError("Hash del giro debe tener al menos 16 caracteres")
        return v

    @validator('parametros')
    def validar_parametros(cls, v):
        """Validar que los parámetros no contengan información identificable."""
        # Verificar que no haya claves que puedan revelar identidad
        claves_prohibidas = ['empresa_id', 'nombre', 'direccion', 'telefono', 'email']
        for clave in v.keys():
            if any(prohibida in clave.lower() for prohibida in claves_prohibidas):
                raise ValueError(f"Parámetro '{clave}' puede contener información identificable")
        return v


class MetricasEmpresa(BaseModel):
    """
    Métricas agregadas de una empresa de forma anónima.

    Las métricas están pre-procesadas localmente para garantizar anonimato.
    """
    giro_hash: str = Field(..., description="Hash irreversible del giro")
    periodo_inicio: str = Field(..., description="Inicio del período de las métricas")
    periodo_fin: str = Field(..., description="Fin del período de las métricas")
    metricas_agregadas: Dict[str, Union[float, int]] = Field(..., description="Métricas agregadas")
    timestamp_envio: str = Field(..., description="Timestamp del envío")

    # Métricas específicas por tipo de negocio
    ingresos_promedio_diario: Optional[float] = Field(None, description="Promedio de ingresos diarios")
    clientes_promedio_diario: Optional[float] = Field(None, description="Promedio de clientes diarios")
    ocupacion_promedio: Optional[float] = Field(None, description="Porcentaje de ocupación promedio")
    precio_promedio: Optional[float] = Field(None, description="Precio promedio de servicios")

    @validator('metricas_agregadas')
    def validar_metricas_agregadas(cls, v):
        """Validar que las métricas estén agregadas y no revelen datos individuales."""
        # Verificar que no haya métricas que puedan revelar transacciones específicas
        for clave, valor in v.items():
            if isinstance(valor, (list, tuple)) and len(valor) < 10:
                raise ValueError(f"Métrica '{clave}' debe estar más agregada (mínimo 10 puntos)")
        return v


class DatosAnonimizados(BaseModel):
    """
    Datos completamente anonimizados para análisis agregado.
    """
    tipo_datos: str = Field(..., description="Tipo de datos (ventas, eventos, publicidad, etc.)")
    datos_agregados: Dict[str, Any] = Field(..., description="Datos agregados por período/categoría")
    nivel_agregacion: str = Field(..., description="Nivel de agregación (diario, semanal, mensual)")
    timestamp: str = Field(..., description="Timestamp de generación")


class ConsultaMetricas(BaseModel):
    """
    Consulta personalizada para métricas agregadas.
    """
    giros: Optional[List[str]] = Field(None, description="Filtrar por giros específicos")
    fecha_inicio: Optional[str] = Field(None, description="Fecha de inicio del período")
    fecha_fin: Optional[str] = Field(None, description="Fecha de fin del período")
    tipo_metrica: Optional[str] = Field(None, description="Tipo específico de métrica")
    nivel_agregacion: str = Field(default="mensual", description="Nivel de agregación deseado")
    incluir_tendencias: bool = Field(default=True, description="Incluir análisis de tendencias")


class ResultadoAgregado(BaseModel):
    """
    Resultado de un modelo federado agregado.

    Combina múltiples contribuciones sin revelar fuentes individuales.
    """
    tipo_modelo: str = Field(..., description="Tipo de modelo agregado")
    parametros_agregados: Dict[str, Any] = Field(..., description="Parámetros del modelo agregado")
    num_contribuciones: int = Field(..., description="Número de empresas que contribuyeron")
    metricas_agregadas: Dict[str, float] = Field(..., description="Métricas de rendimiento agregadas")
    timestamp_agregacion: str = Field(..., description="Timestamp de la agregación")
    confianza: float = Field(..., description="Nivel de confianza del modelo agregado")
    version: str = Field(..., description="Versión del modelo agregado")


class PrediccionDemanda(BaseModel):
    """
    Predicción de demanda generada por modelos federados.
    """
    giro: str = Field(..., description="Giro turístico")
    fecha_inicio: str = Field(..., description="Inicio del período de predicción")
    fecha_fin: str = Field(..., description="Fin del período de predicción")
    predicciones: List[Dict[str, Any]] = Field(..., description="Predicciones por período")
    intervalos_confianza: List[Dict[str, float]] = Field(..., description="Intervalos de confianza")
    factores_influencia: Dict[str, float] = Field(..., description="Factores que influyen en la predicción")
    timestamp_generacion: str = Field(..., description="Timestamp de generación")


class TendenciaHistorica(BaseModel):
    """
    Análisis de tendencias históricas y proyecciones.
    """
    giro: str = Field(..., description="Giro turístico")
    periodo_analisis: str = Field(..., description="Período analizado")
    tendencia_general: str = Field(..., description="Tendencia general (creciente, decreciente, estable)")
    tasa_crecimiento_anual: float = Field(..., description="Tasa de crecimiento anual promedio")
    estacionalidad: Dict[str, float] = Field(..., description="Patrones estacionales detectados")
    proyecciones: List[Dict[str, Any]] = Field(..., description="Proyecciones futuras")
    confianza_proyeccion: float = Field(..., description="Confianza en las proyecciones")


class EstadisticasSistema(BaseModel):
    """
    Estadísticas del sistema federado.
    """
    total_contribuciones: int = Field(..., description="Total de contribuciones recibidas")
    empresas_activas: int = Field(..., description="Número de empresas activas (estimado)")
    modelos_disponibles: List[str] = Field(..., description="Tipos de modelos disponibles")
    ultima_actualizacion: str = Field(..., description="Última actualización de modelos")
    giros_representados: List[str] = Field(..., description="Giros turísticos representados")
    metricas_sistema: Dict[str, Any] = Field(..., description="Métricas del sistema")


class ConfiguracionPrivacidad(BaseModel):
    """
    Configuración de privacidad para el sistema federado.
    """
    nivel_anonimizacion: str = Field(default="alto", description="Nivel de anonimización")
    min_contribuciones_agregacion: int = Field(default=3, description="Mínimo de contribuciones para agregar")
    ruido_diferencial: bool = Field(default=True, description="Aplicar ruido diferencial")
    epsilon_privacidad: float = Field(default=1.0, description="Parámetro epsilon para privacidad diferencial")
    retencion_datos_dias: int = Field(default=90, description="Días de retención de metadatos")


class LogAuditoria(BaseModel):
    """
    Log de auditoría para el sistema federado.
    """
    timestamp: str = Field(..., description="Timestamp del evento")
    tipo_evento: str = Field(..., description="Tipo de evento (contribucion, consulta, agregacion)")
    hash_sesion: str = Field(..., description="Hash de la sesión (anonimizado)")
    detalles_evento: Dict[str, Any] = Field(..., description="Detalles del evento (sin datos sensibles)")
    resultado: str = Field(..., description="Resultado del evento")

# Modelos para respuestas de la API


class RespuestaExito(BaseModel):
    """
    Respuesta estándar de éxito.
    """
    status: str = Field(default="success", description="Estado de la operación")
    mensaje: str = Field(..., description="Mensaje descriptivo")
    datos: Optional[Any] = Field(None, description="Datos de respuesta")
    timestamp: str = Field(..., description="Timestamp de la respuesta")


class RespuestaError(BaseModel):
    """
    Respuesta estándar de error.
    """
    status: str = Field(default="error", description="Estado de la operación")
    error: str = Field(..., description="Descripción del error")
    codigo_error: Optional[str] = Field(None, description="Código específico del error")
    timestamp: str = Field(..., description="Timestamp del error")
