# -*- coding: utf-8 -*-
"""
=============================================================================
SCRIPT DE RESET DE BASE DE DATOS
=============================================================================
Para testing y desarrollo: Resetea la base de datos a estado inicial
ADVERTENCIA: Este script es DESTRUCTIVO - Solo para desarrollo/testing
=============================================================================
"""

import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from inicializar_bd import inicializar_base_datos
except ImportError:
    print("❌ Error: No se encuentra el módulo inicializar_bd.py")
    print("   Asegúrate de estar en el directorio correcto del proyecto")
    sys.exit(1)


DB_FILE = "arbitraje.db"
BACKUP_DIR = Path("backups")
LOGS_DIR = Path("logs")


def crear_backup_antes_reset():
    """Crea un backup de seguridad antes de resetear"""
    
    if not os.path.exists(DB_FILE):
        print("ℹ️  No hay base de datos para respaldar")
        return None
    
    # Crear directorio de backups si no existe
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"ANTES_RESET_{timestamp}.db"
    
    try:
        shutil.copy2(DB_FILE, backup_file)
        tamaño = backup_file.stat().st_size / 1024
        print(f"✅ Backup creado: {backup_file.name} ({tamaño:.1f} KB)")
        return backup_file
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return None


def limpiar_logs():
    """Limpia todos los archivos de log"""
    
    if not LOGS_DIR.exists():
        return
    
    logs_eliminados = 0
    for log_file in LOGS_DIR.glob("*.log"):
        try:
            log_file.unlink()
            logs_eliminados += 1
        except Exception as e:
            print(f"⚠️  No se pudo eliminar {log_file.name}: {e}")
    
    if logs_eliminados > 0:
        print(f"✅ {logs_eliminados} archivo(s) de log eliminados")


def reset_completo(crear_backup=True, limpiar_logs_flag=True):
    """
    Reset completo: Elimina BD y crea una nueva
    
    Args:
        crear_backup: Si True, crea backup antes de borrar
        limpiar_logs_flag: Si True, limpia los logs también
    """
    
    print("\n" + "="*60)
    print("🔄 RESET COMPLETO DE BASE DE DATOS")
    print("="*60)
    
    # 1. Crear backup
    if crear_backup:
        print("\n📦 Paso 1: Creando backup de seguridad...")
        crear_backup_antes_reset()
    
    # 2. Eliminar BD actual
    print("\n🗑️  Paso 2: Eliminando base de datos actual...")
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"✅ {DB_FILE} eliminado")
        except Exception as e:
            print(f"❌ Error al eliminar {DB_FILE}: {e}")
            return False
    else:
        print(f"ℹ️  {DB_FILE} no existe")
    
    # 3. Limpiar logs
    if limpiar_logs_flag:
        print("\n🧹 Paso 3: Limpiando logs...")
        limpiar_logs()
    
    # 4. Crear BD nueva
    print("\n🔨 Paso 4: Creando base de datos nueva...")
    if inicializar_base_datos():
        print("\n" + "="*60)
        print("✅ RESET COMPLETADO CON ÉXITO")
        print("="*60)
        print("\n✨ Base de datos nueva creada")
        print("   • Todas las tablas inicializadas")
        print("   • Configuración por defecto")
        print("   • 6 criptomonedas disponibles")
        print("   • Lista para testing")
        return True
    else:
        print("\n❌ Error al crear la base de datos nueva")
        return False


def reset_solo_datos():
    """
    Reset de solo datos: Mantiene la estructura, borra solo registros
    Útil para testing rápido sin recrear tablas
    """
    
    print("\n" + "="*60)
    print("🔄 RESET DE DATOS (Mantiene estructura)")
    print("="*60)
    
    if not os.path.exists(DB_FILE):
        print("\n❌ No existe base de datos para limpiar")
        return False
    
    import sqlite3
    
    try:
        # Crear backup
        print("\n📦 Creando backup de seguridad...")
        crear_backup_antes_reset()
        
        # Conectar y limpiar
        print("\n🧹 Limpiando datos...")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Tablas a limpiar (en orden para respetar foreign keys)
        tablas_limpiar = [
            'ventas',
            'efectivo_banco',
            'compras',
            'boveda_ciclo',
            'dias',
            'ciclos',
            'apis_config'
        ]
        
        registros_eliminados = 0
        for tabla in tablas_limpiar:
            cursor.execute(f"DELETE FROM {tabla}")
            eliminados = conn.total_changes
            if eliminados > 0:
                print(f"   ✓ {tabla}: {eliminados} registro(s) eliminados")
                registros_eliminados += eliminados
        
        # Resetear configuración a valores por defecto
        cursor.execute("""
            UPDATE config SET
                comision_default = 0.35,
                ganancia_neta_default = 2.0,
                modo_comision = 'manual',
                api_comision_activa = 0,
                limite_ventas_min = 3,
                limite_ventas_max = 5
            WHERE id = 1
        """)
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ LIMPIEZA COMPLETADA")
        print("="*60)
        print(f"\n✨ {registros_eliminados} registro(s) eliminados")
        print("   • Estructura de BD intacta")
        print("   • Configuración reseteada")
        print("   • Lista para testing")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al limpiar datos: {e}")
        return False


def reset_interactivo():
    """Modo interactivo con confirmación"""
    
    print("\n" + "="*60)
    print("⚠️  RESET DE BASE DE DATOS - MODO INTERACTIVO")
    print("="*60)
    
    print("\n⚠️  ADVERTENCIA: Esta acción es DESTRUCTIVA")
    print("\nOpciones:")
    print("  [1] Reset COMPLETO (Borra y crea BD nueva)")
    print("  [2] Reset de DATOS (Solo borra registros)")
    print("  [3] Cancelar")
    
    opcion = input("\nSelecciona (1-3): ").strip()
    
    if opcion == "1":
        print("\n⚠️  RESET COMPLETO")
        print("Esto borrará:")
        print("  • Archivo arbitraje.db completo")
        print("  • Todos los datos y configuraciones")
        print("  • (Se creará backup automático)")
        
        confirmacion = input("\nEscribe 'RESET' en mayúsculas para confirmar: ").strip()
        
        if confirmacion == "RESET":
            limpiar = input("¿Limpiar logs también? (s/n): ").lower() == 's'
            return reset_completo(crear_backup=True, limpiar_logs_flag=limpiar)
        else:
            print("\n❌ Confirmación incorrecta. Cancelado.")
            return False
    
    elif opcion == "2":
        print("\n⚠️  RESET DE DATOS")
        print("Esto borrará:")
        print("  • Todos los ciclos, días, ventas")
        print("  • Configuración de APIs")
        print("  • (Mantiene estructura de tablas)")
        
        confirmacion = input("\nEscribe 'LIMPIAR' en mayúsculas para confirmar: ").strip()
        
        if confirmacion == "LIMPIAR":
            return reset_solo_datos()
        else:
            print("\n❌ Confirmación incorrecta. Cancelado.")
            return False
    
    else:
        print("\n❌ Cancelado")
        return False


def reset_silencioso():
    """
    Reset silencioso para testing automatizado
    NO pide confirmación - usar con cuidado
    """
    
    print("🤖 Modo silencioso: Reset automático sin confirmación")
    return reset_completo(crear_backup=True, limpiar_logs_flag=True)


# ===================================================================
# FUNCIÓN PRINCIPAL
# ===================================================================

def main():
    """Punto de entrada principal"""
    
    print("\n" + "="*60)
    print("SCRIPT DE RESET DE BASE DE DATOS")
    print("Para desarrollo y testing")
    print("="*60)
    
    # Verificar si hay argumentos de línea de comandos
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        
        if modo == '--completo':
            print("\n🤖 Modo: Reset completo (línea de comandos)")
            confirmacion = input("Confirmar con 'RESET': ").strip()
            if confirmacion == "RESET":
                sys.exit(0 if reset_completo() else 1)
            else:
                print("❌ Cancelado")
                sys.exit(1)
        
        elif modo == '--datos':
            print("\n🤖 Modo: Reset de datos (línea de comandos)")
            confirmacion = input("Confirmar con 'LIMPIAR': ").strip()
            if confirmacion == "LIMPIAR":
                sys.exit(0 if reset_solo_datos() else 1)
            else:
                print("❌ Cancelado")
                sys.exit(1)
        
        elif modo == '--silencioso' or modo == '--auto':
            print("\n🤖 Modo: Reset automático (sin confirmación)")
            print("⚠️  Iniciando en 3 segundos...")
            import time
            time.sleep(3)
            sys.exit(0 if reset_silencioso() else 1)
        
        elif modo == '--help':
            print("\n📖 USO:")
            print("  python reset_db.py              → Modo interactivo")
            print("  python reset_db.py --completo   → Reset completo con confirmación")
            print("  python reset_db.py --datos      → Reset de datos con confirmación")
            print("  python reset_db.py --silencioso → Reset automático SIN confirmación")
            print("  python reset_db.py --help       → Muestra esta ayuda")
            sys.exit(0)
        
        else:
            print(f"\n❌ Opción desconocida: {modo}")
            print("Usa --help para ver opciones disponibles")
            sys.exit(1)
    
    # Modo interactivo por defecto
    else:
        exito = reset_interactivo()
        sys.exit(0 if exito else 1)


# ===================================================================
# EJECUCIÓN
# ===================================================================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
