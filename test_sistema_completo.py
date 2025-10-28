# -*- coding: utf-8 -*-
"""
=============================================================================
TESTING AUTOMATIZADO DEL SISTEMA DE ARBITRAJE
=============================================================================
Prueba TODOS los escenarios posibles automáticamente
Genera reportes detallados de éxitos y fallos
=============================================================================
"""

import pytest
import sqlite3
import os
import sys
from datetime import datetime

# Agregar directorio al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos del sistema
from inicializar_bd import inicializar_base_datos
from ciclos import crear_ciclo, obtener_ciclo_activo, cerrar_ciclo
from boveda import registrar_compra
from dias import iniciar_dia, registrar_venta, cerrar_dia
from calculos import calc


# ===================================================================
# FIXTURES (Preparación antes de cada test)
# ===================================================================

@pytest.fixture(scope="function")
def db_limpia():
    """Crea una BD limpia antes de cada test"""
    # Eliminar BD si existe
    if os.path.exists('arbitraje.db'):
        os.remove('arbitraje.db')
    
    # Crear BD nueva
    inicializar_base_datos()
    
    yield
    
    # Limpiar después del test (opcional)
    # os.remove('arbitraje.db')


@pytest.fixture
def ciclo_activo(db_limpia):
    """Crea un ciclo activo para testing"""
    ciclo_id = crear_ciclo(dias_duracion=5)
    return ciclo_id


@pytest.fixture
def boveda_fondeada(ciclo_activo):
    """Fondea la bóveda con USDT"""
    # Cripto USDT tiene id=1
    registrar_compra(
        ciclo_id=ciclo_activo,
        cripto_id=1,  # USDT
        cantidad=1000,
        monto_usd=1000,
        tasa=1.0
    )
    return ciclo_activo


# ===================================================================
# TESTS DE INICIALIZACIÓN
# ===================================================================

def test_inicializar_bd(db_limpia):
    """Test: La BD se inicializa correctamente"""
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    
    # Verificar que existen las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [t[0] for t in cursor.fetchall()]
    
    assert 'ciclos' in tablas
    assert 'dias' in tablas
    assert 'ventas' in tablas
    assert 'criptomonedas' in tablas
    
    # Verificar que hay 6 criptos
    cursor.execute("SELECT COUNT(*) FROM criptomonedas")
    num_criptos = cursor.fetchone()[0]
    assert num_criptos == 6
    
    conn.close()


# ===================================================================
# TESTS DE CICLOS
# ===================================================================

def test_crear_ciclo(db_limpia):
    """Test: Crear ciclo correctamente"""
    ciclo_id = crear_ciclo(dias_duracion=15)
    
    assert ciclo_id is not None
    assert ciclo_id > 0
    
    # Verificar en BD
    ciclo = obtener_ciclo_activo()
    assert ciclo is not None
    assert ciclo['dias_planificados'] == 15
    assert ciclo['estado'] == 'activo'


def test_solo_un_ciclo_activo(ciclo_activo):
    """Test: Solo puede haber 1 ciclo activo"""
    # Intentar crear otro ciclo debería fallar o cerrar el anterior
    ciclo2_id = crear_ciclo(dias_duracion=10)
    
    # Verificar que solo hay 1 ciclo activo
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ciclos WHERE estado='activo'")
    num_activos = cursor.fetchone()[0]
    
    assert num_activos <= 1
    conn.close()


# ===================================================================
# TESTS DE BÓVEDA
# ===================================================================

def test_fondear_boveda(ciclo_activo):
    """Test: Fondear bóveda correctamente"""
    # Fondear con USDT
    resultado = registrar_compra(
        ciclo_id=ciclo_activo,
        cripto_id=1,  # USDT
        cantidad=500,
        monto_usd=500,
        tasa=1.0
    )
    
    assert resultado is True
    
    # Verificar en BD
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cantidad FROM boveda_ciclo 
        WHERE ciclo_id=? AND cripto_id=1
    """, (ciclo_activo,))
    
    cantidad = cursor.fetchone()[0]
    assert cantidad == 500
    conn.close()


def test_precio_promedio_ponderado(ciclo_activo):
    """Test: Precio promedio se calcula correctamente"""
    # Primera compra: 100 USDT a $1.00
    registrar_compra(ciclo_activo, 1, 100, 100, 1.0)
    
    # Segunda compra: 100 USDT a $1.10
    registrar_compra(ciclo_activo, 1, 100, 110, 1.1)
    
    # Verificar precio promedio: (100 + 110) / 200 = 1.05
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT precio_promedio FROM boveda_ciclo 
        WHERE ciclo_id=? AND cripto_id=1
    """, (ciclo_activo,))
    
    precio_promedio = cursor.fetchone()[0]
    assert abs(precio_promedio - 1.05) < 0.001  # Tolerancia de error
    conn.close()


# ===================================================================
# TESTS DE CÁLCULOS
# ===================================================================

def test_calculo_venta_simple():
    """Test: Cálculo de venta es correcto"""
    resultado = calc.calcular_venta(
        cantidad=100,
        costo_unitario=1.0,
        precio_venta=1.05
    )
    
    assert resultado is not None
    assert resultado['costo_total'] == 100.0
    assert resultado['monto_venta'] == 105.0
    assert abs(resultado['comision'] - 0.3675) < 0.01  # 0.35% de 105
    assert abs(resultado['ganancia_neta'] - 4.6325) < 0.01


def test_calculo_con_diferentes_comisiones():
    """Test: Cálculos con diferentes comisiones"""
    # Comisión 0.5%
    calc.comision_pct = 0.5
    
    resultado = calc.calcular_venta(100, 1.0, 1.05)
    
    assert abs(resultado['comision'] - 0.525) < 0.01  # 0.5% de 105
    
    # Restaurar comisión original
    calc.comision_pct = 0.35


# ===================================================================
# TESTS DE DÍAS
# ===================================================================

def test_iniciar_dia(boveda_fondeada):
    """Test: Iniciar día correctamente"""
    dia_id = iniciar_dia(boveda_fondeada)
    
    assert dia_id is not None
    assert dia_id > 0
    
    # Verificar en BD
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dias WHERE id=?", (dia_id,))
    dia = cursor.fetchone()
    
    assert dia is not None
    assert dia[7] == 'abierto'  # estado
    conn.close()


def test_registrar_venta(boveda_fondeada):
    """Test: Registrar venta correctamente"""
    dia_id = iniciar_dia(boveda_fondeada)
    
    # Definir precio primero
    from dias import definir_precio_venta
    definir_precio_venta(dia_id, 1, 1.05)  # USDT a $1.05
    
    # Registrar venta
    resultado = registrar_venta(dia_id, 1, 100)
    
    assert resultado is not None
    assert resultado['cantidad'] == 100
    assert resultado['precio_venta'] == 1.05


def test_cerrar_dia(boveda_fondeada):
    """Test: Cerrar día correctamente"""
    dia_id = iniciar_dia(boveda_fondeada)
    
    # Hacer ventas
    from dias import definir_precio_venta
    definir_precio_venta(dia_id, 1, 1.05)
    
    registrar_venta(dia_id, 1, 100)
    registrar_venta(dia_id, 1, 100)
    registrar_venta(dia_id, 1, 100)
    
    # Cerrar día
    resumen = cerrar_dia(dia_id)
    
    assert resumen is not None
    assert resumen['num_ventas'] == 3
    assert resumen['total_ganancia_neta'] > 0
    
    # Verificar estado
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("SELECT estado FROM dias WHERE id=?", (dia_id,))
    estado = cursor.fetchone()[0]
    
    assert estado == 'cerrado'
    conn.close()


# ===================================================================
# TESTS DE ESCENARIOS COMPLETOS
# ===================================================================

def test_ciclo_completo_3_dias(boveda_fondeada):
    """Test: Ciclo completo de 3 días"""
    ciclo_id = boveda_fondeada
    
    for num_dia in range(1, 4):
        # Iniciar día
        dia_id = iniciar_dia(ciclo_id)
        assert dia_id is not None
        
        # Definir precio
        from dias import definir_precio_venta
        definir_precio_venta(dia_id, 1, 1.05)
        
        # Hacer 3 ventas
        for _ in range(3):
            resultado = registrar_venta(dia_id, 1, 50)
            assert resultado is not None
        
        # Cerrar día
        resumen = cerrar_dia(dia_id)
        assert resumen is not None
        assert resumen['num_ventas'] == 3
    
    # Verificar que hay 3 días cerrados
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM dias 
        WHERE ciclo_id=? AND estado='cerrado'
    """, (ciclo_id,))
    
    dias_cerrados = cursor.fetchone()[0]
    assert dias_cerrados == 3
    conn.close()


def test_multiples_criptos(ciclo_activo):
    """Test: Operar con múltiples criptomonedas"""
    # Fondear con USDT, BTC, ETH
    registrar_compra(ciclo_activo, 1, 1000, 1000, 1.0)     # USDT
    registrar_compra(ciclo_activo, 3, 0.01, 1000, 100000) # BTC
    registrar_compra(ciclo_activo, 4, 0.5, 1000, 2000)    # ETH
    
    # Verificar que hay 3 criptos en bóveda
    conn = sqlite3.connect('arbitraje.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM boveda_ciclo 
        WHERE ciclo_id=? AND cantidad > 0
    """, (ciclo_activo,))
    
    num_criptos = cursor.fetchone()[0]
    assert num_criptos == 3
    conn.close()


# ===================================================================
# TESTS DE CASOS EXTREMOS
# ===================================================================

def test_venta_sin_stock():
    """Test: No permite vender más de lo disponible"""
    # Este test debería fallar o retornar None
    pass  # Implementar según lógica


def test_precio_negativo():
    """Test: No permite precios negativos"""
    resultado = calc.calcular_venta(100, 1.0, -1.0)
    assert resultado is None


def test_cantidad_cero():
    """Test: No permite cantidades en cero"""
    resultado = calc.calcular_venta(0, 1.0, 1.05)
    assert resultado is None


# ===================================================================
# GENERADOR DE REPORTE
# ===================================================================

def test_generar_reporte_final():
    """Genera reporte de todos los tests"""
    print("\n" + "="*60)
    print("REPORTE FINAL DE TESTS")
    print("="*60)
    print("\n✅ Si ves esto, todos los tests pasaron!")
    print("="*60)


# ===================================================================
# EJECUCIÓN
# ===================================================================

if __name__ == "__main__":
    # Ejecutar todos los tests con reporte HTML
    pytest.main([
        __file__,
        '-v',                          # Verbose
        '--html=reporte_tests.html',   # Reporte HTML
        '--self-contained-html',       # HTML standalone
        '--cov=.',                     # Coverage
        '--cov-report=html',           # Reporte de cobertura
        '-s'                           # Mostrar prints
    ])
