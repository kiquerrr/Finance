"""
=============================================================================
INICIALIZACIÓN DE BASE DE DATOS
=============================================================================
Crea la base de datos SOLO LA PRIMERA VEZ
Después, toda la gestión se hace desde el módulo de Mantenimiento
"""

import sqlite3
import os
from datetime import datetime


def inicializar_base_datos(db_path='arbitraje.db'):
    """
    Crea todas las tablas necesarias para el sistema
    Solo se ejecuta la PRIMERA VEZ que se instala el sistema
    """
    
    print("\n🔧 Inicializando base de datos del sistema...")
    print("   (Esto solo ocurre en la primera instalación)\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ===================================================================
        # 1. TABLA DE CONFIGURACIÓN
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY,
                comision_default REAL DEFAULT 0.35,
                ganancia_neta_default REAL DEFAULT 2.0,
                modo_comision TEXT DEFAULT 'manual',
                api_comision_activa INTEGER DEFAULT 0,
                limite_ventas_min INTEGER DEFAULT 3,
                limite_ventas_max INTEGER DEFAULT 5,
                actualizado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar config por defecto
        cursor.execute("SELECT COUNT(*) FROM config")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO config (id, comision_default, ganancia_neta_default)
                VALUES (1, 0.35, 2.0)
            """)
            print("   ✓ Configuración inicial")
        
        # ===================================================================
        # 2. TABLA DE CRIPTOMONEDAS
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS criptomonedas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                simbolo TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL,
                descripcion TEXT
            )
        """)
        
        # Insertar criptomonedas por defecto
        criptos_default = [
            ('Tether', 'USDT', 'stablecoin', 'Moneda estable vinculada al dolar'),
            ('USD Coin', 'USDC', 'stablecoin', 'Moneda estable respaldada por dolares'),
            ('Bitcoin', 'BTC', 'criptomoneda', 'La primera y mas conocida criptomoneda'),
            ('Ethereum', 'ETH', 'criptomoneda', 'Plataforma de contratos inteligentes'),
            ('Binance Coin', 'BNB', 'criptomoneda', 'Token nativo de Binance'),
            ('Dai', 'DAI', 'stablecoin', 'Stablecoin descentralizada')
        ]
        
        for nombre, simbolo, tipo, desc in criptos_default:
            cursor.execute("""
                INSERT OR IGNORE INTO criptomonedas (nombre, simbolo, tipo, descripcion)
                VALUES (?, ?, ?, ?)
            """, (nombre, simbolo, tipo, desc))
        
        print("   ✓ Criptomonedas (6 disponibles)")
        
        # ===================================================================
        # 3. TABLA DE CICLOS
        # ===================================================================
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
        print("   ✓ Tabla de ciclos")
        
        # ===================================================================
        # 4. TABLA DE DÍAS
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER NOT NULL,
                numero_dia INTEGER NOT NULL,
                fecha DATE DEFAULT (date('now')),
                capital_inicial REAL NOT NULL,
                capital_final REAL DEFAULT 0,
                efectivo_recibido REAL DEFAULT 0,
                comisiones_pagadas REAL DEFAULT 0,
                ganancia_bruta REAL DEFAULT 0,
                ganancia_neta REAL DEFAULT 0,
                cripto_operada_id INTEGER,
                precio_publicado REAL,
                estado TEXT DEFAULT 'abierto',
                fecha_cierre TIMESTAMP,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
                FOREIGN KEY (cripto_operada_id) REFERENCES criptomonedas(id)
            )
        """)
        print("   ✓ Tabla de días")
        
        # ===================================================================
        # 5. TABLA DE BÓVEDA
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boveda_ciclo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER NOT NULL,
                cripto_id INTEGER NOT NULL,
                cantidad REAL NOT NULL DEFAULT 0,
                precio_promedio REAL NOT NULL,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
                FOREIGN KEY (cripto_id) REFERENCES criptomonedas(id),
                UNIQUE(ciclo_id, cripto_id)
            )
        """)
        print("   ✓ Tabla de bóveda")
        
        # ===================================================================
        # 6. TABLA DE COMPRAS
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER NOT NULL,
                cripto_id INTEGER NOT NULL,
                cantidad REAL NOT NULL,
                monto_usd REAL NOT NULL,
                tasa REAL NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
                FOREIGN KEY (cripto_id) REFERENCES criptomonedas(id)
            )
        """)
        print("   ✓ Tabla de compras")
        
        # ===================================================================
        # 7. TABLA DE VENTAS
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia_id INTEGER NOT NULL,
                cripto_id INTEGER NOT NULL,
                cantidad REAL NOT NULL,
                precio_unitario REAL NOT NULL,
                costo_total REAL,
                monto_venta REAL,
                comision REAL,
                efectivo_recibido REAL,
                ganancia_bruta REAL,
                ganancia_neta REAL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dia_id) REFERENCES dias(id),
                FOREIGN KEY (cripto_id) REFERENCES criptomonedas(id)
            )
        """)
        print("   ✓ Tabla de ventas")
        
        # ===================================================================
        # 8. TABLA DE EFECTIVO EN BANCO
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS efectivo_banco (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER NOT NULL,
                dia_id INTEGER,
                monto REAL NOT NULL,
                concepto TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
                FOREIGN KEY (dia_id) REFERENCES dias(id)
            )
        """)
        print("   ✓ Tabla de efectivo (pool de reinversión)")
        
        # ===================================================================
        # 9. TABLA DE APIS
        # ===================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apis_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                plataforma TEXT NOT NULL,
                api_key TEXT,
                api_secret TEXT,
                activa INTEGER DEFAULT 1,
                tipo TEXT DEFAULT 'trading',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_actualizacion TIMESTAMP
            )
        """)
        print("   ✓ Tabla de configuración de APIs")
        
        # ===================================================================
        # 10. ÍNDICES PARA OPTIMIZACIÓN
        # ===================================================================
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_dias_ciclo ON dias(ciclo_id)",
            "CREATE INDEX IF NOT EXISTS idx_dias_estado ON dias(estado)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_dia ON ventas(dia_id)",
            "CREATE INDEX IF NOT EXISTS idx_boveda_ciclo ON boveda_ciclo(ciclo_id, cripto_id)",
            "CREATE INDEX IF NOT EXISTS idx_efectivo_ciclo ON efectivo_banco(ciclo_id)",
            "CREATE INDEX IF NOT EXISTS idx_compras_ciclo ON compras(ciclo_id)",
            "CREATE INDEX IF NOT EXISTS idx_ciclos_estado ON ciclos(estado)"
        ]
        
        for indice in indices:
            cursor.execute(indice)
        
        print("   ✓ Índices de optimización")
        
        # ===================================================================
        # COMMIT
        # ===================================================================
        conn.commit()
        
        print(f"\n✅ Base de datos creada correctamente")
        print(f"   Ubicación: {os.path.abspath(db_path)}")
        print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al inicializar: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def primera_instalacion():
    """
    Instalación inicial del sistema
    Se ejecuta UNA SOLA VEZ
    """
    
    print("\n" + "="*60)
    print("INSTALACIÓN INICIAL DEL SISTEMA")
    print("="*60)
    print("\nBienvenido al Sistema de Gestión de Arbitraje P2P v2.0")
    print("\nEsta instalación creará:")
    print("  • Base de datos con todas las tablas")
    print("  • Configuración por defecto")
    print("  • 6 criptomonedas disponibles")
    print("  • Directorios necesarios (logs, backups, exports)")
    
    input("\nPresiona Enter para continuar con la instalación...")
    
    # Crear directorios
    print("\n📁 Creando estructura de directorios...")
    for directorio in ['logs', 'backups', 'exports']:
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            print(f"   ✓ {directorio}/")
        else:
            print(f"   ✓ {directorio}/ (ya existe)")
    
    # Crear base de datos
    if inicializar_base_datos():
        print("\n" + "="*60)
        print("✅ INSTALACIÓN COMPLETADA CON ÉXITO")
        print("="*60)
        print("\nEl sistema está listo para usar.")
        print("\n💡 Recuerda:")
        print("   • Usa [5] Mantenimiento → [1] para crear backups")
        print("   • Usa [5] Mantenimiento → [5] para verificar integridad")
        print("   • Usa [5] Mantenimiento → [9] para optimizar la BD")
        print("\n" + "="*60)
        return True
    else:
        print("\n" + "="*60)
        print("❌ INSTALACIÓN FALLIDA")
        print("="*60)
        return False


def necesita_instalacion():
    """
    Verifica si el sistema necesita instalación inicial
    Solo verifica si existe el archivo de BD
    """
    return not os.path.exists('arbitraje.db')


def setup_inicial():
    """
    Función que se llama desde main.py
    
    SOLO verifica si existe la BD.
    Si no existe → Instala
    Si existe → No hace nada (confía en Mantenimiento para verificaciones)
    """
    
    if necesita_instalacion():
        return primera_instalacion()
    else:
        # BD existe, todo OK
        # Las verificaciones las hace el módulo de Mantenimiento
        return True


# ===================================================================
# EJECUCIÓN DIRECTA
# ===================================================================

if __name__ == "__main__":
    print("="*60)
    print("INSTALADOR DEL SISTEMA DE ARBITRAJE P2P")
    print("="*60)
    
    if necesita_instalacion():
        primera_instalacion()
    else:
        print("\n⚠️  La base de datos ya existe.")
        print("\nOpciones:")
        print("  [1] Ver información de la BD actual")
        print("  [2] Reinstalar (BORRARÁ TODOS LOS DATOS)")
        print("  [3] Salir")
        
        opcion = input("\nSelecciona (1-3): ").strip()
        
        if opcion == "1":
            print("\n📊 Información de la base de datos:")
            print(f"   Ubicación: {os.path.abspath('arbitraje.db')}")
            tamaño = os.path.getsize('arbitraje.db') / 1024
            print(f"   Tamaño: {tamaño:.2f} KB")
            
            # Contar registros
            conn = sqlite3.connect('arbitraje.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM ciclos")
            ciclos = cursor.fetchone()[0]
            print(f"   Ciclos: {ciclos}")
            
            cursor.execute("SELECT COUNT(*) FROM dias WHERE estado='cerrado'")
            dias = cursor.fetchone()[0]
            print(f"   Días operados: {dias}")
            
            cursor.execute("SELECT COUNT(*) FROM ventas")
            ventas = cursor.fetchone()[0]
            print(f"   Ventas: {ventas}")
            
            conn.close()
            
            print("\n✅ BD en buen estado")
            print("   Usa [5] Mantenimiento en el programa para verificaciones")
            
        elif opcion == "2":
            print("\n⚠️  ADVERTENCIA: Esto borrará TODOS los datos")
            confirmar = input("Escribe 'BORRAR' para confirmar: ").strip()
            
            if confirmar == "BORRAR":
                os.remove('arbitraje.db')
                print("✓ BD anterior eliminada")
                primera_instalacion()
            else:
                print("❌ Cancelado")
        else:
            print("Saliendo...")
