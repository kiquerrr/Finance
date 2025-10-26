# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

# =================================================
# FUNCIONES AUXILIARES DEL MÓDULO
# =================================================

def obtener_config_db(clave):
    """Función auxiliar para leer la configuración desde la BD."""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
    resultado = cursor.fetchone()
    conn.close()
    if clave == 'comision_defecto':
        return float(resultado[0]) if resultado else 0.35
    if clave == 'ganancia_defecto':
        return float(resultado[0]) if resultado else 2.0

def consultar_capital_actual(ciclo_id):
    """Calcula el capital por cripto para el ciclo activo."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # Capital por cada cripto
        cursor.execute("""
            SELECT cripto,
                   SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) as cantidad,
                   SUM(CASE WHEN tipo = 'compra' THEN monto_fiat ELSE -monto_fiat END) as valor_fiat
            FROM transacciones 
            WHERE ciclo_id = ?
            GROUP BY cripto
            HAVING cantidad > 0.0001
        """, (ciclo_id,))
        
        criptos = cursor.fetchall()
        conn.close()
        
        # Retornar diccionario con info por cripto
        capital_info = {}
        total_fiat = 0
        
        for cripto_data in criptos:
            cripto = cripto_data[0]
            cantidad = cripto_data[1]
            valor = cripto_data[2]
            total_fiat += valor
            
            capital_info[cripto] = {
                'cantidad': cantidad,
                'valor': valor,
                'costo_promedio': valor / cantidad if cantidad > 0 else 0
            }
        
        capital_info['total_fiat'] = total_fiat
        return capital_info
        
    except sqlite3.Error as e:
        print(f"Error al consultar capital: {e}")
        return {'total_fiat': 0}

def mostrar_capital_detallado(capital_info):
    """Muestra el capital de forma detallada por cripto."""
    import criptomonedas
    
    if not capital_info or capital_info.get('total_fiat', 0) == 0:
        print("Capital inicial del dia: Sin capital")
        return
    
    print("Capital inicial del dia:")
    
    for cripto, info in capital_info.items():
        if cripto == 'total_fiat':
            continue
        
        info_cripto = criptomonedas.obtener_info_cripto(cripto)
        nombre = info_cripto['nombre'] if info_cripto else cripto
        cantidad_fmt = criptomonedas.formatear_cantidad_cripto(info['cantidad'], cripto)
        
        print(f"  - {cantidad_fmt} {nombre} ({cripto}) = ${info['valor']:.2f}")
    
    print(f"  Total: ${capital_info['total_fiat']:.2f} USD")

def consultar_capital_otros_ciclos():
    """Verifica si hay capital en ciclos anteriores."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # Obtener ciclo activo
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        ciclo_activo = cursor.fetchone()
        ciclo_activo_id = ciclo_activo[0] if ciclo_activo else None
        
        if not ciclo_activo_id:
            conn.close()
            return 0.0, 0.0
        
        # Capital en otros ciclos
        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) 
            FROM transacciones WHERE ciclo_id != ?
        """, (ciclo_activo_id,))
        cripto_otros = cursor.fetchone()[0] or 0.0
        
        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto * precio_unitario 
                           ELSE -(cantidad_cripto * precio_unitario) END) 
            FROM transacciones WHERE ciclo_id != ?
        """, (ciclo_activo_id,))
        valor_otros = cursor.fetchone()[0] or 0.0
        
        conn.close()
        return cripto_otros, valor_otros
    except sqlite3.Error as e:
        print(f"Error al consultar otros ciclos: {e}")
        return 0.0, 0.0

def obtener_info_ciclo(ciclo_id):
    """Obtiene información completa de un ciclo."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fecha_inicio, estado 
            FROM ciclos WHERE id = ?
        """, (ciclo_id,))
        info = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*) FROM transacciones WHERE ciclo_id = ?
        """, (ciclo_id,))
        num_trans = cursor.fetchone()[0]
        
        conn.close()
        
        if info:
            return {
                'fecha_inicio': info[0],
                'estado': info[1],
                'num_transacciones': num_trans
            }
        return None
    except sqlite3.Error as e:
        print(f"Error al obtener info del ciclo: {e}")
        return None

def analizar_mercado(costo_promedio):
    """Analiza el mercado, define el precio y aplica validaciones avanzadas."""
    print("-" * 60)
    print("ANÁLISIS DE MERCADO Y DEFINICIÓN DE PRECIO")
    print("-" * 60)
    
    porcentaje_comision = obtener_config_db('comision_defecto')
    porcentaje_ganancia_objetivo = obtener_config_db('ganancia_defecto')
    
    factor_ganancia = 1 + (porcentaje_ganancia_objetivo / 100)
    factor_comision = 1 - (porcentaje_comision / 100)
    
    precio_sugerido = (costo_promedio * factor_ganancia) / factor_comision
    
    print(f"\nUsando {porcentaje_comision}% de comisión y un objetivo de {porcentaje_ganancia_objetivo}% de ganancia...")
    print(f"Costo promedio actual: ${costo_promedio:.4f}")
    print(f"Precio sugerido: ${precio_sugerido:.4f}")
    
    while True:
        try:
            precio_elegido = float(input("\n¿Qué precio vas a publicar en tu anuncio?: "))
            if precio_elegido <= 0:
                print("❌ Error: El precio debe ser un número positivo.")
                continue

            ganancia_neta_real_pct = (((precio_elegido * factor_comision) / costo_promedio) - 1) * 100

            if ganancia_neta_real_pct < 0:
                print(f"\n⚠️  ¡ADVERTENCIA GRAVE! Con el precio ${precio_elegido:.4f} tu ganancia neta será NEGATIVA: {ganancia_neta_real_pct:.2f}%.")
                confirmacion = input("¿Estás seguro de que quieres operar con pérdidas? (s/n): ")
                if confirmacion.lower() in ['s', 'si', 'sí']:
                    print("⚠️  Operación con pérdidas confirmada.")
                    break
            elif ganancia_neta_real_pct < porcentaje_ganancia_objetivo:
                print(f"\n⚠️  ¡ADVERTENCIA! Con el precio ${precio_elegido:.4f} tu ganancia neta será de solo un {ganancia_neta_real_pct:.2f}%.")
                print(f"   No alcanzarás tu meta del {porcentaje_ganancia_objetivo}%.")
                
                if 0 < ganancia_neta_real_pct < 0.5:
                    print("   Este margen es muy bajo y podría resultar en pérdidas por comisiones en transacciones pequeñas.")
                
                confirmacion = input("¿Aún así deseas usar este precio? (s/n): ")
                if confirmacion.lower() in ['s', 'si', 'sí']:
                    break
            else:
                print(f"✅ Buen precio. Tu ganancia neta estimada será de un {ganancia_neta_real_pct:.2f}%.")
                break

        except ValueError:
            print("❌ Error: Ingrese un valor numérico válido.")
            
    return precio_elegido, porcentaje_comision

def registrar_ventas_del_dia(ciclo_id, precio_venta, comision):
    """Registra hasta 3 ventas en la BD, incluyendo todas las validaciones."""
    print("\n" + "-" * 60)
    print("CONTABILIDAD DE CIERRE DEL DÍA")
    print("-" * 60)
    ventas_realizadas = 0
    
    while ventas_realizadas < 3:
        cripto_disponible, costo_promedio_actual = consultar_capital_actual(ciclo_id)
        
        if cripto_disponible < 0.0001:
            print("\n⚠️  No queda capital en la bóveda para vender.")
            break

        print(f"\n💰 Capital actual en bóveda: {cripto_disponible:.4f} cripto.")
        respuesta = input(f"¿Deseas registrar la venta #{ventas_realizadas + 1}? (s/n): ")
        
        if respuesta.lower() in ['s', 'si', 'sí']:
            while True:
                respuesta_cantidad = input(f"  Ingresa la cantidad de cripto vendido (o 'todo'): ")
                if respuesta_cantidad.lower() == 'todo':
                    cantidad_vendida = cripto_disponible
                    print(f"  📤 Vendiendo todo el capital restante: {cantidad_vendida:.4f}")
                    break
                try:
                    cantidad_vendida = float(respuesta_cantidad)
                    if cantidad_vendida <= 0:
                        print("  ❌ Error: La cantidad debe ser mayor a cero.")
                    elif cantidad_vendida > cripto_disponible:
                        print(f"  ❌ Error: No puedes vender más de {cripto_disponible:.4f} cripto.")
                    else:
                        break
                except ValueError:
                    print("  ❌ Error: Ingrese un número o la palabra 'todo'.")
            
            try:
                conn = sqlite3.connect('arbitraje.db')
                cursor = conn.cursor()
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute("""
                    INSERT INTO transacciones (ciclo_id, fecha, tipo, cantidad_cripto, precio_unitario, precio_venta_real, comision_pct)
                    VALUES (?, ?, 'venta', ?, ?, ?, ?)
                """, (ciclo_id, fecha_actual, cantidad_vendida, costo_promedio_actual, precio_venta, comision))
                
                conn.commit()
                conn.close()
                print("  ✅ ¡Venta registrada con éxito!")
                ventas_realizadas += 1
            except sqlite3.Error as e:
                print(f"  ❌ Error al registrar la venta: {e}")
                
        elif respuesta.lower() in ['n', 'no']:
            break
        else:
            print("  ❌ Error: Respuesta no válida. Inténtalo de nuevo.")
            
    print("\n✅ Fase de contabilidad del día finalizada.")

def gestionar_cierre_ciclo(ciclo_id):
    """Gestión INTELIGENTE del cierre de ciclo con validaciones según el estado."""
    print("\n" + "=" * 60)
    print("GESTIÓN DE CIERRE DE CICLO")
    print("=" * 60)
    
    try:
        # Calcular ganancia y capital actual
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(
                (cantidad_cripto * precio_venta_real * (1 - comision_pct / 100)) - 
                (cantidad_cripto * precio_unitario)
            )
            FROM transacciones WHERE ciclo_id = ? AND tipo = 'venta'
        """, (ciclo_id,))
        ganancia_neta = cursor.fetchone()[0] or 0.0

        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) 
            FROM transacciones WHERE ciclo_id = ?
        """, (ciclo_id,))
        cripto_restante = cursor.fetchone()[0] or 0.0

        cursor.execute("""
            SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto * precio_unitario 
                           ELSE -(cantidad_cripto * precio_unitario) END) 
            FROM transacciones WHERE ciclo_id = ?
        """, (ciclo_id,))
        capital_restante_usd = cursor.fetchone()[0] or 0.0

        # Contar transacciones
        cursor.execute("SELECT COUNT(*) FROM transacciones WHERE ciclo_id = ?", (ciclo_id,))
        num_transacciones = cursor.fetchone()[0]

        conn.close()

        # VALIDACIÓN: Ciclo vacío (sin transacciones)
        if num_transacciones == 0:
            print(f"\n⚠️  CICLO VACÍO DETECTADO")
            print(f"   El ciclo #{ciclo_id} no tiene ninguna transacción registrada.")
            print(f"   No hay ganancias ni capital para gestionar.")
            
            print("\n" + "-" * 60)
            print("OPCIONES DISPONIBLES:")
            print("-" * 60)
            print("[1] CERRAR este ciclo vacío y crear uno nuevo")
            print("[2] MANTENER este ciclo activo para fondear y operar")
            print("[3] CANCELAR y volver al menú")
            print("-" * 60)
            
            opcion = input("Selecciona una opción (1-3): ")
            
            if opcion == '1':
                conn = sqlite3.connect('arbitraje.db')
                cursor = conn.cursor()
                fecha_fin = datetime.now().strftime("%Y-%m-%d")
                cursor.execute("""
                    UPDATE ciclos SET estado = 'completado', fecha_fin = ?, ganancia_neta_total = 0
                    WHERE id = ?
                """, (fecha_fin, ciclo_id))
                conn.commit()
                conn.close()
                
                print(f"\n✅ Ciclo vacío #{ciclo_id} cerrado.")
                return True
            elif opcion == '2':
                print(f"\n🔄 Ciclo #{ciclo_id} permanece activo.")
                print("💡 Usa 'Gestión de Bóveda' para fondear o transferir capital.")
                return False
            else:
                print("\n❌ Operación cancelada.")
                return False

        # Mostrar resumen del ciclo
        print(f"\n📊 RESUMEN DEL CICLO #{ciclo_id}:")
        print(f"   📝 Transacciones: {num_transacciones}")
        print(f"   💵 Ganancia Neta Generada: ${ganancia_neta:.2f}")
        print(f"   💰 Capital Cripto Restante: {cripto_restante:.4f}")
        print(f"   💵 Valor del Capital Restante: ${capital_restante_usd:.2f}")
        
        # DETERMINAR QUÉ OPCIONES MOSTRAR SEGÚN EL ESTADO
        hay_ganancia = ganancia_neta > 0.01
        hay_capital = capital_restante_usd > 0.01
        
        print("\n" + "-" * 60)
        print("¿QUÉ DESEAS HACER CON ESTE CICLO?")
        print("-" * 60)
        
        opciones_disponibles = []
        
        # ESCENARIO 1: Hay ganancia Y hay capital
        if hay_ganancia and hay_capital:
            print("[1] Cerrar y RETIRAR TODO (ganancia + capital)")
            opciones_disponibles.append(('1', 'retirar_todo'))
            print("[2] Cerrar y RETIRAR SOLO LA GANANCIA (dejar capital)")
            opciones_disponibles.append(('2', 'retirar_ganancia'))
            print("[3] Cerrar y DEJAR TODO para el próximo ciclo")
            opciones_disponibles.append(('3', 'dejar_todo'))
            print("[4] NO CERRAR - Continuar operando")
            opciones_disponibles.append(('4', 'no_cerrar'))
        
        # ESCENARIO 2: Solo hay ganancia (capital vendido completamente)
        elif hay_ganancia and not hay_capital:
            print("[1] Cerrar y RETIRAR LA GANANCIA")
            opciones_disponibles.append(('1', 'retirar_ganancia_solo'))
            print("[2] Cerrar y DEJAR LA GANANCIA para el próximo ciclo")
            opciones_disponibles.append(('2', 'dejar_ganancia'))
            print("[3] NO CERRAR - Continuar operando")
            opciones_disponibles.append(('3', 'no_cerrar'))
        
        # ESCENARIO 3: Solo hay capital (no hubo ganancias o pérdidas)
        elif not hay_ganancia and hay_capital:
            print("[1] Cerrar y RETIRAR EL CAPITAL")
            opciones_disponibles.append(('1', 'retirar_capital_solo'))
            print("[2] Cerrar y DEJAR EL CAPITAL para el próximo ciclo")
            opciones_disponibles.append(('2', 'dejar_capital'))
            print("[3] NO CERRAR - Continuar operando")
            opciones_disponibles.append(('3', 'no_cerrar'))
        
        # ESCENARIO 4: No hay nada (todo vendido, sin ganancias significativas)
        else:
            print("[1] CERRAR este ciclo (no hay capital ni ganancias)")
            opciones_disponibles.append(('1', 'cerrar_vacio'))
            print("[2] NO CERRAR - Continuar operando")
            opciones_disponibles.append(('2', 'no_cerrar'))
        
        print("-" * 60)
        
        opcion = input(f"Selecciona una opción (1-{len(opciones_disponibles)}): ")
        
        # Buscar la acción correspondiente
        accion = None
        for num, acc in opciones_disponibles:
            if opcion == num:
                accion = acc
                break
        
        if accion is None:
            print("\n❌ Opción no válida. El ciclo permanece activo.")
            return False
        
        # EJECUTAR LA ACCIÓN SELECCIONADA
        return ejecutar_accion_cierre(ciclo_id, accion, ganancia_neta, capital_restante_usd, cripto_restante)
            
    except sqlite3.Error as e:
        print(f"❌ Error al gestionar el cierre: {e}")
        return False

def ejecutar_accion_cierre(ciclo_id, accion, ganancia, capital_usd, cripto):
    """Ejecuta la acción de cierre seleccionada."""
    
    if accion == 'retirar_todo':
        print(f"\n💸 Has decidido RETIRAR TODO del ciclo #{ciclo_id}")
        print(f"   Ganancia: ${ganancia:.2f}")
        print(f"   Capital: ${capital_usd:.2f}")
        print(f"   Total a retirar: ${ganancia + capital_usd:.2f}")
        
        confirmacion = input("\n¿Confirmar cierre y retiro total? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, ganancia)
            print(f"\n✅ ¡Ciclo #{ciclo_id} cerrado exitosamente!")
            print(f"💸 Total retirado: ${ganancia + capital_usd:.2f}")
            print("\n⚠️  IMPORTANTE: Deberás fondear nuevamente para el próximo ciclo.")
            return True
    
    elif accion == 'retirar_ganancia':
        print(f"\n💸 Has decidido RETIRAR SOLO LA GANANCIA")
        print(f"   Ganancia a retirar: ${ganancia:.2f}")
        print(f"   Capital que quedará: ${capital_usd:.2f} ({cripto:.4f} cripto)")
        
        confirmacion = input("\n¿Confirmar cierre y retiro de ganancia? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, ganancia)
            print(f"\n✅ ¡Ciclo #{ciclo_id} cerrado exitosamente!")
            print(f"💵 Ganancia retirada: ${ganancia:.2f}")
            print(f"💰 Capital disponible para próximo ciclo: ${capital_usd:.2f}")
            print("\n💡 TIP: Usa 'Transferir Capital' en Gestión de Bóveda.")
            return True
    
    elif accion == 'dejar_todo':
        total = ganancia + capital_usd
        print(f"\n💰 Has decidido DEJAR TODO para el próximo ciclo")
        print(f"   Total disponible: ${total:.2f}")
        
        confirmacion = input("\n¿Confirmar cierre? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, ganancia)
            print(f"\n✅ ¡Ciclo #{ciclo_id} cerrado exitosamente!")
            print(f"💰 Capital total para próximo ciclo: ${total:.2f}")
            print("\n💡 TIP: Usa 'Transferir Capital' en Gestión de Bóveda.")
            return True
    
    elif accion == 'retirar_ganancia_solo':
        print(f"\n💸 Retirando ganancia de ${ganancia:.2f}")
        confirmacion = input("¿Confirmar? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, ganancia)
            print(f"\n✅ Ciclo cerrado. Ganancia retirada: ${ganancia:.2f}")
            return True
    
    elif accion == 'dejar_ganancia':
        print(f"\n💰 Dejando ganancia de ${ganancia:.2f} para el próximo ciclo")
        confirmacion = input("¿Confirmar? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, ganancia)
            print(f"\n✅ Ciclo cerrado. Ganancia disponible: ${ganancia:.2f}")
            return True
    
    elif accion == 'retirar_capital_solo':
        print(f"\n💸 Retirando capital de ${capital_usd:.2f}")
        confirmacion = input("¿Confirmar? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, 0)
            print(f"\n✅ Ciclo cerrado. Capital retirado: ${capital_usd:.2f}")
            return True
    
    elif accion == 'dejar_capital':
        print(f"\n💰 Dejando capital de ${capital_usd:.2f} para el próximo ciclo")
        confirmacion = input("¿Confirmar? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, 0)
            print(f"\n✅ Ciclo cerrado. Capital disponible: ${capital_usd:.2f}")
            print("\n💡 TIP: Usa 'Transferir Capital' en Gestión de Bóveda.")
            return True
    
    elif accion == 'cerrar_vacio':
        confirmacion = input(f"\n¿Cerrar ciclo #{ciclo_id} vacío? (s/n): ")
        if confirmacion.lower() in ['s', 'si', 'sí']:
            cerrar_ciclo_bd(ciclo_id, 0)
            print(f"\n✅ Ciclo #{ciclo_id} cerrado.")
            return True
    
    elif accion == 'no_cerrar':
        print(f"\n🔄 Ciclo #{ciclo_id} permanece activo.")
        return False
    
    return False

def cerrar_ciclo_bd(ciclo_id, ganancia):
    """Cierra el ciclo en la base de datos."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        fecha_fin = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE ciclos SET estado = 'completado', fecha_fin = ?, ganancia_neta_total = ?
            WHERE id = ?
        """, (fecha_fin, ganancia, ciclo_id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"❌ Error al cerrar ciclo: {e}")

# =================================================
# FUNCIÓN PRINCIPAL DEL MÓDULO
# =================================================

def verificar_o_crear_ciclo():
    """Verifica si hay un ciclo activo y gestiona la decisión del usuario."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        ciclo_activo = cursor.fetchone()
        conn.close()
        
        if ciclo_activo:
            ciclo_id = ciclo_activo[0]
            info = obtener_info_ciclo(ciclo_id)
            cripto_actual, costo_promedio = consultar_capital_actual(ciclo_id)
            cripto_otros, valor_otros = consultar_capital_otros_ciclos()
            
            print(f"\n🔄 CICLO ACTIVO DETECTADO: #{ciclo_id}")
            print(f"   📅 Fecha de inicio: {info['fecha_inicio']}")
            print(f"   📊 Transacciones: {info['num_transacciones']}")
            print(f"   💰 Capital actual: {cripto_actual:.4f} cripto", end="")
            if costo_promedio > 0:
                print(f" (${costo_promedio:.4f} promedio)")
            else:
                print()
            
            # Alertar si hay capital en otros ciclos
            if cripto_otros > 0.01:
                print(f"\n💡 AVISO: Tienes ${valor_otros:.2f} en ciclos anteriores.")
                print(f"   Puedes transferirlo usando 'Gestión de Bóveda → Transferir Capital'")
            
            print("\n" + "-" * 60)
            print("¿QUÉ DESEAS HACER?")
            print("-" * 60)
            print(f"[1] CONTINUAR operando en el ciclo #{ciclo_id}")
            print(f"[2] CERRAR el ciclo #{ciclo_id} e iniciar uno nuevo")
            print("[3] CANCELAR y volver al menú")
            print("-" * 60)
            
            opcion = input("Selecciona una opción (1-3): ")
            
            if opcion == '1':
                return ciclo_id
            elif opcion == '2':
                if gestionar_cierre_ciclo(ciclo_id):
                    print("\n🆕 Creando nuevo ciclo...")
                    return crear_nuevo_ciclo()
                else:
                    return ciclo_id
            else:
                print("\n❌ Operación cancelada.")
                return None
        else:
            print("\n⚠️  No se encontró ningún ciclo de trabajo activo.")
            
            # Verificar si hay capital en ciclos anteriores
            cripto_otros, valor_otros = consultar_capital_otros_ciclos()
            if cripto_otros > 0.01:
                print(f"\n💡 AVISO: Tienes ${valor_otros:.2f} ({cripto_otros:.4f} cripto) en ciclos anteriores.")
                print(f"   Podrás transferirlo al nuevo ciclo desde 'Gestión de Bóveda'.")
            
            respuesta = input("\n¿Deseas iniciar un nuevo ciclo? (s/n): ")
            if respuesta.lower() in ['s', 'si', 'sí']:
                return crear_nuevo_ciclo()
            else:
                return None
                
    except sqlite3.Error as e:
        print(f"❌ Error al verificar ciclo: {e}")
        return None

def crear_nuevo_ciclo():
    """Crea un nuevo ciclo de trabajo."""
    try:
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ciclos (fecha_inicio, estado) VALUES (?, ?)", (fecha_hoy, 'activo'))
        nuevo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"✅ Nuevo ciclo #{nuevo_id} iniciado con fecha {fecha_hoy}.")
        return nuevo_id
    except sqlite3.Error as e:
        print(f"❌ Error al crear ciclo: {e}")
        return None

def ejecutar_dia_de_trabajo():
    """Orquesta todo el flujo de trabajo de un día de operaciones."""
    print("\n" + "=" * 60)
    print("MÓDULO OPERADOR: INICIANDO CICLO DIARIO")
    print("=" * 60)
    
    ciclo_id = verificar_o_crear_ciclo()
    
    if ciclo_id:
        print(f"\n🔄 Trabajando en el ciclo activo #{ciclo_id}.")
        
        cripto_actual, costo_promedio = consultar_capital_actual(ciclo_id)
        print(f"💰 Capital inicial del día: {cripto_actual:.4f} cripto")
        print(f"📊 Costo promedio: ${costo_promedio:.4f}")

        if cripto_actual > 0.0001:
            precio_venta_hoy, comision_hoy = analizar_mercado(costo_promedio)
            print("\n" + "-" * 60)
            print("RESUMEN DEL DÍA")
            print("-" * 60)
            print(f"💲 Precio de venta publicado para hoy: ${precio_venta_hoy:.4f}")
            registrar_ventas_del_dia(ciclo_id, precio_venta_hoy, comision_hoy)
        else:
            print("\n⚠️  No hay capital en la bóveda para operar hoy.")
            print("   Usa el Módulo de Bóveda para fondear o transferir capital.")

        print("\n" + "-" * 60)
        print("GESTIÓN DEL CICLO")
        print("-" * 60)
        cierre = input("¿Deseas gestionar el cierre de este ciclo? (s/n): ")
        if cierre.lower() in ['s', 'si', 'sí']:
            gestionar_cierre_ciclo(ciclo_id)
    else:
        print("\n⚠️  No hay un ciclo activo para trabajar. Volviendo al menú principal.")
