# -*- coding: utf-8 -*-
import os
import sys
import sqlite3

# Importar módulos del sistema
import operador
import boveda
import estadisticas
import database
import utils

# =================================================
# MÓDULOS DE CONFIGURACIÓN Y BASE DE DATOS
# =================================================

def obtener_config(clave):
    """Obtiene un valor de configuración de la base de datos."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"❌ Error al obtener configuración: {e}")
        return None

def actualizar_config(clave, valor):
    """Actualiza un valor de configuración en la base de datos."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, str(valor)))
        conn.commit()
        conn.close()
        print(f"✅ Configuración actualizada: {clave} = {valor}")
    except sqlite3.Error as e:
        print(f"❌ Error al actualizar configuración: {e}")

def modulo_configuracion():
    """Módulo de configuración y mantenimiento del sistema."""
    while True:
        utils.limpiar_pantalla()
        utils.mostrar_separador()
        print("CONFIGURACIÓN Y MANTENIMIENTO")
        utils.mostrar_separador()
        
        comision = obtener_config('comision_defecto') or "No establecido"
        ganancia = obtener_config('ganancia_defecto') or "No establecido"
        
        print(f"\n📊 Configuración Actual:")
        print(f"   Comisión por defecto: {comision}%")
        print(f"   Ganancia neta objetivo: {ganancia}%")
        
        print("\n" + "=" * 60)
        print("[1] Modificar Comisión por Defecto")
        print("[2] Modificar Ganancia Neta por Defecto")
        print("[3] Verificar Integridad de la Base de Datos")
        print("[4] Crear Backup de la Base de Datos")
        print("[5] Volver al Menú Principal")
        utils.mostrar_separador()
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == '1':
            try:
                print("\n📝 Modificar Comisión por Defecto")
                print(f"   Valor actual: {comision}%")
                nuevo_valor = utils.validar_numero_positivo(
                    "Ingrese el nuevo % de comisión (ej: 0.35 para 0.35%): ",
                    permitir_cero=True
                )
                if utils.validar_rango(nuevo_valor, 0, 10, "comisión"):
                    actualizar_config('comision_defecto', nuevo_valor)
                utils.pausar()
            except Exception as e:
                print(f"❌ Error: {e}")
                utils.pausar()
                
        elif opcion == '2':
            try:
                print("\n📝 Modificar Ganancia Neta por Defecto")
                print(f"   Valor actual: {ganancia}%")
                nuevo_valor = utils.validar_numero_positivo(
                    "Ingrese el nuevo % de ganancia objetivo (ej: 2.0 para 2%): ",
                    permitir_cero=True
                )
                if utils.validar_rango(nuevo_valor, 0, 50, "ganancia"):
                    actualizar_config('ganancia_defecto', nuevo_valor)
                utils.pausar()
            except Exception as e:
                print(f"❌ Error: {e}")
                utils.pausar()
                
        elif opcion == '3':
            database.verificar_integridad_db()
            utils.pausar()
            
        elif opcion == '4':
            if utils.confirmar_accion("¿Deseas crear un backup de la base de datos?"):
                database.hacer_backup_db()
            utils.pausar()
            
        elif opcion == '5':
            break
        else:
            print("\n❌ Opción no válida.")
            utils.pausar()

# =================================================
# PROGRAMA PRINCIPAL Y MENÚ
# =================================================

def mostrar_banner():
    """Muestra el banner del sistema."""
    utils.limpiar_pantalla()
    print("=" * 60)
    print("║" + " " * 58 + "║")
    print("║" + "  SISTEMA DE GESTIÓN DE ARBITRAJE P2P".center(58) + "║")
    print("║" + "  Versión 2.0 - Mejorado".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("=" * 60)

def mostrar_menu_principal():
    """Muestra el menú principal y maneja la selección del usuario."""
    # Verificar/crear base de datos al inicio
    database.crear_base_de_datos()
    
    while True:
        mostrar_banner()
        
        # Mostrar información del ciclo activo si existe
        ciclo_activo = utils.obtener_ciclo_activo_id()
        if ciclo_activo:
            print(f"\n🔄 Ciclo Activo: #{ciclo_activo}")
        else:
            print("\n⚠️  No hay ciclo activo")
        
        print("\n" + "=" * 60)
        print("MENÚ PRINCIPAL")
        print("=" * 60)
        print("[1] 🔄 Iniciar/Continuar Ciclo Diario (Operador)")
        print("[2] 💰 Gestión de Bóveda")
        print("[3] 📊 Consultas y Estadísticas")
        print("[4] ⚙️  Configuración y Mantenimiento")
        print("[5] 🚪 Salir")
        utils.mostrar_separador()
        
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            try:
                operador.ejecutar_dia_de_trabajo()
                utils.pausar()
            except Exception as e:
                print(f"\n❌ Error en el módulo operador: {e}")
                utils.pausar()
                
        elif opcion == '2':
            try:
                boveda.mostrar_menu_boveda()
            except Exception as e:
                print(f"\n❌ Error en el módulo bóveda: {e}")
                utils.pausar()
                
        elif opcion == '3':
            try:
                estadisticas.mostrar_menu_estadisticas()
            except Exception as e:
                print(f"\n❌ Error en el módulo estadísticas: {e}")
                utils.pausar()
                
        elif opcion == '4':
            try:
                modulo_configuracion()
            except Exception as e:
                print(f"\n❌ Error en configuración: {e}")
                utils.pausar()
                
        elif opcion == '5':
            utils.limpiar_pantalla()
            print("\n" + "=" * 60)
            print("¡Gracias por usar el Sistema de Arbitraje P2P!")
            print("=" * 60)
            print("\n👋 Hasta luego!")
            sys.exit(0)
        else:
            print("\n❌ Opción no válida. Por favor, seleccione una opción del 1 al 5.")
            utils.pausar()

# =================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# =================================================

if __name__ == '__main__':
    try:
        mostrar_menu_principal()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario.")
        print("👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico en el programa: {e}")
        print("Por favor, contacta al desarrollador si el problema persiste.")
        sys.exit(1)
