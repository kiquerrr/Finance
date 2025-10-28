# test_sistema_completo.py

import pytest
import sqlite3
import os
from unittest.mock import patch
import sys
from datetime import datetime, timedelta

# Nombre del archivo de base de datos de prueba
TEST_DB = 'test_arbitraje.db'
ORIGINAL_SQLITE_CONNECT = sqlite3.connect

# ------------------------------------------------------------------------------------
# 1. FIXTURE DE CONEXIÓN (GLOBAL) - CREA TABLAS Y MOCKEA
# ------------------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def mock_db_connection():
    """
    Mockea sqlite3.connect, crea la estructura de tablas y recarga módulos.
    """
    
    # --- PASO A: Mock de la Conexión ---
    def mock_connect(*args, **kwargs):
        conn = ORIGINAL_SQLITE_CONNECT(TEST_DB, check_same_thread=False)
        conn.row_factory = sqlite3.Row 
        return conn

    with patch('sqlite3.connect', side_effect=mock_connect):
        
        # --- PASO B: CREACIÓN DE TABLAS (CRÍTICO) ---
        # Borrar DB anterior y crear la estructura antes de que los módulos se importen
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        
        # Usamos la conexión mockeada para crear las tablas
        conn = sqlite3.connect(TEST_DB) 
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS ciclos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha_inicio DATE, fecha_fin_estimada DATE, dias_planificados INTEGER, inversion_inicial REAL, estado TEXT, fecha_cierre TIMESTAMP, dias_operados INTEGER, ganancia_total REAL, capital_final REAL, roi_total REAL, notas TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS criptomonedas (id INTEGER PRIMARY KEY, nombre TEXT, simbolo TEXT, tipo TEXT, descripcion TEXT)")
        cursor.execute("INSERT OR IGNORE INTO criptomonedas (id, nombre, simbolo) VALUES (?, ?, ?)", (1, 'Bitcoin', 'BTC'))
        cursor.execute("CREATE TABLE IF NOT EXISTS compras (id INTEGER PRIMARY KEY AUTOINCREMENT, ciclo_id INTEGER, cripto_id INTEGER, cantidad REAL, monto_usd REAL, tasa REAL, fecha TIMESTAMP)")
        cursor.execute("CREATE TABLE IF NOT EXISTS boveda_ciclo (id INTEGER PRIMARY KEY AUTOINCREMENT, ciclo_id INTEGER, cripto_id INTEGER, cantidad REAL, precio_promedio REAL)")
        conn.commit()
        conn.close()

        # --- PASO C: Forzar Recarga de Módulos ---
        if 'ciclos' in sys.modules:
            del sys.modules['ciclos']
        if 'boveda' in sys.modules:
            del sys.modules['boveda']
        
        # Importamos los módulos de nuevo para que usen la DB con tablas
        from ciclos import crear_ciclo, obtener_ciclo_activo
        from boveda import registrar_compra
        
        yield crear_ciclo, obtener_ciclo_activo, registrar_compra

    # Limpieza final de la DB de prueba al terminar la sesión
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

# ------------------------------------------------------------------------------------
# 2. FIXTURE DE SETUP/TEARDOWN (POR FUNCIÓN) - SIMPLIFICADO
# ------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def setup_teardown_db():
    """Borra y recrea el contenido de las tablas entre tests para aislarlos."""
    
    # NOTA: La estructura de tablas ya fue creada por mock_db_connection
    conn = sqlite3.connect(TEST_DB) 
    cursor = conn.cursor()
    
    # Limpiar datos para aislar tests
    cursor.execute("DELETE FROM ciclos")
    cursor.execute("DELETE FROM boveda_ciclo")
    cursor.execute("DELETE FROM compras")
    
    conn.commit()
    conn.close()
    
    yield 

# ------------------------------------------------------------------------------------
# 3. TESTS con Mocking de Input
# ------------------------------------------------------------------------------------

def test_01_crear_ciclo(setup_teardown_db, monkeypatch, mock_db_connection):
    """Prueba que un nuevo ciclo se cree correctamente."""
    
    crear_ciclo, obtener_ciclo_activo, registrar_compra = mock_db_connection

    monkeypatch.setattr('builtins.input', lambda _: 's')
    
    # La limpieza de boveda_ciclo ya está en setup_teardown_db
    
    ciclo_id = crear_ciclo(dias_duracion=7)
    
    assert ciclo_id is not None, "La creación del ciclo falló"
    
    ciclo_activo = obtener_ciclo_activo()
    assert ciclo_activo is not None
    assert ciclo_activo['id'] == ciclo_id
    assert ciclo_activo['estado'] == 'activo'


def test_02_fondear_boveda(setup_teardown_db, monkeypatch, mock_db_connection):
    """Prueba el registro de una compra en un ciclo recién creado."""
    
    crear_ciclo, obtener_ciclo_activo, registrar_compra = mock_db_connection
    
    monkeypatch.setattr('builtins.input', lambda _: 's')
        
    crear_ciclo(dias_duracion=7)
    ciclo_activo = obtener_ciclo_activo()
    
    assert ciclo_activo is not None 
    
    ciclo_id = ciclo_activo['id']
    cripto_id = 1
    cantidad = 0.05
    monto_usd = 3000.00
    tasa = 60000.00 

    exito = registrar_compra(ciclo_id, cripto_id, cantidad, monto_usd, tasa)
    assert exito is True, "El registro de la compra falló."
    
    # Verificar que la bóveda se actualizó
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM boveda_ciclo WHERE ciclo_id = ? AND cripto_id = ?", (ciclo_id, cripto_id))
    
    boveda = cursor.fetchone()
    conn.close()
    
    assert boveda is not None
    assert boveda['cantidad'] == pytest.approx(0.05)
    assert boveda['precio_promedio'] == pytest.approx(60000.00)
