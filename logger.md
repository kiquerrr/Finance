# 📘 GUÍA DE INTEGRACIÓN - Logger y Calculadora

## 🎯 Archivos Creados

1. **`logger.py`** - Sistema de logging completo
2. **`calculos.py`** - Calculadora con fórmulas corregidas

---

## 🔧 PASO 1: Instalación

### Crear los archivos en tu proyecto:

```
proyecto/
├── logger.py          # ← NUEVO
├── calculos.py        # ← NUEVO
├── logs/              # ← Se crea automáticamente
│   ├── general.log
│   ├── operaciones.log
│   ├── calculos.log
│   ├── errores.log
│   ├── boveda.log
│   └── ciclos.log
├── boveda.py
├── dias.py
├── operador.py
└── main.py
```

---

## 🔧 PASO 2: Modificar `boveda.py`

### Agregar imports al inicio:

```python
from logger import log
from calculos import calc
```

### Modificar función de compra:

**ANTES:**
```python
def registrar_compra(ciclo_id, cripto_id, monto_usd, tasa):
    cantidad = monto_usd / tasa
    # ... insertar en BD
    print(f"Compra registrada: {cantidad} {cripto}")
```

**DESPUÉS:**
```python
def registrar_compra(ciclo_id, cripto_id, monto_usd, tasa):
    # Obtener nombre de cripto
    cripto = obtener_cripto_por_id(cripto_id)
    
    # Calcular cantidad
    cantidad = monto_usd / tasa
    
    # REGISTRAR EN LOG
    log.boveda_compra(
        cripto=cripto['nombre'],
        cantidad=cantidad,
        monto_usd=monto_usd,
        tasa=tasa,
        ciclo_id=ciclo_id
    )
    
    # Insertar en BD
    cursor.execute("""
        INSERT INTO compras (ciclo_id, cripto_id, cantidad, monto_usd, tasa, fecha)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (ciclo_id, cripto_id, cantidad, monto_usd, tasa))
    
    print(f"✅ Compra registrada: {cantidad} {cripto['nombre']}")
```

---

## 🔧 PASO 3: Modificar `dias.py`

### Función para iniciar día:

```python
from logger import log
from calculos import calc

def iniciar_dia(ciclo_id, capital_inicial):
    """Inicia un nuevo día de operación"""
    
    # Obtener criptos disponibles
    criptos_disponibles = obtener_criptos_disponibles(ciclo_id)
    
    # Preparar datos para log
    criptos_info = [
        (c['nombre'], c['cantidad'], c['valor_usd']) 
        for c in criptos_disponibles
    ]
    
    # Insertar día en BD
    cursor.execute("""
        INSERT INTO dias (ciclo_id, numero_dia, capital_inicial, estado, fecha)
        VALUES (?, ?, ?, 'abierto', datetime('now'))
    """, (ciclo_id, dia_num, capital_inicial))
    
    dia_id = cursor.lastrowid
    
    # REGISTRAR EN LOG
    log.dia_iniciado(
        ciclo_id=ciclo_id,
        dia_num=dia_num,
        capital_inicial=capital_inicial,
        criptos_disponibles=criptos_info
    )
    
    return dia_id
```

### Función para registrar venta:

```python
def registrar_venta(dia_id, cripto_id, cantidad, precio_venta):
    """Registra una venta con cálculos correctos"""
    
    # Obtener costo promedio
    costo_promedio = obtener_costo_promedio(cripto_id)
    
    # CALCULAR VENTA CON LA CALCULADORA
    resultado = calc.calcular_venta(
        cantidad=cantidad,
        costo_unitario=costo_promedio,
        precio_venta=precio_venta
    )
    
    if not resultado:
        log.error("Error al calcular venta", "Valores inválidos")
        return None
    
    # Insertar en BD
    cursor.execute("""
        INSERT INTO ventas (
            dia_id, cripto_id, cantidad, precio_unitario,
            costo_total, monto_venta, comision, efectivo_recibido,
            ganancia_bruta, ganancia_neta, fecha
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        dia_id, cripto_id, cantidad, precio_venta,
        resultado['costo_total'],
        resultado['monto_venta'],
        resultado['comision'],
        resultado['efectivo_recibido'],
        resultado['ganancia_bruta'],
        resultado['ganancia_neta']
    ))
    
    venta_id = cursor.lastrowid
    
    # Actualizar cantidad en bóveda
    actualizar_cantidad_boveda(cripto_id, -cantidad)
    
    # REGISTRAR EN LOG
    cripto = obtener_cripto_por_id(cripto_id)
    venta_num = obtener_num_venta_del_dia(dia_id)
    
    log.venta_registrada(
        venta_num=venta_num,
        cripto=cripto['nombre'],
        cantidad_vendida=cantidad,
        precio_unitario=precio_venta,
        monto_total=resultado['monto_venta'],
        comision_pagada=resultado['comision'],
        ganancia_neta=resultado['ganancia_neta']
    )
    
    print(f"\n✅ Venta registrada:")
    print(f"   {cantidad} {cripto['nombre']} x ${precio_venta:.4f}")
    print(f"   Efectivo recibido: ${resultado['efectivo_recibido']:.2f}")
    print(f"   Ganancia neta: ${resultado['ganancia_neta']:.2f}")
    
    return resultado
```

### Función para cerrar día:

```python
def cerrar_dia(dia_id):
    """Cierra el día con cálculos correctos"""
    
    # Obtener datos del día
    dia = obtener_dia(dia_id)
    ventas = obtener_ventas_del_dia(dia_id)
    
    # Obtener capital final en criptos
    capital_final_criptos = calcular_capital_actual_criptos(dia['ciclo_id'])
    
    # CALCULAR RESUMEN DEL DÍA
    resumen = calc.calcular_resumen_dia(
        capital_inicial=dia['capital_inicial'],
        ventas=ventas,
        capital_final_criptos=capital_final_criptos
    )
    
    # Actualizar día en BD
    cursor.execute("""
        UPDATE dias SET
            capital_final = ?,
            efectivo_recibido = ?,
            ganancia_bruta = ?,
            ganancia_neta = ?,
            comisiones_pagadas = ?,
            estado = 'cerrado',
            fecha_cierre = datetime('now')
        WHERE id = ?
    """, (
        resumen['capital_final_total'],
        resumen['efectivo_recibido'],
        resumen['total_ganancia_bruta'],
        resumen['total_ganancia_neta'],
        resumen['total_comisiones'],
        dia_id
    ))
    
    # REGISTRAR EN LOG
    log.dia_cerrado(
        ciclo_id=dia['ciclo_id'],
        dia_num=dia['numero_dia'],
        capital_inicial=dia['capital_inicial'],
        capital_final=resumen['capital_final_total'],
        ganancia_dia=resumen['total_ganancia_neta'],
        ventas_realizadas=resumen['num_ventas']
    )
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("CIERRE DEL DÍA DE OPERACIÓN")
    print("="*60)
    print(f"\nCapital inicial: ${dia['capital_inicial']:.2f}")
    print(f"Capital en criptos: ${resumen['capital_final_criptos']:.2f}")
    print(f"Efectivo recibido: ${resumen['efectivo_recibido']:.2f}")
    print(f"Capital final total: ${resumen['capital_final_total']:.2f}")
    print(f"\nComisiones pagadas: ${resumen['total_comisiones']:.2f}")
    print(f"Ganancia bruta: ${resumen['total_ganancia_bruta']:.2f}")
    print(f"Ganancia neta: ${resumen['total_ganancia_neta']:.2f}")
    print(f"\nVentas realizadas: {resumen['num_ventas']}")
    print("="*60)
    
    return resumen
```

---

## 🔧 PASO 4: Agregar tabla de efectivo en banco

### SQL para crear tabla:

```sql
CREATE TABLE IF NOT EXISTS efectivo_banco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ciclo_id INTEGER NOT NULL,
    dia_id INTEGER,
    monto REAL NOT NULL,
    concepto TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ciclo_id) REFERENCES ciclos(id),
    FOREIGN KEY (dia_id) REFERENCES dias(id)
);
```

### Función para registrar efectivo:

```python
def registrar_efectivo_recibido(dia_id, ciclo_id, monto, concepto):
    """Registra efectivo recibido en banco"""
    cursor.execute("""
        INSERT INTO efectivo_banco (ciclo_id, dia_id, monto, concepto, fecha)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (ciclo_id, dia_id, monto, concepto))
    
    log.info(
        f"Efectivo registrado: ${monto:.2f} - {concepto}",
        categoria='boveda'
    )
```

---

## 🔧 PASO 5: Corregir cálculo de capital

### Función correcta para calcular capital:

```python
def calcular_capital_actual(ciclo_id):
    """Calcula el capital actual total (criptos + efectivo)"""
    
    # Capital en criptos
    cursor.execute("""
        SELECT 
            c.nombre,
            c.simbolo,
            bc.cantidad,
            bc.precio_promedio
        FROM boveda_ciclo bc
        JOIN criptomonedas c ON bc.cripto_id = c.id
        WHERE bc.ciclo_id = ? AND bc.cantidad > 0
    """, (ciclo_id,))
    
    criptos = cursor.fetchall()
    
    # Calcular valor de cada cripto
    criptos_info = []
    total_criptos = 0
    
    for cripto in criptos:
        valor = cripto['cantidad'] * cripto['precio_promedio']
        total_criptos += valor
        criptos_info.append({
            'nombre': cripto['nombre'],
            'simbolo': cripto['simbolo'],
            'cantidad': cripto['cantidad'],
            'precio': cripto['precio_promedio'],
            'valor': valor
        })
    
    # Efectivo en banco
    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0) as total_efectivo
        FROM efectivo_banco
        WHERE ciclo_id = ?
    """, (ciclo_id,))
    
    total_efectivo = cursor.fetchone()['total_efectivo']
    
    # Total
    capital_total = total_criptos + total_efectivo
    
    return {
        'criptos': criptos_info,
        'total_criptos': total_criptos,
        'efectivo': total_efectivo,
        'total': capital_total
    }
```

---

## 🔧 PASO 6: Testing

### Script de prueba:

```python
# test_integracion.py

from logger import log
from calculos import calc

def test_completo():
    print("\n" + "="*60)
    print("TEST DE INTEGRACIÓN COMPLETA")
    print("="*60)
    
    # Test 1: Compra
    print("\n--- TEST 1: Compra de 1000 USDT ---")
    log.boveda_compra(
        cripto="USDT",
        cantidad=1000,
        monto_usd=1000,
        tasa=1.00,
        ciclo_id=1
    )
    
    # Test 2: Cálculo de venta
    print("\n--- TEST 2: Venta de 250 USDT a $1.05 ---")
    resultado = calc.calcular_venta(
        cantidad=250,
        costo_unitario=1.00,
        precio_venta=1.05
    )
    
    print(f"Efectivo recibido: ${resultado['efectivo_recibido']:.2f}")
    print(f"Ganancia neta: ${resultado['ganancia_neta']:.2f}")
    
    # Test 3: Ver logs
    print("\n--- TEST 3: Últimas líneas del log ---")
    from logger import ver_log
    print(ver_log('operaciones', 10))

if __name__ == "__main__":
    test_completo()
```

---

## 📊 PASO 7: Estructura de BD Actualizada

```sql
-- Agregar columnas faltantes a la tabla dias
ALTER TABLE dias ADD COLUMN efectivo_recibido REAL DEFAULT 0;
ALTER TABLE dias ADD COLUMN comisiones_pagadas REAL DEFAULT 0;
ALTER TABLE dias ADD COLUMN ganancia_bruta REAL DEFAULT 0;

-- Agregar columnas a la tabla ventas
ALTER TABLE ventas ADD COLUMN efectivo_recibido REAL DEFAULT 0;
ALTER TABLE ventas ADD COLUMN ganancia_bruta REAL DEFAULT 0;
```

---

## ✅ CHECKLIST DE INTEGRACIÓN

- [ ] Copiar `logger.py` al proyecto
- [ ] Copiar `calculos.py` al proyecto
- [ ] Crear tabla `efectivo_banco`
- [ ] Actualizar columnas en tabla `dias`
- [ ] Actualizar columnas en tabla `ventas`
- [ ] Modificar `boveda.py` con imports
- [ ] Modificar `dias.py` con nuevas funciones
- [ ] Actualizar `operador.py` para usar calc y log
- [ ] Ejecutar script de testing
- [ ] Revisar logs generados
- [ ] Probar ciclo completo

---

## 🎯 PRÓXIMOS PASOS

Una vez integrado esto, continuaremos con:

1. ✅ Separación de Configuración y Mantenimiento
2. ✅ Corregir cierre automático de ciclos
3. ✅ Implementar interés compuesto
4. ✅ Agregar registro de inversión inicial
5. ✅ Mejorar visualización de capital
