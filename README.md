# Clúster de Turismo de Nuevo León - Sistema de Analítica Federada

**Sistema de aprendizaje federado que permite a las empresas turísticas colaborar en analítica e inteligencia artificial sin comprometer la privacidad de sus datos.**

---

## 🏢 **PARA EMPRESAS DEL CLÚSTER**

### ¿Qué es el sistema federado?
Hemos desarrollado un sistema de aprendizaje federado que permite a las empresas turísticas colaborar en analítica e inteligencia artificial sin comprometer la privacidad de sus datos, permitiendo:

- **Mejorar sus predicciones** usando el conocimiento colectivo del clúster
- **Comparar su rendimiento** de forma anónima con otras empresas
- **Tomar mejores decisiones** basadas en tendencias del sector
- **Mantener privacidad total** - tus datos nunca salen de tu empresa

### 🌐 **API EN PRODUCCIÓN**
**URL:** `https://federatedstreamapi.onrender.com`
**Estado:** ✅ **ACTIVA Y FUNCIONANDO**

### 🚀 Inicio rápido para empresas

#### 1. Configuración inicial
```bash
# Descargar el cliente federado
git clone <https://github.com/VictorBenitoGR/FederatedStreamAPI>
cd FederatedStreamAPI

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. Configurar tu empresa
```bash
# Ejecutar el configurador de empresa
python scripts/configurar_empresa.py
```

#### 3. Entrenar y enviar modelos
```bash
# Entrenar modelos con tus datos y enviarlos al clúster
python scripts/entrenar_y_enviar.py
```

#### 4. Consultar resultados del clúster
```bash
# Obtener insights del clúster para tomar decisiones
python scripts/consultar_cluster.py
```

### 📊 Casos de uso principales

#### **Predicción de Demanda**
Predice la demanda futura basada en patrones del clúster completo:
```bash
python scripts/predecir_demanda.py --giro hotel --fecha-inicio 2025-07-01 --fecha-fin 2025-08-31
```

#### **Benchmarking anónimo**
Compara tu rendimiento con el promedio del sector:
```bash
python scripts/benchmark_anonimo.py --mi-giro restaurante
```

#### **Análisis de tendencias**
Identifica tendencias estacionales y oportunidades:
```bash
python scripts/analizar_tendencias.py --giro agencia_viajes
```

### 🔒 Garantías de privacidad

- ✅ **Tus datos nunca salen** de tu empresa
- ✅ **IDs completamente anonimizados** (imposible rastrear)
- ✅ **Solo parámetros agregados** se comparten
- ✅ **Ruido diferencial** para mayor seguridad
- ✅ **Auditoría independiente** de privacidad

### 📞 Soporte para empresas

- **URL de la API**: `https://federatedstreamapi.onrender.com`
- **Documentación de la API**: [API_PUBLICA.md](./API_PUBLICA.md)
- **Ejemplos de Next.js**: [ejemplos_nextjs/README.md](./ejemplos_nextjs/README.md)
- **Email**: victorbenitogr@gmail.com

---

## 🛠️ **PARA DESARROLLADORES**

### Arquitectura del sistema

#### Componentes principales

1. **API federada** (`src/api/`)
   - Servidor FastAPI que recibe modelos anonimizados
   - Agregación federada de parámetros de modelos
   - Generación de predicciones y métricas del clúster

2. **Cliente federado** (`src/cliente/`)
   - Entrenamiento local de modelos de ML
   - Anonimización completa de parámetros
   - Envío seguro a la API federada

3. **Scripts para empresas** (`scripts/`)
   - Herramientas fáciles de usar para empresas
   - Configuración automática
   - Workflows simplificados

4. **Generación de datos** (`src/datos_sinteticos/`)
   - Datos sintéticos realistas para desarrollo y testing
   - 100 empresas dummy con tendencias estacionales

### 🚀 Configuración de desarrollo

#### 1. Entorno de desarrollo
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

#### 2. Generar datos de prueba
```bash
# Generar datos sintéticos completos
python src/datos_sinteticos/generar_todos_datos.py

# Analizar tendencias generadas
python src/datos_sinteticos/analizar_datos.py
```

#### 3. Ejecutar tests y demostraciones
```bash
# Demostración completa del sistema
python src/demo/demo_federado.py

# Test de API con clientes reales
python src/demo/test_api_completa.py
```

#### 4. Iniciar API en desarrollo
```bash
# Servidor de desarrollo local
python start.py

# O con uvicorn directamente
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# API en producción (ya desplegada)
# https://federatedstreamapi.onrender.com
```

### 📁 Estructura del proyecto

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

### 🔧 APIs y endpoints

#### Endpoints para empresas
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

#### Endpoints de administración
```
GET  /health                           # Estado del sistema
GET  /admin/stats                      # Estadísticas del sistema
POST /admin/export-results             # Exportar resultados
```

### 📊 Datos sintéticos generados

#### Características de los datos
- **167,387 registros** totales
- **100 empresas** dummy con 10 giros turísticos
- **Tendencias realistas**: estacionalidad, patrones semanales, crecimiento anual
- **Tipos de viajeros**: 10 perfiles diferentes con gastos variables

#### Tendencias implementadas
1. **Estacionalidad**: Verano +80%, Diciembre pico, Febrero baja
2. **Patrones semanales**: Restaurantes +80% fines de semana
3. **Crecimiento anual**: 1.5-2.5% según el giro
4. **Giros específicos**: Hoteles picos en vacaciones, eventos en verano

### 🧪 Testing y validación

#### Tests automatizados
```bash
# Test completo del sistema
python -m pytest tests/

# Test específico de privacidad
python tests/test_privacidad.py

# Test de rendimiento
python tests/test_rendimiento.py
```

#### Validación de privacidad
- **Anonimización**: SHA-256 + 1000 iteraciones + salt único
- **Ruido local**: Ruido gaussiano aplicado a parámetros
- **Ruido diferencial**: Ruido Laplaciano en resultados agregados
- **Validación automática**: Verificación de que no hay información identificable

### 🤝 Contribución al proyecto

#### Workflow de desarrollo
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

#### Áreas de contribución
- **Nuevos algoritmos ML**: Implementar otros tipos de modelos federados
- **Optimización**: Mejorar rendimiento para cientos de empresas
- **Seguridad**: Auditoría y mejoras de privacidad
- **UI/UX**: Dashboard web para empresas
- **Documentación**: Guías y tutoriales

### 📄 Licencia y contacto

- **Licencia**: GNU General Public License 3.0
- **Contacto técnico**: victorbenitogr@gmail.com
- **Repositorio**: [GitHub](https://github.com/cluster-turismo-nl/federated-api)

---

**Nota**: Este proyecto está en desarrollo activo. Los datos generados son completamente sintéticos y no representan empresas reales.