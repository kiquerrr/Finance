import sqlite3

def crear_base_de_datos():
    """Crea la base de datos y las tablas si no existen."""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()

    # ... (las tablas 'ciclos' y 'configuracion' no cambian)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ciclos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT,
            inversion_total REAL DEFAULT 0,
            ganancia_neta_total REAL DEFAULT 0,
            estado TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    ''')

    # <-- TABLA MODIFICADA
    # Hemos añadido 'precio_venta_real' para guardar el precio de la operación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ciclo_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            cantidad_cripto REAL NOT NULL,
            precio_unitario REAL NOT NULL,
            precio_venta_real REAL DEFAULT 0, -- <-- ¡NUEVA COLUMNA!
            comision_pct REAL NOT NULL,
            FOREIGN KEY (ciclo_id) REFERENCES ciclos (id)
        )
    ''')
    # NOTA: La columna 'ganancia_neta' se ha eliminado para calcularla siempre en tiempo real.

    print("[DB] Base de datos y tablas verificadas/creadas con éxito.")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    crear_base_de_datos()
