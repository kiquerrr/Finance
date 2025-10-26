# -*- coding: utf-8 -*-
import os
import sqlite3
import csv
from datetime import datetime

def consultar_estadisticas_generales():
    """Calcula y muestra las estadísticas de todos los ciclos completados."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()

        # Calculamos la ganancia total de todos los ciclos completados
        cursor.execute("SELECT SUM(ganancia_neta_total) FROM ciclos WHERE estado = 'completado'")
        ganancia_historica = cursor.fetchone()[0] or 0.0

        # Contamos cuántos ciclos se han completado
        cursor.execute("SELECT COUNT(id) FROM ciclos WHERE estado = 'completado'")
        ciclos_completados = cursor.fetchone()[0] or 0

        # Calculamos la ganancia promedio por ciclo
        ganancia_promedio = (ganancia_historica / ciclos_completados) if ciclos_completados > 0 else 0

        # Mejor y peor ciclo
        cursor.execute("""
            SELECT id, ganancia_neta_total 
            FROM ciclos 
            WHERE estado = 'completado' 
            ORDER BY ganancia_neta_total DESC 
            LIMIT 1
        """)
        mejor_ciclo = cursor.fetchone()

        cursor.execute("""
            SELECT id, ganancia_neta_total 
            FROM ciclos 
            WHERE estado = 'completado' 
            ORDER BY ganancia_neta_total ASC 
            LIMIT 1
        """)
        peor_ciclo = cursor.fetchone()

        conn.close()

        print("\n" + "=" * 60)
        print("ESTADÍSTICAS GENERALES (HISTÓRICO)")
        print("=" * 60)
        print(f"📊 Ciclos Completados: {ciclos_completados}")
        print(f"💵 Ganancia Neta Total Histórica: ${ganancia_historica:.2f}")
        print(f"📈 Ganancia Promedio por Ciclo: ${ganancia_promedio:.2f}")
        
        if mejor_ciclo:
            print(f"\n🏆 Mejor Ciclo: #{mejor_ciclo[0]} con ${mejor_ciclo[1]:.2f}")
        if peor_ciclo:
            print(f"📉 Peor Ciclo: #{peor_ciclo[0]} con ${peor_ciclo[1]:.2f}")
        print("=" * 60)
    except sqlite3.Error as e:
        print(f"❌ Error al consultar estadísticas: {e}")

def listar_ciclos_completados():
    """Muestra un resumen de cada ciclo que ha sido completado."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, fecha_inicio, fecha_fin, ganancia_neta_total 
            FROM ciclos 
            WHERE estado = 'completado' 
            ORDER BY fecha_inicio DESC
        """)
        ciclos = cursor.fetchall()

        conn.close()

        print("\n" + "=" * 60)
        print("HISTORIAL DE CICLOS COMPLETADOS")
        print("=" * 60)
        
        if not ciclos:
            print("Aún no hay ciclos completados en el historial.")
        else:
            for ciclo in ciclos:
                print(f"\n🔄 Ciclo #{ciclo[0]}:")
                print(f"   📅 Periodo: {ciclo[1]} a {ciclo[2]}")
                print(f"   💰 Ganancia Neta: ${ciclo[3]:.2f}")
        print("=" * 60)
    except sqlite3.Error as e:
        print(f"❌ Error al listar ciclos: {e}")

def ver_ciclo_activo():
    """Muestra información detallada del ciclo activo actual."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, fecha_inicio FROM ciclos WHERE estado = 'activo'")
        ciclo = cursor.fetchone()
        
        if not ciclo:
            print("\n⚠️  No hay ningún ciclo activo actualmente.")
            conn.close()
            return
        
        ciclo_id = ciclo[0]
        fecha_inicio = ciclo[1]
        
        # Obtener número de transacciones
        cursor.execute("SELECT COUNT(*) FROM transacciones WHERE ciclo_id = ?", (ciclo_id,))
        num_transacciones = cursor.fetchone()[0]
        
        # Calcular capital actual
        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) 
            FROM transacciones WHERE ciclo_id = ?
        """, (ciclo_id,))
        cripto_actual = cursor.fetchone()[0] or 0.0
        
        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto * precio_unitario 
                           ELSE -(cantidad_cripto * precio_unitario) END) 
            FROM transacciones WHERE ciclo_id = ?
        """, (ciclo_id,))
        costo_total = cursor.fetchone()[0] or 0.0
        
        # Calcular número de compras y ventas
        cursor.execute("SELECT COUNT(*) FROM transacciones WHERE ciclo_id = ? AND tipo = 'compra'", (ciclo_id,))
        num_compras = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transacciones WHERE ciclo_id = ? AND tipo = 'venta'", (ciclo_id,))
        num_ventas = cursor.fetchone()[0]
        
        conn.close()
        
        costo_promedio = (costo_total / cripto_actual) if cripto_actual > 0 else 0
        
        print("\n" + "=" * 60)
        print("INFORMACIÓN DEL CICLO ACTIVO")
        print("=" * 60)
        print(f"🔄 Ciclo ID: #{ciclo_id}")
        print(f"📅 Fecha de Inicio: {fecha_inicio}")
        print(f"📊 Transacciones Realizadas: {num_transacciones}")
        print(f"   - Compras: {num_compras}")
        print(f"   - Ventas: {num_ventas}")
        print(f"\n💰 Cripto Disponible: {cripto_actual:.4f}")
        print(f"💵 Inversión Total: ${costo_total:.2f}")
        print(f"📈 Costo Promedio: ${costo_promedio:.4f}")
        print("=" * 60)
    except sqlite3.Error as e:
        print(f"❌ Error al consultar ciclo activo: {e}")

def exportar_transacciones_csv():
    """Exporta todas las transacciones a un archivo CSV en el directorio exports/."""
    try:
        # Asegurar que existe el directorio exports
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.ciclo_id, t.fecha, t.tipo, t.cripto, t.cantidad_cripto, 
                   t.precio_unitario, t.precio_venta_real, t.comision_pct, t.monto_fiat
            FROM transacciones t
            ORDER BY t.fecha DESC
        """)
        transacciones = cursor.fetchall()
        conn.close()
        
        if not transacciones:
            print("\n⚠️  No hay transacciones para exportar.")
            return
        
        # Crear nombre de archivo con fecha
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"exports/transacciones_{fecha_actual}.csv"
        
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
            escritor = csv.writer(archivo_csv)
            
            # Escribir encabezados
            escritor.writerow(['ID', 'Ciclo ID', 'Fecha', 'Tipo', 'Cripto', 'Cantidad Cripto', 
                             'Precio Unitario', 'Precio Venta Real', 'Comisión %', 'Monto FIAT'])
            
            # Escribir datos
            for trans in transacciones:
                escritor.writerow(trans)
        
        print(f"\n✅ ¡Exportación exitosa!")
        print(f"📁 Ubicación: {nombre_archivo}")
        print(f"📊 Total de transacciones exportadas: {len(transacciones)}")
        
    except sqlite3.Error as e:
        print(f"❌ Error al exportar transacciones: {e}")
    except IOError as e:
        print(f"❌ Error al crear el archivo CSV: {e}")

def ver_detalle_ciclo():
    """Muestra información detallada de un ciclo específico."""
    try:
        ciclo_id = int(input("\nIngrese el ID del ciclo a consultar: "))
        
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # Obtener información del ciclo
        cursor.execute("""
            SELECT id, fecha_inicio, fecha_fin, ganancia_neta_total, estado
            FROM ciclos WHERE id = ?
        """, (ciclo_id,))
        
        ciclo = cursor.fetchone()
        
        if not ciclo:
            print(f"\n⚠️  No se encontró el ciclo #{ciclo_id}")
            conn.close()
            return
        
        # Obtener transacciones del ciclo
        cursor.execute("""
            SELECT fecha, tipo, cantidad_cripto, precio_unitario, precio_venta_real
            FROM transacciones WHERE ciclo_id = ?
            ORDER BY fecha
        """, (ciclo_id,))
        
        transacciones = cursor.fetchall()
        conn.close()
        
        print("\n" + "=" * 60)
        print(f"DETALLE DEL CICLO #{ciclo[0]}")
        print("=" * 60)
        print(f"📅 Fecha Inicio: {ciclo[1]}")
        print(f"📅 Fecha Fin: {ciclo[2] if ciclo[2] else 'En curso'}")
        print(f"💰 Ganancia Neta: ${ciclo[3]:.2f}")
        print(f"📊 Estado: {ciclo[4].upper()}")
        
        if transacciones:
            print(f"\n🔄 Transacciones ({len(transacciones)}):")
            print("-" * 60)
            for trans in transacciones:
                tipo_emoji = "📥" if trans[1] == 'compra' else "📤"
                print(f"{tipo_emoji} {trans[0]} | {trans[1].upper()}")
                print(f"   Cantidad: {trans[2]:.4f} | Precio: ${trans[3]:.4f}")
                if trans[1] == 'venta' and trans[4]:
                    print(f"   Precio Venta: ${trans[4]:.4f}")
                print("-" * 60)
        else:
            print("\n⚠️  No hay transacciones en este ciclo.")
        
        print("=" * 60)
        
    except ValueError:
        print("\n❌ Error: Ingrese un número válido.")
    except sqlite3.Error as e:
        print(f"❌ Error al consultar el ciclo: {e}")

def mostrar_menu_estadisticas():
    """Muestra el sub-menú de consultas y estadísticas."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("CONSULTAS Y ESTADÍSTICAS")
        print("=" * 60)
        print("[1] Ver Resumen General Histórico")
        print("[2] Listar Ciclos Anteriores")
        print("[3] Ver Información del Ciclo Activo")
        print("[4] Ver Detalle de un Ciclo Específico")
        print("[5] Exportar Transacciones a CSV")
        print("[6] Volver al Menú Principal")
        print("=" * 60)
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            consultar_estadisticas_generales()
            input("\nPresiona Enter para volver...")
        elif opcion == '2':
            listar_ciclos_completados()
            input("\nPresiona Enter para volver...")
        elif opcion == '3':
            ver_ciclo_activo()
            input("\nPresiona Enter para volver...")
        elif opcion == '4':
            ver_detalle_ciclo()
            input("\nPresiona Enter para volver...")
        elif opcion == '5':
            exportar_transacciones_csv()
            input("\nPresiona Enter para volver...")
        elif opcion == '6':
            break
        else:
            input("\n❌ Opción no válida. Presiona Enter...")
