#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
SCRIPT DE INSTALACIÓN Y VERIFICACIÓN
=============================================================================
Instala dependencias y verifica el sistema
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(texto):
    """Imprime encabezado"""
    print("\n" + "="*70)
    print(texto)
    print("="*70)


def verificar_python():
    """Verifica versión de Python"""
    print_header("VERIFICANDO PYTHON")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Se requiere Python 3.7 o superior")
        return False
    
    print("✅ Versión de Python correcta")
    return True


def instalar_dependencias():
    """Instala dependencias desde requirements.txt"""
    print_header("INSTALANDO DEPENDENCIAS")
    
    if not Path("requirements.txt").exists():
        print("⚠️  requirements.txt no encontrado")
        return False
    
    try:
        # Detectar sistema operativo
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            cmd = ["pip3", "install", "-r", "requirements.txt", "--break-system-packages"]
        else:
            cmd = ["pip", "install", "-r", "requirements.txt"]
        
        print(f"Ejecutando: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        print("\n✅ Dependencias instaladas correctamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al instalar dependencias: {e}")
        print("\n💡 Intenta manualmente:")
        print("   pip install matplotlib --break-system-packages")
        return False


def crear_directorios():
    """Crea directorios necesarios"""
    print_header("CREANDO DIRECTORIOS")
    
    directorios = ['logs', 'backups', 'reportes', 'graficos']
    
    for directorio in directorios:
        Path(directorio).mkdir(exist_ok=True)
        print(f"✅ {directorio}/")
    
    return True


def verificar_base_datos():
    """Verifica si existe la base de datos"""
    print_header("VERIFICANDO BASE DE DATOS")
    
    if Path("arbitraje.db").exists():
        print("✅ Base de datos encontrada: arbitraje.db")
        return True
    else:
        print("⚠️  Base de datos no encontrada")
        print("\n💡 Para crear la base de datos, ejecuta:")
        print("   python inicializar_bd.py")
        return False


def verificar_archivos():
    """Verifica archivos principales del sistema"""
    print_header("VERIFICANDO ARCHIVOS DEL SISTEMA")
    
    archivos_requeridos = [
        'main.py',
        'inicializar_bd.py',
        'db_manager.py',
        'logger.py',
        'calculos.py',
        'operador.py',
        'boveda.py',
        'ciclos.py',
        'dias.py',
        'configuracion.py',
        'mantenimiento.py'
    ]
    
    archivos_opcionales = [
        'proyecciones.py',
        'reportes.py',
        'notas.py',
        'alertas.py',
        'graficos.py',
        'validaciones.py',
        'queries.py'
    ]
    
    print("\n📋 Archivos requeridos:")
    faltantes = []
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTA")
            faltantes.append(archivo)
    
    print("\n📋 Archivos opcionales:")
    for archivo in archivos_opcionales:
        if Path(archivo).exists():
            print(f"   ✅ {archivo}")
        else:
            print(f"   ⚠️  {archivo} - No encontrado")
    
    if faltantes:
        print(f"\n❌ Faltan {len(faltantes)} archivo(s) requerido(s)")
        return False
    
    print("\n✅ Todos los archivos requeridos presentes")
    return True


def menu_instalacion():
    """Menú de instalación"""
    
    print("\n" + "="*70)
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║          INSTALACIÓN - SISTEMA DE ARBITRAJE P2P v3.0             ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print("="*70)
    
    print("\n¿Qué deseas hacer?")
    print("[1] Instalación completa (recomendado)")
    print("[2] Solo instalar dependencias")
    print("[3] Solo verificar sistema")
    print("[4] Salir")
    
    opcion = input("\nSelecciona: ").strip()
    
    if opcion == "1":
        instalacion_completa()
    elif opcion == "2":
        instalar_dependencias()
    elif opcion == "3":
        verificar_sistema()
    elif opcion == "4":
        print("\n👋 ¡Hasta pronto!")
    else:
        print("❌ Opción inválida")


def instalacion_completa():
    """Instalación completa del sistema"""
    
    print_header("INSTALACIÓN COMPLETA")
    
    pasos_ok = 0
    pasos_totales = 5
    
    # Paso 1: Verificar Python
    if verificar_python():
        pasos_ok += 1
    
    # Paso 2: Crear directorios
    if crear_directorios():
        pasos_ok += 1
    
    # Paso 3: Verificar archivos
    if verificar_archivos():
        pasos_ok += 1
    
    # Paso 4: Instalar dependencias
    if instalar_dependencias():
        pasos_ok += 1
    
    # Paso 5: Verificar BD
    if verificar_base_datos():
        pasos_ok += 1
    
    # Resumen
    print_header("RESUMEN DE INSTALACIÓN")
    print(f"\n{pasos_ok}/{pasos_totales} pasos completados")
    
    if pasos_ok == pasos_totales:
        print("\n✅ ¡INSTALACIÓN COMPLETA!")
        print("\n🚀 Para iniciar el sistema:")
        print("   python main.py")
    else:
        print("\n⚠️  Instalación incompleta")
        print("\n💡 Pasos faltantes:")
        
        if not Path("arbitraje.db").exists():
            print("   • Ejecuta: python inicializar_bd.py")
    
    input("\nPresiona Enter para continuar...")


def verificar_sistema():
    """Solo verifica el sistema"""
    
    verificar_python()
    verificar_archivos()
    verificar_base_datos()
    
    print_header("VERIFICACIÓN COMPLETA")
    input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    try:
        menu_instalacion()
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalación cancelada")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
