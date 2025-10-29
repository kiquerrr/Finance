#!/bin/bash
# Script de Limpieza del Sistema de Arbitraje P2P
# Versión 3.0

echo "=========================================="
echo "LIMPIEZA DEL PROYECTO"
echo "=========================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para confirmar
confirm() {
    read -p "$1 (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        return 0
    else
        return 1
    fi
}

echo -e "\n${YELLOW}PASO 1: Eliminar archivos obsoletos${NC}"
echo "-------------------------------------------"

# Eliminar __pycache__
if [ -d "__pycache__" ]; then
    echo -e "${RED}Eliminando __pycache__/${NC}"
    rm -rf __pycache__/
    echo "✓ Eliminado"
fi

# Eliminar .pytest_cache
if [ -d ".pytest_cache" ]; then
    echo -e "${RED}Eliminando .pytest_cache/${NC}"
    rm -rf .pytest_cache/
    echo "✓ Eliminado"
fi

# Eliminar configuracion_1
if [ -f "configuracion_1" ]; then
    echo -e "${RED}Eliminando configuracion_1${NC}"
    rm configuracion_1
    echo "✓ Eliminado"
fi

# Eliminar limpiar_proyecto.sh (script antiguo)
if [ -f "limpiar_proyecto.sh" ]; then
    echo -e "${RED}Eliminando limpiar_proyecto.sh (antiguo)${NC}"
    rm limpiar_proyecto.sh
    echo "✓ Eliminado"
fi

# Eliminar reset_db.py (obsoleto)
if [ -f "reset_db.py" ]; then
    echo -e "${RED}Eliminando reset_db.py (obsoleto)${NC}"
    rm reset_db.py
    echo "✓ Eliminado"
fi

# Eliminar exports/ (vacío)
if [ -d "exports" ]; then
    echo -e "${RED}Eliminando exports/ (vacío)${NC}"
    rm -rf exports/
    echo "✓ Eliminado"
fi

# Eliminar Roadmap.md (si existe)
if [ -f "Roadmap.md" ]; then
    if confirm "¿Eliminar Roadmap.md? (no es necesario para producción)"; then
        rm Roadmap.md
        echo "✓ Eliminado"
    fi
fi

echo -e "\n${YELLOW}PASO 2: Crear estructura de directorios${NC}"
echo "-------------------------------------------"

# Crear directorios si no existen
mkdir -p core
mkdir -p modules
mkdir -p features
mkdir -p data
mkdir -p docs

echo "✓ Directorios creados"

echo -e "\n${YELLOW}PASO 3: Reorganizar archivos${NC}"
echo "-------------------------------------------"

# Mover archivos a core/
echo "Moviendo archivos a core/..."
mv -n db_manager.py core/ 2>/dev/null && echo "  ✓ db_manager.py"
mv -n logger.py core/ 2>/dev/null && echo "  ✓ logger.py"
mv -n calculos.py core/ 2>/dev/null && echo "  ✓ calculos.py"
mv -n validaciones.py core/ 2>/dev/null && echo "  ✓ validaciones.py"
mv -n queries.py core/ 2>/dev/null && echo "  ✓ queries.py"

# Mover archivos a modules/
echo "Moviendo archivos a modules/..."
mv -n operador.py modules/ 2>/dev/null && echo "  ✓ operador.py"
mv -n boveda.py modules/ 2>/dev/null && echo "  ✓ boveda.py"
mv -n ciclos.py modules/ 2>/dev/null && echo "  ✓ ciclos.py"
mv -n dias.py modules/ 2>/dev/null && echo "  ✓ dias.py"
mv -n configuracion.py modules/ 2>/dev/null && echo "  ✓ configuracion.py"
mv -n mantenimiento.py modules/ 2>/dev/null && echo "  ✓ mantenimiento.py"

# Mover archivos a features/
echo "Moviendo archivos a features/..."
mv -n proyecciones.py features/ 2>/dev/null && echo "  ✓ proyecciones.py"
mv -n reportes.py features/ 2>/dev/null && echo "  ✓ reportes.py"
mv -n notas.py features/ 2>/dev/null && echo "  ✓ notas.py"
mv -n alertas.py features/ 2>/dev/null && echo "  ✓ alertas.py"
mv -n graficos.py features/ 2>/dev/null && echo "  ✓ graficos.py"

# Mover base de datos a data/
echo "Moviendo base de datos..."
mv -n arbitraje.db data/ 2>/dev/null && echo "  ✓ arbitraje.db"

# Mover documentación a docs/
echo "Moviendo documentación..."
cp README.md docs/ 2>/dev/null && echo "  ✓ README.md (copiado)"
cp INSTALL.md docs/ 2>/dev/null && echo "  ✓ INSTALL.md (copiado)"
cp CHANGELOG.md docs/ 2>/dev/null && echo "  ✓ CHANGELOG.md (copiado)"

echo -e "\n${GREEN}=========================================="
echo "LIMPIEZA COMPLETADA"
echo "==========================================${NC}"

echo -e "\n${YELLOW}Estructura final:${NC}"
tree -L 1 -d --dirsfirst 2>/dev/null || find . -maxdepth 1 -type d | sort

echo -e "\n${YELLOW}IMPORTANTE:${NC}"
echo "- Los archivos fueron MOVIDOS, no copiados"
echo "- Debes actualizar los imports en main.py"
echo "- Ejecuta: python main.py para verificar"

echo -e "\n${GREEN}¿Todo correcto? Continúa con:${NC}"
echo "  1. Actualizar imports en main.py"
echo "  2. Actualizar inicializar_bd.py"
echo "  3. Probar el sistema"
echo "  4. Commit a GitHub"
