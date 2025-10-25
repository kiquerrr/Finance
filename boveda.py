# boveda.py
import os
import sqlite3
from datetime import datetime
import utils  # <-- ¡NUEVO! Importamos nuestro módulo de utilidades

def consultar_boveda():
    """Calcula y muestra el estado actual de la bóveda desde la BD."""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()

    # Sumamos todas las compras y restamos todas las ventas
    cursor.execute("SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) FROM transacciones")
    cripto_total = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto * precio_unitario ELSE -(cantidad_cripto * precio_unitario) END) FROM transacciones")
    costo_total_usd = cursor.fetchone()[0] or 0.0
    
    conn.close()

    costo_promedio = (costo_total_usd / cripto_total) if cripto_total > 0 else 0

    print("\n--- Estado Actual de la Bóveda ---")
    print(f"Cripto Total en Bóveda: {cripto_total:.4f}")
    print(f"Costo Total Invertido: ${costo_total_usd:.2f}")
    print(f"Costo Promedio por Cripto: ${costo_promedio:.4f}")

def fondear_boveda():
    """Registra una nueva transacción de compra en la base de datos."""
    print("\n--- Fondear Bóveda (Registrar Compra) ---")
    
    # <-- ¡CAMBIO CLAVE! Primero, obtenemos el ciclo activo.
    ciclo_id_activo = utils.obtener_ciclo_activo_id()
    
    if not ciclo_id_activo:
        print("\nERROR: No se encontró un ciclo de trabajo activo.")
        print("Por favor, inicia un ciclo desde el 'Módulo Operador' [Opción 1] antes de registrar una compra.")
        return
        
    print(f"Nota: Los fondos se añadirán al ciclo activo #{ciclo_id_activo}.")

    try:
        cantidad = float(input("Ingrese la cantidad de cripto comprado: "))
        precio = float(input("Ingrese el precio de compra por unidad (USD): "))
        if cantidad <= 0 or precio <= 0:
            print("Error: Los valores deben ser positivos.")
            return

        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # <-- ¡CAMBIO CLAVE! Usamos el ID del ciclo activo en lugar de '1'.
        cursor.execute("""
            INSERT INTO transacciones (ciclo_id, fecha, tipo, cantidad_cripto, precio_unitario, comision_pct)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ciclo_id_activo, fecha_actual, 'compra', cantidad, precio, 0)) # Comisión 0 para compras
        
        conn.commit()
        conn.close()
        print("\n¡Compra registrada con éxito en la base de datos!")

    except ValueError:
        print("\nError: Entrada no válida. Por favor, ingrese solo números.")

def mostrar_menu_boveda():
    """Muestra el sub-menú de gestión de bóveda."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==== Gestión de Bóveda ====")
        print("[1] Consultar Estado de la Bóveda")
        print("[2] Fondear Bóveda (Registrar Compra)")
        print("[3] Volver al Menú Principal")
        print("===========================")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            consultar_boveda()
            input("\nPresiona Enter para volver...")
        elif opcion == '2':
            fondear_boveda()
            input("\nPresiona Enter para volver...")
        elif opcion == '3':
            break
        else:
            input("\nOpción no válida. Presiona Enter...")
