# -*- coding: utf-8 -*-
import sqlite3
import os
import shutil
from datetime import datetime

# Crear directorios necesarios
DIRECTORIO_BACKUPS = 'backups'
DIRECTORIO_EXPORTS = 'exports'

def crear_directorios():
    """Crea los directorios necesarios si no existen."""
    if not os.path.exists(DIRECTORIO_BACKUPS):
        os.makedirs(DIRECTORIO_BACKUPS)
        print(f"✅ Directorio '{DIRECTORIO_BACKUPS}/' creado.")
    
    if not os.path.exists(DIRECTORIO_EXPORTS):
        os.makedirs(DIRECTORIO_EXPORTS)
        print(f"✅ Directorio '{DIRECTORIO_EXPORTS}/' creado.")

def crear_base_de_datos():
    """Crea la base de datos y las tablas si no existen (Esquema v3.0)."""
    try:
        crear_directorios()
        
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()

        # Tabla de ciclos (v3.0)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ciclos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_inicio TEXT NOT NULL,
                fecha_fin TEXT,
                cripto TEXT DEFAULT 'USDT',
                inversion_inicial REAL DEFAULT 0,
                ganancia_neta_total REAL DEFAULT 0,
                estado TEXT NOT NULL CHECK(estado IN ('activo', 'completado', 'temporal')),
                dias_planificados INTEGER DEFAULT 15
            )
        ''')

        # Tabla de dias_operacion (NUEVA v3.0)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dias_operacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER NOT NULL,
                numero_dia INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                capital_inicial REAL DEFAULT 0,
                capital_final REAL DEFAULT 0,
                ganancia_dia REAL DEFAULT 0,
                num_ventas INTEGER DEFAULT 0,
                precio_operacion REAL DEFAULT 0,
                estado TEXT NOT NULL CHECK(estado IN ('abierto', 'cerrado')),
                FOREIGN KEY (ciclo_id) REFERENCES ciclos (id),
                UNIQUE(ciclo_id, numero_dia)
            )
        ''')

        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        ''')

        # Tabla de transacciones (v3.0)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ciclo_id INTEGER NOT NULL,
                dia_id INTEGER,
                fecha TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('compra', 'venta')),
                cripto TEXT NOT NULL,
                cantidad_cripto REAL NOT NULL CHECK(cantidad_cripto > 0),
                precio_unitario REAL NOT NULL CHECK(precio_unitario > 0),
                precio_venta_real REAL DEFAULT 0,
                comision_pct REAL NOT NULL CHECK(comision_pct >= 0),
                monto_fiat REAL DEFAULT 0,
                FOREIGN KEY (ciclo_id) REFERENCES ciclos (id),
                FOREIGN KEY (dia_id) REFERENCES dias_operacion (id)
            )
        ''')

        # Tabla de APIs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apis_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plataforma TEXT NOT NULL,
                cripto TEXT NOT NULL,
                api_key TEXT,
                api_secret TEXT,
                comision_compra REAL DEFAULT 0,
                comision_venta REAL DEFAULT 0,
                activo INTEGER DEFAULT 1,
                UNIQUE(plataforma, cripto)
            )
        ''')

        # Insertar valores por defecto
        default_configs = [
            ('comision_defecto', '0.35'),
            ('ganancia_defecto', '2.0'),
            ('cripto_defecto', 'USDT'),
            ('ventas_minimas_dia', '3'),
            ('ventas_maximas_dia', '5'),
            ('dias_ciclo_defecto', '15')
        ]
        cursor.executemany("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)", default_configs)

        conn.commit()
        conn.close()
        
        print("=" * 60)
        print("✅ Base de datos verificada/creada con éxito (Esquema v3.0)")
        print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"❌ Error al crear la base de datos: {e}")

# ... (El resto de las funciones de database.py como hacer_backup_db, etc., van aquí.
# No las repito por brevedad, ya que no cambian, pero asegúrate de tenerlas en tu archivo)

def verificar_integridad_db():
    """Verifica la integridad de la base de datos."""
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # Verificar integridad
        cursor.execute("PRAGMA integrity_check")
        resultado = cursor.fetchone()
        
        if resultado[0] == 'ok':
            print("\n✅ Integridad de la base de datos: OK")
        else:
            print(f"\n⚠️  Problema de integridad: {resultado[0]}")
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM ciclos")
        num_ciclos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transacciones")
        num_transacciones = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM apis_config")
        num_apis = cursor.fetchone()[0]
        
        # Tamaño del archivo
        size = os.path.getsize('arbitraje.db')
        size_kb = size / 1024
        
        print(f"📊 Ciclos registrados: {num_ciclos}")
        print(f"📊 Transacciones registradas: {num_transacciones}")
        print(f"📊 APIs configuradas: {num_apis}")
        print(f"💾 Tamaño de la base de datos: {size_kb:.2f} KB")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Error al verificar integridad: {e}")

def hacer_backup_db():
    """Crea una copia de seguridad de la base de datos en el directorio backups/."""
    try:
        crear_directorios()
        
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_backup = f"{DIRECTORIO_BACKUPS}/arbitraje_backup_{fecha_actual}.db"
        
        shutil.copy2('arbitraje.db', nombre_backup)
        
        size = os.path.getsize(nombre_backup)
        size_kb = size / 1024
        
        print(f"\n✅ Backup creado exitosamente")
        print(f"📁 Ubicación: {nombre_backup}")
        print(f"💾 Tamaño: {size_kb:.2f} KB")
        
        limpiar_backups_antiguos()
        
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")

def limpiar_backups_antiguos(max_backups=10):
    """Mantiene solo los últimos N backups."""
    try:
        if not os.path.exists(DIRECTORIO_BACKUPS):
            return
        
        backups = [f for f in os.listdir(DIRECTORIO_BACKUPS) if f.endswith('.db')]
        backups.sort(reverse=True)
        
        if len(backups) > max_backups:
            for backup in backups[max_backups:]:
                ruta_completa = os.path.join(DIRECTORIO_BACKUPS, backup)
                os.remove(ruta_completa)
            print(f"🗑️  {len(backups) - max_backups} backups antiguos eliminados.")
    except Exception as e:
        print(f"⚠️  Error al limpiar backups: {e}")

def listar_backups():
    """Lista todos los backups disponibles."""
    try:
        crear_directorios()
        
        if not os.path.exists(DIRECTORIO_BACKUPS):
            print("\n⚠️  No hay backups disponibles.")
            return []
        
        backups = [f for f in os.listdir(DIRECTORIO_BACKUPS) if f.endswith('.db')]
        
        if not backups:
            print("\n⚠️  No hay backups disponibles.")
            return []
        
        backups.sort(reverse=True)
        
        print("\n" + "=" * 60)
        print("BACKUPS DISPONIBLES")
        print("=" * 60)
        
        backups_info = []
        for i, backup in enumerate(backups, 1):
            ruta_completa = os.path.join(DIRECTORIO_BACKUPS, backup)
            size = os.path.getsize(ruta_completa)
            size_kb = size / 1024
            fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
            
            print(f"\n[{i}] {backup}")
            print(f"    📅 Fecha: {fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    💾 Tamaño: {size_kb:.2f} KB")
            
            backups_info.append({
                'numero': i,
                'nombre': backup,
                'ruta': ruta_completa,
                'fecha': fecha_modificacion,
                'size': size_kb
            })
        
        print("=" * 60)
        return backups_info
        
    except Exception as e:
        print(f"❌ Error al listar backups: {e}")
        return []

def restaurar_backup():
    """Restaura una base de datos desde un backup."""
    print("\n" + "=" * 60)
    print("RESTAURAR BASE DE DATOS DESDE BACKUP")
    print("=" * 60)
    
    backups = listar_backups()
    
    if not backups:
        return
    
    print("\n⚠️  ADVERTENCIA: Esta acción sobrescribirá la base de datos actual.")
    print("   Se creará un backup automático de la BD actual antes de restaurar.")
    
    try:
        seleccion = input("\nSelecciona el número del backup a restaurar (0 para cancelar): ")
        
        if seleccion == '0':
            print("❌ Operación cancelada.")
            return
        
        num_backup = int(seleccion)
        
        if num_backup < 1 or num_backup > len(backups):
            print("❌ Número de backup inválido.")
            return
        
        backup_seleccionado = backups[num_backup - 1]
        
        print(f"\n📋 Vas a restaurar:")
        print(f"   {backup_seleccionado['nombre']}")
        print(f"   Fecha: {backup_seleccionado['fecha'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        confirmacion = input("\n¿Estás seguro? Escribe 'RESTAURAR' para confirmar: ")
        
        if confirmacion.upper() != 'RESTAURAR':
            print("❌ Operación cancelada.")
            return
        
        print("\n🔄 Creando backup de seguridad de la BD actual...")
        fecha_seguridad = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_seguridad = f"{DIRECTORIO_BACKUPS}/pre_restauracion_{fecha_seguridad}.db"
        shutil.copy2('arbitraje.db', backup_seguridad)
        print(f"✅ Backup de seguridad creado: {backup_seguridad}")
        
        print(f"\n🔄 Restaurando {backup_seleccionado['nombre']}...")
        shutil.copy2(backup_seleccionado['ruta'], 'arbitraje.db')
        
        print("\n✅ ¡Base de datos restaurada exitosamente!")
        print("💡 TIP: Reinicia el programa para que los cambios surtan efecto.")
        
    except ValueError:
        print("❌ Error: Debes ingresar un número.")
    except Exception as e:
        print(f"❌ Error al restaurar backup: {e}")

if __name__ == '__main__':
    crear_base_de_datos()
    verificar_integridad_db()
