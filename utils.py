# utils.py
import sqlite3

def confirmar_accion(mensaje):
    """
    Función reutilizable para pedir confirmación (s/n) al usuario.
    Maneja varias entradas y vuelve a preguntar si la respuesta no es válida.
    Devuelve True para 'sí' y False para 'no'.
    """
    while True:
        # Añadimos .strip() para eliminar espacios y .lower() para convertir a minúsculas
        respuesta = input(f"{mensaje} (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí']:
            return True
        elif respuesta in ['n', 'no']:
            return False
        else:
            print("  Error: Respuesta no válida. Por favor, introduce 's' o 'n'.")

def obtener_ciclo_activo_id():
    """
    Busca en la base de datos un ciclo con estado 'activo'.
    Devuelve el ID del ciclo si lo encuentra, de lo contrario devuelve None.
    """
    conn = None
    try:
        conn = sqlite3.connect('arbitraje.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM ciclos WHERE estado = 'activo'")
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"Error de base de datos al obtener ciclo activo: {e}")
        return None
    finally:
        if conn:
            conn.close()
