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
        print("   ✅ Tabla dias_operacion creada.")
        
        # 2. Agregar columnas a ciclos
        print("\n2. Actualizando tabla ciclos...")
        cursor.execute("PRAGMA table_info(ciclos)")
        columnas_ciclos = [col[1] for col in cursor.fetchall()]
        
        if 'dias_planificados' not in columnas_ciclos:
            cursor.execute("ALTER TABLE ciclos ADD COLUMN dias_planificados INTEGER DEFAULT 15")
            print("   ✅ Columna dias_planificados agregada.")
        
        if 'inversion_inicial' not in columnas_ciclos:
            cursor.execute("ALTER TABLE ciclos ADD COLUMN inversion_inicial REAL DEFAULT 0")
            print("   ✅ Columna inversion_inicial agregada.")
        
        # 3. Agregar columna dia_id a transacciones
        print("\n3. Actualizando tabla transacciones...")
        cursor.execute("PRAGMA table_info(transacciones)")
        columnas_trans = [col[1] for col in cursor.fetchall()]
        
        if 'dia_id' not in columnas_trans:
            cursor.execute("ALTER TABLE transacciones ADD COLUMN dia_id INTEGER")
            print("   ✅ Columna dia_id agregada.")
        
        # 4. Agregar nuevas configuraciones
        print("\n4. Agregando configuraciones nuevas...")
        default_configs = [
            ('ventas_minimas_dia', '3'),
            ('ventas_maximas_dia', '5'),
            ('dias_ciclo_defecto', '15')
        ]
        cursor.executemany("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)", default_configs)
        print("   ✅ Configuraciones agregadas.")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 MIGRACION COMPLETADA EXITOSAMENTE 🎉")
        print("=" * 60)
        print("\nCambios aplicados:")
        print("  - Tabla dias_operacion creada")
        print("  - Ciclos actualizados con dias_planificados e inversion_inicial")
        print("  - Transacciones actualizadas con dia_id")
        print("  - Configuraciones de ventas y días por ciclo agregadas")
        print("\n👉 Ahora puedes ejecutar el programa principal: python3 main.py")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error durante la migracion: {e}")
        print("\nSi el error persiste, considera hacer un backup y empezar con una BD nueva.")

if __name__ == '__main__':
    migrar_base_datos_v3()
