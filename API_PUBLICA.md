# API Pública - Clúster de Turismo NL

**Endpoints públicos para consumir datos anónimos del clúster desde aplicaciones web.**

---

## 🌐 **ENDPOINTS DISPONIBLES**

### Base URL
```
https://federatedstreamapi.onrender.com
```

### 📊 **Resumen General del Clúster**
```http
GET /public/cluster/overview
```

**Respuesta:**
```json
{
  "cluster_stats": {
    "total_giros": 9,
    "periodo_datos": {
      "inicio": "2020-01-01",
      "fin": "2025-12-31"
    },
    "total_registros": 163348
  },
  "economia": {
    "ingresos_totales": 48399491477,
    "ingreso_promedio_diario": 308473,
    "clientes_totales": 16695425,
    "ticket_promedio": 2899
  },
  "eventos": {
    "total_eventos": 1448,
    "asistentes_totales": 1233135,
    "asistentes_promedio": 852,
    "ocupacion_promedio": 79.1
  },
  "viajeros": {
    "perfiles_analizados": 5000,
    "gasto_promedio": 42775,
    "estancia_promedio": 5.2,
    "tipos_viajero": 10
  },
  "metadata": {
    "ultima_actualizacion": "2025-05-26T17:51:36.685007",
    "nivel_privacidad": "datos_completamente_anonimos",
    "empresas_identificables": false
  }
}
```

### 📈 **Tendencias Estacionales**
```http
GET /public/cluster/tendencias-estacionales
```

**Respuesta:**
```json
{
  "tendencias_mensuales": [
    {
      "mes": "Enero",
      "mes_numero": 1,
      "factor_estacional": 0.343,
      "porcentaje_vs_promedio": -65.7
    },
    {
      "mes": "Julio",
      "mes_numero": 7,
      "factor_estacional": 1.988,
      "porcentaje_vs_promedio": 98.8
    }
  ],
  "temporada_alta": {
    "mes": "Julio",
    "factor_estacional": 1.988
  },
  "temporada_baja": {
    "mes": "Febrero",
    "factor_estacional": 0.269
  },
  "metadata": {
    "periodo_analisis": {
      "inicio": "2020-01-01",
      "fin": "2025-12-31"
    },
    "ultima_actualizacion": "2025-01-27T..."
  }
}
```

### 🏷️ **Estadísticas por Giro**
```http
GET /public/giros/estadisticas
```

**Respuesta:**
```json
{
  "estadisticas_por_giro": [
    {
      "giro": "hotel",
      "empresas_participantes": 12,
      "ingresos_totales": 15234567890,
      "ingresos_promedio": 45678,
      "clientes_totales": 2345678,
      "clientes_promedio": 234,
      "precio_promedio": 2890,
      "registros_totales": 18456
    }
  ],
  "resumen": {
    "total_giros": 9,
    "giro_lider": "hotel",
    "ingresos_cluster": 48399491477
  },
  "metadata": {
    "datos_anonimizados": true,
    "nivel_agregacion": "por_giro",
    "ultima_actualizacion": "2025-01-27T..."
  }
}
```

### 🎪 **Resumen de Eventos**
```http
GET /public/eventos/resumen
```

**Respuesta:**
```json
{
  "resumen_eventos": {
    "total_eventos": 1448,
    "asistentes_totales": 1233135,
    "asistentes_promedio": 852,
    "ocupacion_promedio": 79.1,
    "capacidad_total": 1558800,
    "tipos_evento": 8,
    "eventos_por_tipo": {
      "concierto": 245,
      "conferencia": 198,
      "festival": 156
    },
    "tendencia_asistencia": {
      "maximo": 2500,
      "minimo": 50,
      "mediana": 800
    }
  },
  "metadata": {
    "datos_anonimizados": true,
    "empresas_no_identificables": true,
    "ultima_actualizacion": "2025-01-27T..."
  }
}
```

### 👥 **Perfiles de Viajeros**
```http
GET /public/viajeros/perfiles
```

**Respuesta:**
```json
{
  "perfiles_viajeros": [
    {
      "tipo_viajero": "ejecutivo",
      "cantidad": 523,
      "porcentaje": 10.5,
      "gasto_promedio": 85420,
      "edad_promedio": 42,
      "estancia_promedio": 3.2,
      "grupo_promedio": 1.1
    }
  ],
  "estadisticas_generales": {
    "total_perfiles": 5000,
    "gasto_promedio_general": 42775,
    "edad_promedio_general": 38,
    "estancia_promedio_general": 5.2,
    "tipos_viajero_unicos": 10
  },
  "metadata": {
    "datos_completamente_anonimos": true,
    "sin_informacion_personal": true,
    "ultima_actualizacion": "2025-01-27T..."
  }
}
```

### 📦 **Exportar Todos los Datos**
```http
GET /public/export/all
```

**Respuesta:** Objeto JSON con todos los endpoints anteriores consolidados.

---

## 📁 **ARCHIVOS ESTÁTICOS**

### Generar Archivos JSON
```bash
python scripts/generar_datos_publicos.py
```

**Archivos generados en `public_data/`:**
- `cluster_overview.json` - Resumen general
- `tendencias_estacionales.json` - Tendencias por mes
- `estadisticas_giros.json` - Stats por giro turístico
- `resumen_eventos.json` - Datos de eventos
- `perfiles_viajeros.json` - Análisis de viajeros
- `all_data.json` - Todos los datos consolidados
- `nextjs_config.json` - Configuración para Next.js

---

## 🚀 **INTEGRACIÓN CON NEXT.JS**

### Opción 1: Archivos Estáticos
```typescript
// lib/data.ts
import clusterData from '../public_data/cluster_overview.json';
import tendenciasData from '../public_data/tendencias_estacionales.json';

export const getClusterOverview = () => clusterData;
export const getTendenciasEstacionales = () => tendenciasData;
```

### Opción 2: API Calls
```typescript
// lib/api.ts
const API_BASE = 'https://federatedstreamapi.onrender.com';

export async function getClusterOverview() {
  const response = await fetch(`${API_BASE}/public/cluster/overview`);
  return response.json();
}

export async function getTendenciasEstacionales() {
  const response = await fetch(`${API_BASE}/public/cluster/tendencias-estacionales`);
  return response.json();
}
```

### Opción 3: Híbrida (Recomendada)
```typescript
// lib/data.ts
const USE_STATIC = process.env.NODE_ENV === 'production';
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function getClusterOverview() {
  if (USE_STATIC) {
    // Usar archivos estáticos en producción
    const data = await import('../public_data/cluster_overview.json');
    return data.default;
  } else {
    // Usar API en desarrollo
    const response = await fetch(`${API_BASE}/public/cluster/overview`);
    return response.json();
  }
}
```

---

## 📊 **EJEMPLOS DE COMPONENTES**

### Dashboard Principal
```tsx
// components/ClusterDashboard.tsx
import { useEffect, useState } from 'react';
import { getClusterOverview } from '../lib/data';

export default function ClusterDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getClusterOverview().then(setData);
  }, []);

  if (!data) return <div>Cargando...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">Ingresos Totales</h3>
        <p className="text-3xl font-bold text-green-600">
          ${data.economia.ingresos_totales.toLocaleString()}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">Clientes Totales</h3>
        <p className="text-3xl font-bold text-blue-600">
          {data.economia.clientes_totales.toLocaleString()}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">Eventos Realizados</h3>
        <p className="text-3xl font-bold text-purple-600">
          {data.eventos.total_eventos.toLocaleString()}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold">Giros Participantes</h3>
        <p className="text-3xl font-bold text-orange-600">
          {data.cluster_stats.total_giros}
        </p>
      </div>
    </div>
  );
}
```

### Gráfico de Tendencias
```tsx
// components/TendenciasChart.tsx
import { Line } from 'react-chartjs-2';
import { getTendenciasEstacionales } from '../lib/data';

export default function TendenciasChart() {
  const [tendencias, setTendencias] = useState(null);

  useEffect(() => {
    getTendenciasEstacionales().then(setTendencias);
  }, []);

  const chartData = {
    labels: tendencias?.tendencias_mensuales.map(t => t.mes) || [],
    datasets: [{
      label: 'Factor Estacional',
      data: tendencias?.tendencias_mensuales.map(t => t.factor_estacional) || [],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-xl font-semibold mb-4">Tendencias Estacionales</h3>
      <Line data={chartData} />
    </div>
  );
}
```

---

## 🔧 **CONFIGURACIÓN**

### Variables de Entorno
```env
# .env.local
NEXT_PUBLIC_API_URL=https://federatedstreamapi.onrender.com
NEXT_PUBLIC_USE_STATIC_DATA=false
```

### CORS (si usas API directa)
```python
# En tu FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo, en producción especifica dominios
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

### Cache Headers
```python
# En los endpoints públicos
@router.get("/cluster/overview")
async def obtener_resumen_cluster(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    # ... resto del código
```

---

## 🔒 **PRIVACIDAD Y SEGURIDAD**

### ✅ **Garantías de Privacidad**
- **Datos completamente agregados** - No hay información individual
- **IDs anonimizados** - Imposible rastrear empresas específicas
- **Sin datos sensibles** - Solo métricas agregadas públicas
- **Validación automática** - Verificación de anonimización

### 🛡️ **Medidas de Seguridad**
- **Rate limiting** en endpoints públicos
- **CORS configurado** para dominios específicos
- **Cache headers** para optimizar rendimiento
- **Validación de entrada** en todos los endpoints

---

## 📈 **CASOS DE USO**

### Dashboard Público del Clúster
- Mostrar métricas generales del sector turístico
- Visualizar tendencias estacionales
- Comparar rendimiento entre giros

### Portal de Transparencia
- Publicar resultados agregados del clúster
- Mostrar impacto económico del turismo
- Demostrar valor del sistema federado

### Herramientas de Análisis
- Benchmarking sectorial anónimo
- Estudios de mercado turístico
- Reportes de tendencias estacionales

---

## 🚀 **DEPLOY EN VERCEL**

### 1. Archivos Estáticos
```bash
# Generar datos
python scripts/generar_datos_publicos.py

# Copiar a tu proyecto Next.js
cp -r public_data/ ../mi-app-nextjs/public/
```

### 2. API Endpoints
```bash
# Tu API ya está desplegada en:
# https://federatedstreamapi.onrender.com
```

### 3. Configuración Next.js
```json
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://federatedstreamapi.onrender.com/:path*'
      }
    ];
  }
};
```

---

**¿Necesitas ayuda con algún endpoint específico o integración particular?** 🤝 