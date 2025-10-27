#!/bin/bash
# -*- coding: utf-8 -*-

# ============================================================
# SCRIPT DE LIMPIEZA DEL PROYECTO
# ============================================================
# Elimina archivos viejos, backups sueltos y cache
# ============================================================

echo "============================================================"
echo "LIMPIEZA DEL PROYECTO"
echo "============================================================"

# Archivos a MANTENER (nuevos y necesarios)
ARCHIVOS_NECESARIOS=(
    "main.py"
    "operador.py"
    "boveda.py"
    "dias.py"
    "ciclos.py"
    "logger.py"
    "calculos.py"
    "configuracion.py"
    "mantenimiento.py"
    "inicializar_bd.py"
    "reset_db.py"
    "arbitraje.db"
    "README.md"
    "Roadmap.md"
)

# Archivos VIEJOS a eliminar (ya no se usan)
ARCHIVOS_VIEJOS=(
    "arbitraje.py"
    "capital.py"
    "criptomonedas.py"
    "database.py"
    "estadisticas.py"
    "utils.py"
    "apis.py"
    "actualizar_bd.py"
    "migrar_bd.py"
)

echo ""
echo "🗑️  Eliminando archivos viejos..."
echo ""

eliminados=0

for archivo in "${ARCHIVOS_VIEJOS[@]}"; do
    if [ -f "$archivo" ]; then
        echo "   ✓ Eliminando: $archivo"
        rm "$archivo"
        ((eliminados++))
    fi
done

# Eliminar backups sueltos en raíz
echo ""
echo "🗑️  Eliminando backups sueltos..."
echo ""

for backup in arbitraje_backup_*.db; do
    if [ -f "$backup" ]; then
        echo "   ✓ Moviendo a backups/: $backup"
        mv "$backup" backups/
    fi
done

# Limpiar cache de Python
echo ""
echo "🧹 Limpiando cache de Python..."
echo ""

if [ -d "__pycache__" ]; then
    echo "   ✓ Eliminando __pycache__/"
    rm -rf __pycache__
fi

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# Resumen
echo ""
echo "============================================================"
echo "✅ LIMPIEZA COMPLETADA"
echo "============================================================"
echo ""
echo "📊 Resumen:"
echo "   • Archivos viejos eliminados: $eliminados"
echo "   • Backups movidos a backups/"
echo "   • Cache de Python limpiado"
echo ""
echo "📁 Archivos actuales (necesarios):"
for archivo in "${ARCHIVOS_NECESARIOS[@]}"; do
    if [ -f "$archivo" ]; then
        echo "   ✓ $archivo"
    elif [ -d "$archivo" ]; then
        echo "   ✓ $archivo/"
    fi
done

echo ""
echo "============================================================"
