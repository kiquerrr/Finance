# -*- coding: utf-8 -*-
"""
=============================================================================
SISTEMA DE GESTIÓN DE ARBITRAJE P2P
Versión 2.0 - Mejorado
=============================================================================
Sistema completo para gestión de operaciones de arbitraje P2P
con logging, cálculos precisos y mantenimiento profesional
"""

import os
import sys
from datetime import datetime

# Importar módulos del sistema
try:
    from logger import log
    from calculos import calc
    from configuracion import menu_configuracion
    from mantenimiento import menu_mantenimiento, obtener_info_sistema
    from ciclos import (
        obtener_ciclo_activo, 
        gestionar_ciclo_activo,
        mostrar_estadisticas_completas
    )
    from boveda import menu_boveda
    from operador import modulo_operador
    import sqlite3
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print("Asegúrate de tener todos los módulos necesarios:")
    print("  - logger.py")
    print("  - calculos.py")
    print("  - configuracion.py")
    print("  - mantenimiento.py")
    print("  - ciclos.py")
    print("  - boveda.py")
    print("  - dias.py")
    print("  - operador.py")
    sys.exit(1)


# ===================================================================
# CONFIGURACIÓN
# ===================================================================

VERSION = "2.0"
TITULO = "SISTEMA DE GESTIÓN DE ARBITRAJE P2P"


# ===================================================================
# FUNCIONES AUXILIARES
# ===================================================================

def limpiar_pantalla():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa y espera Enter"""
    input("\nPresiona Enter para continuar...")


def mostrar_banner():
    """Muestra el banner del sistema"""
    ciclo = obtener_ciclo_activo()
    
    print("\n" + "="*60)
    print("║" + " "*58 + "║")
    print("║" + TITULO.center(58) + "║")
    print("║" + f"Versión {VERSION} - Mejorado".center(58) + "║")
    print("║" + " "*58 + "║")
    print("="*60)
    
    if ciclo:
        print(f"\n🔄 Ciclo Activo: #{ciclo['id']}")
    else:
        print(f"\n⚠️  No hay ciclo activo")


def verificar_base_datos():
    """Verifica que la base de datos esté configurada correctamente"""
    try:
        # Usar la función de inicialización automática
        from inicializar_bd import setup_inicial
        
        if setup_inicial():
            return True
        else:
            print("\n❌ No se pudo inicializar la base de datos")
            pausar()
            return False
        
    except ImportError:
        print("\n❌ Error: No se encuentra el archivo inicializar_bd.py")
        print("   Asegúrate de tener todos los archivos del sistema")
        pausar()
        return False
    except Exception as e:
        print(f"❌ Error al verificar base de datos: {e}")
        pausar()
        return False


# ===================================================================
# MÓDULOS PRINCIPALES
# ===================================================================

def modulo_consultas():
    """Módulo de consultas y estadísticas"""
    while True:
        limpiar_pantalla()
        print("\n" + "="*60)
        print("CONSULTAS Y ESTADÍSTICAS")
        print("="*60)
        
        print("\n[1] Estadísticas Generales de Ciclos")
        print("[2] Progreso del Ciclo Actual")
        print("[3] Historial de Días")
        print("[4] Resumen de Ventas")
        print("[5] Estado de la Bóveda")
        print("[6] Ver Logs del Sistema")
        print("[7] Volver al Menú Principal")
        print("="*60)
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            mostrar_estadisticas_completas()
            pausar()
        
        elif opcion == "2":
            ciclo = obtener_ciclo_activo()
            if ciclo:
                from dias import mostrar_progreso_ciclo
                mostrar_progreso_ciclo(ciclo['id'])
            else:
                print("\n⚠️  No hay ciclo activo")
            pausar()
        
        elif opcion == "3":
            ciclo = obtener_ciclo_activo()
            if ciclo:
                from dias import obtener_resumen_dias
                dias = obtener_resumen_dias(ciclo['id'])
                
                print("\n" + "="*60)
                print("HISTORIAL DE DÍAS")
                print("="*60)
                
                for dia in dias:
                    estado_emoji = "✅" if dia['estado'] == 'cerrado' else "🔄"
                    print(f"\n{estado_emoji} Día #{dia['numero_dia']} - {dia['fecha']}")
                    print(f"   Capital inicial: ${dia['capital_inicial']:.2f}")
                    print(f"   Capital final: ${dia['capital_final']:.2f}")
                    print(f"   Ganancia: ${dia['ganancia_neta']:.2f}")
                    print(f"   Estado: {dia['estado'].upper()}")
            else:
                print("\n⚠️  No hay ciclo activo")
            pausar()
        
        elif opcion == "4":
            print("\n[Función de resumen de ventas - Por implementar]")
            pausar()
        
        elif opcion == "5":
            from boveda import consultar_boveda
            consultar_boveda()
            pausar()
        
        elif opcion == "6":
            submenu_logs()
        
        elif opcion == "7":
            break
        
        else:
            print("❌ Opción inválida")
            pausar()


def submenu_logs():
    """Submenú para ver logs"""
    while True:
        limpiar_pantalla()
        print("\n" + "="*60)
        print("LOGS DEL SISTEMA")
        print("="*60)
        
        print("\n[1] Log General")
        print("[2] Log de Operaciones")
        print("[3] Log de Cálculos")
        print("[4] Log de Errores")
        print("[5] Log de Bóveda")
        print("[6] Log de Ciclos")
        print("[7] Buscar en Logs")
        print("[8] Volver")
        print("="*60)
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion in ["1", "2", "3", "4", "5", "6"]:
            categorias = {
                "1": "general",
                "2": "operaciones",
                "3": "calculos",
                "4": "errores",
                "5": "boveda",
                "6": "ciclos"
            }
            
            categoria = categorias[opcion]
            
            try:
                lineas_input = input("\n¿Cuántas líneas mostrar? (50): ").strip()
                lineas = int(lineas_input) if lineas_input else 50
            except ValueError:
                lineas = 50
            
            from logger import ver_log
            contenido = ver_log(categoria, lineas)
            
            print("\n" + "="*60)
            print(f"LOG: {categoria.upper()}")
            print("="*60)
            print(contenido)
            pausar()
        
        elif opcion == "7":
            texto = input("\nTexto a buscar: ").strip()
            categoria = input("Categoría (general/operaciones/calculos/errores/boveda/ciclos): ").strip()
            
            from logger import buscar_en_logs
            resultados = buscar_en_logs(texto, categoria)
            
            print(f"\n{len(resultados)} resultado(s) encontrado(s):")
            for resultado in resultados[:20]:  # Mostrar máximo 20
                print(resultado)
            pausar()
        
        elif opcion == "8":
            break
        
        else:
            print("❌ Opción inválida")
            pausar()


# ===================================================================
# MENÚ PRINCIPAL
# ===================================================================

def menu_principal():
    """Menú principal del sistema"""
    
    # Verificar base de datos al inicio
    if not verificar_base_datos():
        print("❌ No se pudo verificar la base de datos")
        return
    
    # Registrar inicio del sistema
    log.info("Sistema iniciado", categoria='general')
    
    while True:
        limpiar_pantalla()
        mostrar_banner()
        
        print("\n" + "="*60)
        print("MENÚ PRINCIPAL")
        print("="*60)
        print("[1] 🔄 Iniciar/Continuar Ciclo Diario (Operador)")
        print("[2] 💰 Gestión de Bóveda")
        print("[3] 📊 Consultas y Estadísticas")
        print("[4] ⚙️  Configuración")
        print("[5] 🔧 Mantenimiento")
        print("[6] 🚪 Salir")
        print("="*60)
        
        # Mostrar información del sistema
        try:
            info = obtener_info_sistema()
            print(f"\nℹ️  BD: {info['tamaño_bd']:.1f}MB | Backups: {info['num_backups']} | Logs: {info['tamaño_logs']:.1f}MB")
        except:
            pass
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            # Módulo Operador
            try:
                modulo_operador()
            except Exception as e:
                log.error("Error en módulo operador", str(e))
                print(f"\n❌ Error en el módulo operador: {e}")
                pausar()
        
        elif opcion == "2":
            # Gestión de Bóveda
            try:
                menu_boveda()
            except Exception as e:
                log.error("Error en gestión de bóveda", str(e))
                print(f"\n❌ Error en gestión de bóveda: {e}")
                pausar()
        
        elif opcion == "3":
            # Consultas y Estadísticas
            try:
                modulo_consultas()
            except Exception as e:
                log.error("Error en consultas", str(e))
                print(f"\n❌ Error en consultas: {e}")
                pausar()
        
        elif opcion == "4":
            # Configuración
            try:
                menu_configuracion()
            except Exception as e:
                log.error("Error en configuración", str(e))
                print(f"\n❌ Error en configuración: {e}")
                pausar()
        
        elif opcion == "5":
            # Mantenimiento
            try:
                menu_mantenimiento()
            except Exception as e:
                log.error("Error en mantenimiento", str(e))
                print(f"\n❌ Error en mantenimiento: {e}")
                pausar()
        
        elif opcion == "6":
            # Salir
            print("\n" + "="*60)
            confirmar = input("¿Estás seguro de que deseas salir? (s/n): ").strip().lower()
            
            if confirmar == 's':
                log.info("Sistema cerrado por el usuario", categoria='general')
                print("\n👋 ¡Hasta pronto!")
                print("="*60)
                break
        
        else:
            print("\n❌ Opción inválida")
            pausar()


# ===================================================================
# PUNTO DE ENTRADA
# ===================================================================

def main():
    """Función principal del programa"""
    
    try:
        # Mensaje de bienvenida
        limpiar_pantalla()
        print("\n" + "="*60)
        print("║" + " "*58 + "║")
        print("║" + TITULO.center(58) + "║")
        print("║" + f"Versión {VERSION}".center(58) + "║")
        print("║" + " "*58 + "║")
        print("="*60)
        print("\n✨ Iniciando sistema...")
        
        # Verificar estructura de directorios
        import os
        for directorio in ['logs', 'backups', 'exports']:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                print(f"   ✓ Directorio '{directorio}' creado")
        
        print("\n✅ Sistema listo")
        pausar()
        
        # Ejecutar menú principal
        menu_principal()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción del usuario detectada")
        log.advertencia("Sistema interrumpido por usuario (Ctrl+C)", categoria='general')
        print("👋 Cerrando sistema...")
    
    except Exception as e:
        print(f"\n\n❌ ERROR CRÍTICO: {e}")
        log.error("Error crítico en main", str(e), categoria='errores')
        print("\nPor favor, revisa los logs o contacta soporte")
        pausar()
    
    finally:
        print("\n" + "="*60)
        print("Sistema cerrado")
        print("="*60 + "\n")


# ===================================================================
# EJECUCIÓN
# ===================================================================

if __name__ == "__main__":
    main()
