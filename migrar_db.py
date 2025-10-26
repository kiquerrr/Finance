# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime

def migrar_base_datos_v3():
    """Migra la base de datos a la version 3.0 con ciclos globales y dias."""
    print("=" * 60)
    print("MIGRACION A VERSION 3.0 - CICLOS GLOBALES Y DIAS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        
        # 1. Crear tabla dias_operacion
        print("\n1. Creando tabla dias_operacion...")
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
        print("   Tabla dias_operacion creada.")
        
        # 2. Agregar columnas a ciclos
        print("\n2. Actualizando tabla ciclos...")
        cursor.execute("PRAGMA table_info(ciclos)")
        columnas_ciclos = [col[1] for col in cursor.fetchall()]
        
        if 'dias_planificados' not in columnas_ciclos:
            cursor.execute("ALTER TABLE ciclos ADD COLUMN dias_planificados INTEGER DEFAULT 15")
            print("   Columna dias_planificados agregada.")
        
        if 'inversion_inicial' not in columnas_ciclos:
            cursor.execute("ALTER TABLE ciclos ADD COLUMN inversion_inicial REAL DEFAULT 0")
            print("   Columna inversion_inicial agregada.")
        
        # 3. Agregar columna dia_id a transacciones
        print("\n3. Actualizando tabla transacciones...")
        cursor.execute("PRAGMA table_info(transacciones)")
        columnas_trans = [col[1] for col in cursor.fetchall()]
        
        if 'dia_id' not in columnas_trans:
            cursor.execute("ALTER TABLE transacciones ADD COLUMN dia_id INTEGER")
            print("   Columna dia_id agregada.")
        
        # 4. Agregar nuevas configuraciones
        print("\n4. Agregando configuraciones nuevas...")
        cursor.execute("""
            INSERT OR IGNORE INTO configuracion (clave, valor) 
            VALUES ('ventas_minimas_dia', '3')
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO configuracion (clave, valor) 
            VALUES ('ventas_maximas_dia', '5')
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO configuracion (clave, valor) 
            VALUES ('dias_ciclo_defecto', '15')
        """)
        print("   Configuraciones agregadas.")
        
        # 5. Migrar ciclos existentes
        print("\n5. Migrando ciclos existentes...")
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        ciclos_activos = cursor.fetchall()
        
        for ciclo in ciclos_activos:
            ciclo_id = ciclo[0]
            
            # Calcular capital del ciclo
            cursor.execute("""
                SELECT SUM(CASE WHEN tipo = 'compra' THEN monto_fiat ELSE 0 END)
                FROM transacciones
                WHERE ciclo_id = ?
            """, (ciclo_id,))
            
            inversion = cursor.fetchone()[0] or 0
            
            # Actualizar ciclo
            cursor.execute("""
                UPDATE ciclos
                SET dias_planificados = 15, inversion_inicial = ?
                WHERE id = ?
            """, (inversion, ciclo_id))
            
            # Crear dia inicial para ciclos activos
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO dias_operacion 
                (ciclo_id, numero_dia, fecha, capital_inicial, capital_final, estado)
                VALUES (?, 1, ?, ?, ?, 'abierto')
            """, (ciclo_id, fecha_actual, inversion, inversion))
            
            print(f"   Ciclo #{ciclo_id} migrado con inversion de ${inversion:.2f}")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("MIGRACION COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nCambios aplicados:")
        print("  - Tabla dias_operacion creada")
        print("  - Ciclos actualizados con dias_planificados")
        print("  - Transacciones preparadas para dia_id")
        print("  - Configuraciones de ventas agregadas")
        print("\nPuedes ejecutar: python3 main.py")
        
    except sqlite3.Error as e:
        print(f"\nError durante la migracion: {e}")
        print("\nSi el error persiste:")
        print("1. Hacer backup: cp arbitraje.db arbitraje_backup.db")
        print("2. Borrar BD: rm arbitraje.db")
        print("3. Ejecutar: python3 main.py")

if __name__ == '__main__':
    migrar_base_datos_v3()
