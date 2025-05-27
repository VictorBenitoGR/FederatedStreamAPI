# Ejemplos de Integración con Next.js

**Cómo usar los datos del Clúster de Turismo NL en tu aplicación Next.js**

---

## 🚀 **SETUP INICIAL**

### 1. Copiar Archivos de Datos
```bash
# Desde el proyecto del clúster
cp -r public_data/ ../mi-app-nextjs/public/cluster-data/
```

### 2. Instalar Dependencias
```bash
npm install chart.js react-chartjs-2
npm install @types/node  # Si usas TypeScript
```

### 3. Configurar Variables de Entorno
```env
# .env.local
NEXT_PUBLIC_API_URL=https://federatedstreamapi.onrender.com
NEXT_PUBLIC_USE_STATIC_DATA=true
```

---

## 📊 **COMPONENTES DE EJEMPLO**

### Dashboard Principal
```tsx
// components/ClusterDashboard.tsx
'use client';

import { useEffect, useState } from 'react';

interface ClusterData {
  cluster_stats: {
    total_giros: number;
    total_registros: number;
  };
  economia: {
    ingresos_totales: number;
    clientes_totales: number;
    ticket_promedio: number;
  };
  eventos: {
    total_eventos: number;
    asistentes_totales: number;
  };
}

export default function ClusterDashboard() {
  const [data, setData] = useState<ClusterData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Usar archivos estáticos
        const response = await fetch('/cluster-data/cluster_overview.json');
        const clusterData = await response.json();
        setData(clusterData);
      } catch (error) {
        console.error('Error cargando datos:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center text-red-600">
        Error cargando datos del clúster
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">
        Clúster de Turismo de Nuevo León
      </h1>
      
      {/* Métricas Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Ingresos Totales"
          value={`$${(data.economia.ingresos_totales / 1000000000).toFixed(1)}B`}
          subtitle="Miles de millones de pesos"
          color="green"
        />
        
        <MetricCard
          title="Clientes Atendidos"
          value={`${(data.economia.clientes_totales / 1000000).toFixed(1)}M`}
          subtitle="Millones de clientes"
          color="blue"
        />
        
        <MetricCard
          title="Eventos Realizados"
          value={data.eventos.total_eventos.toLocaleString()}
          subtitle="Total de eventos"
          color="purple"
        />
        
        <MetricCard
          title="Giros Participantes"
          value={data.cluster_stats.total_giros.toString()}
          subtitle="Sectores turísticos"
          color="orange"
        />
      </div>

      {/* Información Adicional */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Resumen del Clúster</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600">Ticket Promedio</p>
            <p className="text-2xl font-bold text-gray-900">
              ${data.economia.ticket_promedio.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Asistentes a Eventos</p>
            <p className="text-2xl font-bold text-gray-900">
              {data.eventos.asistentes_totales.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Registros Analizados</p>
            <p className="text-2xl font-bold text-gray-900">
              {data.cluster_stats.total_registros.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente auxiliar para métricas
interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  color: 'green' | 'blue' | 'purple' | 'orange';
}

function MetricCard({ title, value, subtitle, color }: MetricCardProps) {
  const colorClasses = {
    green: 'text-green-600 bg-green-50 border-green-200',
    blue: 'text-blue-600 bg-blue-50 border-blue-200',
    purple: 'text-purple-600 bg-purple-50 border-purple-200',
    orange: 'text-orange-600 bg-orange-50 border-orange-200'
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]}`}>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <p className={`text-3xl font-bold ${colorClasses[color].split(' ')[0]}`}>
        {value}
      </p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </div>
  );
}
```

### Gráfico de Tendencias Estacionales
```tsx
// components/TendenciasChart.tsx
'use client';

import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TendenciaData {
  tendencias_mensuales: Array<{
    mes: string;
    factor_estacional: number;
    porcentaje_vs_promedio: number;
  }>;
  temporada_alta: {
    mes: string;
    factor_estacional: number;
  };
  temporada_baja: {
    mes: string;
    factor_estacional: number;
  };
}

export default function TendenciasChart() {
  const [tendencias, setTendencias] = useState<TendenciaData | null>(null);

  useEffect(() => {
    async function loadTendencias() {
      try {
        const response = await fetch('/cluster-data/tendencias_estacionales.json');
        const data = await response.json();
        setTendencias(data);
      } catch (error) {
        console.error('Error cargando tendencias:', error);
      }
    }

    loadTendencias();
  }, []);

  if (!tendencias) {
    return <div>Cargando tendencias...</div>;
  }

  const chartData = {
    labels: tendencias.tendencias_mensuales.map(t => t.mes),
    datasets: [
      {
        label: 'Factor Estacional',
        data: tendencias.tendencias_mensuales.map(t => t.factor_estacional),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Tendencias Estacionales del Clúster Turístico',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const value = context.parsed.y;
            const percentage = ((value - 1) * 100).toFixed(1);
            return `Factor: ${value.toFixed(3)} (${percentage}% vs promedio)`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Factor Estacional'
        }
      }
    },
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Análisis Estacional</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-medium text-green-800">Temporada Alta</h3>
            <p className="text-2xl font-bold text-green-600">
              {tendencias.temporada_alta.mes}
            </p>
            <p className="text-sm text-green-600">
              Factor: {tendencias.temporada_alta.factor_estacional.toFixed(2)}x
            </p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="font-medium text-red-800">Temporada Baja</h3>
            <p className="text-2xl font-bold text-red-600">
              {tendencias.temporada_baja.mes}
            </p>
            <p className="text-sm text-red-600">
              Factor: {tendencias.temporada_baja.factor_estacional.toFixed(2)}x
            </p>
          </div>
        </div>
      </div>
      
      <Line data={chartData} options={options} />
    </div>
  );
}
```

### Análisis de Perfiles de Viajeros
```tsx
// components/PerfilesViajeros.tsx
'use client';

import { useEffect, useState } from 'react';

interface PerfilViajero {
  tipo_viajero: string;
  cantidad: number;
  porcentaje: number;
  gasto_promedio: number;
  edad_promedio: number;
  estancia_promedio: number;
}

interface PerfilesData {
  perfiles_viajeros: PerfilViajero[];
  estadisticas_generales: {
    total_perfiles: number;
    gasto_promedio_general: number;
    edad_promedio_general: number;
    estancia_promedio_general: number;
  };
}

export default function PerfilesViajeros() {
  const [perfiles, setPerfiles] = useState<PerfilesData | null>(null);

  useEffect(() => {
    async function loadPerfiles() {
      try {
        const response = await fetch('/cluster-data/perfiles_viajeros.json');
        const data = await response.json();
        setPerfiles(data);
      } catch (error) {
        console.error('Error cargando perfiles:', error);
      }
    }

    loadPerfiles();
  }, []);

  if (!perfiles) {
    return <div>Cargando perfiles de viajeros...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Estadísticas Generales</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">
              {perfiles.estadisticas_generales.total_perfiles.toLocaleString()}
            </p>
            <p className="text-sm text-gray-600">Perfiles Analizados</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              ${perfiles.estadisticas_generales.gasto_promedio_general.toLocaleString()}
            </p>
            <p className="text-sm text-gray-600">Gasto Promedio</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">
              {perfiles.estadisticas_generales.edad_promedio_general} años
            </p>
            <p className="text-sm text-gray-600">Edad Promedio</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-orange-600">
              {perfiles.estadisticas_generales.estancia_promedio_general.toFixed(1)} días
            </p>
            <p className="text-sm text-gray-600">Estancia Promedio</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Tipos de Viajeros</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {perfiles.perfiles_viajeros.map((perfil, index) => (
            <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium text-gray-900 capitalize">
                  {perfil.tipo_viajero.replace('_', ' ')}
                </h3>
                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                  {perfil.porcentaje}%
                </span>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Gasto promedio:</span>
                  <span className="font-medium">${perfil.gasto_promedio.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Edad promedio:</span>
                  <span className="font-medium">{perfil.edad_promedio} años</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Estancia:</span>
                  <span className="font-medium">{perfil.estancia_promedio.toFixed(1)} días</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Cantidad:</span>
                  <span className="font-medium">{perfil.cantidad.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## 🔧 **UTILIDADES Y HOOKS**

### Hook para Cargar Datos
```tsx
// hooks/useClusterData.ts
import { useState, useEffect } from 'react';

export function useClusterData<T>(endpoint: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        
        const useStatic = process.env.NEXT_PUBLIC_USE_STATIC_DATA === 'true';
        
        let response;
        if (useStatic) {
          // Usar archivos estáticos
          response = await fetch(`/cluster-data/${endpoint}.json`);
        } else {
          // Usar API
          const apiUrl = process.env.NEXT_PUBLIC_API_URL;
          response = await fetch(`${apiUrl}/public/${endpoint}`);
        }
        
        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [endpoint]);

  return { data, loading, error };
}

// Hooks específicos
export const useClusterOverview = () => useClusterData('cluster_overview');
export const useTendenciasEstacionales = () => useClusterData('tendencias_estacionales');
export const usePerfilesViajeros = () => useClusterData('perfiles_viajeros');
```

### Utilidades de Formato
```tsx
// utils/formatters.ts
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat('es-MX').format(num);
}

export function formatCompactNumber(num: number): string {
  if (num >= 1000000000) {
    return `${(num / 1000000000).toFixed(1)}B`;
  } else if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toString();
}

export function formatPercentage(value: number): string {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
}
```

---

## 📱 **PÁGINA COMPLETA DE EJEMPLO**

```tsx
// app/dashboard/page.tsx
import ClusterDashboard from '@/components/ClusterDashboard';
import TendenciasChart from '@/components/TendenciasChart';
import PerfilesViajeros from '@/components/PerfilesViajeros';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Dashboard Principal */}
          <ClusterDashboard />
          
          {/* Tendencias Estacionales */}
          <TendenciasChart />
          
          {/* Perfiles de Viajeros */}
          <PerfilesViajeros />
          
          {/* Footer */}
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <p className="text-gray-600">
              Datos del Clúster de Turismo de Nuevo León
            </p>
            <p className="text-sm text-gray-500">
              Información completamente anonimizada • Última actualización: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## 🚀 **DEPLOY EN VERCEL**

### 1. Configurar Variables de Entorno
```bash
# En Vercel Dashboard
NEXT_PUBLIC_USE_STATIC_DATA=true
NEXT_PUBLIC_API_URL=https://federatedstreamapi.onrender.com
```

### 2. Script de Build
```json
// package.json
{
  "scripts": {
    "build": "next build",
    "start": "next start",
    "update-data": "curl -o public/cluster-data/all_data.json https://federatedstreamapi.onrender.com/public/export/all"
  }
}
```

### 3. Actualización Automática de Datos
```yaml
# .github/workflows/update-data.yml
name: Update Cluster Data
on:
  schedule:
    - cron: '0 6 * * *'  # Diario a las 6 AM
  workflow_dispatch:

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Update data
        run: |
          curl -o public/cluster-data/cluster_overview.json https://federatedstreamapi.onrender.com/public/cluster/overview
          curl -o public/cluster-data/tendencias_estacionales.json https://federatedstreamapi.onrender.com/public/cluster/tendencias-estacionales
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add public/cluster-data/
          git commit -m "Update cluster data" || exit 0
          git push
```

---

**¡Listo para crear tu dashboard del clúster turístico! 🎉** 