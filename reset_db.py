# reset_db.py
# -*- coding: utf-8 -*-
import os
import sqlite3
import database # Importamos tu módulo para reusar la función de creación

DB_FILE = "arbitraje.db"

def reset_database():
    """
    Script de alto riesgo para eliminar y recrear la base de datos.
    Pide una confirmación explícita para evitar ejecuciones accidentales.
    """
    print("=" * 60)
    print("⚠️  ¡ADVERTENCIA DE ACCIÓN DESTRUCTIVA! ⚠️")
    print("=" * 60)
    print(f"Estás a punto de BORRAR COMPLETAMENTE la base de datos '{DB_FILE}'.")
    print("TODA la información de ciclos, transacciones y configuración se perderá.")
    print("Esta acción es IRREVERSIBLE.")
    print("-" * 60)
    
    confirmacion = input("Para continuar, escribe la palabra 'RESET' en mayúsculas: ")
    
    if confirmacion == "RESET":
        print(f"\nConfirmación aceptada. Procediendo a reiniciar '{DB_FILE}'...")
        try:
            # 1. Eliminar el archivo de la base de datos si existe
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                print(f"✅ Archivo '{DB_FILE}' eliminado.")
            
            # 2. Llamar a la función de creación para generar una base limpia
            print("▶️  Creando una nueva base de datos desde cero...")
            database.crear_base_de_datos() # Reutilizamos tu código para crearla
            
            print("\n" + "=" * 60)
            print("🎉 ¡REINICIO COMPLETADO!")
            print("La base de datos está limpia y lista para un nuevo comienzo.")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Ocurrió un error durante el reinicio: {e}")
    else:
        print("\n❌ Confirmación incorrecta. El reinicio ha sido CANCELADO.")
        print("La base de datos no ha sido modificada.")

if __name__ == '__main__':
    reset_database()
