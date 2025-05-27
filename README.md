# Clúster de Turismo de Nuevo León - Sistema de Analítica Federada

**Sistema de aprendizaje federado que permite a las empresas turísticas colaborar en analítica e inteligencia artificial sin comprometer la privacidad de sus datos.**

---

## 🏢 **PARA EMPRESAS DEL CLÚSTER**

### ¿Qué es el Sistema Federado?

El sistema permite que tu empresa:
- **Mejore sus predicciones** usando el conocimiento colectivo del clúster
- **Compare su rendimiento** de forma anónima con otras empresas
- **Tome mejores decisiones** basadas en tendencias del sector
- **Mantenga privacidad total** - tus datos nunca salen de tu empresa

### 🚀 Inicio Rápido para Empresas

#### 1. Configuración Inicial
```bash
# Descargar el cliente federado
git clone <repository-url>
cd FederatedStreamAPI

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Configurar tu Empresa
```bash
# Ejecutar el configurador de empresa
python scripts/configurar_empresa.py
```

#### 3. Entrenar y Enviar Modelos
```bash
# Entrenar modelos con tus datos y enviarlos al clúster
python scripts/entrenar_y_enviar.py
```

#### 4. Consultar Resultados del Clúster
```bash
# Obtener insights del clúster para tomar decisiones
python scripts/consultar_cluster.py
```

### 📊 Casos de Uso Principales

#### **Predicción de Demanda**
Predice la demanda futura basada en patrones del clúster completo:
```bash
python scripts/predecir_demanda.py --giro hotel --fecha-inicio 2025-07-01 --fecha-fin 2025-08-31
```

#### **Benchmarking Anónimo**
Compara tu rendimiento con el promedio del sector:
```bash
python scripts/benchmark_anonimo.py --mi-giro restaurante
```

#### **Análisis de Tendencias**
Identifica tendencias estacionales y oportunidades:
```bash
python scripts/analizar_tendencias.py --giro agencia_viajes
```

### 🔒 Garantías de Privacidad

- ✅ **Tus datos nunca salen** de tu empresa
- ✅ **IDs completamente anonimizados** (imposible rastrear)
- ✅ **Solo parámetros agregados** se comparten
- ✅ **Ruido diferencial** para mayor seguridad
- ✅ **Auditoría independiente** de privacidad

### 📞 Soporte para Empresas

- **Email**: soporte@cluster-turismo-nl.com
- **Teléfono**: +52 (81) 1234-5678
- **Documentación**: [docs.cluster-turismo-nl.com](https://docs.cluster-turismo-nl.com)

---

## 🛠️ **PARA DESARROLLADORES**

### Arquitectura del Sistema

#### Componentes Principales

1. **API Federada** (`src/api/`)
   - Servidor FastAPI que recibe modelos anonimizados
   - Agregación federada de parámetros de modelos
   - Generación de predicciones y métricas del clúster

2. **Cliente Federado** (`src/cliente/`)
   - Entrenamiento local de modelos de ML
   - Anonimización completa de parámetros
   - Envío seguro a la API federada

3. **Scripts para Empresas** (`scripts/`)
   - Herramientas fáciles de usar para empresas
   - Configuración automática
   - Workflows simplificados

4. **Generación de Datos** (`src/datos_sinteticos/`)
   - Datos sintéticos realistas para desarrollo y testing
   - 100 empresas dummy con tendencias estacionales

### 🚀 Configuración de Desarrollo

#### 1. Entorno de Desarrollo
```bash
# Clonar repositorio
git clone <repository-url>
cd FederatedStreamAPI

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Generar Datos de Prueba
```bash
# Generar datos sintéticos completos
python src/datos_sinteticos/generar_todos_datos.py

# Analizar tendencias generadas
python src/datos_sinteticos/analizar_datos.py
```

#### 3. Ejecutar Tests y Demos
```bash
# Demostración completa del sistema
python src/demo/demo_federado.py

# Test de API con clientes reales
python src/demo/test_api_completa.py
```

#### 4. Iniciar API en Desarrollo
```bash
# Servidor de desarrollo
python src/api/main.py

# O con uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 📁 Estructura del Proyecto

```
FederatedStreamAPI/
├── scripts/                           # Scripts para empresas
│   ├── configurar_empresa.py          # Configuración inicial
│   ├── entrenar_y_enviar.py           # Entrenamiento y envío
│   ├── consultar_cluster.py           # Consultas del clúster
│   ├── predecir_demanda.py            # Predicciones
│   ├── benchmark_anonimo.py           # Benchmarking
│   └── analizar_tendencias.py         # Análisis de tendencias
├── src/
│   ├── api/                           # API FastAPI
│   ├── cliente/                       # Cliente federado
│   ├── datos_sinteticos/              # Generación de datos
│   └── demo/                          # Demostraciones
├── data/
│   ├── datos_sinteticos/              # Datos sintéticos (167K registros)
│   └── resultados/                    # Resultados anonimizados
└── docs/                              # Documentación técnica
```

### 🔧 APIs y Endpoints

#### Endpoints para Empresas
```
POST /federated/submit-model           # Enviar modelo entrenado
POST /federated/submit-metrics         # Enviar métricas agregadas
GET  /federated/get-aggregated/{tipo}  # Obtener modelo agregado
GET  /metrics/general                  # Métricas generales del clúster
GET  /metrics/by-sector/{giro}         # Métricas por giro
POST /metrics/query                    # Consultas personalizadas
POST /predictions/demand               # Predicciones de demanda
GET  /predictions/trends/{giro}        # Tendencias por giro
```

#### Endpoints de Administración
```
GET  /health                           # Estado del sistema
GET  /admin/stats                      # Estadísticas del sistema
POST /admin/export-results             # Exportar resultados
```

### 📊 Datos Sintéticos Generados

#### Características de los Datos
- **167,387 registros** totales
- **100 empresas** dummy con 10 giros turísticos
- **Tendencias realistas**: estacionalidad, patrones semanales, crecimiento anual
- **Tipos de viajeros**: 10 perfiles diferentes con gastos variables

#### Tendencias Implementadas
1. **Estacionalidad**: Verano +80%, Diciembre pico, Febrero baja
2. **Patrones Semanales**: Restaurantes +80% fines de semana
3. **Crecimiento Anual**: 1.5-2.5% según el giro
4. **Giros Específicos**: Hoteles picos en vacaciones, eventos en verano

### 🧪 Testing y Validación

#### Tests Automatizados
```bash
# Test completo del sistema
python -m pytest tests/

# Test específico de privacidad
python tests/test_privacidad.py

# Test de rendimiento
python tests/test_rendimiento.py
```

#### Validación de Privacidad
- **Anonimización**: SHA-256 + 1000 iteraciones + salt único
- **Ruido Local**: Ruido gaussiano aplicado a parámetros
- **Ruido Diferencial**: Ruido Laplaciano en resultados agregados
- **Validación Automática**: Verificación de que no hay información identificable

### 🤝 Contribución al Proyecto

#### Workflow de Desarrollo
1. Fork el repositorio
2. Crear rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "Agregar nueva funcionalidad"`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

#### Estándares de Código
- **Documentación**: NumPy Docstring para todas las funciones
- **Tipo de datos**: Type hints en Python
- **Testing**: Cobertura mínima del 80%
- **Privacidad**: Validación automática de anonimización

#### Áreas de Contribución
- **Nuevos algoritmos ML**: Implementar otros tipos de modelos federados
- **Optimización**: Mejorar rendimiento para cientos de empresas
- **Seguridad**: Auditoría y mejoras de privacidad
- **UI/UX**: Dashboard web para empresas
- **Documentación**: Guías y tutoriales

### 📄 Licencia y Contacto

- **Licencia**: GNU General Public License 3.0
- **Contacto Técnico**: victorbenitogr@gmail.com
- **Repositorio**: [GitHub](https://github.com/cluster-turismo-nl/federated-api)

---

**Nota**: Este proyecto está en desarrollo activo. Los datos generados son completamente sintéticos y no representan empresas reales.