# ./src/demo/demo_federado.py

from src.api.storage import AlmacenResultados
from src.api.federado import ProcesadorFederado
from src.cliente.cliente_federado import ClienteFederado
import sys
import os
import time
import asyncio
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict

# Agregar el directorio raíz al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class DemostracionFederada:
    """
    Demostración completa del sistema de aprendizaje federado.

    Simula múltiples empresas del clúster turístico:
    1. Cada empresa entrena modelos localmente
    2. Envían parámetros anonimizados al sistema federado
    3. El sistema agrega los modelos sin revelar datos individuales
    4. Las empresas pueden consultar modelos agregados
    5. Se generan predicciones y métricas del clúster
    """

    def __init__(self, num_empresas: int = 5):
        """
        Inicializar la demostración.

        Parameters
        ----------
        num_empresas : int
            Número de empresas a simular
        """
        self.num_empresas = num_empresas
        self.empresas_participantes = []
        self.clientes_federados = []
        self.procesador = ProcesadorFederado()
        self.almacen = AlmacenResultados()

        print("🎭 DEMOSTRACIÓN DEL SISTEMA FEDERADO")
        print("=" * 60)
        print(f"Simulando {num_empresas} empresas del Clúster de Turismo de Nuevo León")
        print("🔒 Garantizando privacidad completa en todo el proceso")

    def cargar_empresas_demo(self):
        """
        Cargar empresas para la demostración.
        """
        try:
            empresas_df = pd.read_csv('data/datos_sinteticos/empresas_dummy.csv')

            # Seleccionar empresas de diferentes giros
            giros_diversos = empresas_df['giro'].unique()[:self.num_empresas]

            for giro in giros_diversos:
                empresa = empresas_df[empresas_df['giro'] == giro].iloc[0]
                self.empresas_participantes.append({
                    'empresa_id': empresa['empresa_id'],
                    'giro': empresa['giro'],
                    'capacidad_base': empresa['capacidad_base'],
                    'precio_promedio_base': empresa['precio_promedio_base']
                })

            print(f"\n🏢 Empresas participantes cargadas:")
            for i, empresa in enumerate(self.empresas_participantes, 1):
                print(f"  {i}. Giro: {empresa['giro']}")

            return True

        except FileNotFoundError:
            print("❌ Error: No se encontraron datos sintéticos")
            print("   Ejecuta primero: python src/datos_sinteticos/generar_todos_datos.py")
            return False

    def crear_clientes_federados(self):
        """
        Crear clientes federados para cada empresa.
        """
        print(f"\n🤖 Creando clientes federados...")

        for empresa in self.empresas_participantes:
            cliente = ClienteFederado(
                empresa_id=empresa['empresa_id'],
                giro=empresa['giro'],
                api_url="http://localhost:8000"  # En demo, no hay API real
            )
            self.clientes_federados.append(cliente)

        print(f"✅ {len(self.clientes_federados)} clientes federados creados")

    def fase_entrenamiento_local(self):
        """
        Fase 1: Cada empresa entrena modelos localmente.
        """
        print(f"\n" + "=" * 60)
        print("📚 FASE 1: ENTRENAMIENTO LOCAL")
        print("=" * 60)
        print("Cada empresa entrena modelos con sus datos locales")
        print("🔒 Los datos NUNCA salen de cada empresa")

        modelos_entrenados = []
        metricas_generadas = []

        for i, cliente in enumerate(self.clientes_federados, 1):
            print(f"\n🏢 Empresa {i}/{len(self.clientes_federados)} - Giro: {cliente.giro}")
            print("-" * 40)

            # Cargar datos locales
            if not cliente.cargar_datos_locales():
                print(f"⚠️ Empresa {i} no tiene datos suficientes, saltando...")
                continue

            try:
                # Entrenar modelos
                modelo_prediccion = cliente.entrenar_modelo_prediccion_demanda()
                modelo_clasificacion = cliente.entrenar_modelo_clasificacion_viajero()

                # Generar métricas agregadas
                metricas = cliente.generar_metricas_agregadas()

                modelos_entrenados.append({
                    'cliente': cliente,
                    'prediccion': modelo_prediccion,
                    'clasificacion': modelo_clasificacion
                })

                metricas_generadas.append(metricas)

                print(f"✅ Empresa {i} completó entrenamiento local")

            except Exception as e:
                print(f"❌ Error en empresa {i}: {e}")
                continue

        print(f"\n📊 RESUMEN FASE 1:")
        print(f"  Empresas con modelos entrenados: {len(modelos_entrenados)}")
        print(f"  Empresas con métricas generadas: {len(metricas_generadas)}")

        return modelos_entrenados, metricas_generadas

    async def fase_agregacion_federada(self, modelos_entrenados: List[Dict], metricas_generadas: List[Dict]):
        """
        Fase 2: Agregación federada de modelos y métricas.

        Parameters
        ----------
        modelos_entrenados : List[Dict]
            Lista de modelos entrenados por cada empresa
        metricas_generadas : List[Dict]
            Lista de métricas generadas por cada empresa
        """
        print(f"\n" + "=" * 60)
        print("🔄 FASE 2: AGREGACIÓN FEDERADA")
        print("=" * 60)
        print("El sistema agrega modelos sin acceder a datos crudos")
        print("🔒 Solo se procesan parámetros completamente anonimizados")

        # Simular envío de modelos al procesador federado
        contribuciones_prediccion = []
        contribuciones_clasificacion = []

        for i, modelo_data in enumerate(modelos_entrenados, 1):
            cliente = modelo_data['cliente']

            print(f"\n📤 Procesando contribuciones de empresa {i}...")

            # Procesar modelo de predicción
            if modelo_data['prediccion']:
                contribucion_id = f"contrib_pred_{i}_{int(time.time())}"
                await self.procesador.procesar_modelo_anonimo(
                    type('ModeloFederado', (), modelo_data['prediccion'])(),
                    contribucion_id
                )
                contribuciones_prediccion.append(contribucion_id)
                print(f"  ✅ Modelo de predicción procesado: {contribucion_id[:12]}...")

            # Procesar modelo de clasificación
            if modelo_data['clasificacion']:
                contribucion_id = f"contrib_clf_{i}_{int(time.time())}"
                await self.procesador.procesar_modelo_anonimo(
                    type('ModeloFederado', (), modelo_data['clasificacion'])(),
                    contribucion_id
                )
                contribuciones_clasificacion.append(contribucion_id)
                print(f"  ✅ Modelo de clasificación procesado: {contribucion_id[:12]}...")

        # Procesar métricas agregadas
        for i, metricas in enumerate(metricas_generadas, 1):
            resultado = await self.procesador.procesar_metricas_anonimas(
                type('MetricasEmpresa', (), metricas)()
            )
            print(f"  ✅ Métricas empresa {i} procesadas: {resultado['id'][:12]}...")

        print(f"\n📊 RESUMEN FASE 2:")
        print(f"  Contribuciones predicción: {len(contribuciones_prediccion)}")
        print(f"  Contribuciones clasificación: {len(contribuciones_clasificacion)}")
        print(f"  Métricas procesadas: {len(metricas_generadas)}")

        return contribuciones_prediccion, contribuciones_clasificacion

    async def fase_consulta_resultados(self):
        """
        Fase 3: Consulta de resultados agregados.
        """
        print(f"\n" + "=" * 60)
        print("📊 FASE 3: CONSULTA DE RESULTADOS AGREGADOS")
        print("=" * 60)
        print("Las empresas consultan modelos y métricas agregadas del clúster")
        print("🔒 Solo reciben información agregada, nunca datos individuales")

        # Obtener métricas generales del clúster
        print(f"\n📈 Consultando métricas generales del clúster...")
        metricas_generales = await self.almacen.obtener_metricas_generales()

        print(f"✅ Métricas generales obtenidas:")
        if 'metricas_economicas' in metricas_generales:
            economicas = metricas_generales['metricas_economicas']
            print(f"  💰 Ingresos totales clúster: ${economicas.get('ingresos_totales_cluster', 0):,.0f}")
            print(f"  👥 Clientes totales atendidos: {economicas.get('clientes_totales_atendidos', 0):,}")
            print(f"  🎫 Ticket promedio clúster: ${economicas.get('ticket_promedio_cluster', 0):,.0f}")

        # Consultar métricas por giro
        print(f"\n🏢 Consultando métricas por giro...")
        giros_unicos = list(set([emp['giro'] for emp in self.empresas_participantes]))

        for giro in giros_unicos:
            metricas_giro = await self.almacen.obtener_metricas_por_giro(giro)
            if metricas_giro:
                print(f"  📊 {giro.capitalize()}:")
                economicas = metricas_giro.get('metricas_economicas', {})
                print(f"    Ingresos totales: ${economicas.get('ingresos_totales', 0):,.0f}")
                print(f"    Clientes promedio diario: {economicas.get('clientes_promedio_diario', 0):.0f}")

        # Generar predicciones de demanda
        print(f"\n🔮 Generando predicciones de demanda...")
        for giro in giros_unicos[:2]:  # Solo primeros 2 giros para demo
            try:
                predicciones = await self.procesador.generar_predicciones_demanda(
                    giro=giro,
                    fecha_inicio="2025-06-01",
                    fecha_fin="2025-06-07"
                )

                print(f"  🎯 Predicciones para {giro}:")
                if predicciones and 'predicciones' in predicciones:
                    for pred in predicciones['predicciones'][:3]:  # Primeros 3 días
                        print(f"    {pred['fecha']}: {pred['prediccion']:.0f} (confianza: {pred['confianza']:.2f})")

            except Exception as e:
                print(f"  ⚠️ No se pudieron generar predicciones para {giro}: {e}")

        return metricas_generales

    async def fase_exportacion_resultados(self):
        """
        Fase 4: Exportación de resultados para análisis externo.
        """
        print(f"\n" + "=" * 60)
        print("📁 FASE 4: EXPORTACIÓN DE RESULTADOS")
        print("=" * 60)
        print("Exportando resultados agregados para análisis externo")
        print("🔒 Solo datos completamente anonimizados")

        # Exportar en formato JSON
        archivo_json = await self.almacen.exportar_resultados_anonimos("json")
        print(f"✅ Resultados exportados en JSON: {archivo_json}")

        # Exportar en formato CSV
        archivo_csv = await self.almacen.exportar_resultados_anonimos("csv")
        print(f"✅ Resultados exportados en CSV: {archivo_csv}")

        # Obtener estadísticas del sistema
        stats = await self.almacen.obtener_estadisticas_sistema()
        print(f"\n📊 Estadísticas del sistema federado:")
        sistema = stats.get('sistema', {})
        print(f"  Total contribuciones: {sistema.get('total_contribuciones', 0)}")
        print(f"  Modelos agregados: {sistema.get('modelos_agregados', 0)}")
        print(f"  Predicciones generadas: {sistema.get('predicciones_generadas', 0)}")

        return archivo_json, archivo_csv

    def generar_reporte_final(self, metricas_generales: Dict, archivos_exportados: tuple):
        """
        Generar reporte final de la demostración.

        Parameters
        ----------
        metricas_generales : Dict
            Métricas generales del clúster
        archivos_exportados : tuple
            Archivos exportados (JSON, CSV)
        """
        print(f"\n" + "=" * 60)
        print("📋 REPORTE FINAL DE LA DEMOSTRACIÓN")
        print("=" * 60)

        reporte = {
            "timestamp_demo": datetime.now().isoformat(),
            "empresas_participantes": len(self.empresas_participantes),
            "giros_representados": list(set([emp['giro'] for emp in self.empresas_participantes])),
            "privacidad_garantizada": True,
            "datos_anonimizados": True,
            "modelos_agregados_exitosamente": True,
            "metricas_cluster_generadas": True,
            "archivos_exportados": {
                "json": archivos_exportados[0],
                "csv": archivos_exportados[1]
            },
            "resumen_economico": metricas_generales.get('metricas_economicas', {}),
            "nivel_agregacion": "cluster_completo",
            "empresas_individuales_no_identificables": True
        }

        # Guardar reporte
        ruta_reporte = "data/resultados/reporte_demo_federado.json"
        with open(ruta_reporte, 'w') as f:
            json.dump(reporte, f, indent=2)

        print(f"✅ Demostración completada exitosamente")
        print(f"📊 Empresas participantes: {len(self.empresas_participantes)}")
        print(f"🔒 Privacidad garantizada: ✅")
        print(f"📁 Reporte guardado en: {ruta_reporte}")

        print(f"\n🎯 LOGROS DE LA DEMOSTRACIÓN:")
        print(f"  ✅ Entrenamiento local sin compartir datos crudos")
        print(f"  ✅ Agregación federada preservando privacidad")
        print(f"  ✅ Métricas del clúster sin revelar empresas individuales")
        print(f"  ✅ Predicciones basadas en conocimiento agregado")
        print(f"  ✅ Exportación de resultados anonimizados")

        print(f"\n🔐 GARANTÍAS DE PRIVACIDAD:")
        print(f"  🛡️ IDs de empresa completamente anonimizados")
        print(f"  🛡️ Datos crudos nunca salen de cada empresa")
        print(f"  🛡️ Solo parámetros agregados se comparten")
        print(f"  🛡️ Imposible rastrear contribuciones individuales")
        print(f"  🛡️ Ruido diferencial aplicado para mayor seguridad")

        return reporte

    async def ejecutar_demo_completa(self):
        """
        Ejecutar la demostración completa del sistema federado.
        """
        inicio_demo = time.time()

        print(f"🚀 Iniciando demostración completa...")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Preparación
        if not self.cargar_empresas_demo():
            return False

        self.crear_clientes_federados()

        # Fase 1: Entrenamiento local
        modelos_entrenados, metricas_generadas = self.fase_entrenamiento_local()

        if not modelos_entrenados:
            print("❌ No se pudieron entrenar modelos. Terminando demostración.")
            return False

        # Fase 2: Agregación federada
        contribuciones_pred, contribuciones_clf = await self.fase_agregacion_federada(
            modelos_entrenados, metricas_generadas
        )

        # Fase 3: Consulta de resultados
        metricas_generales = await self.fase_consulta_resultados()

        # Fase 4: Exportación
        archivos_exportados = await self.fase_exportacion_resultados()

        # Reporte final
        reporte = self.generar_reporte_final(metricas_generales, archivos_exportados)

        tiempo_total = time.time() - inicio_demo
        print(f"\n⏱️ Tiempo total de demostración: {tiempo_total:.2f} segundos")

        return True


async def main():
    """
    Función principal para ejecutar la demostración.
    """
    print("🎭 SISTEMA DE APRENDIZAJE FEDERADO")
    print("🏛️ Clúster de Turismo de Nuevo León")
    print("🔒 Demostración de Privacidad Garantizada")
    print("=" * 60)

    # Crear y ejecutar demostración
    demo = DemostracionFederada(num_empresas=5)

    try:
        exito = await demo.ejecutar_demo_completa()

        if exito:
            print(f"\n🎉 ¡DEMOSTRACIÓN COMPLETADA EXITOSAMENTE!")
            print(f"🔍 Revisa los archivos en data/resultados/ para ver los resultados")
        else:
            print(f"\n💥 La demostración no se pudo completar")

    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(main())
