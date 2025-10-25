import os
import sqlite3
import csv # Para exportar datos

def consultar_estadisticas_generales():
    """Calcula y muestra las estadísticas de todos los ciclos completados."""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()

    # Calculamos la ganancia total de todos los ciclos completados
    cursor.execute("SELECT SUM(ganancia_neta_total) FROM ciclos WHERE estado = 'completado'")
    ganancia_historica = cursor.fetchone()[0] or 0.0

    # Contamos cuántos ciclos se han completado
    cursor.execute("SELECT COUNT(id) FROM ciclos WHERE estado = 'completado'")
    ciclos_completados = cursor.fetchone()[0] or 0

    conn.close()

    print("\n--- Estadísticas Generales (Histórico) ---")
    print(f"Ciclos Completados: {ciclos_completados}")
    print(f"Ganancia Neta Total Histórica: ${ganancia_historica:.2f}")
    # Aquí podríamos añadir más estadísticas en el futuro, como el ROI promedio.

def listar_ciclos_completados():
    """Muestra un resumen de cada ciclo que ha sido completado."""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, fecha_inicio, fecha_fin, ganancia_neta_total FROM ciclos WHERE estado = 'completado' ORDER BY fecha_inicio DESC")
    ciclos = cursor.fetchall()

    conn.close()

    print("\n--- Historial de Ciclos Completados ---")
    if not ciclos:
        print("Aún no hay ciclos completados en el historial.")
    else:
        for ciclo in ciclos:
            print(f"  - Ciclo #{ciclo[0]}:")
            print(f"    - Periodo: {ciclo[1]} a {ciclo[2]}")
            print(f"    - Ganancia Neta: ${ciclo[3]:.2f}")

def mostrar_menu_estadisticas():
    """Muestra el sub-menú de consultas y estadísticas."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==== Consultas y Estadísticas ====")
        print("[1] Ver Resumen General Histórico")
        print("[2] Listar Ciclos Anteriores")
        print("[3] Exportar Transacciones a CSV (Próximamente)")
        print("[4] Volver al Menú Principal")
        print("==================================")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            consultar_estadisticas_generales()
            input("\nPresiona Enter para volver...")
        elif opcion == '2':
            listar_ciclos_completados()
            input("\nPresiona Enter para volver...")
        elif opcion == '3':
            input("\nEsta función estará disponible en futuras versiones. Presiona Enter...")
        elif opcion == '4':
            break
        else:
            input("\nOpción no válida. Presiona Enter...")
