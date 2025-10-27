# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

def obtener_dia_actual(ciclo_id):
    """Obtiene el dia de operacion actual (abierto) de un ciclo."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, numero_dia, capital_inicial, num_ventas
            FROM dias_operacion
            WHERE ciclo_id = ? AND estado = 'abierto'
            ORDER BY numero_dia DESC
            LIMIT 1
        """, (ciclo_id,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            return {
                'id': resultado[0],
                'numero_dia': resultado[1],
                'capital_inicial': resultado[2],
                'num_ventas': resultado[3]
            }
        return None
        
    except sqlite3.Error as e:
        print(f"Error al obtener dia actual: {e}")
        return None

def crear_nuevo_dia(ciclo_id, capital_inicial):
    """Crea un nuevo dia de operacion dentro de un ciclo."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # Obtener el ultimo numero de dia
        cursor.execute("SELECT MAX(numero_dia) FROM dias_operacion WHERE ciclo_id = ?", (ciclo_id,))
        ultimo_dia = cursor.fetchone()[0] or 0
        
        nuevo_numero_dia = ultimo_dia + 1
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            INSERT INTO dias_operacion 
            (ciclo_id, numero_dia, fecha, capital_inicial, capital_final, estado)
            VALUES (?, ?, ?, ?, ?, 'abierto')
        """, (ciclo_id, nuevo_numero_dia, fecha_actual, capital_inicial, capital_inicial))
        
        dia_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Dia #{nuevo_numero_dia} iniciado con ${capital_inicial:.2f}")
        return dia_id
        
    except sqlite3.Error as e:
        print(f"❌ Error al crear nuevo dia: {e}")
        return None

def cerrar_dia_actual(ciclo_id, dia_id):
    """Cierra el dia actual calculando ganancia y capital final."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # Obtener capital inicial y ventas del día
        cursor.execute("SELECT capital_inicial, num_ventas FROM dias_operacion WHERE id = ?", (dia_id,))
        info_dia = cursor.fetchone()
        if not info_dia:
            print(f"❌ Error: No se encontró el día con ID {dia_id}.")
            conn.close()
            return None
        capital_inicial = info_dia[0]
        num_ventas = info_dia[1]

        # Calcular capital final del CICLO
        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN monto_fiat ELSE -monto_fiat END)
            FROM transacciones
            WHERE ciclo_id = ?
        """, (ciclo_id,))
        capital_final_ciclo = cursor.fetchone()[0] or 0.0
        
        # Calcular ganancia SOLO de las ventas del día
        cursor.execute("""
            SELECT SUM(
                (monto_fiat) - (cantidad_cripto * precio_unitario * (1 + comision_pct / 100))
            )
            FROM transacciones
            WHERE dia_id = ? AND tipo = 'venta'
        """, (dia_id,))
        ganancia_dia = cursor.fetchone()[0] or 0.0
        
        # Actualizar dia
        cursor.execute("""
            UPDATE dias_operacion
            SET capital_final = ?, ganancia_dia = ?, estado = 'cerrado'
            WHERE id = ?
        """, (capital_final_ciclo, ganancia_dia, dia_id))
        
        conn.commit()
        conn.close()
        
        return {
            'capital_inicial': capital_inicial,
            'capital_final': capital_final_ciclo,
            'ganancia': ganancia_dia,
            'num_ventas': num_ventas
        }
        
    except sqlite3.Error as e:
        print(f"❌ Error al cerrar dia: {e}")
        return None

def obtener_resumen_dias(ciclo_id):
    """Obtiene resumen de todos los dias de un ciclo."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT numero_dia, fecha, capital_inicial, capital_final, 
                   ganancia_dia, num_ventas, estado
            FROM dias_operacion
            WHERE ciclo_id = ?
            ORDER BY numero_dia
        """, (ciclo_id,))
        
        dias = cursor.fetchall()
        conn.close()
        
        return dias
        
    except sqlite3.Error as e:
        print(f"❌ Error al obtener resumen de dias: {e}")
        return []

def incrementar_ventas_dia(dia_id):
    """Incrementa el contador de ventas del dia."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("UPDATE dias_operacion SET num_ventas = num_ventas + 1 WHERE id = ?", (dia_id,))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error al incrementar ventas: {e}")
        return False

def validar_limite_ventas(dia_id):
    """Valida si se ha alcanzado el limite de ventas del dia."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # Obtener configuracion
        cursor.execute("SELECT valor FROM configuracion WHERE clave = 'ventas_maximas_dia'")
        max_ventas = int(cursor.fetchone()[0])
        
        # Obtener ventas del dia
        cursor.execute("SELECT num_ventas FROM dias_operacion WHERE id = ?", (dia_id,))
        ventas_actuales = cursor.fetchone()[0]
        
        conn.close()
        
        return ventas_actuales < max_ventas, ventas_actuales, max_ventas
        
    except sqlite3.Error as e:
        print(f"❌ Error al validar limite: {e}")
        return False, 0, 5
