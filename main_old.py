# -*- coding: utf-8 -*-
"""
=============================================================================
SISTEMA DE ARBITRAJE P2P - MENÚ PRINCIPAL
=============================================================================
Sistema completo de gestión de arbitraje de criptomonedas
Versión 3.0 - Actualizado con todas las funcionalidades
"""

import os
import sys
from datetime import datetime

# Imports de módulos core
from logger import log
from db_manager import db, verificar_conexion

# Imports de módulos principales
from boveda import menu_boveda
from ciclos import menu_ciclos
from operador import menu_operador_avanzado
from configuracion import menu_configuracion
from mantenimiento import menu_mantenimiento

# Imports de nuevas funcionalidades
from proyecciones import menu_proyecciones
from reportes import menu_reportes
from notas import menu_notas
from alertas import menu_alertas, mostrar_banner_alertas, SistemaAlertas
from graficos import menu_graficos, verificar_matplotlib

# Imports de utilidades
from queries import queries


# ===================================================================
# FUNCIONES DE UTILIDAD
# ===================================================================

def limpiar_pantalla():
    """Limpia la pantalla según el sistema operativo"""
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_banner():
    """Muestra el banner del sistema"""
    print("\n" + "="*70)
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║           SISTEMA DE ARBITRAJE P2P - VERSIÓN 3.0                 ║")
    print("║                  Gestión Completa de Operaciones                  ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print("="*70)


def mostrar_info_sistema():
    """Muestra información del sistema al inicio"""
    
    # Verificar conexión a BD
    if not verificar_conexion():
        print("\n❌ ERROR: No se pudo conectar a la base de datos")
        print("   Ejecuta 'python inicializar_bd.py' primero")
        sys.exit(1)
    
    # Obtener estadísticas generales
    stats = queries.obtener_estadisticas_generales()
    
    print(f"\n📊 Estado del Sistema:")
    print(f"   Ciclos totales: {stats['total_ciclos']}")
    print(f"   Ciclos activos: {stats['ciclos_activos']}")
    print(f"   Días operados: {stats['dias_operados']}")
    print(f"   Ventas totales: {stats['total_ventas']}")
    
    if stats['ganancia_total'] > 0:
        print(f"   Ganancia acumulada: ${stats['ganancia_total']:.2f}")
    
    # Mostrar ciclo activo si existe
    ciclo = queries.obtener_ciclo_activo()
    if ciclo:
        print(f"\n🔄 Ciclo activo: #{ciclo['id']}")
        
        # Verificar si hay día abierto
        dia_abierto = queries.obtener_dia_abierto(ciclo['id'])
        if dia_abierto:
            print(f"   📅 Día #{dia_abierto['numero_dia']} abierto")
    else:
        print("\n⚠️  No hay ciclo activo")
    
    print("="*70)


def verificar_alertas_inicio():
    """Verifica y muestra alertas al inicio"""
    try:
        # Verificar alertas del sistema
        sistema = SistemaAlertas()
        sistema.verificar_todas()
        
        # Mostrar banner si hay alertas
        mostrar_banner_alertas()
        
    except Exception as e:
        log.error("Error al verificar alertas", str(e))
        # No bloquear el sistema si falla


# ===================================================================
# MENÚS
# ===================================================================

def menu_operaciones():
    """Menú de operaciones diarias"""
    
    while True:
        limpiar_pantalla()
        print("\n" + "="*70)
        print("OPERACIONES DIARIAS")
        print("="*70)
        print("[1] Iniciar/Continuar Día de Operación")
        print("[2] Menú Avanzado del Operador")
        print("[3] Volver")
        print("="*70)
        
        opcion = input("\nSelecciona: ").strip()
        
        if opcion == "1":
            from operador import modulo_operador
            modulo_operador()
        elif opcion == "2":
            menu_operador_avanzado()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida")
            input("\nPresiona Enter...")


def menu_analisis():
    """Menú de análisis y reportes"""
    
    while True:
        limpiar_pantalla()
        print("\n" + "="*70)
        print("ANÁLISIS Y REPORTES")
        print("="*70)
        print("[1] Proyecciones y Simulaciones")
        print("[2] Generar Reportes")
        print("[3] Gráficos de Rendimiento")
        print("[4] Estadísticas Generales")
        print("[5] Volver")
        print("="*70)
        
        opcion = input("\nSelecciona: ").strip()
        
        if opcion == "1":
            menu_proyecciones()
        elif opcion == "2":
            menu_reportes()
        elif opcion == "3":
            if verificar_matplotlib():
                menu_graficos()
            else:
                print("\n⚠️  matplotlib no está instalado")
                print("Instala con: pip install matplotlib --break-system-packages")
                input("\nPresiona Enter...")
        elif opcion == "4":
            mostrar_estadisticas_detalladas()
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida")
            input("\nPresiona Enter...")


def menu_gestion():
    """Menú de gestión del sistema"""
    
    while True:
        limpiar_pantalla()
        print("\n" + "="*70)
        print("GESTIÓN DEL SISTEMA")
        print("="*70)
        print("[1] Gestión de Bóveda")
        print("[2] Gestión de Ciclos")
        print("[3] Configuración")
        print("[4] Notas y Observaciones")
        print("[5] Sistema de Alertas")
        print("[6] Mantenimiento")
        print("[7] Volver")
        print("="*70)
        
        opcion = input("\nSelecciona: ").strip()
        
        if opcion == "1":
            menu_boveda()
        elif opcion == "2":
            menu_ciclos()
        elif opcion == "3":
            menu_configuracion()
        elif opcion == "4":
            menu_notas()
        elif opcion == "5":
            menu_alertas()
        elif opcion == "6":
            menu_mantenimiento()
        elif opcion == "7":
            break
        else:
            print("❌ Opción inválida")
            input("\nPresiona Enter...")


def mostrar_estadisticas_detalladas():
    """Muestra estadísticas detalladas del sistema"""
    
    limpiar_pantalla()
    print("\n" + "="*70)
    print("ESTADÍSTICAS COMPLETAS DEL SISTEMA")
    print("="*70)
    
    stats = queries.obtener_estadisticas_generales()
    
    print("\n📊 RESUMEN GENERAL:")
    print(f"   Total de ciclos: {stats['total_ciclos']}")
    print(f"   Ciclos activos: {stats['ciclos_activos']}")
    print(f"   Días operados: {stats['dias_operados']}")
    print(f"   Total de ventas: {stats['total_ventas']}")
    print(f"   Total de compras: {stats['total_compras']}")
    
    print(f"\n💰 FINANCIERO:")
    print(f"   Capital invertido: ${stats['capital_invertido']:.2f}")
    print(f"   Ganancia total: ${stats['ganancia_total']:.2f}")
    
    if stats['capital_invertido'] > 0:
        roi_global = (stats['ganancia_total'] / stats['capital_invertido']) * 100
        print(f"   ROI global: {roi_global:.2f}%")
    
    # Estadísticas del ciclo activo
    ciclo = queries.obtener_ciclo_activo()
    if ciclo:
        print(f"\n🔄 CICLO ACTIVO (#{ciclo['id']}):")
        print(f"   Fecha inicio: {ciclo['fecha_inicio']}")
        print(f"   Días operados: {ciclo['dias_operados']}/{ciclo['dias_planificados']}")
        print(f"   Inversión inicial: ${ciclo['inversion_inicial']:.2f}")
        
        # Capital en bóveda
        capital_boveda = queries.obtener_capital_boveda(ciclo['id'])
        print(f"   Capital en bóveda: ${capital_boveda:.2f}")
        
        # Ganancia acumulada del ciclo
        with db.get_cursor(commit=False) as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(ganancia_neta), 0) as total
                FROM dias WHERE ciclo_id = ? AND estado = 'cerrado'
            """, (ciclo['id'],))
            ganancia_ciclo = cursor.fetchone()['total']
        
        print(f"   Ganancia acumulada: ${ganancia_ciclo:.2f}")
        
        if ciclo['inversion_inicial'] > 0:
            roi_ciclo = (ganancia_ciclo / ciclo['inversion_inicial']) * 100
            print(f"   ROI ciclo: {roi_ciclo:.2f}%")
    
    # Configuración actual
    config = queries.obtener_config()
    if config:
        print(f"\n⚙️  CONFIGURACIÓN:")
        print(f"   Comisión: {config['comision_default']}%")
        print(f"   Ganancia objetivo: {config['ganancia_neta_default']}%")
        print(f"   Límites de ventas: {config['limite_ventas_min']}-{config['limite_ventas_max']}/día")
    
    # Alertas pendientes
    from alertas import SistemaAlertas
    sistema_alertas = SistemaAlertas()
    num_alertas = sistema_alertas.contar_alertas_no_leidas()
    
    if num_alertas > 0:
        print(f"\n🔔 ALERTAS:")
        print(f"   {num_alertas} alerta(s) pendiente(s)")
    
    print("\n" + "="*70)
    
    input("\nPresiona Enter para volver...")


def menu_ayuda():
    """Menú de ayuda y documentación"""
    
    limpiar_pantalla()
    print("\n" + "="*70)
    print("AYUDA Y DOCUMENTACIÓN")
    print("="*70)
    
    print("""
📖 GUÍA RÁPIDA:

1. PRIMER USO:
   • Ejecuta 'python inicializar_bd.py' para crear la BD
   • Configura comisión y ganancia objetivo en Configuración
   • Fondea la bóveda comprando criptomonedas

2. OPERACIÓN DIARIA:
   • Operaciones > Iniciar Día
   • Define precio de venta
   • Registra ventas
   • Cierra el día
   • (Opcional) Aplica interés compuesto

3. CICLOS:
   • Un ciclo es un período de operación (ej: 15 días)
   • Se crea automáticamente al operar
   • Puedes extenderlo o cerrarlo manualmente

4. REPORTES Y ANÁLISIS:
   • Proyecciones: Simula escenarios futuros
   • Reportes: Exporta datos a CSV/TXT
   • Gráficos: Visualiza tu rendimiento

5. ALERTAS:
   • El sistema detecta situaciones importantes
   • Revisa alertas regularmente

6. MANTENIMIENTO:
   • Crea backups periódicamente
   • Optimiza la BD cada mes
   • Verifica integridad si hay problemas

7. NOTAS:
   • Documenta incidentes y aprendizajes
   • Útil para mejorar estrategias

📁 ARCHIVOS IMPORTANTES:
   • arbitraje.db - Base de datos principal
   • logs/ - Registro de todas las operaciones
   • backups/ - Copias de seguridad
   • reportes/ - Reportes exportados
   • graficos/ - Gráficos generados

🔧 COMANDOS ÚTILES:
   • python main.py - Iniciar sistema
   • python inicializar_bd.py - Reiniciar BD
   • pip install -r requirements.txt - Instalar dependencias

⚠️  RECOMENDACIONES:
   • Haz backups antes de operaciones importantes
   • No cierres días sin haber registrado ventas
   • Respeta los límites de ventas para evitar bloqueos
   • Documenta incidentes importantes en Notas
   • Revisa alertas al inicio de cada sesión

📞 SOPORTE:
   • Logs detallados en logs/
   • Verifica integridad en Mantenimiento
   • Consulta el README.md para más info
    """)
    
    print("="*70)
    input("\nPresiona Enter para volver...")


# ===================================================================
# MENÚ PRINCIPAL
# ===================================================================

def menu_principal():
    """Menú principal del sistema"""
    
    while True:
        limpiar_pantalla()
        mostrar_banner()
        mostrar_info_sistema()
        
        print("\n" + "="*70)
        print("MENÚ PRINCIPAL")
        print("="*70)
        print("[1] Operaciones Diarias")
        print("[2] Análisis y Reportes")
        print("[3] Gestión del Sistema")
        print("[4] Ayuda y Documentación")
        print("[5] Salir")
        print("="*70)
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            menu_operaciones()
        elif opcion == "2":
            menu_analisis()
        elif opcion == "3":
            menu_gestion()
        elif opcion == "4":
            menu_ayuda()
        elif opcion == "5":
            confirmar_salida()
            break
        else:
            print("\n❌ Opción inválida")
            input("\nPresiona Enter para continuar...")


def confirmar_salida():
    """Confirma salida del sistema"""
    
    print("\n" + "="*70)
    
    # Verificar si hay día abierto
    ciclo = queries.obtener_ciclo_activo()
    if ciclo:
        dia_abierto = queries.obtener_dia_abierto(ciclo['id'])
        if dia_abierto:
            print("⚠️  ADVERTENCIA: Hay un día abierto")
            print(f"   Día #{dia_abierto['numero_dia']} del ciclo #{ciclo['id']}")
            print("   Considera cerrarlo antes de salir")
            print()
    
    # Alertas pendientes
    from alertas import SistemaAlertas
    sistema_alertas = SistemaAlertas()
    num_alertas = sistema_alertas.contar_alertas_no_leidas()
    
    if num_alertas > 0:
        print(f"🔔 Tienes {num_alertas} alerta(s) pendiente(s)")
        print()
    
    print("¿Estás seguro que deseas salir?")
    confirmar = input("(s/n): ").lower()
    
    if confirmar == 's':
        print("\n👋 ¡Hasta pronto!")
        print("="*70)
        log.info("Sistema cerrado por el usuario", categoria='general')
    else:
        print("\n✅ Continuando...")
        input("\nPresiona Enter...")


# ===================================================================
# INICIALIZACIÓN
# ===================================================================

def inicializar_sistema():
    """Inicializa el sistema y verifica requisitos"""
    
    try:
        # Verificar conexión a BD
        if not verificar_conexion():
            print("\n❌ ERROR: No se pudo conectar a la base de datos")
            print("\n💡 Solución:")
            print("   1. Ejecuta: python inicializar_bd.py")
            print("   2. Si el problema persiste, verifica que arbitraje.db existe")
            sys.exit(1)
        
        # Verificar estructura de directorios
        from pathlib import Path
        directorios = ['logs', 'backups', 'reportes', 'graficos']
        for directorio in directorios:
            Path(directorio).mkdir(exist_ok=True)
        
        # Verificar alertas al inicio
        verificar_alertas_inicio()
        
        log.info("Sistema iniciado correctamente", categoria='general')
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        log.error("Error al inicializar sistema", str(e))
        sys.exit(1)


# ===================================================================
# PUNTO DE ENTRADA
# ===================================================================

def main():
    """Función principal"""
    
    try:
        # Inicializar sistema
        if not inicializar_sistema():
            return
        
        # Mostrar banner inicial
        limpiar_pantalla()
        mostrar_banner()
        print("\n🚀 Sistema iniciado correctamente")
        print("📝 Todos los logs se guardan en: logs/")
        input("\nPresiona Enter para continuar...")
        
        # Iniciar menú principal
        menu_principal()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción por teclado detectada")
        print("👋 Cerrando sistema...")
        log.info("Sistema interrumpido por usuario (Ctrl+C)", categoria='general')
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        log.error("Error inesperado en main", str(e))
        input("\nPresiona Enter para salir...")
    
    finally:
        print("\n" + "="*70)
        print("Sistema cerrado")
        print("="*70)


if __name__ == "__main__":
    main()
