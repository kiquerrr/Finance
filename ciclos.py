# -*- coding: utf-8 -*-
"""
=============================================================================
MÓDULO DE CICLOS - Gestión de Ciclos Globales (CORREGIDO)
=============================================================================
Maneja el ciclo de vida completo de los ciclos de arbitraje
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
# CREAR CICLO
# ===================================================================

def crear_ciclo(dias_duracion=15):
    """
    Crea un nuevo ciclo global
    
    Args:
        dias_duracion: Duración planificada del ciclo en días
    
    Returns:
        int: ID del ciclo creado
    """
    
    fecha_inicio = datetime.now().date()
    fecha_fin = fecha_inicio + timedelta(days=dias_duracion)
    
    # CORRECCIÓN: Calcular inversión inicial correctamente
    cursor.execute("""
        SELECT COALESCE(SUM(bc.cantidad * bc.precio_promedio), 0) as capital_inicial
        FROM boveda_ciclo bc
        WHERE bc.cantidad > 0
    """)
    
    inversion_inicial = cursor.fetchone()['capital_inicial']
    
    # Si no hay capital, advertir
    if inversion_inicial == 0:
        print("\n⚠️  ADVERTENCIA: No hay capital en la bóveda")
        print("    La inversión inicial será $0.00")
        print("    Fondea la bóveda antes de operar")
        
        continuar = input("\n¿Continuar creando el ciclo? (s/n): ").lower()
        if continuar != 's':
            print("❌ Creación de ciclo cancelada")
            return None
    
    # Insertar ciclo
    cursor.execute("""
        INSERT INTO ciclos (
            fecha_inicio, 
            fecha_fin_estimada, 
            dias_planificados,
            inversion_inicial,
            estado
        ) VALUES (?, ?, ?, ?, 'activo')
    """, (
        fecha_inicio.strftime('%Y-%m-%d'),
        fecha_fin.strftime('%Y-%m-%d'),
        dias_duracion,
        inversion_inicial
    ))
    
    ciclo_id = cursor.lastrowid
    conn.commit()
    
    # Registrar en log
    log.ciclo_creado(
        ciclo_id=ciclo_id,
        dias=dias_duracion,
        capital_inicial=inversion_inicial,
        fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
        fecha_fin=fecha_fin.strftime('%Y-%m-%d')
    )
    
    print(f"\n✅ Nuevo ciclo #{ciclo_id} creado exitosamente!")
    print(f"    Duración: {dias_duracion} días")
    print(f"    Fecha inicio: {fecha_inicio}")
    print(f"    Fecha fin estimada: {fecha_fin}")
    print(f"    Inversión inicial: ${inversion_inicial:.2f}")
    
    return ciclo_id


# ===================================================================
# OBTENER INFORMACIÓN DE CICLOS
# ===================================================================

def obtener_ciclo_activo():
    """Obtiene el ciclo actualmente activo"""
    cursor.execute("""
        SELECT * FROM ciclos
        WHERE estado = 'activo'
        ORDER BY id DESC
        LIMIT 1
    """)
    return cursor.fetchone()


def obtener_ciclo(ciclo_id):
    """Obtiene información de un ciclo específico"""
    cursor.execute("SELECT * FROM ciclos WHERE id = ?", (ciclo_id,))
    return cursor.fetchone()


def calcular_dias_transcurridos(ciclo_id):
    """Calcula cuántos días han transcurrido desde el inicio del ciclo"""
    ciclo = obtener_ciclo(ciclo_id)
    if not ciclo:
        return 0
    
    fecha_inicio = datetime.strptime(ciclo['fecha_inicio'], '%Y-%m-%d').date()
    dias_transcurridos = (datetime.now().date() - fecha_inicio).days
    
    return dias_transcurridos


def calcular_dias_restantes(ciclo_id):
    """Calcula cuántos días faltan para completar el ciclo"""
    ciclo = obtener_ciclo(ciclo_id)
    if not ciclo:
        return 0
    
    dias_transcurridos = calcular_dias_transcurridos(ciclo_id)
    dias_restantes = max(0, ciclo['dias_planificados'] - dias_transcurridos)
    
    return dias_restantes


def verificar_ciclo_completado(ciclo_id):
    """
    Verifica si el ciclo ha alcanzado su duración planificada
    
    Returns:
        tuple: (completado: bool, mensaje: str)
    """
    ciclo = obtener_ciclo(ciclo_id)
    if not ciclo:
        return False, "Ciclo no encontrado"
    
    dias_transcurridos = calcular_dias_transcurridos(ciclo_id)
    dias_planificados = ciclo['dias_planificados']
    
    if dias_transcurridos >= dias_planificados:
        return True, f"El ciclo ha completado sus {dias_planificados} días planificados"
    
    return False, f"Quedan {dias_planificados - dias_transcurridos} días para completar el ciclo"


# ===================================================================
# VALIDACIONES DE CICLO
# ===================================================================

def puede_operar_dia(ciclo_id):
    """
    Verifica si se puede operar un nuevo día en el ciclo
    
    Returns:
        tuple: (puede_operar: bool, mensaje: str, accion_sugerida: str)
    """
    
    ciclo = obtener_ciclo(ciclo_id)
    if not ciclo:
        return False, "Ciclo no encontrado", None
    
    if ciclo['estado'] != 'activo':
        return False, f"El ciclo está {ciclo['estado']}", None
    
    # Verificar si el ciclo ha completado su duración
    completado, mensaje = verificar_ciclo_completado(ciclo_id)
    
    if completado:
        return False, mensaje, "CERRAR_O_EXTENDER"
    
    # Verificar si hay un día abierto
    cursor.execute("""
        SELECT * FROM dias
        WHERE ciclo_id = ? AND estado = 'abierto'
    """, (ciclo_id,))
    
    dia_abierto = cursor.fetchone()
    if dia_abierto:
        return False, f"Ya hay un día abierto (#{dia_abierto['numero_dia']})", "CERRAR_DIA"
    
    return True, "Puede operar", None


# ===================================================================
# GESTIÓN DEL CICLO
# ===================================================================

def extender_ciclo(ciclo_id, dias_adicionales):
    """Extiende la duración de un ciclo"""
    
    ciclo = obtener_ciclo(ciclo_id)
    if not ciclo:
        log.error("Ciclo no encontrado", f"ID: {ciclo_id}")
        return False
    
    dias_nuevos = ciclo['dias_planificados'] + dias_adicionales
    fecha_inicio = datetime.strptime(ciclo['fecha_inicio'], '%Y-%m-%d').date()
    fecha_fin_nueva = fecha_inicio + timedelta(days=dias_nuevos)
    
    cursor.execute("""
        UPDATE ciclos SET
            dias_planificados = ?,
            fecha_fin_estimada = ?
        WHERE id = ?
    """, (dias_nuevos, fecha_fin_nueva.strftime('%Y-%m-%d'), ciclo_id))
    
    conn.commit()
    
    log.info(
        f"Ciclo #{ciclo_id} extendido: {ciclo['dias_planificados']} → {dias_nuevos} días",
        categoria='ciclos'
    )
    
    print(f"\n✅ Ciclo extendido")
    print(f"    Duración nueva: {dias_nuevos} días")
    print(f"    Nueva fecha fin: {fecha_fin_nueva}")
    
    return True


def cerrar_ciclo(ciclo_id, forzar=False):
    """
    Cierra un ciclo global
    
    Args:
        ciclo_id: ID del ciclo a cerrar
        forzar: Si es True, cierra aunque no haya completado los días
    
    Returns:
        bool: True si se cerró exitosamente
    """
    
    ciclo = obtener_ciclo(ciclo_id)
    if not ciclo:
        log.error("Ciclo no encontrado", f"ID: {ciclo_id}")
        return False
    
    if ciclo['estado'] != 'activo':
        log.advertencia(f"El ciclo #{ciclo_id} ya está {ciclo['estado']}", categoria='ciclos')
        print(f"⚠️  El ciclo ya está {ciclo['estado']}")
        return False
    
    # Verificar si hay días abiertos
    cursor.execute("""
        SELECT COUNT(*) as dias_abiertos
        FROM dias
        WHERE ciclo_id = ? AND estado = 'abierto'
    """, (ciclo_id,))
    
    dias_abiertos = cursor.fetchone()['dias_abiertos']
    if dias_abiertos > 0:
        print(f"❌ No se puede cerrar el ciclo: hay {dias_abiertos} día(s) abierto(s)")
        print("    Cierra todos los días antes de cerrar el ciclo")
        return False
    
    # Verificar si el ciclo está completo
    if not forzar:
        completado, mensaje = verificar_ciclo_completado(ciclo_id)
        if not completado:
            print(f"\n⚠️  {mensaje}")
            confirmar = input("¿Deseas cerrar el ciclo antes de tiempo? (s/n): ").lower()
            if confirmar != 's':
                print("❌ Cierre cancelado")
                return False
    
    # Calcular datos finales
    dias_transcurridos = calcular_dias_transcurridos(ciclo_id)
    
    # Obtener días operados
    cursor.execute("""
        SELECT COUNT(*) as dias_operados
        FROM dias
        WHERE ciclo_id = ? AND estado = 'cerrado'
    """, (ciclo_id,))
    dias_operados = cursor.fetchone()['dias_operados']
    
    # Calcular ganancia total
    cursor.execute("""
        SELECT COALESCE(SUM(ganancia_neta), 0) as ganancia_total
        FROM dias
        WHERE ciclo_id = ? AND estado = 'cerrado'
    """, (ciclo_id,))
    ganancia_total = cursor.fetchone()['ganancia_total']
    
    # Calcular capital final
    cursor.execute("""
        SELECT COALESCE(SUM(bc.cantidad * bc.precio_promedio), 0) as capital_criptos
        FROM boveda_ciclo bc
        WHERE bc.ciclo_id = ? AND bc.cantidad > 0
    """, (ciclo_id,))
    capital_criptos = cursor.fetchone()['capital_criptos']
    
    # Efectivo en pool
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0) as efectivo
        FROM efectivo_banco
        WHERE ciclo_id = ?
    """, (ciclo_id,))
    efectivo = cursor.fetchone()['efectivo']
    
    capital_final = capital_criptos + efectivo
    
    # Calcular ROI
    inversion_inicial = ciclo['inversion_inicial']
    roi_total = (ganancia_total / inversion_inicial * 100) if inversion_inicial > 0 else 0
    
    # Actualizar ciclo
    cursor.execute("""
        UPDATE ciclos SET
            estado = 'cerrado',
            fecha_cierre = ?,
            dias_operados = ?,
            ganancia_total = ?,
            capital_final = ?,
            roi_total = ?
        WHERE id = ?
    """, (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        dias_operados,
        ganancia_total,
        capital_final,
        roi_total,
        ciclo_id
    ))
    
    conn.commit()
    
    # Registrar en log
    log.ciclo_cerrado(
        ciclo_id=ciclo_id,
        dias_operados=dias_operados,
        inversion_inicial=inversion_inicial,
        ganancia_total=ganancia_total,
        capital_final=capital_final
    )
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("CICLO CERRADO")
    print("="*60)
    print(f"\n📊 RESUMEN DEL CICLO #{ciclo_id}")
    print(f"    Duración planificada: {ciclo['dias_planificados']} días")
    print(f"    Días transcurridos: {dias_transcurridos}")
    print(f"    Días operados: {dias_operados}")
    
    print(f"\n💰 BALANCE FINANCIERO:")
    print(f"    Inversión inicial: ${inversion_inicial:.2f}")
    print(f"    Ganancia total: ${ganancia_total:.2f}")
    print(f"    Capital final: ${capital_final:.2f}")
    print(f"    ROI total: {roi_total:.2f}%")
    
    if dias_operados > 0:
        ganancia_promedio = ganancia_total / dias_operados
        roi_diario = roi_total / dias_operados
        print(f"\n📈 PROMEDIOS:")
        print(f"    Ganancia diaria promedio: ${ganancia_promedio:.2f}")
        print(f"    ROI diario promedio: {roi_diario:.2f}%")
    
    print("="*60)
    
    return True


# ===================================================================
# MOSTRAR INFORMACIÓN
# ===================================================================

def mostrar_info_ciclo(ciclo_id):
    """Muestra información detallada de un ciclo"""
    
    ciclo = obtener_ciclo(ciclo_id)
    if not ciclo:
        print("❌ Ciclo no encontrado")
        return
    
    dias_transcurridos = calcular_dias_transcurridos(ciclo_id)
    dias_restantes = calcular_dias_restantes(ciclo_id)
    
    # Capital actual
    cursor.execute("""
        SELECT 
            c.nombre,
            c.simbolo,
            bc.cantidad,
            bc.precio_promedio,
            (bc.cantidad * bc.precio_promedio) as valor
        FROM boveda_ciclo bc
        JOIN criptomonedas c ON bc.cripto_id = c.id
        WHERE bc.ciclo_id = ? AND bc.cantidad > 0
    """, (ciclo_id,))
    
    criptos = cursor.fetchall()
    capital_criptos = sum(c['valor'] for c in criptos)
    
    # Efectivo
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0) as efectivo
        FROM efectivo_banco WHERE ciclo_id = ?
    """, (ciclo_id,))
    efectivo = cursor.fetchone()['efectivo']
    
    capital_total = capital_criptos + efectivo
    
    print("\n" + "="*60)
    print(f"CICLO GLOBAL #{ciclo_id}")
    print("="*60)
    print(f"\n🗓️ FECHAS:")
    print(f"    Inicio: {ciclo['fecha_inicio']}")
    print(f"    Fin estimada: {ciclo['fecha_fin_estimada']}")
    print(f"    Estado: {ciclo['estado'].upper()}")
    
    print(f"\n⏱️ PROGRESO:")
    print(f"    Días planificados: {ciclo['dias_planificados']}")
    print(f"    Días transcurridos: {dias_transcurridos}")
    print(f"    Días restantes: {dias_restantes}")
    
    avance = (dias_transcurridos / ciclo['dias_planificados'] * 100) if ciclo['dias_planificados'] > 0 else 0
    print(f"    Avance: {avance:.1f}%")
    
    print(f"\n💰 CAPITAL:")
    print(f"    Inversión inicial: ${ciclo['inversion_inicial']:.2f}")
    
    if criptos:
        print(f"\n    Criptos actuales:")
        for cripto in criptos:
            print(f"      • {cripto['cantidad']:.8f} {cripto['simbolo']} = ${cripto['valor']:.2f}")
    
    if efectivo > 0:
        print(f"\n    Efectivo en pool: ${efectivo:.2f}")
    
    print(f"\n    Capital total actual: ${capital_total:.2f}")
    
    # Ganancia acumulada
    cursor.execute("""
        SELECT COALESCE(SUM(ganancia_neta), 0) as ganancia
        FROM dias WHERE ciclo_id = ? AND estado = 'cerrado'
    """, (ciclo_id,))
    ganancia = cursor.fetchone()['ganancia']
    
    if ganancia > 0:
        roi = (ganancia / ciclo['inversion_inicial'] * 100) if ciclo['inversion_inicial'] > 0 else 0
        print(f"\n📈 RENDIMIENTO:")
        print(f"    Ganancia acumulada: ${ganancia:.2f}")
        print(f"    ROI: {roi:.2f}%")
    
    print("="*60)


def mostrar_opciones_ciclo(ciclo_id):
    """Muestra las opciones disponibles para un ciclo"""
    
    completado, mensaje = verificar_ciclo_completado(ciclo_id)
    puede_operar, msg_operar, accion = puede_operar_dia(ciclo_id)
    
    print("\n" + "="*60)
    print("¿QUÉ DESEAS HACER?")
    print("="*60)
    
    opciones = []
    
    # Verificar si hay día abierto
    cursor.execute("""
        SELECT * FROM dias
        WHERE ciclo_id = ? AND estado = 'abierto'
    """, (ciclo_id,))
    dia_abierto = cursor.fetchone()
    
    if dia_abierto:
        print(f"⚠️  Hay un día abierto (#{dia_abierto['numero_dia']}). Debes cerrarlo primero.")
        print("[1] CERRAR día actual y continuar")
        opciones.append("CERRAR_DIA_CONTINUAR") # Cambiado para evitar conflicto
    elif puede_operar:
        print("[1] CONTINUAR operando en el ciclo (Abrir nuevo día)")
        opciones.append("CONTINUAR")
    else:
        if accion == "CERRAR_O_EXTENDER":
            print("⚠️  El ciclo ha completado su duración planificada")
        elif accion is None:
             print("⚠️  No se puede operar en este momento.")
    
    print("[2] VER PROGRESO y estadísticas del ciclo")
    opciones.append("PROGRESO")
    
    # Lógica para opciones 3 y 4
    if completado:
        print("[3] EXTENDER el ciclo (agregar más días)")
        opciones.append("EXTENDER")
        print("[4] CERRAR el ciclo e iniciar uno nuevo")
        opciones.append("CERRAR")
        print("[5] CANCELAR y volver al menú")
        opciones.append("CANCELAR")
    else:
        # En este caso, la opción 3 es CERRAR
        print("[3] CERRAR el ciclo e iniciar uno nuevo (Cierre anticipado)")
        opciones.append("CERRAR")
        print("[4] CANCELAR y volver al menú")
        opciones.append("CANCELAR")
    
    print("="*60)
    
    return opciones


# ===================================================================
# MENÚ INTERACTIVO
# ===================================================================

def gestionar_ciclo_activo():
    """Gestiona el ciclo activo con opciones inteligentes"""
    
    ciclo = obtener_ciclo_activo()
    
    if not ciclo:
        print("\n⚠️  No hay ciclo activo")
        print("\n¿Deseas iniciar un nuevo ciclo global? (s/n): ", end='')
        respuesta = input().strip().lower()
        
        if respuesta == 's':
            return crear_nuevo_ciclo_interactivo()
        return None
    
    # Mostrar información del ciclo
    mostrar_info_ciclo(ciclo['id'])
    
    while True:
        # Mostrar opciones
        opciones = mostrar_opciones_ciclo(ciclo['id'])
        
        seleccion = input("\nSelecciona una opción: ").strip()
        
        # Opciones para ciclos NO COMPLETADOS
        if not verificar_ciclo_completado(ciclo['id'])[0]:
            if seleccion == "1":
                if "CONTINUAR" in opciones or "CERRAR_DIA_CONTINUAR" in opciones:
                    return ciclo['id']  # Retornar para continuar operando o ir al submenú del día
                else:
                    print("❌ Opción inválida o no disponible.")
                    continue

            elif seleccion == "2":
                from dias import mostrar_progreso_ciclo
                mostrar_progreso_ciclo(ciclo['id'])
                input("\nPresiona Enter para continuar...")
                # Repetir bucle para mostrar info y opciones de nuevo
            
            elif seleccion == "3":
                if "CERRAR" in opciones:
                    return cerrar_y_crear_nuevo(ciclo['id'])
                else:
                    print("❌ Opción inválida o no disponible.")

            elif seleccion == "4":
                if "CANCELAR" in opciones:
                    return None  # Cancelar
                else:
                    print("❌ Opción inválida o no disponible.")
            
            else:
                 print("❌ Opción inválida")

        # Opciones para ciclos COMPLETADOS
        else:
            if seleccion == "1":
                if "CERRAR_DIA_CONTINUAR" in opciones:
                     return ciclo['id'] # Cierra día y luego se le ofrecerá CERRAR/EXTENDER
                else:
                    print("❌ Opción inválida. El ciclo completó su duración, no puede CONTINUAR operando un día nuevo.")

            elif seleccion == "2":
                from dias import mostrar_progreso_ciclo
                mostrar_progreso_ciclo(ciclo['id'])
                input("\nPresiona Enter para continuar...")
                # Repetir bucle para mostrar info y opciones de nuevo
            
            elif seleccion == "3":
                if "EXTENDER" in opciones:
                    # Opción de extender
                    try:
                        dias = int(input("\n¿Cuántos días adicionales?: "))
                        extender_ciclo(ciclo['id'], dias)
                        input("\nPresiona Enter para continuar...")
                        # Repetir bucle para mostrar info y opciones de nuevo
                    except ValueError:
                        print("❌ Número inválido")
                else:
                    print("❌ Opción inválida o no disponible.")

            elif seleccion == "4":
                if "CERRAR" in opciones:
                    return cerrar_y_crear_nuevo(ciclo['id'])
                else:
                    print("❌ Opción inválida o no disponible.")
            
            elif seleccion == "5":
                if "CANCELAR" in opciones:
                    return None  # Cancelar
                else:
                    print("❌ Opción inválida o no disponible.")
            
            else:
                print("❌ Opción inválida")


def crear_nuevo_ciclo_interactivo():
    """Crea un nuevo ciclo de forma interactiva"""
    
    print("\n" + "="*60)
    print("CREAR NUEVO CICLO GLOBAL")
    print("="*60)
    
    try:
        dias_input = input("\n¿Cuántos días durará este ciclo?\n(Por defecto: 15 días)\nDías del ciclo (Enter para 15): ").strip()
        dias = int(dias_input) if dias_input else 15
        
        if dias < 1:
            print("❌ Debe ser al menos 1 día")
            return None
        
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=dias)
        
        print(f"\nFecha inicio: {fecha_inicio}")
        print(f"Fecha fin estimada: {fecha_fin}")
        print(f"Duración: {dias} días")
        
        confirmar = input("\n¿Confirmar creación del ciclo? (s/n): ").strip().lower()
        
        if confirmar == 's':
            ciclo_id = crear_ciclo(dias)
            return ciclo_id
        else:
            print("❌ Creación cancelada")
            return None
            
    except ValueError:
        print("❌ Número de días inválido")
        return None


def cerrar_y_crear_nuevo(ciclo_id):
    """Cierra el ciclo actual y opcionalmente crea uno nuevo"""
    
    print("\n" + "="*60)
    print("CIERRE DEL CICLO GLOBAL")
    print("="*60)
    
    # Mostrar progreso antes de cerrar
    from dias import mostrar_progreso_ciclo
    mostrar_progreso_ciclo(ciclo_id)
    
    # Cerrar ciclo
    if cerrar_ciclo(ciclo_id):
        print("\n¿Deseas iniciar un nuevo ciclo? (s/n): ", end='')
        respuesta = input().strip().lower()
        
        if respuesta == 's':
            return crear_nuevo_ciclo_interactivo()
    
    return None


# ===================================================================
# ESTADÍSTICAS DE CICLOS
# ===================================================================

def obtener_estadisticas_generales():
    """Obtiene estadísticas generales de todos los ciclos"""
    
    # Total de ciclos
    cursor.execute("SELECT COUNT(*) as total FROM ciclos")
    total_ciclos = cursor.fetchone()['total']
    
    # Ciclos activos
    cursor.execute("SELECT COUNT(*) as activos FROM ciclos WHERE estado = 'activo'")
    ciclos_activos = cursor.fetchone()['activos']
    
    # Ciclos cerrados
    cursor.execute("SELECT COUNT(*) as cerrados FROM ciclos WHERE estado = 'cerrado'")
    ciclos_cerrados = cursor.fetchone()['cerrados']
    
    # Ganancia total histórica
    cursor.execute("SELECT COALESCE(SUM(ganancia_total), 0) as ganancia FROM ciclos WHERE estado = 'cerrado'")
    ganancia_total = cursor.fetchone()['ganancia']
    
    # Inversión total histórica
    cursor.execute("SELECT COALESCE(SUM(inversion_inicial), 0) as inversion FROM ciclos")
    inversion_total = cursor.fetchone()['inversion']
    
    # ROI promedio
    cursor.execute("""
        SELECT AVG(roi_total) as roi_promedio
        FROM ciclos
        WHERE estado = 'cerrado' AND roi_total IS NOT NULL
    """)
    roi_promedio = cursor.fetchone()['roi_promedio'] or 0
    
    return {
        'total_ciclos': total_ciclos,
        'ciclos_activos': ciclos_activos,
        'ciclos_cerrados': ciclos_cerrados,
        'ganancia_total': ganancia_total,
        'inversion_total': inversion_total,
        'roi_promedio': roi_promedio
    }


def listar_ciclos_historicos(limite=10):
    """Lista los últimos ciclos cerrados"""
    
    cursor.execute("""
        SELECT *
        FROM ciclos
        WHERE estado = 'cerrado'
        ORDER BY fecha_cierre DESC
        LIMIT ?
    """, (limite,))
    
    return cursor.fetchall()


def mostrar_estadisticas_completas():
    """Muestra estadísticas completas de todos los ciclos"""
    
    stats = obtener_estadisticas_generales()
    
    print("\n" + "="*60)
    print("ESTADÍSTICAS GENERALES DE CICLOS")
    print("="*60)
    
    print(f"\n📊 RESUMEN:")
    print(f"    Total de ciclos: {stats['total_ciclos']}")
    print(f"    Ciclos activos: {stats['ciclos_activos']}")
    print(f"    Ciclos cerrados: {stats['ciclos_cerrados']}")
    
    print(f"\n💰 FINANCIERO:")
    print(f"    Inversión total histórica: ${stats['inversion_total']:.2f}")
    print(f"    Ganancia total histórica: ${stats['ganancia_total']:.2f}")
    print(f"    ROI promedio: {stats['roi_promedio']:.2f}%")
    
    # Últimos ciclos
    ciclos_recientes = listar_ciclos_historicos(5)
    
    if ciclos_recientes:
        print(f"\n📜 ÚLTIMOS CICLOS CERRADOS:")
        for ciclo in ciclos_recientes:
            print(f"\n    Ciclo #{ciclo['id']}")
            print(f"    • Fechas: {ciclo['fecha_inicio']} → {ciclo['fecha_cierre']}")
            print(f"    • Días operados: {ciclo['dias_operados']}")
            print(f"    • Ganancia: ${ciclo['ganancia_total']:.2f}")
            print(f"    • ROI: {ciclo['roi_total']:.2f}%")
    
    print("="*60)


# ===================================================================
# FUNCIONES DE UTILIDAD
# ===================================================================

def hay_ciclo_activo():
    """Verifica si hay un ciclo activo"""
    ciclo = obtener_ciclo_activo()
    return ciclo is not None


def obtener_id_ciclo_activo():
    """Obtiene el ID del ciclo activo"""
    ciclo = obtener_ciclo_activo()
    return ciclo['id'] if ciclo else None


def validar_puede_fondear():
    """Valida si se puede fondear la bóveda (ya NO requiere ciclo activo)"""
    # Ahora se puede fondear sin ciclo activo
    return True, "Puedes fondear en cualquier momento"


# ===================================================================
# INICIALIZACIÓN
# ===================================================================

def inicializar_tabla_ciclos():
    """Crea la tabla de ciclos si no existe"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ciclos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_inicio DATE NOT NULL,
            fecha_fin_estimada DATE,
            fecha_cierre TIMESTAMP,
            dias_planificados INTEGER NOT NULL,
            dias_operados INTEGER DEFAULT 0,
            inversion_inicial REAL DEFAULT 0,
            ganancia_total REAL DEFAULT 0,
            capital_final REAL DEFAULT 0,
            roi_total REAL DEFAULT 0,
            estado TEXT DEFAULT 'activo',
            notas TEXT
        )
    """)
    conn.commit()


# Inicializar al importar el módulo
inicializar_tabla_ciclos()


if __name__ == "__main__":
    # Testing
    print("Módulo de Ciclos - Testing")
    gestionar_ciclo_activo()
