#!/bin/bash
echo "Arreglando imports en todos los archivos..."

# Función para actualizar imports en un archivo
fix_file() {
    local file=$1
    echo "  Procesando: $file"
    
    # Backup
    cp "$file" "${file}.bak"
    
    # Arreglar imports
    sed -i 's/^from db_manager import/from core.db_manager import/g' "$file"
    sed -i 's/^from logger import/from core.logger import/g' "$file"
    sed -i 's/^from calculos import/from core.calculos import/g' "$file"
    sed -i 's/^from validaciones import/from core.validaciones import/g' "$file"
    sed -i 's/^from queries import/from core.queries import/g' "$file"
    
    sed -i 's/^from boveda import/from modules.boveda import/g' "$file"
    sed -i 's/^from ciclos import/from modules.ciclos import/g' "$file"
    sed -i 's/^from operador import/from modules.operador import/g' "$file"
    sed -i 's/^from configuracion import/from modules.configuracion import/g' "$file"
    sed -i 's/^from mantenimiento import/from modules.mantenimiento import/g' "$file"
    sed -i 's/^from dias import/from modules.dias import/g' "$file"
    
    sed -i 's/^from proyecciones import/from features.proyecciones import/g' "$file"
    sed -i 's/^from reportes import/from features.reportes import/g' "$file"
    sed -i 's/^from notas import/from features.notas import/g' "$file"
    sed -i 's/^from alertas import/from features.alertas import/g' "$file"
    sed -i 's/^from graficos import/from features.graficos import/g' "$file"
}

# Arreglar archivos en core/
for file in core/*.py; do
    [ -f "$file" ] && fix_file "$file"
done

# Arreglar archivos en modules/
for file in modules/*.py; do
    [ -f "$file" ] && fix_file "$file"
done

# Arreglar archivos en features/
for file in features/*.py; do
    [ -f "$file" ] && fix_file "$file"
done

echo ""
echo "✅ Imports arreglados en todos los archivos"
echo ""
echo "Archivos de backup creados con extensión .bak"
echo "Si algo falla, puedes restaurar con:"
echo "  cp archivo.py.bak archivo.py"
