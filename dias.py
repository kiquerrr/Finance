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
    
    ciclo_id = dia['ciclo_id']
    
    # Obtener ventas del día
    ventas = obtener_ventas_del_dia(dia_id)
    
    if not ventas:
        log.advertencia("No hay ventas registradas para cerrar", f"Día #{dia['numero_dia']}")
    
    # Calcular capital final en criptos
    capital_final_criptos = calcular_capital_actual_criptos(ciclo_id)
    
    # CALCULAR RESUMEN DEL DÍA
    resumen = calc.calcular_resumen_dia(
        capital_inicial=dia['capital_inicial'],
        ventas=ventas,
        capital_final_criptos=capital_final_criptos
    )
    
    # Actualizar día en BD
    cursor.execute("""
        UPDATE dias SET
            capital_final = ?,
            efectivo_recibido = ?,
            ganancia_bruta = ?,
            ganancia_neta = ?,
            comisiones_pagadas = ?,
            estado = 'cerrado',
            fecha_cierre = datetime('now')
        WHERE id = ?
    """, (
        resumen['capital_final_total'],
        resumen['efectivo_recibido'],
        resumen['total_ganancia_bruta'],
        resumen['total_ganancia_neta'],
        resumen['total_comisiones'],
        dia_id
    ))
    conn.commit()
    
    # REGISTRAR EN LOG
    log.dia_cerrado(
        ciclo_id=ciclo_id,
        dia_num=dia['numero_dia'],
        capital_inicial=dia['capital_inicial'],
        capital_final=resumen['capital_final_total'],
        ganancia_dia=resumen['total_ganancia_neta'],
        ventas_realizadas=resumen['num_ventas']
    )
    
    # Mostrar resumen detallado
    print("\n" + "="*60)
    print("CIERRE DEL DÍA DE OPERACIÓN")
    print("="*60)
    print(f"\n📊 DÍA #{dia['numero_dia']}")
    print(f"Ventas realizadas: {resumen['num_ventas']}")
    print(f"\n💰 CAPITAL:")
    print(f"   Inicial: ${dia['capital_inicial']:.2f}")
    print(f"   En criptos: ${resumen['capital_final_criptos']:.2f}")
    print(f"   Efectivo recibido: ${resumen['efectivo_recibido']:.2f}")
    print(f"   Final total: ${resumen['capital_final_total']:.2f}")
    print(f"\n💸 COSTOS Y GANANCIAS:")
    print(f"   Comisiones pagadas: ${resumen['total_comisiones']:.2f}")
    print(f"   Ganancia bruta: ${resumen['total_ganancia_bruta']:.2f}")
    print(f"   Ganancia neta: ${resumen['total_ganancia_neta']:.2f}")
    print(f"\n📈 RENDIMIENTO:")
    roi = (resumen['total_ganancia_neta'] / dia['capital_inicial'] * 100) if dia['capital_inicial'] > 0 else 0
    print(f"   ROI del día: {roi:.2f}%")
    print("="*60)
    
    return resumen


# ===================================================================
# POOL DE REINVERSIÓN (INTERÉS COMPUESTO)
# ===================================================================

def aplicar_interes_compuesto(ciclo_id):
    """
    Convierte el efectivo del pool en cripto para el siguiente día
    Implementa interés compuesto automático
    """
    
    # Obtener efectivo disponible en el pool
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0) as total_efectivo
        FROM efectivo_banco
        WHERE ciclo_id = ?
    """, (ciclo_id,))
    
    efectivo_disponible = cursor.fetchone()['total_efectivo']
    
    if efectivo_disponible <= 0:
        log.info("No hay efectivo en el pool de reinversión", categoria='operaciones')
        return None
    
    print(f"\n💰 Pool de reinversión: ${efectivo_disponible:.2f} USD disponibles")
    print("\n¿Deseas reinvertir este efectivo en cripto para el siguiente día?")
    print("[1] Sí, reinvertir todo (Interés compuesto)")
    print("[2] No, mantener como efectivo")
    
    opcion = input("\nSelecciona (1-2): ").strip()
    
    if opcion != "1":
        log.info(f"Efectivo mantenido sin reinvertir: ${efectivo_disponible:.2f}", categoria='operaciones')
        return None
    
    # Seleccionar cripto para reinvertir
    print("\n¿En qué cripto deseas reinvertir?")
    cursor.execute("SELECT id, nombre, simbolo FROM criptomonedas ORDER BY nombre")
    criptos = cursor.fetchall()
    
    for i, c in enumerate(criptos, 1):
        print(f"[{i}] {c['nombre']} ({c['simbolo']})")
    
    try:
        seleccion = int(input("\nSelecciona: ")) - 1
        cripto_seleccionada = criptos[seleccion]
    except:
        print("❌ Selección inválida")
        return None
    
    # Pedir tasa de compra
    print(f"\nIngresa la tasa de compra actual de {cripto_seleccionada['simbolo']}:")
    try:
        tasa = float(input(f"1 {cripto_seleccionada['simbolo']} = $"))
    except:
        print("❌ Tasa inválida")
        return None
    
    # Calcular cantidad a comprar
    cantidad_comprada = efectivo_disponible / tasa
    
    print(f"\n📋 RESUMEN DE REINVERSIÓN:")
    print(f"   Efectivo a reinvertir: ${efectivo_disponible:.2f}")
    print(f"   Cripto: {cripto_seleccionada['nombre']}")
    print(f"   Tasa: 1 {cripto_seleccionada['simbolo']} = ${tasa:.4f}")
    print(f"   Cantidad: {cantidad_comprada:.8f} {cripto_seleccionada['simbolo']}")
    
    confirmar = input("\n¿Confirmar reinversión? (s/n): ").lower()
    if confirmar != 's':
        log.info("Reinversión cancelada", categoria='operaciones')
        return None
    
    # Agregar a la bóveda
    cursor.execute("""
        SELECT cantidad, precio_promedio 
        FROM boveda_ciclo 
        WHERE ciclo_id = ? AND cripto_id = ?
    """, (ciclo_id, cripto_seleccionada['id']))
    
    boveda_actual = cursor.fetchone()
    
    if boveda_actual:
        # Ya existe, calcular nuevo promedio ponderado
        cantidad_anterior = boveda_actual['cantidad']
        precio_anterior = boveda_actual['precio_promedio']
        
        costo_anterior = cantidad_anterior * precio_anterior
        costo_nuevo = cantidad_comprada * tasa
        costo_total = costo_anterior + costo_nuevo
        cantidad_total = cantidad_anterior + cantidad_comprada
        precio_promedio_nuevo = costo_total / cantidad_total
        
        cursor.execute("""
            UPDATE boveda_ciclo
            SET cantidad = ?,
                precio_promedio = ?
            WHERE ciclo_id = ? AND cripto_id = ?
        """, (cantidad_total, precio_promedio_nuevo, ciclo_id, cripto_seleccionada['id']))
    else:
        # No existe, crear nuevo registro
        cursor.execute("""
            INSERT INTO boveda_ciclo (ciclo_id, cripto_id, cantidad, precio_promedio)
            VALUES (?, ?, ?, ?)
        """, (ciclo_id, cripto_seleccionada['id'], cantidad_comprada, tasa))
    
    # Limpiar el pool de efectivo (ya se reinvirtió)
    cursor.execute("""
        DELETE FROM efectivo_banco WHERE ciclo_id = ?
    """, (ciclo_id,))
    
    conn.commit()
    
    # REGISTRAR EN LOG
    log.boveda_compra(
        cripto=cripto_seleccionada['nombre'],
        cantidad=cantidad_comprada,
        monto_usd=efectivo_disponible,
        tasa=tasa,
        ciclo_id=ciclo_id
    )
    
    log.info(
        f"INTERÉS COMPUESTO APLICADO: ${efectivo_disponible:.2f} reinvertidos en "
        f"{cantidad_comprada:.8f} {cripto_seleccionada['simbolo']}",
        categoria='operaciones'
    )
    
    print(f"\n✅ ¡Reinversión completada!")
    print(f"   Capital aumentado por interés compuesto")
    print(f"   Nuevo saldo: {cantidad_comprada:.8f} {cripto_seleccionada['simbolo']}")
    
    return {
        'monto_reinvertido': efectivo_disponible,
        'cripto': cripto_seleccionada['nombre'],
        'cantidad': cantidad_comprada,
        'tasa': tasa
    }


# ===================================================================
# RESUMEN Y PROGRESO
# ===================================================================

def obtener_progreso_ciclo(ciclo_id):
    """Obtiene el progreso completo del ciclo"""
    
    # Info del ciclo
    cursor.execute("""
        SELECT * FROM ciclos WHERE id = ?
    """, (ciclo_id,))
    ciclo = cursor.fetchone()
    
    if not ciclo:
        return None
    
    # Días del ciclo
    dias = obtener_resumen_dias(ciclo_id)
    
    # Capital actual
    capital = calcular_capital_actual_criptos(ciclo_id)
    
    # Efectivo en pool
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0) as efectivo
        FROM efectivo_banco WHERE ciclo_id = ?
    """, (ciclo_id,))
    efectivo = cursor.fetchone()['efectivo']
    
    # Ganancia acumulada
    cursor.execute("""
        SELECT COALESCE(SUM(ganancia_neta), 0) as ganancia_total
        FROM dias WHERE ciclo_id = ? AND estado = 'cerrado'
    """, (ciclo_id,))
    ganancia_total = cursor.fetchone()['ganancia_total']
    
    # Calcular días transcurridos
    fecha_inicio = datetime.strptime(ciclo['fecha_inicio'], '%Y-%m-%d')
    dias_transcurridos = (datetime.now() - fecha_inicio).days
    dias_restantes = max(0, ciclo['dias_planificados'] - dias_transcurridos)
    
    return {
        'ciclo': ciclo,
        'dias': dias,
        'dias_transcurridos': dias_transcurridos,
        'dias_restantes': dias_restantes,
        'capital_criptos': capital,
        'efectivo_pool': efectivo,
        'capital_total': capital + efectivo,
        'ganancia_total': ganancia_total
    }


def mostrar_progreso_ciclo(ciclo_id):
    """Muestra el progreso del ciclo en pantalla"""
    
    progreso = obtener_progreso_ciclo(ciclo_id)
    if not progreso:
        print("❌ No se pudo obtener el progreso del ciclo")
        return
    
    ciclo = progreso['ciclo']
    avance_pct = (progreso['dias_transcurridos'] / ciclo['dias_planificados'] * 100) if ciclo['dias_planificados'] > 0 else 0
    
    print("\n" + "="*60)
    print("PROGRESO DEL CICLO GLOBAL")
    print("="*60)
    print(f"\n🔄 Ciclo #{ciclo['id']}")
    print(f"Fecha inicio: {ciclo['fecha_inicio']}")
    print(f"Días planificados: {ciclo['dias_planificados']}")
    print(f"Días transcurridos: {progreso['dias_transcurridos']}")
    print(f"Días restantes: {progreso['dias_restantes']}")
    print(f"Avance: {avance_pct:.1f}%")
    
    print(f"\n💰 CAPITAL:")
    print(f"Inversión inicial: ${ciclo['inversion_inicial']:.2f}")
    print(f"En criptos: ${progreso['capital_criptos']:.2f}")
    print(f"En pool (efectivo): ${progreso['efectivo_pool']:.2f}")
    print(f"Total actual: ${progreso['capital_total']:.2f}")
    
    print(f"\n📊 RENDIMIENTO:")
    print(f"Ganancia acumulada: ${progreso['ganancia_total']:.2f}")
    if ciclo['inversion_inicial'] > 0:
        roi = (progreso['ganancia_total'] / ciclo['inversion_inicial']) * 100
        print(f"ROI total: {roi:.2f}%")
    
    if progreso['dias']:
        print(f"\n📅 Resumen de días:")
        for dia in progreso['dias']:
            estado_emoji = "✅" if dia['estado'] == 'cerrado' else "🔄"
            print(f"  {estado_emoji} Día {dia['numero_dia']:2d} ({dia['fecha']}) - ${dia['ganancia_neta']:7.2f} [{dia['estado'].upper()}]")
    
    print("="*60)


# ===================================================================
# FUNCIONES DE UTILIDAD
# ===================================================================

def validar_limite_ventas(dia_id):
    """Valida si se puede registrar otra venta según el límite diario"""
    ventas_hoy = contar_ventas_del_dia(dia_id)
    
    MINIMO_VENTAS = 3
    MAXIMO_VENTAS = 5
    
    if ventas_hoy >= MAXIMO_VENTAS:
        return False, f"Límite alcanzado: {MAXIMO_VENTAS} ventas por día"
    
    return True, f"{ventas_hoy}/{MAXIMO_VENTAS} ventas realizadas"


def verificar_capital_disponible(ciclo_id):
    """Verifica si hay capital disponible para operar"""
    criptos = obtener_criptos_disponibles(ciclo_id)
    
    if not criptos:
        # Verificar si hay efectivo en el pool
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as efectivo
            FROM efectivo_banco WHERE ciclo_id = ?
        """, (ciclo_id,))
        efectivo = cursor.fetchone()['efectivo']
        
        if efectivo > 0:
            return True, f"Hay ${efectivo:.2f} en el pool de reinversión"
        return False, "No hay capital disponible"
    
    return True, f"{len(criptos)} cripto(s) disponible(s)"


# ===================================================================
# COMMIT Y CIERRE
# ===================================================================

def guardar_cambios():
    """Guarda los cambios en la base de datos"""
    conn.commit()
    log.info("Cambios guardados en la base de datos", categoria='general')


def cerrar_conexion():
    """Cierra la conexión a la base de datos"""
    conn.close()
    log.info("Conexión a base de datos cerrada", categoria='general')
