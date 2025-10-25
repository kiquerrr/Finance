import os
import sys
import sqlite3
import operador
import boveda
import estadisticas # <-- ¡NUEVO! Importamos el módulo de estadísticas

# =================================================
# MÓDULOS DE CONFIGURACIÓN Y BASE DE DATOS
# =================================================
def obtener_config(clave):
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def actualizar_config(clave, valor):
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, str(valor)))
    conn.commit()
    conn.close()

def modulo_configuracion():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==== Configuración y Mantenimiento ====")
        comision = obtener_config('comision_defecto') or "No establecido"
        ganancia = obtener_config('ganancia_defecto') or "No establecido"
        print(f"[1] Ver Configuración Actual (Comisión: {comision}%, Ganancia: {ganancia}%)")
        print("[2] Modificar Comisión por Defecto")
        print("[3] Modificar Ganancia Neta por Defecto")
        print("[4] Volver al Menú Principal")
        print("========================================")
        opcion = input("Seleccione una opción: ")
        if opcion == '1':
            input(f"\nComisión actual: {comision}%\nGanancia neta actual: {ganancia}%\n\nPresiona Enter para continuar...")
        elif opcion == '2':
            try:
                nuevo_valor = float(input("Ingrese el nuevo % de comisión por defecto: "))
                actualizar_config('comision_defecto', nuevo_valor)
            except ValueError: print("Error: valor no válido.")
        elif opcion == '3':
            try:
                nuevo_valor = float(input("Ingrese el nuevo % de ganancia neta por defecto: "))
                actualizar_config('ganancia_defecto', nuevo_valor)
            except ValueError: print("Error: valor no válido.")
        elif opcion == '4':
            break
        else:
            input("\nOpción no válida. Presiona Enter...")

# =================================================
# PROGRAMA PRINCIPAL Y MENÚ
# =================================================
def mostrar_menu_principal():
    """Muestra el menú principal y maneja la selección del usuario."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==== Sistema de Gestión de Arbitraje P2P ====")
        print("[1] Iniciar/Continuar Ciclo Diario (Operador)")
        print("[2] Gestión de Bóveda")
        print("[3] Consultas y Estadísticas")
        print("[4] Configuración y Mantenimiento")
        print("[5] Salir")
        print("=============================================")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            operador.ejecutar_dia_de_trabajo()
            input("\nPresiona Enter para volver al menú...")
        elif opcion == '2':
            boveda.mostrar_menu_boveda()
        elif opcion == '3':
            # <-- ¡NUEVO! Llamamos al menú del módulo de estadísticas
            estadisticas.mostrar_menu_estadisticas()
        elif opcion == '4':
            modulo_configuracion()
        elif opcion == '5':
            print("\nSaliendo del sistema. ¡Hasta luego!")
            sys.exit()
        else:
            input("\nOpción no válida. Presiona Enter...")

if __name__ == '__main__':
    mostrar_menu_principal()
