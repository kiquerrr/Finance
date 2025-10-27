"""
=============================================================================
MÓDULO DE MANTENIMIENTO
=============================================================================
Gestiona el mantenimiento de la base de datos y el sistema:
- Backups y restauración
- Verificación de integridad
- Limpieza de datos
- Logs y registros
- Optimización
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from logger import log

# Conexión a la base de datos
conn = sqlite3.connect('arbitraje.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


# ===================================================================
# DIRECTORIOS DE MANTENIMIENTO
# ===================================================================

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


# ===================================================================
# BACKUPS
# ===================================================================

def crear_backup():
    """Crea un backup completo de la base de datos"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"arbitraje_backup_{timestamp}.db"
    
    try:
        # Copiar archivo de base de datos directamente
        shutil.copy2('arbitraje.db', backup_file)
        
        # Calcular tamaño del backup
        tamaño_mb = backup_file.stat().st_size / (1024 * 1024)
        
        log.info(
            f"Backup creado exitosamente: {backup_file.name} ({tamaño_mb:.2f} MB)",
            categoria='general'
        )
        
        print(f"\n✅ Backup creado exitosamente")
        print(f"   Archivo: {backup_file.name}")
        print(f"   Tamaño: {tamaño_mb:.2f} MB")
        print(f"   Ubicación: {backup_file.absolute()}")
        
        return backup_file
        
    except Exception as e:
        log.error("Error al crear backup", str(e))
        print(f"❌ Error al crear backup: {e}")
        return None


def listar_backups():
    """Lista todos los backups disponibles"""
    
    backups = sorted(BACKUP_DIR.glob("arbitraje_backup_*.db"), reverse=True)
    
    if not backups:
        print("\n⚠️  No hay backups disponibles")
        return []
    
    print("\n" + "="*60)
    print("BACKUPS DISPONIBLES")
    print("="*60)
    
    backup_info = []
    for i, backup in enumerate(backups, 1):
        stat = backup.stat()
        tamaño_mb = stat.st_size / (1024 * 1024)
        fecha = datetime.fromtimestamp(stat.st_mtime)
        
        backup_info.append({
            'numero': i,
            'archivo': backup,
            'tamaño': tamaño_mb,
            'fecha': fecha
        })
        
        print(f"\n[{i}] {backup.name}")
        print(f"    Fecha: {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Tamaño: {tamaño_mb:.2f} MB")
    
    print("="*60)
    return backup_info


def restaurar_backup(backup_file):
    """Restaura la base de datos desde un backup"""
    
    if not backup_file.exists():
        log.error("Backup no encontrado", str(backup_file))
        print(f"❌ Backup no encontrado: {backup_file}")
        return False
    
    print(f"\n⚠️  ADVERTENCIA: Esta acción sobrescribirá la base de datos actual")
    print(f"   Se restaurará desde: {backup_file.name}")
    
    confirmar = input("\n¿Estás seguro? (escribe 'CONFIRMAR' para continuar): ").strip()
    
    if confirmar != "CONFIRMAR":
        print("❌ Restauración cancelada")
        return False
    
    try:
        # Crear backup de seguridad antes de restaurar
        print("\nCreando backup de seguridad de la BD actual...")
        backup_seguridad = crear_backup()
        
        # Copiar el backup sobre la BD actual
        shutil.copy2(backup_file, 'arbitraje.db')
        
        log.info(f"Base de datos restaurada desde {backup_file.name}", categoria='general')
        
        print(f"\n✅ Base de datos restaurada exitosamente")
        if backup_seguridad:
            print(f"   Backup de seguridad guardado como: {backup_seguridad.name}")
        
        return True
        
    except Exception as e:
        log.error("Error al restaurar backup", str(e))
        print(f"❌ Error al restaurar: {e}")
        return False


def eliminar_backups_antiguos(dias=30):
    """Elimina backups más antiguos que X días"""
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    backups_eliminados = 0
    
    print(f"\nBuscando backups de más de {dias} días...")
    
    for backup in BACKUP_DIR.glob("*.db"):
        fecha_backup = datetime.fromtimestamp(backup.stat().st_mtime)
        
        if fecha_backup < fecha_limite:
            try:
                print(f"   Eliminando: {backup.name} ({fecha_backup.strftime('%Y-%m-%d')})")
                backup.unlink()
                backups_eliminados += 1
                log.info(f"Backup antiguo eliminado: {backup.name}", categoria='general')
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {backup.name}: {e}")
    
    if backups_eliminados == 0:
        print(f"   ℹ️  No se encontraron backups de más de {dias} días")
    else:
        print(f"\n✅ {backups_eliminados} backup(s) antiguo(s) eliminado(s)")
    
    return backups_eliminados


# ===================================================================
# VERIFICACIÓN DE INTEGRIDAD
# ===================================================================

def verificar_integridad_bd():
    """Verifica la integridad de la base de datos"""
    
    print("\n" + "="*60)
    print("VERIFICANDO INTEGRIDAD DE LA BASE DE DATOS")
    print("="*60)
    
    errores = []
    
    # 1. Verificar integridad de SQLite
    print("\n[1/6] Verificando integridad de SQLite...")
    cursor.execute("PRAGMA integrity_check")
    resultado = cursor.fetchone()[0]
    
    if resultado == "ok":
        print("   ✅ Integridad SQLite: OK")
    else:
        print(f"   ❌ Problemas de integridad: {resultado}")
        errores.append(f"SQLite integrity: {resultado}")
    
    # 2. Verificar tablas requeridas
    print("\n[2/6] Verificando tablas requeridas...")
    tablas_requeridas = [
        'config', 'ciclos', 'dias', 'criptomonedas',
        'boveda_ciclo', 'compras', 'ventas', 'efectivo_banco'
    ]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas_existentes = [t[0] for t in cursor.fetchall()]
    
    for tabla in tablas_requeridas:
        if tabla in tablas_existentes:
            print(f"   ✅ Tabla '{tabla}': OK")
        else:
            print(f"   ❌ Tabla '{tabla}': FALTA")
            errores.append(f"Tabla faltante: {tabla}")
    
    # 3. Verificar referencias foráneas
    print("\n[3/6] Verificando referencias foráneas...")
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    
    if not fk_errors:
        print("   ✅ Referencias foráneas: OK")
    else:
        print(f"   ❌ {len(fk_errors)} error(es) de referencias foráneas")
        errores.extend([f"FK error: {e}" for e in fk_errors])
    
    # 4. Verificar consistencia de datos
    print("\n[4/6] Verificando consistencia de datos...")
    
    # Verificar que las cantidades no sean negativas
    cursor.execute("SELECT COUNT(*) FROM boveda_ciclo WHERE cantidad < 0")
    cantidades_negativas = cursor.fetchone()[0]
    
    if cantidades_negativas == 0:
        print("   ✅ Cantidades en bóveda: OK")
    else:
        print(f"   ❌ {cantidades_negativas} cantidad(es) negativa(s) en bóveda")
        errores.append(f"Cantidades negativas: {cantidades_negativas}")
    
    # 5. Verificar huérfanos
    print("\n[5/6] Verificando registros huérfanos...")
    
    cursor.execute("""
        SELECT COUNT(*) FROM dias
        WHERE ciclo_id NOT IN (SELECT id FROM ciclos)
    """)
    dias_huerfanos = cursor.fetchone()[0]
    
    if dias_huerfanos == 0:
        print("   ✅ Días sin huérfanos: OK")
    else:
        print(f"   ❌ {dias_huerfanos} día(s) huérfano(s)")
        errores.append(f"Días huérfanos: {dias_huerfanos}")
    
    # 6. Verificar índices
    print("\n[6/6] Verificando índices...")
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
    num_indices = cursor.fetchone()[0]
    print(f"   ℹ️  {num_indices} índice(s) encontrado(s)")
    
    # Resumen
    print("\n" + "="*60)
    if not errores:
        print("✅ VERIFICACIÓN COMPLETADA SIN ERRORES")
        log.info("Verificación de integridad: OK", categoria='general')
    else:
        print(f"❌ VERIFICACIÓN COMPLETADA CON {len(errores)} ERROR(ES)")
        for error in errores:
            print(f"   • {error}")
        log.advertencia(f"Verificación con errores: {len(errores)}", categoria='errores')
    print("="*60)
    
    return len(errores) == 0


def reparar_bd():
    """Intenta reparar problemas comunes en la BD"""
    
    print("\n" + "="*60)
    print("REPARACIÓN DE BASE DE DATOS")
    print("="*60)
    
    reparaciones = 0
    
    # Crear conexión nueva para reparaciones
    conn_repair = sqlite3.connect('arbitraje.db')
    cursor_repair = conn_repair.cursor()
    
    try:
        # 1. Eliminar registros huérfanos
        print("\n[1/3] Eliminando registros huérfanos...")
        cursor_repair.execute("""
            DELETE FROM dias
            WHERE ciclo_id NOT IN (SELECT id FROM ciclos)
        """)
        dias_eliminados = conn_repair.total_changes
        if dias_eliminados > 0:
            print(f"   ✅ {dias_eliminados} día(s) huérfano(s) eliminado(s)")
            reparaciones += 1
        
        cursor_repair.execute("""
            DELETE FROM ventas
            WHERE dia_id NOT IN (SELECT id FROM dias)
        """)
        ventas_eliminadas = conn_repair.total_changes - dias_eliminados
        if ventas_eliminadas > 0:
            print(f"   ✅ {ventas_eliminadas} venta(s) huérfana(s) eliminada(s)")
            reparaciones += 1
        
        # 2. Corregir cantidades negativas
        print("\n[2/3] Corrigiendo cantidades negativas...")
        cursor_repair.execute("""
            UPDATE boveda_ciclo
            SET cantidad = 0
            WHERE cantidad < 0
        """)
        cantidades_antes = conn_repair.total_changes
        cantidades_corregidas = cantidades_antes - dias_eliminados - ventas_eliminadas
        if cantidades_corregidas > 0:
            print(f"   ✅ {cantidades_corregidas} cantidad(es) corregida(s)")
            reparaciones += 1
        
        # 3. Optimizar BD
        print("\n[3/3] Optimizando base de datos...")
        conn_repair.commit()
        conn_repair.close()
        
        # Crear nueva conexión para VACUUM (sin transacción)
        conn_vacuum = sqlite3.connect('arbitraje.db')
        conn_vacuum.execute("VACUUM")
        conn_vacuum.execute("ANALYZE")
        conn_vacuum.close()
        
        print("   ✅ Base de datos optimizada")
        reparaciones += 1
        
        print("\n" + "="*60)
        print(f"✅ REPARACIÓN COMPLETADA: {reparaciones} acción(es) realizada(s)")
        print("="*60)
        
        log.info(f"Reparación de BD: {reparaciones} acciones", categoria='general')
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la reparación: {e}")
        log.error("Error en reparación de BD", str(e))
        conn_repair.rollback()
        conn_repair.close()
        return False


# ===================================================================
# LIMPIEZA DE DATOS
# ===================================================================

def limpiar_datos_antiguos(dias=90):
    """Limpia datos antiguos de más de X días"""
    
    print(f"\n⚠️  Esta acción eliminará datos de más de {dias} días")
    confirmar = input("¿Continuar? (s/n): ").lower()
    
    if confirmar != 's':
        print("❌ Limpieza cancelada")
        return False
    
    # Crear backup antes de limpiar
    print("\nCreando backup de seguridad...")
    if not crear_backup():
        print("❌ No se pudo crear backup. Limpieza cancelada.")
        return False
    
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    
    print(f"\nLimpiando datos anteriores a {fecha_limite}...")
    
    # Crear conexión nueva para limpieza
    conn_clean = sqlite3.connect('arbitraje.db')
    cursor_clean = conn_clean.cursor()
    
    try:
        # Eliminar ciclos cerrados antiguos y sus datos relacionados
        cursor_clean.execute("""
            DELETE FROM ciclos
            WHERE estado = 'cerrado'
            AND fecha_inicio < ?
        """, (fecha_limite,))
        
        ciclos_eliminados = conn_clean.total_changes
        conn_clean.commit()
        conn_clean.close()
        
        print(f"✅ {ciclos_eliminados} ciclo(s) antiguo(s) eliminado(s)")
        log.info(f"Limpieza: {ciclos_eliminados} ciclos eliminados", categoria='general')
        
        return True
        
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")
        log.error("Error en limpieza de datos", str(e))
        conn_clean.rollback()
        conn_clean.close()
        return False


def limpiar_logs_antiguos(dias=30):
    """Limpia logs antiguos"""
    
    fecha_limite = datetime.now() - timedelta(days=dias)
    logs_procesados = 0
    
    for log_file in LOGS_DIR.glob("*.log"):
        # Leer log y filtrar líneas antiguas
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
            
            lineas_nuevas = []
            for linea in lineas:
                # Extraer fecha de la línea (formato: [YYYY-MM-DD HH:MM:SS])
                if linea.startswith('['):
                    try:
                        fecha_str = linea[1:20]
                        fecha_linea = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                        if fecha_linea >= fecha_limite:
                            lineas_nuevas.append(linea)
                    except:
                        lineas_nuevas.append(linea)
                else:
                    lineas_nuevas.append(linea)
            
            # Reescribir log
            with open(log_file, 'w', encoding='utf-8') as f:
                f.writelines(lineas_nuevas)
            
            logs_procesados += 1
            
        except Exception as e:
            print(f"⚠️  Error procesando {log_file.name}: {e}")
    
    print(f"✅ {logs_procesados} archivo(s) de log procesado(s)")
    return True


# ===================================================================
# ESTADÍSTICAS Y REPORTES
# ===================================================================

def generar_reporte_bd():
    """Genera un reporte del estado de la base de datos"""
    
    print("\n" + "="*60)
    print("REPORTE DEL ESTADO DE LA BASE DE DATOS")
    print("="*60)
    
    # Tamaño de la BD
    bd_size = Path('arbitraje.db').stat().st_size / (1024 * 1024)
    print(f"\n📊 Tamaño de la BD: {bd_size:.2f} MB")
    
    # Conteo de registros
    print("\n📋 Registros por tabla:")
    
    tablas = ['ciclos', 'dias', 'criptomonedas', 'boveda_ciclo', 
              'compras', 'ventas', 'efectivo_banco', 'apis_config']
    
    for tabla in tablas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"   • {tabla}: {count}")
        except:
            print(f"   • {tabla}: N/A")
    
    # Ciclos activos vs cerrados
    cursor.execute("SELECT estado, COUNT(*) FROM ciclos GROUP BY estado")
    print("\n🔄 Ciclos:")
    for row in cursor.fetchall():
        print(f"   • {row[0]}: {row[1]}")
    
    # Espacio usado por logs
    logs_size = sum(f.stat().st_size for f in LOGS_DIR.glob("*.log")) / (1024 * 1024)
    print(f"\n📝 Tamaño total de logs: {logs_size:.2f} MB")
    
    # Backups disponibles
    backups_count = len(list(BACKUP_DIR.glob("arbitraje_backup_*.db")))
    backups_size = sum(f.stat().st_size for f in BACKUP_DIR.glob("*.db")) / (1024 * 1024)
    print(f"\n💾 Backups: {backups_count} archivo(s), {backups_size:.2f} MB")
    
    print("="*60)
    
    return True


# ===================================================================
# OPTIMIZACIÓN
# ===================================================================

def optimizar_bd():
    """Optimiza la base de datos"""
    
    print("\n" + "="*60)
    print("OPTIMIZACIÓN DE BASE DE DATOS")
    print("="*60)
    
    # Tamaño antes
    tamaño_antes = Path('arbitraje.db').stat().st_size / (1024 * 1024)
    print(f"\nTamaño actual: {tamaño_antes:.2f} MB")
    
    print("\nEjecutando optimización...")
    
    try:
        # Crear conexión nueva sin transacción para VACUUM
        conn_opt = sqlite3.connect('arbitraje.db')
        
        # 1. VACUUM - compacta la BD eliminando espacio no utilizado
        print("   [1/3] Compactando base de datos (VACUUM)...")
        conn_opt.execute("VACUUM")
        
        # 2. ANALYZE - actualiza estadísticas para mejor rendimiento
        print("   [2/3] Actualizando estadísticas (ANALYZE)...")
        conn_opt.execute("ANALYZE")
        
        # 3. Reindexar
        print("   [3/3] Reconstruyendo índices (REINDEX)...")
        conn_opt.execute("REINDEX")
        
        conn_opt.close()
        
        # Tamaño después
        tamaño_despues = Path('arbitraje.db').stat().st_size / (1024 * 1024)
        ahorro = tamaño_antes - tamaño_despues
        
        print("\n✅ Optimización completada")
        print(f"   Tamaño final: {tamaño_despues:.2f} MB")
        if ahorro > 0:
            print(f"   Espacio recuperado: {ahorro:.2f} MB ({ahorro/tamaño_antes*100:.1f}%)")
        print("="*60)
        
        log.info(f"BD optimizada: {tamaño_antes:.2f}MB → {tamaño_despues:.2f}MB", categoria='general')
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en optimización: {e}")
        log.error("Error al optimizar BD", str(e))
        return False


def crear_indices_optimizacion():
    """Crea índices adicionales para optimizar consultas"""
    
    print("\nCreando índices de optimización...")
    
    indices = [
        ("idx_dias_ciclo", "CREATE INDEX IF NOT EXISTS idx_dias_ciclo ON dias(ciclo_id)"),
        ("idx_ventas_dia", "CREATE INDEX IF NOT EXISTS idx_ventas_dia ON ventas(dia_id)"),
        ("idx_boveda_ciclo", "CREATE INDEX IF NOT EXISTS idx_boveda_ciclo ON boveda_ciclo(ciclo_id, cripto_id)"),
        ("idx_efectivo_ciclo", "CREATE INDEX IF NOT EXISTS idx_efectivo_ciclo ON efectivo_banco(ciclo_id)"),
        ("idx_compras_ciclo", "CREATE INDEX IF NOT EXISTS idx_compras_ciclo ON compras(ciclo_id)"),
    ]
    
    creados = 0
    for nombre, sql in indices:
        try:
            cursor.execute(sql)
            print(f"   ✅ {nombre}")
            creados += 1
        except Exception as e:
            print(f"   ⚠️  {nombre}: {e}")
    
    conn.commit()
    print(f"\n✅ {creados}/{len(indices)} índice(s) creado(s)/verificado(s)")
    
    return True


# ===================================================================
# MENÚ DE MANTENIMIENTO
# ===================================================================

def menu_mantenimiento():
    """Menú interactivo de mantenimiento"""
    
    while True:
        print("\n" + "="*60)
        print("MANTENIMIENTO DEL SISTEMA")
        print("="*60)
        
        print("\n💾 BACKUPS:")
        print("[1] Crear Backup")
        print("[2] Restaurar Backup")
        print("[3] Listar Backups")
        print("[4] Eliminar Backups Antiguos")
        
        print("\n🔍 VERIFICACIÓN:")
        print("[5] Verificar Integridad de la BD")
        print("[6] Reparar Base de Datos")
        
        print("\n🧹 LIMPIEZA:")
        print("[7] Limpiar Datos Antiguos")
        print("[8] Limpiar Logs Antiguos")
        
        print("\n⚡ OPTIMIZACIÓN:")
        print("[9] Optimizar Base de Datos")
        print("[10] Crear Índices de Optimización")
        
        print("\n📊 REPORTES:")
        print("[11] Generar Reporte del Sistema")
        print("[12] Ver Estadísticas de Logs")
        
        print("\n[13] Volver al Menú Principal")
        print("="*60)
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            crear_backup()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "2":
            backups = listar_backups()
            if backups:
                try:
                    num = int(input("\nSelecciona el número de backup a restaurar: "))
                    if 1 <= num <= len(backups):
                        restaurar_backup(backups[num-1]['archivo'])
                except ValueError:
                    print("❌ Número inválido")
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "3":
            listar_backups()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "4":
            try:
                dias = int(input("Eliminar backups de más de cuántos días? (30): ") or "30")
                eliminar_backups_antiguos(dias)
            except ValueError:
                print("❌ Número inválido")
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "5":
            verificar_integridad_bd()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "6":
            reparar_bd()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "7":
            try:
                dias = int(input("Eliminar datos de más de cuántos días? (90): ") or "90")
                limpiar_datos_antiguos(dias)
            except ValueError:
                print("❌ Número inválido")
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "8":
            try:
                dias = int(input("Limpiar logs de más de cuántos días? (30): ") or "30")
                limpiar_logs_antiguos(dias)
            except ValueError:
                print("❌ Número inválido")
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "9":
            optimizar_bd()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "10":
            crear_indices_optimizacion()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "11":
            generar_reporte_bd()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "12":
            ver_estadisticas_logs()
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "13":
            break
        
        else:
            print("❌ Opción inválida")


def ver_estadisticas_logs():
    """Muestra estadísticas de los logs"""
    
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE LOGS")
    print("="*60)
    
    categorias = ['general', 'operaciones', 'calculos', 'errores', 'boveda', 'ciclos']
    
    for categoria in categorias:
        log_file = LOGS_DIR / f"{categoria}.log"
        
        if not log_file.exists():
            print(f"\n📄 {categoria}.log: No existe")
            continue
        
        # Estadísticas del archivo
        tamaño = log_file.stat().st_size / 1024  # KB
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        # Contar por nivel
        info_count = sum(1 for l in lineas if '[INFO]' in l)
        warning_count = sum(1 for l in lineas if '[WARNING]' in l)
        error_count = sum(1 for l in lineas if '[ERROR]' in l)
        
        print(f"\n📄 {categoria}.log:")
        print(f"   Tamaño: {tamaño:.2f} KB")
        print(f"   Total de entradas: {len(lineas)}")
        print(f"   INFO: {info_count} | WARNING: {warning_count} | ERROR: {error_count}")
    
    print("="*60)


# ===================================================================
# MANTENIMIENTO AUTOMÁTICO
# ===================================================================

def mantenimiento_automatico():
    """Ejecuta tareas de mantenimiento automático"""
    
    print("\n" + "="*60)
    print("MANTENIMIENTO AUTOMÁTICO")
    print("="*60)
    print("\nEjecutando tareas de mantenimiento...")
    
    # 1. Crear backup
    print("\n[1/4] Creando backup...")
    crear_backup()
    
    # 2. Verificar integridad
    print("\n[2/4] Verificando integridad...")
    verificar_integridad_bd()
    
    # 3. Optimizar
    print("\n[3/4] Optimizando base de datos...")
    optimizar_bd()
    
    # 4. Limpiar backups antiguos
    print("\n[4/4] Limpiando backups antiguos (>30 días)...")
    eliminar_backups_antiguos(30)
    
    print("\n" + "="*60)
    print("✅ MANTENIMIENTO AUTOMÁTICO COMPLETADO")
    print("="*60)
    
    log.info("Mantenimiento automático ejecutado", categoria='general')
    return True


# ===================================================================
# UTILIDADES
# ===================================================================

def obtener_tamaño_bd():
    """Obtiene el tamaño de la base de datos en MB"""
    return Path('arbitraje.db').stat().st_size / (1024 * 1024)


def obtener_info_sistema():
    """Obtiene información del sistema"""
    
    info = {
        'tamaño_bd': obtener_tamaño_bd(),
        'num_backups': len(list(BACKUP_DIR.glob("*.db"))),
        'tamaño_logs': sum(f.stat().st_size for f in LOGS_DIR.glob("*.log")) / (1024 * 1024),
        'ultimo_backup': None
    }
    
    # Obtener último backup
    backups = sorted(BACKUP_DIR.glob("arbitraje_backup_*.db"), reverse=True)
    if backups:
        info['ultimo_backup'] = datetime.fromtimestamp(backups[0].stat().st_mtime)
    
    return info


# ===================================================================
# EXPORTACIÓN DE DATOS
# ===================================================================

def exportar_datos_csv(tabla, archivo=None):
    """Exporta una tabla a CSV"""
    
    if not archivo:
        archivo = f"{tabla}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        cursor.execute(f"SELECT * FROM {tabla}")
        datos = cursor.fetchall()
        
        if not datos:
            print(f"⚠️  La tabla {tabla} está vacía")
            return False
        
        # Obtener nombres de columnas
        columnas = [description[0] for description in cursor.description]
        
        # Escribir CSV
        with open(archivo, 'w', encoding='utf-8') as f:
            # Encabezados
            f.write(','.join(columnas) + '\n')
            
            # Datos
            for fila in datos:
                valores = [str(v).replace(',', ';') if v is not None else '' for v in fila]
                f.write(','.join(valores) + '\n')
        
        print(f"✅ Datos exportados a {archivo}")
        log.info(f"Datos de {tabla} exportados a {archivo}", categoria='general')
        return True
        
    except Exception as e:
        log.error(f"Error al exportar {tabla}", str(e))
        print(f"❌ Error: {e}")
        return False


def exportar_todo():
    """Exporta todas las tablas a CSV"""
    
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    tablas = ['ciclos', 'dias', 'criptomonedas', 'boveda_ciclo', 
              'compras', 'ventas', 'efectivo_banco', 'config']
    
    print(f"\nExportando todas las tablas a {export_dir}/...")
    
    for tabla in tablas:
        archivo = export_dir / f"{tabla}_{timestamp}.csv"
        exportar_datos_csv(tabla, archivo)
    
    print(f"\n✅ Todas las tablas exportadas")
    return True


# ===================================================================
# INICIALIZACIÓN
# ===================================================================

if __name__ == "__main__":
    # Si se ejecuta directamente, mostrar el menú
    menu_mantenimiento()
