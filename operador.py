"""
=============================================================================
MÓDULO OPERADOR - Gestión de Operaciones Diarias
=============================================================================
Coordina todas las operaciones del día: precio, ventas, cierre
"""

import sqlite3
from logger import log
from calculos import calc
from ciclos import (
    obtener_ciclo_activo,
    gestionar_ciclo_activo,
    puede_operar_dia,
    mostrar_info_ciclo
)
from dias import (
    iniciar_dia,
    obtener_dia_actual,
    definir_precio_venta,
    registrar_venta,
    cerrar_dia,
    aplicar_interes_compuesto,
    obtener_criptos_disponibles,
    validar_limite_ventas
)

# Conexión a la base de datos
conn = sqlite3.connect('arbitraje.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


# ===================================================================
# FUNCIÓN PRINCIPAL DEL OPERADOR
# ===================================================================

def modulo_operador():
    """
    Módulo principal del operador
    Coordina todo el flujo de operación diaria
    """
    
    log.separador('operaciones')
    log.info("Módulo operador iniciado", categoria='operaciones')
    
    print("\n" + "="*60)
    print("MODULO OPERADOR: INICIANDO DIA DE OPERACION")
    print("="*60)
    
    try:
        # 1. Gestionar ciclo activo o crear uno nuevo
        ciclo_id = gestionar_ciclo_activo()
        
        if not ciclo_id:
            print("\n⚠️  No hay ciclo activo. Volviendo al menú principal...")
            input("\nPresiona Enter para continuar...")
            return
        
        # 2. Verificar si puede operar
        puede_operar, mensaje, accion = puede_operar_dia(ciclo_id)
        
        if not puede_operar:
            if accion == "CERRAR_DIA":
                print(f"\n⚠️  {mensaje}")
                print("Debes cerrar el día abierto antes de continuar.")
                
                cerrar_dia_actual = input("\n¿Deseas cerrar el día actual? (s/n): ").lower()
                if cerrar_dia_actual == 's':
                    dia_actual = obtener_dia_actual(ciclo_id)
                    if dia_actual:
                        ejecutar_cierre_dia(dia_actual['id'], ciclo_id)
                
                input("\nPresiona Enter para continuar...")
                return
            
            elif accion == "CERRAR_O_EXTENDER":
                print(f"\n⚠️  {mensaje}")
                print("Opciones:")
                print("  [1] Extender el ciclo")
                print("  [2] Cerrar el ciclo")
                print("  [3] Volver")
                
                opcion = input("\nSelecciona: ").strip()
                
                if opcion == "1":
                    from ciclos import extender_ciclo
                    dias_extra = int(input("¿Cuántos días adicionales?: "))
                    extender_ciclo(ciclo_id, dias_extra)
                elif opcion == "2":
                    from ciclos import cerrar_ciclo
                    cerrar_ciclo(ciclo_id)
                
                input("\nPresiona Enter para continuar...")
                return
        
        # 3. Trabajar en el ciclo
        print(f"\nTrabajando en el ciclo global #{ciclo_id}.")
        
        # 4. Iniciar o continuar día
        dia_id = obtener_dia_actual(ciclo_id)
        
        if not dia_id:
            # Iniciar nuevo día
            print("\nIniciando nuevo dia de operacion...")
            dia_id = iniciar_dia(ciclo_id)
            
            if not dia_id:
                print("❌ No se pudo iniciar el día")
                input("\nPresiona Enter para continuar...")
                return
        
        # 5. Ejecutar operaciones del día
        ejecutar_operaciones_dia(dia_id, ciclo_id)
        
    except Exception as e:
        log.error("Error en módulo operador", str(e))
        print(f"\n❌ Error en el módulo operador: {e}")
        input("\nPresiona Enter para continuar...")


# ===================================================================
# OPERACIONES DEL DÍA
# ===================================================================

def ejecutar_operaciones_dia(dia_id, ciclo_id):
    """Ejecuta todas las operaciones del día"""
    
    # Obtener información del día
    cursor.execute("SELECT * FROM dias WHERE id = ?", (dia_id,))
    dia = cursor.fetchone()
    
    # Mostrar información del día
    print(f"\nDia de operacion #{dia['numero_dia']}")
    print(f"Capital inicial del dia: ${dia['capital_inicial']:.2f}")
    
    # Obtener criptos disponibles
    criptos = obtener_criptos_disponibles(ciclo_id)
    
    if not criptos:
        print("\n❌ No hay criptos disponibles para operar")
        print("   Fondea la bóveda antes de operar")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\nCapital actual:")
    for cripto in criptos:
        print(f"  - {cripto['cantidad']:.8f} {cripto['nombre']} ({cripto['simbolo']}) = ${cripto['valor_usd']:.2f}")
    
    total = sum(c['valor_usd'] for c in criptos)
    print(f"  Total: ${total:.2f} USD")
    
    # Seleccionar cripto para operar
    cripto_seleccionada = seleccionar_cripto(criptos)
    
    if not cripto_seleccionada:
        print("\n❌ No se seleccionó ninguna cripto")
        input("\nPresiona Enter para continuar...")
        return
    
    # Definir precio de venta
    precio_definido = definir_precio_operacion(dia_id, cripto_seleccionada)
    
    if not precio_definido:
        print("\n❌ No se definió el precio")
        input("\nPresiona Enter para continuar...")
        return
    
    # Realizar ventas
    ejecutar_ventas_dia(dia_id, ciclo_id, cripto_seleccionada)
    
    # Cerrar día
    print("\n" + "-"*60)
    print("CIERRE DEL DIA")
    print("-"*60)
    
    cerrar = input("\n¿Deseas cerrar el dia de operacion? (s/n): ").lower()
    
    if cerrar == 's':
        ejecutar_cierre_dia(dia_id, ciclo_id)
    else:
        print("\n⚠️  Día no cerrado. Puedes continuar después.")
        input("\nPresiona Enter para continuar...")


def seleccionar_cripto(criptos):
    """Permite seleccionar una cripto para operar"""
    
    print("\n¿Con cual cripto deseas operar hoy?")
    
    for i, cripto in enumerate(criptos, 1):
        print(f"[{i}] {cripto['nombre']} ({cripto['simbolo']}) - {cripto['cantidad']:.8f} disponibles")
    
    try:
        seleccion = int(input("\nSelecciona (numero): ")) - 1
        
        if 0 <= seleccion < len(criptos):
            return criptos[seleccion]
        else:
            print("❌ Selección inválida")
            return None
    except ValueError:
        print("❌ Entrada inválida")
        return None


def definir_precio_operacion(dia_id, cripto):
    """Define el precio de venta para el día"""
    
    print("\n" + "-"*60)
    print("ANALISIS DE MERCADO Y DEFINICION DE PRECIO")
    print("-"*60)
    
    # Obtener configuración
    cursor.execute("SELECT comision_default, ganancia_neta_default FROM config WHERE id = 1")
    config = cursor.fetchone()
    
    comision = config['comision_default']
    ganancia_objetivo = config['ganancia_neta_default']
    
    print(f"\nUsando {comision}% de comision y un objetivo de {ganancia_objetivo}% de ganancia...")
    print(f"Costo promedio actual: ${cripto['precio_promedio']:.4f}")
    
    # Calcular precio sugerido
    precio_sugerido = calc.calcular_precio_sugerido(
        cripto['precio_promedio'],
        ganancia_objetivo
    )
    
    print(f"Precio sugerido: ${precio_sugerido:.4f}")
    
    # Pedir precio al usuario
    try:
        precio_publicado = float(input("\n¿Que precio vas a publicar en tu anuncio?: "))
        
        if precio_publicado <= 0:
            print("❌ Precio inválido")
            return False
        
        # Calcular ganancia estimada
        ganancia_estimada = calc.calcular_ganancia_neta_estimada(
            cripto['precio_promedio'],
            precio_publicado
        )
        
        if ganancia_estimada < 0:
            print(f"\n⚠️  ADVERTENCIA: Precio muy bajo. Tendrás pérdidas de {abs(ganancia_estimada):.2f}%")
            confirmar = input("¿Continuar de todos modos? (s/n): ").lower()
            if confirmar != 's':
                return False
        else:
            print(f"Buen precio. Tu ganancia neta estimada sera de un {ganancia_estimada:.2f}%.")
        
        # Registrar precio
        ganancia_neta_estimada = definir_precio_venta(dia_id, cripto['id'], precio_publicado)
        
        print("\n" + "-"*60)
        print("RESUMEN DEL DIA")
        print("-"*60)
        print(f"Cripto seleccionada: {cripto['simbolo']}")
        print(f"Precio de venta publicado para hoy: ${precio_publicado:.4f}")
        
        return True
        
    except ValueError:
        print("❌ Precio inválido")
        return False


def ejecutar_ventas_dia(dia_id, ciclo_id, cripto):
    """Ejecuta el proceso de ventas del día"""
    
    print("\n" + "-"*60)
    print("CONTABILIDAD DE CIERRE DEL DIA")
    print("-"*60)
    
    # Obtener límites
    cursor.execute("SELECT limite_ventas_min, limite_ventas_max FROM config WHERE id = 1")
    config = cursor.fetchone()
    
    minimo = config['limite_ventas_min']
    maximo = config['limite_ventas_max']
    
    print(f"\nLimite de ventas por dia: {minimo} minimo, {maximo} maximo")
    print("IMPORTANTE: Para evitar bloqueos bancarios, respeta el limite de ventas.")
    
    # Obtener día y precio
    cursor.execute("SELECT precio_publicado FROM dias WHERE id = ?", (dia_id,))
    dia_info = cursor.fetchone()
    precio_venta = dia_info['precio_publicado']
    
    ventas_realizadas = 0
    cantidad_disponible = cripto['cantidad']
    
    while ventas_realizadas < maximo and cantidad_disponible > 0:
        print(f"\nCapital actual de {cripto['nombre']}: {cantidad_disponible:.8f}")
        print(f"Ventas realizadas hoy: {ventas_realizadas}/{maximo}")
        
        if ventas_realizadas >= minimo:
            print(f"Ya alcanzaste el minimo de {minimo} ventas.")
            continuar = input("¿Deseas registrar otra venta? (s/n): ").lower()
            if continuar != 's':
                break
        
        # Preguntar si desea registrar venta
        vender = input(f"\n¿Deseas registrar la venta #{ventas_realizadas + 1}? (s/n): ").lower()
        
        if vender == 's':
            print(f"  Ingresa la cantidad de {cripto['simbolo']} vendido (o 'todo'): ", end='')
            cantidad_input = input().strip().lower()
            
            if cantidad_input == 'todo':
                cantidad = cantidad_disponible
                print(f"  Vendiendo todo el capital restante: {cantidad:.8f}")
            else:
                try:
                    cantidad = float(cantidad_input)
                    
                    if cantidad <= 0:
                        print("  ❌ Cantidad inválida")
                        continue
                    
                    if cantidad > cantidad_disponible:
                        print(f"  ❌ No tienes suficiente. Disponible: {cantidad_disponible:.8f}")
                        continue
                
                except ValueError:
                    print("  ❌ Cantidad inválida")
                    continue
            
            # Registrar venta
            resultado = registrar_venta(dia_id, cripto['id'], cantidad)
            
            if resultado:
                print("  ✅ Venta registrada con exito!")
                ventas_realizadas += 1
                cantidad_disponible -= cantidad
                
                if cantidad_disponible <= 0:
                    print("\nNo queda capital de esta cripto para vender.")
                    break
            else:
                print("  ❌ Error al registrar venta")
        else:
            if ventas_realizadas < minimo:
                print(f"\n⚠️  Aún no alcanzas el mínimo de {minimo} ventas")
                continuar = input("¿Seguro que quieres detenerte? (s/n): ").lower()
                if continuar == 's':
                    break
            else:
                break
    
    # Verificar límite máximo
    if ventas_realizadas >= maximo:
        print(f"\nLIMITE ALCANZADO: Has realizado {maximo} ventas hoy.")
        print("Para evitar bloqueos bancarios, no puedes hacer mas ventas hoy.")
    
    # Advertencia si no alcanzó el mínimo
    if ventas_realizadas < minimo:
        print(f"\n⚠️  ADVERTENCIA: Solo realizaste {ventas_realizadas} ventas.")
        print(f"El minimo recomendado es {minimo} ventas por dia.")
    
    print("\nFase de contabilidad del dia finalizada.")


def ejecutar_cierre_dia(dia_id, ciclo_id):
    """Ejecuta el cierre del día"""
    
    # Cerrar día
    resumen = cerrar_dia(dia_id)
    
    if not resumen:
        print("\n❌ Error al cerrar el día")
        input("\nPresiona Enter para continuar...")
        return
    
def ejecutar_cierre_dia(dia_id, ciclo_id):
    """Ejecuta el cierre del día"""
    
    # Cerrar día
    resumen = cerrar_dia(dia_id)
    
    if not resumen:
        print("\n❌ Error al cerrar el día")
        input("\nPresiona Enter para continuar...")
        return
    
    # Preguntar si desea ver progreso del ciclo
    print("\n¿Deseas ver el progreso del ciclo global? (s/n): ", end='')
    ver_progreso = input().strip().lower()
    
    if ver_progreso == 's':
        from dias import mostrar_progreso_ciclo
        mostrar_progreso_ciclo(ciclo_id)
    
    # Preguntar si desea aplicar interés compuesto
    print("\n💡 INTERÉS COMPUESTO:")
    print(f"   Tienes ${resumen['efectivo_recibido']:.2f} en el pool de reinversión")
    print("\n¿Deseas reinvertir este efectivo en cripto? (s/n): ", end='')
    aplicar_interes = input().strip().lower()
    
    if aplicar_interes == 's':
        resultado = aplicar_interes_compuesto(ciclo_id)
        if resultado:
            print("\n✅ Interés compuesto aplicado exitosamente")
            print("   El capital aumentó para el próximo día de operación")
        else:
            print("\n⚠️  No se aplicó el interés compuesto")
    
    input("\nPresiona Enter para continuar...")


def validar_cierre_antes_salir(dia_id, ciclo_id):
    """
    Valida que el día esté cerrado antes de salir del operador
    NUEVA FUNCIÓN - Previene dejar días abiertos
    """
    
    # Verificar si hay día abierto
    cursor.execute("""
        SELECT * FROM dias WHERE id = ? AND estado = 'abierto'
    """, (dia_id,))
    
    dia_abierto = cursor.fetchone()
    
    if dia_abierto:
        print("\n" + "="*60)
        print("⚠️  ADVERTENCIA: DÍA SIN CERRAR")
        print("="*60)
        print(f"\nEl día #{dia_abierto['numero_dia']} está ABIERTO")
        print("Si sales ahora, NO podrás continuar operando.")
        print("\n¿Qué deseas hacer?")
        print("  [1] Cerrar el día ahora (RECOMENDADO)")
        print("  [2] Salir sin cerrar (NO RECOMENDADO)")
        
        opcion = input("\nSelecciona (1-2): ").strip()
        
        if opcion == "1":
            print("\nCerrando día...")
            ejecutar_cierre_dia(dia_id, ciclo_id)
            return True
        else:
            print("\n⚠️  Saliendo sin cerrar el día...")
            print("   IMPORTANTE: Deberás cerrar el día manualmente con SQL")
            input("\nPresiona Enter para continuar...")
            return False
    
    return True


# ===================================================================
# FUNCIONES AUXILIARES
# ===================================================================

def mostrar_resumen_operaciones():
    """Muestra un resumen de las operaciones del sistema"""
    
    print("\n" + "="*60)
    print("RESUMEN DE OPERACIONES")
    print("="*60)
    
    # Ciclos
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) as activos,
            SUM(CASE WHEN estado = 'cerrado' THEN 1 ELSE 0 END) as cerrados
        FROM ciclos
    """)
    
    ciclos = cursor.fetchone()
    print(f"\n📊 Ciclos:")
    print(f"   Total: {ciclos['total']}")
    print(f"   Activos: {ciclos['activos']}")
    print(f"   Cerrados: {ciclos['cerrados']}")
    
    # Días operados
    cursor.execute("""
        SELECT COUNT(*) as total_dias
        FROM dias WHERE estado = 'cerrado'
    """)
    
    dias = cursor.fetchone()
    print(f"\n📅 Días operados: {dias['total_dias']}")
    
    # Ventas realizadas
    cursor.execute("SELECT COUNT(*) as total_ventas FROM ventas")
    ventas = cursor.fetchone()
    print(f"\n💰 Ventas realizadas: {ventas['total_ventas']}")
    
    # Ganancia total histórica
    cursor.execute("""
        SELECT COALESCE(SUM(ganancia_total), 0) as ganancia
        FROM ciclos WHERE estado = 'cerrado'
    """)
    
    ganancia = cursor.fetchone()
    print(f"\n📈 Ganancia total histórica: ${ganancia['ganancia']:.2f}")
    
    print("="*60)


def verificar_estado_sistema():
    """Verifica el estado general del sistema"""
    
    print("\n" + "="*60)
    print("VERIFICACIÓN DEL SISTEMA")
    print("="*60)
    
    problemas = []
    
    # 1. Verificar ciclo activo
    ciclo = obtener_ciclo_activo()
    if ciclo:
        print("\n✅ Ciclo activo detectado")
        
        # Verificar si hay días abiertos
        cursor.execute("""
            SELECT COUNT(*) as dias_abiertos
            FROM dias WHERE ciclo_id = ? AND estado = 'abierto'
        """, (ciclo['id'],))
        
        dias_abiertos = cursor.fetchone()['dias_abiertos']
        
        if dias_abiertos > 0:
            print(f"⚠️  Hay {dias_abiertos} día(s) abierto(s)")
            problemas.append("Días abiertos sin cerrar")
        else:
            print("✅ No hay días abiertos")
    else:
        print("\n⚠️  No hay ciclo activo")
        problemas.append("Sin ciclo activo")
    
    # 2. Verificar capital en bóveda
    cursor.execute("""
        SELECT COUNT(*) as criptos_con_saldo
        FROM boveda_ciclo WHERE cantidad > 0
    """)
    
    criptos = cursor.fetchone()['criptos_con_saldo']
    
    if criptos > 0:
        print(f"✅ Capital disponible: {criptos} cripto(s)")
    else:
        print("⚠️  No hay capital en la bóveda")
        problemas.append("Sin capital para operar")
    
    # 3. Verificar logs
    from pathlib import Path
    logs_dir = Path("logs")
    
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"✅ Sistema de logs activo: {len(log_files)} archivo(s)")
    else:
        print("⚠️  Directorio de logs no encontrado")
        problemas.append("Sistema de logs no configurado")
    
    # 4. Verificar backups
    backups_dir = Path("backups")
    
    if backups_dir.exists():
        backups = list(backups_dir.glob("*.db"))
        if backups:
            print(f"✅ Backups disponibles: {len(backups)}")
        else:
            print("⚠️  No hay backups disponibles")
            problemas.append("Sin backups de seguridad")
    else:
        print("⚠️  Directorio de backups no encontrado")
        problemas.append("Sin sistema de backups")
    
    # Resumen
    print("\n" + "="*60)
    if problemas:
        print(f"⚠️  {len(problemas)} problema(s) detectado(s):")
        for problema in problemas:
            print(f"   • {problema}")
    else:
        print("✅ Sistema en perfecto estado")
    print("="*60)
    
    return len(problemas) == 0


# ===================================================================
# MENÚ AVANZADO DEL OPERADOR
# ===================================================================

def menu_operador_avanzado():
    """Menú con opciones avanzadas para el operador"""
    
    while True:
        print("\n" + "="*60)
        print("OPERADOR - MENÚ AVANZADO")
        print("="*60)
        
        print("\n[1] Iniciar/Continuar Día de Operación")
        print("[2] Ver Resumen de Operaciones")
        print("[3] Verificar Estado del Sistema")
        print("[4] Consultar Capital Disponible")
        print("[5] Ver Último Día Operado")
        print("[6] Volver al Menú Principal")
        print("="*60)
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            modulo_operador()
        
        elif opcion == "2":
            mostrar_resumen_operaciones()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "3":
            verificar_estado_sistema()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "4":
            ciclo = obtener_ciclo_activo()
            if ciclo:
                criptos = obtener_criptos_disponibles(ciclo['id'])
                
                print("\n" + "="*60)
                print("CAPITAL DISPONIBLE")
                print("="*60)
                
                if criptos:
                    total = 0
                    for cripto in criptos:
                        print(f"\n{cripto['nombre']} ({cripto['simbolo']}):")
                        print(f"  Cantidad: {cripto['cantidad']:.8f}")
                        print(f"  Precio promedio: ${cripto['precio_promedio']:.4f}")
                        print(f"  Valor total: ${cripto['valor_usd']:.2f}")
                        total += cripto['valor_usd']
                    
                    print(f"\n{'='*60}")
                    print(f"TOTAL: ${total:.2f} USD")
                else:
                    print("\n⚠️  No hay capital disponible")
            else:
                print("\n⚠️  No hay ciclo activo")
            
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "5":
            ciclo = obtener_ciclo_activo()
            if ciclo:
                cursor.execute("""
                    SELECT * FROM dias
                    WHERE ciclo_id = ? AND estado = 'cerrado'
                    ORDER BY numero_dia DESC
                    LIMIT 1
                """, (ciclo['id'],))
                
                ultimo_dia = cursor.fetchone()
                
                if ultimo_dia:
                    print("\n" + "="*60)
                    print("ÚLTIMO DÍA OPERADO")
                    print("="*60)
                    print(f"\nDía #{ultimo_dia['numero_dia']}")
                    print(f"Fecha: {ultimo_dia['fecha']}")
                    print(f"Capital inicial: ${ultimo_dia['capital_inicial']:.2f}")
                    print(f"Capital final: ${ultimo_dia['capital_final']:.2f}")
                    print(f"Ganancia neta: ${ultimo_dia['ganancia_neta']:.2f}")
                    
                    # Contar ventas
                    cursor.execute("""
                        SELECT COUNT(*) as ventas
                        FROM ventas WHERE dia_id = ?
                    """, (ultimo_dia['id'],))
                    
                    ventas = cursor.fetchone()['ventas']
                    print(f"Ventas realizadas: {ventas}")
                else:
                    print("\n⚠️  No hay días operados en este ciclo")
            else:
                print("\n⚠️  No hay ciclo activo")
            
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "6":
            break
        
        else:
            print("\n❌ Opción inválida")
            input("\nPresiona Enter para continuar...")


# ===================================================================
# FUNCIÓN PARA TESTING
# ===================================================================

def test_operador():
    """Función de testing del módulo operador"""
    
    print("\n" + "="*60)
    print("TEST DEL MÓDULO OPERADOR")
    print("="*60)
    
    # Test 1: Verificar ciclo activo
    print("\n[Test 1] Verificando ciclo activo...")
    ciclo = obtener_ciclo_activo()
    
    if ciclo:
        print(f"✅ Ciclo #{ciclo['id']} activo")
    else:
        print("⚠️  No hay ciclo activo")
    
    # Test 2: Verificar capital
    print("\n[Test 2] Verificando capital disponible...")
    if ciclo:
        criptos = obtener_criptos_disponibles(ciclo['id'])
        print(f"✅ {len(criptos)} cripto(s) disponible(s)")
    else:
        print("⚠️  No se puede verificar sin ciclo activo")
    
    # Test 3: Verificar configuración
    print("\n[Test 3] Verificando configuración...")
    cursor.execute("SELECT * FROM config WHERE id = 1")
    config = cursor.fetchone()
    
    if config:
        print(f"✅ Comisión: {config['comision_default']}%")
        print(f"✅ Ganancia objetivo: {config['ganancia_neta_default']}%")
    else:
        print("❌ No hay configuración")
    
    print("\n" + "="*60)
    print("FIN DEL TEST")
    print("="*60)


# ===================================================================
# EJECUCIÓN DIRECTA
# ===================================================================

if __name__ == "__main__":
    print("Módulo Operador - Versión 2.0")
    print("\n1. Ejecutar operador")
    print("2. Menú avanzado")
    print("3. Test")
    
    opcion = input("\nSelecciona: ").strip()
    
    if opcion == "1":
        modulo_operador()
    elif opcion == "2":
        menu_operador_avanzado()
    elif opcion == "3":
        test_operador()
    else:
        print("Opción inválida")
