"""
=============================================================================
MÓDULO DE DÍAS - Gestión de días de operación (CORREGIDO)
=============================================================================
Integrado con logger.py y calculos.py para precisión total
"""

import sqlite3
from datetime import datetime, timedelta
from logger import log
from calculos import calc

# Conexión a la base de datos
conn = sqlite3.connect('arbitraje.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


# ===================================================================
# FUNCIONES DE OBTENCIÓN DE DATOS
# ===================================================================

def obtener_cripto_por_id(cripto_id):
    """Obtiene información de una criptomoneda"""
    cursor.execute("""
        SELECT id, nombre, simbolo, tipo
        FROM criptomonedas
        WHERE id = ?
    """, (cripto_id,))
    return cursor.fetchone()


def obtener_costo_promedio(cripto_id, ciclo_id):
    """Obtiene el costo promedio de una cripto en un ciclo"""
    cursor.execute("""
        SELECT precio_promedio
        FROM boveda_ciclo
        WHERE cripto_id = ? AND ciclo_id = ?
    """, (cripto_id, ciclo_id))
    
    resultado = cursor.fetchone()
    return resultado['precio_promedio'] if resultado else 0


def obtener_cantidad_disponible(cripto_id, ciclo_id):
    """Obtiene la cantidad disponible de una cripto"""
    cursor.execute("""
        SELECT cantidad
        FROM boveda_ciclo
        WHERE cripto_id = ? AND ciclo_id = ?
    """, (cripto_id, ciclo_id))
    
    resultado = cursor.fetchone()
    return resultado['cantidad'] if resultado else 0


def obtener_criptos_disponibles(ciclo_id):
    """Obtiene todas las criptos con cantidad > 0 en un ciclo"""
    cursor.execute("""
        SELECT 
            c.id,
            c.nombre,
            c.simbolo,
            bc.cantidad,
            bc.precio_promedio,
            (bc.cantidad * bc.precio_promedio) as valor_usd
        FROM boveda_ciclo bc
        JOIN criptomonedas c ON bc.cripto_id = c.id
        WHERE bc.ciclo_id = ? AND bc.cantidad > 0
        ORDER BY c.nombre
    """, (ciclo_id,))
    
    return cursor.fetchall()


def calcular_capital_actual_criptos(ciclo_id):
    """Calcula el valor total de las criptos disponibles"""
    criptos = obtener_criptos_disponibles(ciclo_id)
    
    criptos_info = [
        (c['nombre'], c['cantidad'], c['precio_promedio'])
        for c in criptos
    ]
    
    return calc.calcular_capital_total(criptos_info)


def obtener_dia(dia_id):
    """Obtiene información de un día"""
    cursor.execute("""
        SELECT * FROM dias WHERE id = ?
    """, (dia_id,))
    return cursor.fetchone()


def obtener_dia_actual(ciclo_id):
    """Obtiene el día actual activo del ciclo"""
    cursor.execute("""
        SELECT * FROM dias
        WHERE ciclo_id = ? AND estado = 'abierto'
        ORDER BY numero_dia DESC
        LIMIT 1
    """, (ciclo_id,))
    return cursor.fetchone()


def obtener_ventas_del_dia(dia_id):
    """Obtiene todas las ventas de un día"""
    cursor.execute("""
        SELECT 
            v.*,
            c.nombre as cripto_nombre,
            c.simbolo as cripto_simbolo
        FROM ventas v
        JOIN criptomonedas c ON v.cripto_id = c.id
        WHERE v.dia_id = ?
        ORDER BY v.fecha
    """, (dia_id,))
    return cursor.fetchall()


def contar_ventas_del_dia(dia_id):
    """Cuenta cuántas ventas se han hecho en el día"""
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM ventas
        WHERE dia_id = ?
    """, (dia_id,))
    return cursor.fetchone()['total']


def obtener_resumen_dias(ciclo_id):
    """Obtiene resumen de todos los días de un ciclo"""
    cursor.execute("""
        SELECT 
            numero_dia,
            fecha,
            capital_inicial,
            capital_final,
            ganancia_neta,
            estado
        FROM dias
        WHERE ciclo_id = ?
        ORDER BY numero_dia
    """, (ciclo_id,))
    return cursor.fetchall()


# ===================================================================
# INICIAR DÍA
# ===================================================================

def iniciar_dia(ciclo_id):
    """Inicia un nuevo día de operación"""
    
    # Verificar si ya hay un día abierto
    dia_actual = obtener_dia_actual(ciclo_id)
    if dia_actual:
        log.advertencia(
            f"Ya existe un día abierto (#{dia_actual['numero_dia']}) en el ciclo #{ciclo_id}",
            categoria='operaciones'
        )
        return dia_actual['id']
    
    # Calcular número de día
    cursor.execute("""
        SELECT COALESCE(MAX(numero_dia), 0) + 1 as siguiente_dia
        FROM dias
        WHERE ciclo_id = ?
    """, (ciclo_id,))
    numero_dia = cursor.fetchone()['siguiente_dia']
    
    # Calcular capital inicial del día
    capital_inicial = calcular_capital_actual_criptos(ciclo_id)
    
    # Obtener criptos disponibles para log
    criptos_disponibles = obtener_criptos_disponibles(ciclo_id)
    criptos_info = [
        (c['nombre'], c['cantidad'], c['valor_usd']) 
        for c in criptos_disponibles
    ]
    
    # Insertar día en BD
    cursor.execute("""
        INSERT INTO dias (
            ciclo_id, numero_dia, capital_inicial, 
            estado, fecha
        ) VALUES (?, ?, ?, 'abierto', datetime('now'))
    """, (ciclo_id, numero_dia, capital_inicial))
    
    dia_id = cursor.lastrowid
    conn.commit()
    
    # REGISTRAR EN LOG
    log.dia_iniciado(
        ciclo_id=ciclo_id,
        dia_num=numero_dia,
        capital_inicial=capital_inicial,
        criptos_disponibles=criptos_info
    )
    
    print(f"✅ Día #{numero_dia} iniciado con ${capital_inicial:.2f}")
    
    return dia_id


# ===================================================================
# DEFINIR PRECIO DE VENTA
# ===================================================================

def definir_precio_venta(dia_id, cripto_id, precio_publicado):
    """Registra el precio de venta para el día"""
    
    # Obtener día y ciclo
    dia = obtener_dia(dia_id)
    ciclo_id = dia['ciclo_id']
    
    # Obtener info de la cripto
    cripto = obtener_cripto_por_id(cripto_id)
    costo_promedio = obtener_costo_promedio(cripto_id, ciclo_id)
    
    # Obtener configuración
    cursor.execute("SELECT comision_default, ganancia_neta_default FROM config WHERE id = 1")
    config = cursor.fetchone()
    comision = config['comision_default']
    ganancia_objetivo = config['ganancia_neta_default']
    
    # Calcular ganancia neta estimada con el precio publicado
    ganancia_neta_estimada = calc.calcular_ganancia_neta_estimada(
        costo_promedio=costo_promedio,
        precio_venta=precio_publicado
    )
    
    # Actualizar día con la info
    cursor.execute("""
        UPDATE dias SET
            cripto_operada_id = ?,
            precio_publicado = ?
        WHERE id = ?
    """, (cripto_id, precio_publicado, dia_id))
    conn.commit()
    
    # REGISTRAR EN LOG
    log.precio_definido(
        cripto=cripto['nombre'],
        costo_promedio=costo_promedio,
        comision=comision,
        ganancia_objetivo=ganancia_objetivo,
        precio_publicado=precio_publicado,
        ganancia_neta_estimada=ganancia_neta_estimada
    )
    
    return ganancia_neta_estimada


# ===================================================================
# REGISTRAR VENTA
# ===================================================================

def registrar_venta(dia_id, cripto_id, cantidad):
    """Registra una venta con cálculos correctos"""
    
    # Obtener día y ciclo
    dia = obtener_dia(dia_id)
    ciclo_id = dia['ciclo_id']
    precio_venta = dia['precio_publicado']
    
    # Validar que haya precio publicado
    if not precio_venta or precio_venta <= 0:
        log.error("No se ha definido precio de venta", f"Día #{dia['numero_dia']}")
        return None
    
    # Obtener info de la cripto
    cripto = obtener_cripto_por_id(cripto_id)
    costo_promedio = obtener_costo_promedio(cripto_id, ciclo_id)
    cantidad_disponible = obtener_cantidad_disponible(cripto_id, ciclo_id)
    
    # Validar cantidad disponible
    if cantidad > cantidad_disponible:
        log.error(
            f"Cantidad insuficiente de {cripto['nombre']}",
            f"Disponible: {cantidad_disponible}, Solicitado: {cantidad}"
        )
        return None
    
    # CALCULAR VENTA CON LA CALCULADORA
    resultado = calc.calcular_venta(
        cantidad=cantidad,
        costo_unitario=costo_promedio,
        precio_venta=precio_venta
    )
    
    if not resultado:
        log.error("Error al calcular venta", "Valores inválidos")
        return None
    
    # Insertar venta en BD
    cursor.execute("""
        INSERT INTO ventas (
            dia_id, cripto_id, cantidad, precio_unitario,
            costo_total, monto_venta, comision, efectivo_recibido,
            ganancia_bruta, ganancia_neta, fecha
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        dia_id, cripto_id, cantidad, precio_venta,
        resultado['costo_total'],
        resultado['monto_venta'],
        resultado['comision'],
        resultado['efectivo_recibido'],
        resultado['ganancia_bruta'],
        resultado['ganancia_neta']
    ))
    
    venta_id = cursor.lastrowid
    
    # Actualizar cantidad en bóveda (RESTAR la cantidad vendida)
    cursor.execute("""
        UPDATE boveda_ciclo
        SET cantidad = cantidad - ?
        WHERE cripto_id = ? AND ciclo_id = ?
    """, (cantidad, cripto_id, ciclo_id))
    
    # Registrar efectivo recibido en banco
    cursor.execute("""
        INSERT INTO efectivo_banco (ciclo_id, dia_id, monto, concepto, fecha)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (
        ciclo_id, 
        dia_id, 
        resultado['efectivo_recibido'],
        f"Venta de {cantidad} {cripto['simbolo']}"
    ))
    
    conn.commit()
    
    # Contar ventas del día
    venta_num = contar_ventas_del_dia(dia_id)
    
    # REGISTRAR EN LOG
    log.venta_registrada(
        venta_num=venta_num,
        cripto=cripto['nombre'],
        cantidad_vendida=cantidad,
        precio_unitario=precio_venta,
        monto_total=resultado['monto_venta'],
        comision_pagada=resultado['comision'],
        ganancia_neta=resultado['ganancia_neta']
    )
    
    # Mostrar resultado
    print(f"\n✅ Venta #{venta_num} registrada:")
    print(f"   {cantidad} {cripto['simbolo']} x ${precio_venta:.4f}")
    print(f"   Monto venta: ${resultado['monto_venta']:.2f}")
    print(f"   Comisión: ${resultado['comision']:.2f}")
    print(f"   Efectivo recibido: ${resultado['efectivo_recibido']:.2f}")
    print(f"   Ganancia neta: ${resultado['ganancia_neta']:.2f}")
    
    return resultado


# ===================================================================
# CERRAR DÍA
# ===================================================================

def cerrar_dia(dia_id):
    """Cierra el día con cálculos correctos"""
    
    # Obtener datos del día
    dia = obtener_dia(dia_id)
    if not dia:
        log.error("Día no encontrado", f"ID: {dia_id}")
        return None
    
    if dia['estado'] == 'cerrado':
        log.advertencia("El día ya está cerrado", f"Día #{dia['numero_dia']}")
        return None
    
    ciclo_id = dia['ciclo_
