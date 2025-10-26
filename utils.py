# -*- coding: utf-8 -*-
import sqlite3
import os
import re
from datetime import datetime

def confirmar_accion(mensaje):
    """Funcion reutilizable para pedir confirmacion (s/n) al usuario."""
    while True:
        respuesta = input(f"{mensaje} (s/n): ").lower().strip()
        if respuesta in ['s', 'si']:
            return True
        elif respuesta in ['n', 'no']:
            return False
        else:
            print("  Error: Respuesta no valida. Por favor, introduce 's' o 'n'.")

def obtener_ciclo_activo_id():
    """Busca en la base de datos un ciclo con estado 'activo'."""
    conn = None
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"Error de base de datos al obtener ciclo activo: {e}")
        return None
    finally:
        if conn:
            conn.close()

def validar_ciclo_existe(ciclo_id):
    """Valida que un ciclo existe en la base de datos."""
    conn = None
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ciclos WHERE id = ?", (ciclo_id,))
        resultado = cursor.fetchone()
        return resultado is not None
    except sqlite3.Error as e:
        print(f"Error al validar ciclo: {e}")
        return False
    finally:
        if conn:
            conn.close()

def validar_ciclo_estado(ciclo_id, estado_esperado='activo'):
    """Valida que un ciclo tiene un estado especifico."""
    conn = None
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT estado FROM ciclos WHERE id = ?", (ciclo_id,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0] == estado_esperado
        return False
    except sqlite3.Error as e:
        print(f"Error al validar estado del ciclo: {e}")
        return False
    finally:
        if conn:
            conn.close()

def validar_numero_positivo(prompt, permitir_cero=False):
    """Solicita al usuario un numero y valida que sea positivo."""
    while True:
        try:
            valor = float(input(prompt))
            if permitir_cero and valor >= 0:
                return valor
            elif not permitir_cero and valor > 0:
                return valor
            else:
                print("Error: El valor debe ser positivo.")
        except ValueError:
            print("Error: Por favor, ingrese un numero valido.")

def validar_entrada_segura(entrada, tipo='texto'):
    """Valida que una entrada no contenga caracteres peligrosos."""
    patrones_peligrosos = [
        r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bEXEC\b|\bUNION\b)",
        r"(--|;|\/\*|\*\/|xp_|sp_)"
    ]
    
    for patron in patrones_peligrosos:
        if re.search(patron, str(entrada), re.IGNORECASE):
            print("Entrada sospechosa detectada. Por seguridad, fue rechazada.")
            return False
    
    if tipo == 'numero':
        try:
            float(entrada)
            return True
        except ValueError:
            return False
    elif tipo == 'cripto':
        return bool(re.match(r'^[A-Z]{2,10}$', entrada))
    elif tipo == 'email':
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', entrada))
    
    return True

def formatear_moneda(cantidad):
    """Formatea una cantidad como moneda USD."""
    return f"${cantidad:,.2f}"

def formatear_cripto(cantidad, decimales=4):
    """Formatea una cantidad de criptomoneda."""
    return f"{cantidad:.{decimales}f}"

def calcular_ganancia_porcentual(precio_compra, precio_venta, comision_pct):
    """Calcula el porcentaje de ganancia neta despues de comisiones."""
    if precio_compra <= 0:
        return 0
    
    factor_comision = 1 - (comision_pct / 100)
    precio_neto = precio_venta * factor_comision
    ganancia_pct = ((precio_neto / precio_compra) - 1) * 100
    
    return ganancia_pct

def obtener_fecha_actual():
    """Devuelve la fecha y hora actual en formato estandar."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def obtener_fecha_simple():
    """Devuelve solo la fecha actual sin hora."""
    return datetime.now().strftime("%Y-%m-%d")

def limpiar_pantalla():
    """Limpia la pantalla de la consola de manera multiplataforma."""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_separador(caracter="=", longitud=60):
    """Muestra una linea separadora."""
    print(caracter * longitud)

def pausar():
    """Pausa la ejecucion esperando que el usuario presione Enter."""
    input("\nPresiona Enter para continuar...")

def validar_rango(valor, minimo, maximo, nombre_campo="valor"):
    """Valida que un valor este dentro de un rango."""
    if minimo <= valor <= maximo:
        return True
    else:
        print(f"Error: {nombre_campo} debe estar entre {minimo} y {maximo}")
        return False

def validar_opcion_menu(opcion, opciones_validas):
    """Valida que una opcion de menu sea valida."""
    return opcion in opciones_validas

def registrar_log(mensaje, nivel='INFO'):
    """Registra un mensaje en un archivo de log."""
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        fecha = datetime.now().strftime("%Y-%m-%d")
        archivo_log = f"logs/sistema_{fecha}.log"
        timestamp = obtener_fecha_actual()
        
        with open(archivo_log, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{nivel}] {mensaje}\n")
    except Exception as e:
        print(f"No se pudo escribir en el log: {e}")

def validar_capital_disponible(ciclo_id, cantidad_requerida, cripto):
    """Valida que haya suficiente capital disponible en un ciclo."""
    conn = None
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END)
            FROM transacciones
            WHERE ciclo_id = ? AND cripto = ?
        """, (ciclo_id, cripto))
        
        capital_disponible = cursor.fetchone()[0] or 0.0
        return capital_disponible >= cantidad_requerida
        
    except sqlite3.Error as e:
        print(f"Error al validar capital: {e}")
        return False
    finally:
        if conn:
            conn.close()

def calcular_costo_promedio_ponderado(ciclo_id, cripto, nueva_cantidad, nuevo_precio):
    """Calcula el nuevo costo promedio ponderado al agregar capital."""
    conn = None
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END),
                SUM(CASE WHEN tipo = 'compra' THEN monto_fiat ELSE -monto_fiat END)
            FROM transacciones
            WHERE ciclo_id = ? AND cripto = ?
        """, (ciclo_id, cripto))
        
        resultado = cursor.fetchone()
        cantidad_actual = resultado[0] or 0.0
        valor_actual = resultado[1] or 0.0
        
        cantidad_total = cantidad_actual + nueva_cantidad
        valor_total = valor_actual + (nueva_cantidad * nuevo_precio)
        
        if cantidad_total > 0:
            return valor_total / cantidad_total
        return nuevo_precio
        
    except sqlite3.Error as e:
        print(f"Error al calcular costo promedio: {e}")
        return nuevo_precio
    finally:
        if conn:
            conn.close()
