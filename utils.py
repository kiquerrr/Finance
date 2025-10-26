# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

def confirmar_accion(mensaje):
    """
    Función reutilizable para pedir confirmación (s/n) al usuario.
    Maneja varias entradas y vuelve a preguntar si la respuesta no es válida.
    Devuelve True para 'sí' y False para 'no'.
    """
    while True:
        respuesta = input(f"{mensaje} (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí']:
            return True
        elif respuesta in ['n', 'no']:
            return False
        else:
            print("  ❌ Error: Respuesta no válida. Por favor, introduce 's' o 'n'.")

def obtener_ciclo_activo_id():
    """
    Busca en la base de datos un ciclo con estado 'activo'.
    Devuelve el ID del ciclo si lo encuentra, de lo contrario devuelve None.
    """
    conn = None
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos al obtener ciclo activo: {e}")
        return None
    finally:
        if conn:
            conn.close()

def validar_numero_positivo(prompt, permitir_cero=False):
    """
    Solicita al usuario un número y valida que sea positivo.
    
    Args:
        prompt (str): Mensaje a mostrar al usuario
        permitir_cero (bool): Si True, permite el valor 0
    
    Returns:
        float: El número validado
    """
    while True:
        try:
            valor = float(input(prompt))
            if permitir_cero and valor >= 0:
                return valor
            elif not permitir_cero and valor > 0:
                return valor
            else:
                print("❌ Error: El valor debe ser positivo.")
        except ValueError:
            print("❌ Error: Por favor, ingrese un número válido.")

def formatear_moneda(cantidad):
    """
    Formatea una cantidad como moneda USD.
    
    Args:
        cantidad (float): La cantidad a formatear
    
    Returns:
        str: La cantidad formateada
    """
    return f"${cantidad:,.2f}"

def formatear_cripto(cantidad, decimales=4):
    """
    Formatea una cantidad de criptomoneda.
    
    Args:
        cantidad (float): La cantidad a formatear
        decimales (int): Número de decimales a mostrar
    
    Returns:
        str: La cantidad formateada
    """
    return f"{cantidad:.{decimales}f}"

def calcular_ganancia_porcentual(precio_compra, precio_venta, comision_pct):
    """
    Calcula el porcentaje de ganancia neta después de comisiones.
    
    Args:
        precio_compra (float): Precio de compra por unidad
        precio_venta (float): Precio de venta por unidad
        comision_pct (float): Porcentaje de comisión
    
    Returns:
        float: Porcentaje de ganancia neta
    """
    if precio_compra <= 0:
        return 0
    
    factor_comision = 1 - (comision_pct / 100)
    precio_neto = precio_venta * factor_comision
    ganancia_pct = ((precio_neto / precio_compra) - 1) * 100
    
    return ganancia_pct

def obtener_fecha_actual():
    """
    Devuelve la fecha y hora actual en formato estándar.
    
    Returns:
        str: Fecha y hora en formato 'YYYY-MM-DD HH:MM:SS'
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def obtener_fecha_simple():
    """
    Devuelve solo la fecha actual sin hora.
    
    Returns:
        str: Fecha en formato 'YYYY-MM-DD'
    """
    return datetime.now().strftime("%Y-%m-%d")

def limpiar_pantalla():
    """
    Limpia la pantalla de la consola de manera multiplataforma.
    """
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_separador(caracter="=", longitud=60):
    """
    Muestra una línea separadora.
    
    Args:
        caracter (str): Caracter a usar para el separador
        longitud (int): Longitud del separador
    """
    print(caracter * longitud)

def pausar():
    """
    Pausa la ejecución esperando que el usuario presione Enter.
    """
    input("\nPresiona Enter para continuar...")

def validar_rango(valor, minimo, maximo, nombre_campo="valor"):
    """
    Valida que un valor esté dentro de un rango.
    
    Args:
        valor (float): Valor a validar
        minimo (float): Valor mínimo permitido
        maximo (float): Valor máximo permitido
        nombre_campo (str): Nombre del campo para mensajes de error
    
    Returns:
        bool: True si el valor está en el rango, False en caso contrario
    """
    if minimo <= valor <= maximo:
        return True
    else:
        print(f"❌ Error: {nombre_campo} debe estar entre {minimo} y {maximo}")
        return False
