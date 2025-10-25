# operador.py
import sqlite3
from datetime import datetime
import utils  # <-- ¡NUEVO! Importamos nuestro módulo de utilidades

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
    """Calcula el cripto total y el costo promedio para el ciclo activo."""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) 
        FROM transacciones WHERE ciclo_id = ?
    """, (ciclo_id,))
    cripto_actual = cursor.fetchone()[0] or 0.0

    cursor.execute("""
        SELECT SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto * precio_unitario ELSE -(cantidad_cripto * precio_unitario) END) 
        FROM transacciones WHERE ciclo_id = ?
    """, (ciclo_id,))
    costo_total_actual = cursor.fetchone()[0] or 0.0

    conn.close()
    
    costo_promedio = (costo_total_actual / cripto_actual) if cripto_actual > 0.0001 else 0
    return cripto_actual, costo_promedio

def analizar_mercado(costo_promedio):
    """Analiza el mercado, define el precio y aplica validaciones avanzadas."""
    print("---------------------------------------------------------")
    print("ANÁLISIS DE MERCADO Y DEFINICIÓN DE PRECIO")
    print("---------------------------------------------------------")
    
    porcentaje_comision = obtener_config_db('comision_defecto')
    porcentaje_ganancia_objetivo = obtener_config_db('ganancia_defecto')
    
    factor_ganancia = 1 + (porcentaje_ganancia_objetivo / 100)
    factor_comision = 1 - (porcentaje_comision / 100)
    
    precio_sugerido = (costo_promedio * factor_ganancia) / factor_comision
    
    print(f"\nUsando {porcentaje_comision}% de comisión y un objetivo de {porcentaje_ganancia_objetivo}% de ganancia...")
    print(f"El precio sugerido es: {precio_sugerido:.4f}")
    
    while True:
        try:
            precio_elegido = float(input("\n¿Qué precio vas a publicar en tu anuncio?: "))
            if precio_elegido <= 0:
                print("Error: El precio debe ser un número positivo.")
                continue

            ganancia_neta_real_pct = (((precio_elegido * factor_comision) / costo_promedio) - 1) * 100

            if ganancia_neta_real_pct < 0:
                print(f"¡ADVERTENCIA GRAVE! Con el precio {precio_elegido:.4f} tu ganancia neta será NEGATIVA: {ganancia_neta_real_pct:.2f}%.")
                if utils.confirmar_accion("¿Estás seguro de que quieres operar con pérdidas?"):
                    break 
            
            elif ganancia_neta_real_pct < porcentaje_ganancia_objetivo:
                print(f"¡ADVERTENCIA! Con el precio {precio_elegido:.4f} tu ganancia neta será de solo un {ganancia_neta_real_pct:.2f}%. No alcanzarás tu meta del {porcentaje_ganancia_objetivo}%.")
                
                if 0 < ganancia_neta_real_pct < 0.5:
                    print("Este margen es muy bajo y podría resultar en pérdidas por comisiones en transacciones pequeñas.")
                
                if utils.confirmar_accion("¿Aún así deseas usar este precio?"):
                    break 
            
            else:
                print(f"Buen precio. Tu ganancia neta estimada será de un {ganancia_neta_real_pct:.2f}%.")
                break

        except ValueError:
            print("Error: Ingrese un valor numérico.")
            
    return precio_elegido, porcentaje_comision

def registrar_ventas_del_dia(ciclo_id, precio_venta, comision):
    """Registra hasta 3 ventas en la BD, incluyendo todas las validaciones."""
    print("\n---------------------------------------------------------")
    print("CONTABILIDAD DE CIERRE DEL DÍA")
    print("---------------------------------------------------------")
    ventas_realizadas = 0
    while ventas_realizadas < 3:
        cripto_disponible, costo_promedio_actual = consultar_capital_actual(ciclo_id)
        if cripto_disponible < 0.0001:
            print("No queda capital en la bóveda para vender.")
            break

        print(f"\nCapital actual en bóveda: {cripto_disponible:.4f} cripto.")
        if utils.confirmar_accion(f"¿Deseas registrar la venta #{ventas_realizadas + 1}?"):
            while True:
                respuesta_cantidad = input(f"  Ingresa la cantidad de cripto vendido (o 'todo'): ")
                if respuesta_cantidad.lower().strip() == 'todo':
                    cantidad_vendida = cripto_disponible
                    print(f"  Vendiendo todo el capital restante: {cantidad_vendida:.4f}")
                    break
                try:
                    cantidad_vendida = float(respuesta_cantidad)
                    if cantidad_vendida <= 0:
                        print("  Error: La cantidad debe ser mayor a cero.")
                    elif cantidad_vendida > cripto_disponible:
                        print(f"  Error: No puedes vender más de {cripto_disponible:.4f} cripto.")
                    else:
                        break
                except ValueError:
                    print("  Error: Ingrese un número o la palabra 'todo'.")
            
            conn = sqlite3.connect('arbitraje.db')
            cursor = conn.cursor()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO transacciones (ciclo_id, fecha, tipo, cantidad_cripto, precio_unitario, precio_venta_real, comision_pct)
                VALUES (?, ?, 'venta', ?, ?, ?, ?)
            """, (ciclo_id, fecha_actual, cantidad_vendida, costo_promedio_actual, precio_venta, comision))
            conn.commit()
            conn.close()
            print("  ¡Venta registrada con éxito!")
            ventas_realizadas += 1
        else:
            break
            
    print("\nFase de contabilidad del día finalizada.")

def finalizar_ciclo_activo(ciclo_id):
    """Calcula la ganancia neta automáticamente y cierra el ciclo."""
    print("\n--- Finalizando Ciclo de Trabajo ---")
    if utils.confirmar_accion(f"¿Estás seguro de que deseas cerrar el ciclo #{ciclo_id}?"):
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM( (cantidad_cripto * precio_venta_real * (1 - comision_pct / 100)) - (cantidad_cripto * precio_unitario) )
            FROM transacciones WHERE ciclo_id = ? AND tipo = 'venta'
        """, (ciclo_id,))
        ganancia_final = cursor.fetchone()[0] or 0.0

        fecha_fin = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            UPDATE ciclos SET estado = 'completado', fecha_fin = ?, ganancia_neta_total = ?
            WHERE id = ?
        """, (fecha_fin, ganancia_final, ciclo_id))

        conn.commit()
        conn.close()
        print(f"\n¡Ciclo #{ciclo_id} cerrado con una ganancia neta de ${ganancia_final:.2f}!")
        return True
    return False

# =================================================
# FUNCIÓN PRINCIPAL DEL MÓDULO
# =================================================

def verificar_o_crear_ciclo():
    """Busca o crea un ciclo activo y devuelve su ID."""
    ciclo_activo_id = utils.obtener_ciclo_activo_id() # Usamos la nueva función
    if ciclo_activo_id:
        return ciclo_activo_id
    else:
        print("\nNo se encontró ningún ciclo de trabajo activo.")
        if utils.confirmar_accion("¿Deseas iniciar un nuevo ciclo?"):
            conn = sqlite3.connect('arbitraje.db')
            cursor = conn.cursor()
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO ciclos (fecha_inicio, estado) VALUES (?, ?)", (fecha_hoy, 'activo'))
            nuevo_id = cursor.lastrowid
            conn.commit()
            conn.close()
            print(f"Nuevo ciclo #{nuevo_id} iniciado con fecha {fecha_hoy}.")
            return nuevo_id
        else:
            return None

def ejecutar_dia_de_trabajo():
    """Orquesta todo el flujo de trabajo de un día de operaciones."""
    print("\n--- Módulo Operador: Iniciando Ciclo Diario ---")
    ciclo_id = verificar_o_crear_ciclo()
    
    if ciclo_id:
        print(f"\nTrabajando en el ciclo activo #{ciclo_id}.")
        
        cripto_actual, costo_promedio = consultar_capital_actual(ciclo_id)
        print(f"Capital inicial del día: {cripto_actual:.4f} cripto con un costo promedio de ${costo_promedio:.4f}")

        if cripto_actual > 0.0001:
            precio_venta_hoy, comision_hoy = analizar_mercado(costo_promedio)
            print("\n--- Resumen del Día ---")
            print(f"Precio de venta publicado para hoy: {precio_venta_hoy:.4f}")
            registrar_ventas_del_dia(ciclo_id, precio_venta_hoy, comision_hoy)
        else:
            print("\nNo hay capital en la bóveda para operar hoy. Usa el Módulo de Bóveda para fondear.")

        print("\n--- Gestión del Ciclo ---")
        if utils.confirmar_accion("¿Deseas finalizar y cerrar este ciclo de trabajo?"):
            finalizar_ciclo_activo(ciclo_id)
    else:
        print("\nNo hay un ciclo activo para trabajar. Volviendo al menú principal.")
