# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime, timedelta
import dias

# =================================================
# FUNCIONES AUXILIARES DEL MODULO
# =================================================

def obtener_config_db(clave):
    """Funcion auxiliar para leer la configuracion desde la BD."""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,))
    resultado = cursor.fetchone()
    conn.close()
    if clave == 'comision_defecto':
        return float(resultado[0]) if resultado else 0.35
    if clave == 'ganancia_defecto':
        return float(resultado[0]) if resultado else 2.0
    if clave == 'ventas_minimas_dia':
        return int(resultado[0]) if resultado else 3
    if clave == 'ventas_maximas_dia':
        return int(resultado[0]) if resultado else 5
    if clave == 'dias_ciclo_defecto':
        return int(resultado[0]) if resultado else 15
    return None

def obtener_info_ciclo_completa(ciclo_id):
    """Obtiene informacion completa del ciclo global."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT fecha_inicio, dias_planificados, inversion_inicial, estado, cripto
            FROM ciclos WHERE id = ?
        """, (ciclo_id,))
        info = cursor.fetchone()
        
        # Contar dias transcurridos
        cursor.execute("""
            SELECT COUNT(*) FROM dias_operacion WHERE ciclo_id = ?
        """, (ciclo_id,))
        dias_transcurridos = cursor.fetchone()[0] or 0
        
        # Contar transacciones
        cursor.execute("""
            SELECT COUNT(*) FROM transacciones WHERE ciclo_id = ?
        """, (ciclo_id,))
        num_trans = cursor.fetchone()[0]
        
        conn.close()
        
        if info:
            return {
                'fecha_inicio': info[0],
                'dias_planificados': info[1],
                'inversion_inicial': info[2],
                'estado': info[3],
                'cripto': info[4],
                'dias_transcurridos': dias_transcurridos,
                'num_transacciones': num_trans
            }
        return None
    except sqlite3.Error as e:
        print(f"Error al obtener info del ciclo: {e}")
        return None

def consultar_capital_ciclo(ciclo_id):
    """Calcula el capital actual del ciclo por cripto."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
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
        print("Capital actual: $0.00 USD")
        return
    
    print("Capital actual:")
    
    for cripto, info in capital_info.items():
        if cripto == 'total_fiat':
            continue
        
        info_cripto = criptomonedas.obtener_info_cripto(cripto)
        nombre = info_cripto['nombre'] if info_cripto else cripto
        cantidad_fmt = criptomonedas.formatear_cantidad_cripto(info['cantidad'], cripto)
        
        print(f"  - {cantidad_fmt} {nombre} ({cripto}) = ${info['valor']:.2f}")
    
    print(f"  Total: ${capital_info['total_fiat']:.2f} USD")

def analizar_mercado(costo_promedio):
    """Analiza el mercado, define el precio y aplica validaciones avanzadas."""
    print("-" * 60)
    print("ANALISIS DE MERCADO Y DEFINICION DE PRECIO")
    print("-" * 60)
    
    porcentaje_comision = obtener_config_db('comision_defecto')
    porcentaje_ganancia_objetivo = obtener_config_db('ganancia_defecto')
    
    factor_ganancia = 1 + (porcentaje_ganancia_objetivo / 100)
    factor_comision = 1 - (porcentaje_comision / 100)
    
    precio_sugerido = (costo_promedio * factor_ganancia) / factor_comision
    
    print(f"\nUsando {porcentaje_comision}% de comision y un objetivo de {porcentaje_ganancia_objetivo}% de ganancia...")
    print(f"Costo promedio actual: ${costo_promedio:.4f}")
    print(f"Precio sugerido: ${precio_sugerido:.4f}")
    
    while True:
        try:
            precio_elegido = float(input("\nQue precio vas a publicar en tu anuncio?: "))
            if precio_elegido <= 0:
                print("Error: El precio debe ser un numero positivo.")
                continue

            ganancia_neta_real_pct = (((precio_elegido * factor_comision) / costo_promedio) - 1) * 100

            if ganancia_neta_real_pct < 0:
                print(f"\nADVERTENCIA GRAVE! Con el precio ${precio_elegido:.4f} tu ganancia neta sera NEGATIVA: {ganancia_neta_real_pct:.2f}%.")
                confirmacion = input("Estas seguro de que quieres operar con perdidas? (s/n): ")
                if confirmacion.lower() in ['s', 'si']:
                    print("Operacion con perdidas confirmada.")
                    break
            elif ganancia_neta_real_pct < porcentaje_ganancia_objetivo:
                print(f"\nADVERTENCIA! Con el precio ${precio_elegido:.4f} tu ganancia neta sera de solo un {ganancia_neta_real_pct:.2f}%.")
                print(f"   No alcanzaras tu meta del {porcentaje_ganancia_objetivo}%.")
                
                if 0 < ganancia_neta_real_pct < 0.5:
                    print("   Este margen es muy bajo y podria resultar en perdidas por comisiones en transacciones pequenas.")
                
                confirmacion = input("Aun asi deseas usar este precio? (s/n): ")
                if confirmacion.lower() in ['s', 'si']:
                    break
            else:
                print(f"Buen precio. Tu ganancia neta estimada sera de un {ganancia_neta_real_pct:.2f}%.")
                break

        except ValueError:
            print("Error: Ingrese un valor numerico valido.")
            
    return precio_elegido, porcentaje_comision

def registrar_ventas_del_dia(ciclo_id, dia_id, precio_venta, comision, cripto, cantidad_disponible, costo_promedio):
    """Registra ventas del dia con limite configurable."""
    print("\n" + "-" * 60)
    print("CONTABILIDAD DE CIERRE DEL DIA")
    print("-" * 60)
    
    # Obtener limites
    ventas_min = obtener_config_db('ventas_minimas_dia')
    ventas_max = obtener_config_db('ventas_maximas_dia')
    
    print(f"\nLimite de ventas por dia: {ventas_min} minimo, {ventas_max} maximo")
    print("IMPORTANTE: Para evitar bloqueos bancarios, respeta el limite de ventas.")
    
    # Obtener ventas actuales del dia
    puede_vender, ventas_actuales, max_ventas = dias.validar_limite_ventas(dia_id)
    
    import criptomonedas
    info_cripto = criptomonedas.obtener_info_cripto(cripto)
    nombre_cripto = info_cripto['nombre'] if info_cripto else cripto
    
    cantidad_actual = cantidad_disponible
    
    while puede_vender:
        if cantidad_actual < 0.0001:
            print("\nNo queda capital de esta cripto para vender.")
            break

        cantidad_fmt = criptomonedas.formatear_cantidad_cripto(cantidad_actual, cripto)
        print(f"\nCapital actual de {nombre_cripto}: {cantidad_fmt}")
        print(f"Ventas realizadas hoy: {ventas_actuales}/{max_ventas}")
        
        if ventas_actuales >= ventas_min:
            print(f"Ya alcanzaste el minimo de {ventas_min} ventas.")
            continuar = input("Deseas registrar otra venta? (s/n): ")
            if continuar.lower() not in ['s', 'si']:
                break
        
        respuesta = input(f"\nDeseas registrar la venta #{ventas_actuales + 1}? (s/n): ")
        
        if respuesta.lower() in ['s', 'si']:
            while True:
                respuesta_cantidad = input(f"  Ingresa la cantidad de {cripto} vendido (o 'todo'): ")
                if respuesta_cantidad.lower() == 'todo':
                    cantidad_vendida = cantidad_actual
                    print(f"  Vendiendo todo el capital restante: {criptomonedas.formatear_cantidad_cripto(cantidad_vendida, cripto)}")
                    break
                try:
                    cantidad_vendida = float(respuesta_cantidad)
                    if cantidad_vendida <= 0:
                        print("  Error: La cantidad debe ser mayor a cero.")
                    elif cantidad_vendida > cantidad_actual:
                        print(f"  Error: No puedes vender mas de {cantidad_fmt}")
                    else:
                        break
                except ValueError:
                    print("  Error: Ingrese un numero o la palabra 'todo'.")
            
            try:
                conn = sqlite3.connect('arbitraje.db')
                cursor = conn.cursor()
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                monto_fiat_venta = cantidad_vendida * precio_venta
                
                cursor.execute("""
                    INSERT INTO transacciones 
                    (ciclo_id, dia_id, fecha, tipo, cripto, cantidad_cripto, precio_unitario, precio_venta_real, comision_pct, monto_fiat)
                    VALUES (?, ?, ?, 'venta', ?, ?, ?, ?, ?, ?)
                """, (ciclo_id, dia_id, fecha_actual, cripto, cantidad_vendida, costo_promedio, precio_venta, comision, monto_fiat_venta))
                
                conn.commit()
                conn.close()
                
                # Incrementar contador de ventas
                dias.incrementar_ventas_dia(dia_id)
                
                print("  Venta registrada con exito!")
                cantidad_actual -= cantidad_vendida
                ventas_actuales += 1
                
                # Validar limite de nuevo
                puede_vender, ventas_actuales, max_ventas = dias.validar_limite_ventas(dia_id)
                
                if not puede_vender:
                    print(f"\nLIMITE ALCANZADO: Has realizado {max_ventas} ventas hoy.")
                    print("Para evitar bloqueos bancarios, no puedes hacer mas ventas hoy.")
                    break
                    
            except sqlite3.Error as e:
                print(f"  Error al registrar la venta: {e}")
                
        elif respuesta.lower() in ['n', 'no']:
            break
        else:
            print("  Error: Respuesta no valida. Intentalo de nuevo.")
    
    # Validar minimo de ventas
    if ventas_actuales < ventas_min:
        print(f"\nADVERTENCIA: Solo realizaste {ventas_actuales} ventas.")
        print(f"El minimo recomendado es {ventas_min} ventas por dia.")
            
    print("\nFase de contabilidad del dia finalizada.")

def cerrar_dia_operacion(ciclo_id, dia_id):
    """Cierra el dia de operacion y muestra resumen."""
    print("\n" + "=" * 60)
    print("CIERRE DEL DIA DE OPERACION")
    print("=" * 60)
    
    resumen = dias.cerrar_dia_actual(ciclo_id, dia_id)
    
    if resumen:
        print(f"\nCapital inicial del dia: ${resumen['capital_inicial']:.2f}")
        print(f"Capital final del dia: ${resumen['capital_final']:.2f}")
        print(f"Ganancia del dia: ${resumen['ganancia']:.2f}")
        print(f"Ventas realizadas: {resumen['num_ventas']}")
        print("\nDia cerrado exitosamente!")
        return True
    else:
        print("\nError al cerrar el dia.")
        return False

def mostrar_progreso_ciclo(ciclo_id):
    """Muestra el progreso del ciclo global."""
    info = obtener_info_ciclo_completa(ciclo_id)
    
    if not info:
        return
    
    print("\n" + "=" * 60)
    print("PROGRESO DEL CICLO GLOBAL")
    print("=" * 60)
    
    dias_restantes = info['dias_planificados'] - info['dias_transcurridos']
    porcentaje_avance = (info['dias_transcurridos'] / info['dias_planificados']) * 100
    
    print(f"Ciclo #{ciclo_id}")
    print(f"Fecha inicio: {info['fecha_inicio']}")
    print(f"Dias planificados: {info['dias_planificados']}")
    print(f"Dias transcurridos: {info['dias_transcurridos']}")
    print(f"Dias restantes: {dias_restantes}")
    print(f"Avance: {porcentaje_avance:.1f}%")
    print(f"Inversion inicial: ${info['inversion_inicial']:.2f}")
    
    # Mostrar resumen de dias
    dias_resumen = dias.obtener_resumen_dias(ciclo_id)
    
    if dias_resumen:
        print("\nResumen de dias:")
        ganancia_acumulada = 0
        for dia in dias_resumen:
            ganancia_acumulada += dia[4]  # ganancia_dia
            estado_emoji = "CERRADO" if dia[6] == 'cerrado' else "ABIERTO"
            print(f"  Dia {dia[0]:2d} ({dia[1]}) - ${dia[4]:6.2f} [{estado_emoji}]")
        
        print(f"\nGanancia acumulada: ${ganancia_acumulada:.2f}")
        
        capital_actual = consultar_capital_ciclo(ciclo_id)
        print(f"Capital actual total: ${capital_actual.get('total_fiat', 0):.2f}")
    
    print("=" * 60)

def gestionar_cierre_ciclo_global(ciclo_id):
    """Gestiona el cierre completo del ciclo global."""
    print("\n" + "=" * 60)
    print("CIERRE DEL CICLO GLOBAL")
    print("=" * 60)
    
    # Mostrar progreso final
    mostrar_progreso_ciclo(ciclo_id)
    
    info = obtener_info_ciclo_completa(ciclo_id)
    
    if info['dias_transcurridos'] < info['dias_planificados']:
        print(f"\nADVERTENCIA: El ciclo esta planificado para {info['dias_planificados']} dias.")
        print(f"Solo han transcurrido {info['dias_transcurridos']} dias.")
        confirmacion = input("\nDeseas cerrar el ciclo antes de tiempo? (s/n): ")
        if confirmacion.lower() not in ['s', 'si']:
            print("Cierre cancelado.")
            return False
    
    # Calcular ganancia total
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(ganancia_dia) FROM dias_operacion WHERE ciclo_id = ?
        """, (ciclo_id,))
        ganancia_total = cursor.fetchone()[0] or 0.0
        
        # Obtener capital final
        capital_final = consultar_capital_ciclo(ciclo_id)
        total_fiat_final = capital_final.get('total_fiat', 0)
        
        fecha_fin = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE ciclos 
            SET estado = 'completado', fecha_fin = ?, ganancia_neta_total = ?
            WHERE id = ?
        """, (fecha_fin, ganancia_total, ciclo_id))
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("BALANCE FINAL DEL CICLO GLOBAL")
        print("=" * 60)
        print(f"Inversion inicial: ${info['inversion_inicial']:.2f}")
        print(f"Ganancia neta total: ${ganancia_total:.2f}")
        print(f"Capital final: ${total_fiat_final:.2f}")
        print(f"Dias operados: {info['dias_transcurridos']}")
        print(f"ROI: {(ganancia_total / info['inversion_inicial'] * 100):.2f}%")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error al cerrar ciclo: {e}")
        return False

def crear_nuevo_ciclo_global():
    """Crea un nuevo ciclo global con duracion planificada."""
    print("\n" + "=" * 60)
    print("CREAR NUEVO CICLO GLOBAL")
    print("=" * 60)
    
    # Preguntar duracion
    dias_defecto = obtener_config_db('dias_ciclo_defecto')
    print(f"\nCuantos dias durara este ciclo?")
    print(f"(Por defecto: {dias_defecto} dias)")
    
    try:
        dias_input = input(f"Dias del ciclo (Enter para {dias_defecto}): ").strip()
        dias_ciclo = int(dias_input) if dias_input else dias_defecto
        
        if dias_ciclo < 1:
            print("Error: El ciclo debe durar al menos 1 dia.")
            return None
        
        if dias_ciclo > 90:
            print("Advertencia: Ciclos muy largos pueden ser dificiles de gestionar.")
            confirmacion = input(f"Confirmar ciclo de {dias_ciclo} dias? (s/n): ")
            if confirmacion.lower() not in ['s', 'si']:
                return None
        
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        fecha_fin_estimada = (datetime.now() + timedelta(days=dias_ciclo)).strftime("%Y-%m-%d")
        
        print(f"\nFecha inicio: {fecha_hoy}")
        print(f"Fecha fin estimada: {fecha_fin_estimada}")
        print(f"Duracion: {dias_ciclo} dias")
        
        confirmacion_final = input("\nConfirmar creacion del ciclo? (s/n): ")
        if confirmacion_final.lower() not in ['s', 'si']:
            print("Creacion cancelada.")
            return None
        
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ciclos (fecha_inicio, dias_planificados, estado)
            VALUES (?, ?, 'activo')
        """, (fecha_hoy, dias_ciclo))
        nuevo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"\nNuevo ciclo #{nuevo_id} creado exitosamente!")
        print(f"Duracion: {dias_ciclo} dias")
        return nuevo_id
        
    except ValueError:
        print("Error: Ingresa un numero valido.")
        return None
    except sqlite3.Error as e:
        print(f"Error al crear ciclo: {e}")
        return None

def verificar_o_crear_ciclo():
    """Verifica si hay un ciclo activo y gestiona la decision del usuario."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        ciclo_activo = cursor.fetchone()
        conn.close()
        
        if ciclo_activo:
            ciclo_id = ciclo_activo[0]
            info = obtener_info_ciclo_completa(ciclo_id)
            capital_info = consultar_capital_ciclo(ciclo_id)
            
            print(f"\nCICLO GLOBAL ACTIVO DETECTADO: #{ciclo_id}")
            print(f"   Fecha inicio: {info['fecha_inicio']}")
            print(f"   Dias planificados: {info['dias_planificados']}")
            print(f"   Dias transcurridos: {info['dias_transcurridos']}")
            print(f"   Dias restantes: {info['dias_planificados'] - info['dias_transcurridos']}")
            print(f"   Inversion inicial: ${info['inversion_inicial']:.2f}")
            
            # Mostrar capital
            if capital_info.get('total_fiat', 0) > 0:
                print(f"   Capital actual:")
                import criptomonedas
                for cripto, info_cripto in capital_info.items():
                    if cripto == 'total_fiat':
                        continue
                    info_c = criptomonedas.obtener_info_cripto(cripto)
                    nombre = info_c['nombre'] if info_c else cripto
                    cantidad_fmt = criptomonedas.formatear_cantidad_cripto(info_cripto['cantidad'], cripto)
                    print(f"      {cantidad_fmt} {nombre} = ${info_cripto['valor']:.2f}")
                print(f"   Total: ${capital_info['total_fiat']:.2f} USD")
            else:
                print(f"   Capital actual: $0.00 USD")
            
            print("\n" + "-" * 60)
            print("QUE DESEAS HACER?")
            print("-" * 60)
            print(f"[1] CONTINUAR operando en el ciclo #{ciclo_id}")
            print(f"[2] VER PROGRESO del ciclo #{ciclo_id}")
            print(f"[3] CERRAR el ciclo #{ciclo_id} e iniciar uno nuevo")
            print("[4] CANCELAR y volver al menu")
            print("-" * 60)
            
            opcion = input("Selecciona una opcion (1-4): ")
            
            if opcion == '1':
                return ciclo_id
            elif opcion == '2':
                mostrar_progreso_ciclo(ciclo_id)
                input("\nPresiona Enter para continuar...")
                return verificar_o_crear_ciclo()
            elif opcion == '3':
                if gestionar_cierre_ciclo_global(ciclo_id):
                    print("\nCreando nuevo ciclo...")
                    return crear_nuevo_ciclo_global()
                else:
                    return ciclo_id
            else:
                print("\nOperacion cancelada.")
                return None
        else:
            print("\nNo se encontro ningun ciclo global activo.")
            respuesta = input("\nDeseas iniciar un nuevo ciclo global? (s/n): ")
            if respuesta.lower() in ['s', 'si']:
                return crear_nuevo_ciclo_global()
            else:
                return None
                
    except sqlite3.Error as e:
        print(f"Error al verificar ciclo: {e}")
        return None

def ejecutar_dia_de_trabajo():
    """Orquesta todo el flujo de trabajo de un dia de operaciones."""
    print("\n" + "=" * 60)
    print("MODULO OPERADOR: INICIANDO DIA DE OPERACION")
    print("=" * 60)
    
    ciclo_id = verificar_o_crear_ciclo()
    
    if not ciclo_id:
        print("\nNo hay un ciclo activo para trabajar. Volviendo al menu principal.")
        return
    
    print(f"\nTrabajando en el ciclo global #{ciclo_id}.")
    
    # Verificar si hay un dia abierto
    dia_actual = dias.obtener_dia_actual(ciclo_id)
    
    if not dia_actual:
        # Crear nuevo dia
        print("\nIniciando nuevo dia de operacion...")
        capital_info = consultar_capital_ciclo(ciclo_id)
        capital_inicial = capital_info.get('total_fiat', 0)
        
        if capital_inicial == 0:
            print("\nNo hay capital para operar.")
            print("Usa el Modulo de Boveda para fondear.")
            return
        
        dia_id = dias.crear_nuevo_dia(ciclo_id, capital_inicial)
        if not dia_id:
            print("Error al crear dia de operacion.")
            return
        
        dia_actual = dias.obtener_dia_actual(ciclo_id)
    
    print(f"\nDia de operacion #{dia_actual['numero_dia']}")
    print(f"Capital inicial del dia: ${dia_actual['capital_inicial']:.2f}")
    
    # Obtener capital actual
    capital_info = consultar_capital_ciclo(ciclo_id)
    mostrar_capital_detallado(capital_info)
    
    if capital_info.get('total_fiat', 0) > 0.0001:
        # Elegir cripto para operar
        print("\nCon cual cripto deseas operar hoy?")
        criptos_disponibles = [c for c in capital_info.keys() if c != 'total_fiat']
        
        for i, cripto in enumerate(criptos_disponibles, 1):
            info = capital_info[cripto]
            import criptomonedas
            info_c = criptomonedas.obtener_info_cripto(cripto)
            nombre = info_c['nombre'] if info_c else cripto
            cantidad_fmt = criptomonedas.formatear_cantidad_cripto(info['cantidad'], cripto)
            print(f"[{i}] {nombre} ({cripto}) - {cantidad_fmt} disponibles")
        
        try:
            seleccion = int(input("\nSelecciona (numero): "))
            if 1 <= seleccion <= len(criptos_disponibles):
                cripto_elegida = criptos_disponibles[seleccion - 1]
                info_cripto = capital_info[cripto_elegida]
                
                # Analizar mercado
                precio_venta_hoy, comision_hoy = analizar_mercado(info_cripto['costo_promedio'])
                print("\n" + "-" * 60)
                print("RESUMEN DEL DIA")
                print("-" * 60)
                print(f"Cripto seleccionada: {cripto_elegida}")
                print(f"Precio de venta publicado para hoy: ${precio_venta_hoy:.4f}")
                
                # Registrar ventas
                registrar_ventas_del_dia(
                    ciclo_id, 
                    dia_actual['id'], 
                    precio_venta_hoy, 
                    comision_hoy, 
                    cripto_elegida, 
                    info_cripto['cantidad'],
                    info_cripto['costo_promedio']
                )
                
                # Cerrar dia
                print("\n" + "-" * 60)
                print("CIERRE DEL DIA")
                print("-" * 60)
                cierre = input("Deseas cerrar el dia de operacion? (s/n): ")
                if cierre.lower() in ['s', 'si']:
                    if cerrar_dia_operacion(ciclo_id, dia_actual['id']):
                        # Preguntar si quiere ver progreso
                        ver_progreso = input("\nDeseas ver el progreso del ciclo global? (s/n): ")
                        if ver_progreso.lower() in ['s', 'si']:
                            mostrar_progreso_ciclo(ciclo_id)
            else:
                print("\nOpcion invalida.")
        except ValueError:
            print("\nError: Ingresa un numero valido.")
    else:
        print("\nNo hay capital en la boveda para operar hoy.")
        print("   Usa el Modulo de Boveda para fondear o transferir capital.")