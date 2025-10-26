# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime
import criptomonedas

def obtener_ciclo_activo():
    """Obtiene el ID del ciclo activo o None si no existe."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"Error al obtener ciclo activo: {e}")
        return None

def consultar_boveda():
    """Calcula y muestra el estado actual de la boveda desde la BD."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()

        # Capital TOTAL por cripto
        cursor.execute("""
            SELECT cripto, 
                   SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) as cantidad,
                   SUM(CASE WHEN tipo = 'compra' THEN monto_fiat ELSE -monto_fiat END) as valor_fiat
            FROM transacciones
            GROUP BY cripto
            HAVING cantidad > 0.0001
        """)
        criptos_totales = cursor.fetchall()

        # Capital en el ciclo ACTIVO
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        ciclo_activo = cursor.fetchone()
        
        print("\n" + "=" * 60)
        print("ESTADO ACTUAL DE LA BOVEDA")
        print("=" * 60)
        
        if not criptos_totales:
            print("\nLa boveda esta vacia.")
            print("Usa la opcion [2] para fondear.")
        else:
            print("\nCAPITAL TOTAL (Todas las criptos):")
            total_fiat = 0
            for cripto_data in criptos_totales:
                cripto = cripto_data[0]
                cantidad = cripto_data[1]
                valor = cripto_data[2]
                total_fiat += valor
                
                info_cripto = criptomonedas.obtener_info_cripto(cripto)
                nombre = info_cripto['nombre'] if info_cripto else cripto
                cantidad_fmt = criptomonedas.formatear_cantidad_cripto(cantidad, cripto)
                
                print(f"\n   {nombre} ({cripto}):")
                print(f"   Cantidad: {cantidad_fmt}")
                print(f"   Valor: ${valor:.2f}")
                print(f"   Precio promedio: ${(valor/cantidad):.4f}")
            
            print(f"\n   TOTAL EN FIAT: ${total_fiat:.2f}")
        
        if ciclo_activo:
            ciclo_id = ciclo_activo[0]
            
            cursor.execute("""
                SELECT cripto,
                       SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) as cantidad,
                       SUM(CASE WHEN tipo = 'compra' THEN monto_fiat ELSE -monto_fiat END) as valor_fiat
                FROM transacciones 
                WHERE ciclo_id = ?
                GROUP BY cripto
                HAVING cantidad > 0.0001
            """, (ciclo_id,))
            criptos_activo = cursor.fetchall()
            
            print(f"\nCAPITAL EN CICLO ACTIVO (#{ciclo_id}):")
            
            if not criptos_activo:
                print("   Sin capital en este ciclo.")
                
                if criptos_totales:
                    print("\n   Tienes capital en ciclos anteriores.")
                    print("   Usa la opcion [4] para transferirlo.")
            else:
                total_activo = 0
                for cripto_data in criptos_activo:
                    cripto = cripto_data[0]
                    cantidad = cripto_data[1]
                    valor = cripto_data[2]
                    total_activo += valor
                    
                    info_cripto = criptomonedas.obtener_info_cripto(cripto)
                    nombre = info_cripto['nombre'] if info_cripto else cripto
                    cantidad_fmt = criptomonedas.formatear_cantidad_cripto(cantidad, cripto)
                    
                    print(f"\n   {nombre} ({cripto}):")
                    print(f"   Disponible: {cantidad_fmt}")
                    print(f"   Valor: ${valor:.2f}")
                
                print(f"\n   TOTAL EN CICLO: ${total_activo:.2f}")
                
                capital_otros = total_fiat - total_activo
                if capital_otros > 0.01:
                    print(f"\n   Capital en ciclos anteriores: ${capital_otros:.2f}")
                    print("   Usa [4] para transferirlo al ciclo activo.")
        else:
            print("\nNo hay ciclo activo.")
            if criptos_totales:
                print("Crea un ciclo y transfiere el capital.")
        
        conn.close()
        print("=" * 60)
    except sqlite3.Error as e:
        print(f"Error al consultar la boveda: {e}")

def fondear_boveda():
    """Registra una nueva compra con monto en FIAT y seleccion de cripto."""
    print("\n" + "=" * 60)
    print("FONDEAR BOVEDA (REGISTRAR COMPRA)")
    print("=" * 60)
    
    ciclo_id = obtener_ciclo_activo()
    
    if ciclo_id is None:
        print("\nError: No hay un ciclo activo.")
        print("   Debes crear un ciclo desde el Modulo Operador primero.")
        input("\nPresiona Enter para continuar...")
        return
    
    print(f"\nRegistrando compra en el ciclo activo #{ciclo_id}")
    
    cripto = criptomonedas.seleccionar_cripto()
    info_cripto = criptomonedas.obtener_info_cripto(cripto)
    
    try:
        print(f"\nIngresa el monto que vas a invertir:")
        monto_fiat = float(input("Monto en USD: $"))
        
        if monto_fiat <= 0:
            print("Error: El monto debe ser positivo.")
            input("\nPresiona Enter para continuar...")
            return
        
        print(f"\nIngresa la tasa de compra de {cripto}:")
        print(f"   (Cuantos USD cuesta 1 {cripto}?)")
        tasa_compra = float(input(f"1 {cripto} = $"))
        
        if tasa_compra <= 0:
            print("Error: La tasa debe ser positiva.")
            input("\nPresiona Enter para continuar...")
            return
        
        cantidad_cripto = monto_fiat / tasa_compra
        cantidad_fmt = criptomonedas.formatear_cantidad_cripto(cantidad_cripto, cripto)
        
        print(f"\n" + "=" * 60)
        print("RESUMEN DE LA COMPRA")
        print("=" * 60)
        print(f"Criptomoneda: {info_cripto['nombre']} ({cripto})")
        print(f"Monto invertido: ${monto_fiat:.2f} USD")
        print(f"Tasa de compra: 1 {cripto} = ${tasa_compra:.4f}")
        print(f"Cantidad comprada: {cantidad_fmt} {cripto}")
        print(f"Precio unitario: ${tasa_compra:.4f}")
        print("=" * 60)
        
        confirmacion = input("\nConfirmar esta compra? (s/n): ")
        if confirmacion.lower() not in ['s', 'si']:
            print("Compra cancelada.")
            input("\nPresiona Enter para continuar...")
            return

        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO transacciones 
            (ciclo_id, fecha, tipo, cripto, cantidad_cripto, precio_unitario, comision_pct, monto_fiat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ciclo_id, fecha_actual, 'compra', cripto, cantidad_cripto, tasa_compra, 0, monto_fiat))
        
        conn.commit()
        conn.close()
        
        print("\nCompra registrada con exito!")
        print(f"Ahora tienes {cantidad_fmt} {cripto} en tu boveda.")
        
    except ValueError:
        print("\nError: Entrada no valida. Por favor, ingrese solo numeros.")
    except sqlite3.Error as e:
        print(f"\nError al registrar la compra: {e}")
    
    input("\nPresiona Enter para continuar...")

def ver_historial_transacciones():
    """Muestra el historial de transacciones con filtros."""
    print("\n" + "=" * 60)
    print("HISTORIAL DE TRANSACCIONES")
    print("=" * 60)
    
    print("\nFiltrar por:")
    print("[1] Todas las transacciones")
    print("[2] Solo del ciclo activo")
    print("[3] Por tipo (compra/venta)")
    print("[4] Por criptomoneda")
    print("[5] Cancelar")
    
    opcion = input("\nSelecciona una opcion: ")
    
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        if opcion == '1':
            cursor.execute("""
                SELECT id, ciclo_id, fecha, tipo, cripto, cantidad_cripto, precio_unitario, monto_fiat
                FROM transacciones 
                ORDER BY fecha DESC
                LIMIT 50
            """)
            titulo = "TODAS LAS TRANSACCIONES (Ultimas 50)"
            
        elif opcion == '2':
            ciclo_id = obtener_ciclo_activo()
            if not ciclo_id:
                print("\nNo hay ciclo activo.")
                conn.close()
                input("\nPresiona Enter para continuar...")
                return
            
            cursor.execute("""
                SELECT id, ciclo_id, fecha, tipo, cripto, cantidad_cripto, precio_unitario, monto_fiat
                FROM transacciones 
                WHERE ciclo_id = ?
                ORDER BY fecha DESC
            """, (ciclo_id,))
            titulo = f"TRANSACCIONES DEL CICLO ACTIVO #{ciclo_id}"
            
        elif opcion == '3':
            print("\n[1] Compras")
            print("[2] Ventas")
            tipo_op = input("Selecciona: ")
            tipo = 'compra' if tipo_op == '1' else 'venta'
            
            cursor.execute("""
                SELECT id, ciclo_id, fecha, tipo, cripto, cantidad_cripto, precio_unitario, monto_fiat
                FROM transacciones 
                WHERE tipo = ?
                ORDER BY fecha DESC
                LIMIT 50
            """, (tipo,))
            titulo = f"TRANSACCIONES DE {tipo.upper()}"
            
        elif opcion == '4':
            cripto = input("\nIngresa el simbolo de la cripto (ej: USDT): ").upper()
            cursor.execute("""
                SELECT id, ciclo_id, fecha, tipo, cripto, cantidad_cripto, precio_unitario, monto_fiat
                FROM transacciones 
                WHERE cripto = ?
                ORDER BY fecha DESC
                LIMIT 50
            """, (cripto,))
            titulo = f"TRANSACCIONES DE {cripto}"
            
        else:
            conn.close()
            return
        
        transacciones = cursor.fetchall()
        conn.close()
        
        print("\n" + "=" * 60)
        print(titulo)
        print("=" * 60)
        
        if not transacciones:
            print("\nNo hay transacciones con estos filtros.")
        else:
            for trans in transacciones:
                tipo_emoji = ">>>" if trans[3] == 'compra' else "<<<"
                info_cripto = criptomonedas.obtener_info_cripto(trans[4])
                nombre_cripto = info_cripto['nombre'] if info_cripto else trans[4]
                cantidad_fmt = criptomonedas.formatear_cantidad_cripto(trans[5], trans[4])
                
                print(f"\n{tipo_emoji} ID: {trans[0]} | Ciclo #{trans[1]} | {trans[2]}")
                print(f"   {trans[3].upper()}: {cantidad_fmt} {nombre_cripto} ({trans[4]})")
                print(f"   Precio: ${trans[6]:.4f} | Monto FIAT: ${trans[7]:.2f}")
                print("-" * 60)
        
    except sqlite3.Error as e:
        print(f"Error al consultar transacciones: {e}")
    
    input("\nPresiona Enter para continuar...")

def transferir_capital_a_ciclo_activo():
    """Transfiere todo el capital de ciclos anteriores al ciclo activo."""
    print("\n" + "=" * 60)
    print("TRANSFERIR CAPITAL AL CICLO ACTIVO")
    print("=" * 60)
    
    ciclo_activo = obtener_ciclo_activo()
    
    if ciclo_activo is None:
        print("\nError: No hay un ciclo activo.")
        print("   Debes crear un ciclo desde el Modulo Operador primero.")
        input("\nPresiona Enter para continuar...")
        return
    
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cripto,
                   SUM(CASE WHEN tipo = 'compra' THEN cantidad_cripto ELSE -cantidad_cripto END) as cantidad,
                   SUM(CASE WHEN tipo = 'compra' THEN monto_fiat ELSE -monto_fiat END) as valor_fiat
            FROM transacciones 
            WHERE ciclo_id != ?
            GROUP BY cripto
            HAVING cantidad > 0.0001
        """, (ciclo_activo,))
        
        criptos_otros = cursor.fetchall()
        
        if not criptos_otros:
            print("\nNo hay capital en ciclos anteriores para transferir.")
            conn.close()
            input("\nPresiona Enter para continuar...")
            return
        
        print(f"\nCapital disponible en ciclos anteriores:")
        total_transferir = 0
        
        for cripto_data in criptos_otros:
            cripto = cripto_data[0]
            cantidad = cripto_data[1]
            valor = cripto_data[2]
            total_transferir += valor
            
            info_cripto = criptomonedas.obtener_info_cripto(cripto)
            nombre = info_cripto['nombre'] if info_cripto else cripto
            cantidad_fmt = criptomonedas.formatear_cantidad_cripto(cantidad, cripto)
            costo_promedio = valor / cantidad if cantidad > 0 else 0
            
            print(f"\n   {nombre} ({cripto}):")
            print(f"   Cantidad: {cantidad_fmt}")
            print(f"   Valor: ${valor:.2f}")
            print(f"   Costo promedio: ${costo_promedio:.4f}")
        
        print(f"\n   TOTAL A TRANSFERIR: ${total_transferir:.2f}")
        print(f"\nDestino: Ciclo activo #{ciclo_activo}")
        
        confirmacion = input(f"\nTransferir TODO este capital al ciclo #{ciclo_activo}? (s/n): ")
        
        if confirmacion.lower() not in ['s', 'si']:
            print("Transferencia cancelada.")
            conn.close()
            input("\nPresiona Enter para continuar...")
            return
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transferencias_exitosas = 0
        
        for cripto_data in criptos_otros:
            cripto = cripto_data[0]
            cantidad = cripto_data[1]
            valor = cripto_data[2]
            costo_promedio = valor / cantidad if cantidad > 0 else 0
            
            cursor.execute("""
                INSERT INTO transacciones 
                (ciclo_id, fecha, tipo, cripto, cantidad_cripto, precio_unitario, comision_pct, monto_fiat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ciclo_activo, fecha_actual, 'compra', cripto, cantidad, costo_promedio, 0, valor))
            
            transferencias_exitosas += 1
        
        conn.commit()
        conn.close()
        
        print(f"\nTransferencia exitosa!")
        print(f"{transferencias_exitosas} criptomoneda(s) transferida(s)")
        print(f"Total: ${total_transferir:.2f}")
        print(f"Ciclo destino: #{ciclo_activo}")
        
    except sqlite3.Error as e:
        print(f"Error al transferir capital: {e}")
    
    input("\nPresiona Enter para continuar...")

def mostrar_menu_boveda():
    """Muestra el sub-menu de gestion de boveda."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("GESTION DE BOVEDA")
        print("=" * 60)
        print("[1] Consultar Estado de la Boveda")
        print("[2] Fondear Boveda (Registrar Compra)")
        print("[3] Ver Historial de Transacciones")
        print("[4] Transferir Capital al Ciclo Activo")
        print("[5] Volver al Menu Principal")
        print("=" * 60)
        opcion = input("Selecciona una opcion: ")

        if opcion == '1':
            consultar_boveda()
            input("\nPresiona Enter para volver...")
        elif opcion == '2':
            fondear_boveda()
        elif opcion == '3':
            ver_historial_transacciones()
        elif opcion == '4':
            transferir_capital_a_ciclo_activo()
        elif opcion == '5':
            break
        else:
            input("\nOpcion no valida. Presiona Enter...")
