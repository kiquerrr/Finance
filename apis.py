# -*- coding: utf-8 -*-
import sqlite3
import os

class GestorAPIs:
    def __init__(self):
        self.conn = sqlite3.connect('arbitraje.db')
    
    def agregar_api(self, plataforma, cripto, api_key, api_secret, 
                    comision_compra, comision_venta):
        """Agrega o actualiza configuración de API."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO apis_config 
                (plataforma, cripto, api_key, api_secret, comision_compra, comision_venta, activo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (plataforma, cripto, api_key, api_secret, comision_compra, comision_venta))
            self.conn.commit()
            print(f"✅ API de {plataforma} para {cripto} configurada exitosamente.")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al guardar API: {e}")
            return False
    
    def obtener_api(self, plataforma, cripto):
        """Obtiene configuración de una API."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM apis_config 
                WHERE plataforma = ? AND cripto = ? AND activo = 1
            """, (plataforma, cripto))
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error al obtener API: {e}")
            return None
    
    def listar_apis(self):
        """Lista todas las APIs configuradas."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM apis_config WHERE activo = 1 ORDER BY plataforma, cripto")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error al listar APIs: {e}")
            return []
    
    def consultar_tasa_binance(self, cripto):
        """Consulta tasa actual desde Binance API (requiere requests)."""
        try:
            import requests
            # API pública de Binance (no requiere autenticación)
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={cripto}USDT"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                precio = float(data['price'])
                return precio
            else:
                print(f"⚠️  Error HTTP: {response.status_code}")
                return None
        except ImportError:
            print("⚠️  El módulo 'requests' no está instalado.")
            print("   Instálalo con: pip install requests")
            return None
        except Exception as e:
            print(f"❌ Error al consultar API: {e}")
            return None
    
    def probar_conexion(self, plataforma, cripto):
        """Prueba la conexión con una API."""
        print(f"\n🔍 Probando conexión con {plataforma} para {cripto}...")
        
        if plataforma.lower() == 'binance':
            tasa = self.consultar_tasa_binance(cripto)
            if tasa:
                print(f"✅ Conexión exitosa con Binance!")
                print(f"💱 Precio actual de {cripto}/USDT: ${tasa:.4f}")
                return True
            else:
                print(f"❌ No se pudo conectar con Binance")
                return False
        else:
            print(f"⚠️  Plataforma {plataforma} aún no implementada.")
            print(f"   Por ahora solo Binance está disponible.")
            return False
    
    def actualizar_todas_tasas(self):
        """Actualiza tasas de todas las APIs configuradas."""
        apis = self.listar_apis()
        
        if not apis:
            print("\n⚠️  No hay APIs configuradas.")
            return
        
        print("\n" + "=" * 60)
        print("🔄 ACTUALIZANDO TASAS DESDE APIs")
        print("=" * 60)
        
        exitos = 0
        errores = 0
        
        for api in apis:
            plataforma = api[1]
            cripto = api[2]
            
            print(f"\n🔍 {plataforma} - {cripto}...", end=" ")
            
            if plataforma.lower() == 'binance':
                tasa = self.consultar_tasa_binance(cripto)
                if tasa:
                    print(f"✅ ${tasa:.4f}")
                    exitos += 1
                else:
                    print(f"❌ Error")
                    errores += 1
            else:
                print(f"⚠️  No implementada")
                errores += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Exitosas: {exitos} | ❌ Errores: {errores}")
        print("=" * 60)
    
    def eliminar_api(self, api_id):
        """Desactiva una API."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE apis_config SET activo = 0 WHERE id = ?", (api_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al eliminar API: {e}")
            return False
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


def menu_apis():
    """Menú principal de gestión de APIs."""
    gestor = GestorAPIs()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("⚙️  CONFIGURACIÓN DE APIs Y PLATAFORMAS")
        print("=" * 60)
        print("[1] Agregar/Editar API de Plataforma")
        print("[2] Ver APIs Configuradas")
        print("[3] Probar Conexión con API")
        print("[4] Actualizar Tasas desde APIs")
        print("[5] Eliminar API")
        print("[6] Volver al Menú Principal")
        print("=" * 60)
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            agregar_api_interactivo(gestor)
        elif opcion == '2':
            listar_apis_configuradas(gestor)
        elif opcion == '3':
            probar_conexion_interactivo(gestor)
        elif opcion == '4':
            gestor.actualizar_todas_tasas()
            input("\nPresiona Enter para continuar...")
        elif opcion == '5':
            eliminar_api_interactivo(gestor)
        elif opcion == '6':
            break
        else:
            input("\n❌ Opción no válida. Presiona Enter...")


def agregar_api_interactivo(gestor):
    """Interfaz para agregar API."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("➕ AGREGAR/EDITAR CONFIGURACIÓN DE API")
    print("=" * 60)
    
    print("\n📱 Plataformas disponibles:")
    print("[1] Binance (con API pública funcional)")
    print("[2] Kraken (próximamente)")
    print("[3] Coinbase (próximamente)")
    print("[4] Otra (manual)")
    
    opcion_plat = input("\nSelecciona plataforma: ")
    
    if opcion_plat == '1':
        plataforma = 'Binance'
    elif opcion_plat == '2':
        plataforma = 'Kraken'
    elif opcion_plat == '3':
        plataforma = 'Coinbase'
    elif opcion_plat == '4':
        plataforma = input("  Nombre de la plataforma: ")
    else:
        print("❌ Opción inválida.")
        input("\nPresiona Enter para continuar...")
        return
    
    cripto = input("\n💰 Símbolo de cripto (ej: BTC, ETH, USDT): ").upper()
    
    print("\n🔐 Credenciales de API:")
    print("💡 Para Binance con API pública, puedes dejar en blanco.")
    api_key = input("API Key (Enter para omitir): ").strip()
    api_secret = input("API Secret (Enter para omitir): ").strip()
    
    try:
        print("\n💸 Comisiones:")
        comision_compra = float(input("Comisión de compra % (ej: 0.35): "))
        comision_venta = float(input("Comisión de venta % (ej: 0.35): "))
        
        # Guardar
        if gestor.agregar_api(plataforma, cripto, api_key, api_secret, 
                             comision_compra, comision_venta):
            
            # Probar conexión
            if plataforma.lower() == 'binance':
                print("\n🔍 Probando conexión automáticamente...")
                gestor.probar_conexion(plataforma, cripto)
        
    except ValueError:
        print("❌ Error: Las comisiones deben ser números.")
    
    input("\nPresiona Enter para continuar...")


def listar_apis_configuradas(gestor):
    """Muestra todas las APIs configuradas."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    apis = gestor.listar_apis()
    
    print("=" * 60)
    print("📋 APIs CONFIGURADAS")
    print("=" * 60)
    
    if not apis:
        print("\n⚠️  No hay APIs configuradas.")
        print("💡 Usa la opción [1] para agregar una API.")
    else:
        for i, api in enumerate(apis, 1):
            print(f"\n🔧 [{i}] {api[1]} - {api[2]}")
            print(f"    API Key: {'✅ Configurada' if api[3] else '⚠️  No configurada'}")
            print(f"    Comisión compra: {api[5]}%")
            print(f"    Comisión venta: {api[6]}%")
            print(f"    Estado: {'✅ Activa' if api[7] else '❌ Inactiva'}")
    
    print("=" * 60)
    input("\nPresiona Enter para continuar...")


def probar_conexion_interactivo(gestor):
    """Interfaz para probar conexión."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    apis = gestor.listar_apis()
    
    print("=" * 60)
    print("🔍 PROBAR CONEXIÓN CON API")
    print("=" * 60)
    
    if not apis:
        print("\n⚠️  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n📋 APIs disponibles:")
    for i, api in enumerate(apis, 1):
        print(f"[{i}] {api[1]} - {api[2]}")
    
    try:
        opcion = int(input("\nSelecciona API a probar (0 para cancelar): "))
        
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(apis):
            api_seleccionada = apis[opcion - 1]
            gestor.probar_conexion(api_seleccionada[1], api_seleccionada[2])
        else:
            print("❌ Opción inválida.")
    except ValueError:
        print("❌ Debes ingresar un número.")
    
    input("\nPresiona Enter para continuar...")


def eliminar_api_interactivo(gestor):
    """Interfaz para eliminar API."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    apis = gestor.listar_apis()
    
    print("=" * 60)
    print("🗑️  ELIMINAR CONFIGURACIÓN DE API")
    print("=" * 60)
    
    if not apis:
        print("\n⚠️  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n📋 APIs disponibles:")
    for i, api in enumerate(apis, 1):
        print(f"[{i}] {api[1]} - {api[2]}")
    
    try:
        opcion = int(input("\nSelecciona API a eliminar (0 para cancelar): "))
        
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(apis):
            api_seleccionada = apis[opcion - 1]
            print(f"\n⚠️  Vas a eliminar: {api_seleccionada[1]} - {api_seleccionada[2]}")
            confirmacion = input("¿Estás seguro? (s/n): ")
            
            if confirmacion.lower() in ['s', 'si', 'sí']:
                if gestor.eliminar_api(api_seleccionada[0]):
                    print("✅ API eliminada (desactivada).")
                else:
                    print("❌ Error al eliminar API.")
        else:
            print("❌ Opción inválida.")
    except ValueError:
        print("❌ Debes ingresar un número.")
    
    input("\nPresiona Enter para continuar...")
