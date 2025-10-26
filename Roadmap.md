# 📋 ROADMAP DE MEJORAS - Sistema Arbitraje P2P

## ✅ COMPLETADO (En esta sesión)

1. ✅ Operador.py arreglado (código completo)
2. ✅ Directorios `backups/` y `exports/` creados automáticamente
3. ✅ Sistema de backups mejorado con limpieza automática
4. ✅ Función de restaurar BD desde backup
5. ✅ Base de datos preparada para multi-cripto
6. ✅ Exportación CSV a carpeta `exports/`

---

## 🔄 EN PROGRESO (Siguiente fase)

### **PRIORIDAD ALTA** 🔴

#### 1. **Sistema de Criptomonedas Múltiples**
**Estado:** Base de datos lista, falta implementación

**Archivos a modificar:**
- `boveda.py` - Agregar selector de cripto en fondeo
- `operador.py` - Trabajar con cripto específica
- `estadisticas.py` - Filtrar por cripto

**Cambios necesarios:**
```python
# En fondeo:
- Preguntar: ¿Qué cripto vas a fondear? (USDT, BTC, ETH, etc.)
- Calcular cantidad según tasa de compra
```

#### 2. **Fondeo Mejorado con FIAT**
**Estado:** Pendiente

**Lógica nueva:**
```
Usuario ingresa: $100 USD
Sistema pregunta: ¿Qué cripto comprar? → USDT
Sistema consulta tasa: 1 USDT = $1.05
Sistema calcula: 100 / 1.05 = 95.238 USDT
Sistema registra: 95.238 USDT comprados por $100
```

**Archivos:**
- `boveda.py` - Reescribir función `fondear_boveda()`

#### 3. **Configuración de APIs** (NUEVA OPCIÓN [6])
**Estado:** Tabla creada, falta interfaz

**Menú nuevo en main.py:**
```
[6] ⚙️  Configuración de APIs y Plataformas
    [1] Agregar/Editar API de Plataforma
    [2] Ver APIs Configuradas
    [3] Probar Conexión API
    [4] Actualizar Tasas desde API
    [5] Volver
```

**Datos a guardar:**
- Plataforma (Binance, Kraken, etc.)
- Cripto (USDT, BTC, ETH, etc.)
- API Key
- API Secret
- Comisión de compra
- Comisión de venta

---

### **PRIORIDAD MEDIA** 🟡

#### 4. **Consultas Mejoradas en Estadísticas**

**Opción 1 - Ver Resumen General:**
```
Agregar:
- Total invertido histórico
- ROI promedio
- Mejor mes/semana
- Gráfico ASCII de ganancias
```

**Opción 2 - Listar Ciclos:**
```
Agregar filtros:
- Por fecha (rango)
- Por cripto
- Por monto mínimo de ganancia
- Ordenar por ganancia/fecha
```

**Opción 3 - Ver Ciclo Activo:**
```
Agregar:
- Cripto operada
- Tasa promedio de compra
- Tasa promedio de venta
- Hora de inicio del ciclo
- Tiempo transcurrido
- Proyección de ganancia
```

**Opción 4 - Ver Detalle de Ciclo:**
```
Mejorar:
- Búsqueda por ID, fecha o rango
- Mostrar todas las transacciones
- Calcular métricas del ciclo
```

#### 5. **Ver Historial de Transacciones (Bóveda)**

**Agregar filtros:**
- Por tipo (compra/venta)
- Por cripto
- Por fecha (día específico, rango)
- Por monto mínimo
- Paginación (10, 25, 50 resultados)

---

### **PRIORIDAD BAJA** 🟢

#### 6. **Integración con APIs Reales**
**Estado:** Futuro

**APIs a integrar:**
- Binance API
- Kraken API  
- Coinbase API

**Funcionalidades:**
- Consultar tasas en tiempo real
- Actualizar comisiones automáticamente
- Sincronizar transacciones (opcional)

#### 7. **Dashboard Visual**
**Estado:** Futuro lejano

- Gráficos con matplotlib
- Reportes PDF
- Interfaz gráfica (Tkinter/PyQt)

---

## 📝 DETALLE DE IMPLEMENTACIÓN

### **FASE 1: Multi-Cripto y Fondeo Mejorado** (2-3 horas)

#### Paso 1: Actualizar `boveda.py`

```python
def fondear_boveda_mejorado():
    # 1. Verificar ciclo activo
    # 2. Mostrar criptos disponibles
    # 3. Pedir monto en FIAT
    # 4. Consultar tasa de compra (API o manual)
    # 5. Calcular cantidad de cripto
    # 6. Mostrar resumen
    # 7. Confirmar y registrar
```

**Ejemplo de flujo:**
```
¿Qué cripto vas a comprar?
[1] USDT (Tether)
[2] BTC (Bitcoin)
[3] ETH (Ethereum)
Selecciona: 1

Ingresa el monto en USD que vas a invertir: 1000

🔍 Consultando tasa de compra para USDT...
💱 Tasa actual: 1 USDT = $1.0520 USD
📊 Con $1000 comprarás: 950.57 USDT

¿Confirmar compra? (s/n):
```

#### Paso 2: Agregar selector de cripto en operador

```python
def analizar_mercado(costo_promedio, cripto):
    # Añadir el símbolo de la cripto en mensajes
    print(f"Operando con {cripto}")
    print(f"Precio sugerido de {cripto}: ${precio:.4f}")
```

#### Paso 3: Actualizar estadísticas con filtros

```python
def listar_ciclos_con_filtros():
    print("Filtrar por:")
    print("[1] Todos los ciclos")
    print("[2] Por cripto")
    print("[3] Por rango de fechas")
    print("[4] Por ganancia mínima")
    
    # Implementar lógica de filtros
```

---

### **FASE 2: Configuración de APIs** (3-4 horas)

#### Crear nuevo módulo: `apis.py`

```python
# apis.py
import sqlite3

def agregar_api():
    """Agrega configuración de API."""
    plataforma = input("Plataforma (ej: Binance): ")
    cripto = input("Cripto (ej: USDT): ")
    api_key = input("API Key: ")
    api_secret = input("API Secret (oculto): ")
    comision_compra = float(input("Comisión de compra %: "))
    comision_venta = float(input("Comisión de venta %: "))
    
    # Guardar en BD
    
def consultar_tasa_api(plataforma, cripto):
    """Consulta tasa desde API configurada."""
    # Implementar llamada a API
    pass

def actualizar_tasas():
    """Actualiza todas las tasas desde APIs."""
    # Para cada API configurada:
    #   - Consultar tasa actual
    #   - Actualizar en configuración
    pass
```

#### Integrar en `main.py`:

```python
def modulo_apis():
    while True:
        print("==== Configuración de APIs ====")
        print("[1] Agregar/Editar API")
        print("[2] Ver APIs Configuradas")
        print("[3] Probar Conexión")
        print("[4] Actualizar Tasas")
        print("[5] Volver")
        
        # Llamar funciones de apis.py
```

---

### **FASE 3: Mejoras en Consultas** (2 horas)

#### Actualizar `estadisticas.py`:

1. **Consultar estadísticas generales:**
```python
# Agregar:
- Total invertido histórico
- ROI = (ganancia_total / inversion_total) * 100
- Ciclo más rentable (por ROI, no solo por monto)
- Promedio de días por ciclo
```

2. **Ver ciclo activo:**
```python
# Agregar:
- Hora de inicio (extraer de fecha_inicio)
- Tiempo transcurrido en días/horas
- Proyección: "Si cierras ahora ganarías $X"
- Cripto principal operada
```

3. **Ver detalle de ciclo:**
```python
# Mejorar búsqueda:
def buscar_ciclo():
    print("[1] Por ID")
    print("[2] Por rango de fechas")
    print("[3] Por cripto")
    
    opcion = input("Selecciona: ")
    
    if opcion == '1':
        ciclo_id = int(input("ID del ciclo: "))
        mostrar_detalle(ciclo_id)
    elif opcion == '2':
        fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ")
        fecha_fin = input("Fecha fin (YYYY-MM-DD): ")
        listar_ciclos_en_rango(fecha_inicio, fecha_fin)
    elif opcion == '3':
        cripto = input("Cripto (ej: USDT): ")
        listar_ciclos_por_cripto(cripto)
```

---

## 🎯 PLAN DE EJECUCIÓN RECOMENDADO

### **Semana 1: Fundamentos Multi-Cripto**
- ✅ Día 1-2: Database actualizada (HECHO)
- 🔄 Día 3: Fondeo mejorado con FIAT
- 🔄 Día 4: Selector de cripto en operador
- 🔄 Día 5: Testing y correcciones

### **Semana 2: APIs y Automatización**
- ⏳ Día 1-2: Módulo apis.py básico
- ⏳ Día 3: Integración con Binance API (ejemplo)
- ⏳ Día 4: Actualización automática de tasas
- ⏳ Día 5: Testing de APIs

### **Semana 3: Mejoras en Consultas**
- ⏳ Día 1: Filtros en estadísticas
- ⏳ Día 2: Búsquedas avanzadas
- ⏳ Día 3: Consultas más descriptivas
- ⏳ Día 4-5: Testing y documentación

---

## 📦 ARCHIVOS A CREAR/MODIFICAR

### **Archivos Nuevos:**
1. ✅ `backups/` (directorio) - CREADO
2. ✅ `exports/` (directorio) - CREADO
3. ⏳ `apis.py` - Gestión de APIs - **PENDIENTE**
4. ⏳ `criptomonedas.py` - Catálogo de criptos - **PENDIENTE**

### **Archivos a Modificar:**

#### **ALTA PRIORIDAD:**
1. ✅ `database.py` - Base multi-cripto - **COMPLETADO**
2. 🔄 `boveda.py` - Fondeo mejorado - **EN PROGRESO**
3. 🔄 `operador.py` - Multi-cripto - **EN PROGRESO**
4. ⏳ `main.py` - Agregar opción [6] APIs - **PENDIENTE**

#### **MEDIA PRIORIDAD:**
5. ⏳ `estadisticas.py` - Filtros y consultas - **PENDIENTE**
6. ⏳ `utils.py` - Funciones para APIs - **PENDIENTE**

---

## 💡 SUGERENCIAS DE IMPLEMENTACIÓN

### **1. Sistema de Criptomonedas (criptomonedas.py)**

```python
# criptomonedas.py
CRIPTOS_DISPONIBLES = {
    'USDT': {
        'nombre': 'Tether',
        'simbolo': 'USDT',
        'decimales': 4,
        'tipo': 'stablecoin'
    },
    'BTC': {
        'nombre': 'Bitcoin',
        'simbolo': 'BTC',
        'decimales': 8,
        'tipo': 'crypto'
    },
    'ETH': {
        'nombre': 'Ethereum',
        'simbolo': 'ETH',
        'decimales': 6,
        'tipo': 'crypto'
    },
    'USDC': {
        'nombre': 'USD Coin',
        'simbolo': 'USDC',
        'decimales': 4,
        'tipo': 'stablecoin'
    }
}

def listar_criptos():
    """Muestra lista de criptos disponibles."""
    print("\n💰 CRIPTOMONEDAS DISPONIBLES:")
    for i, (codigo, info) in enumerate(CRIPTOS_DISPONIBLES.items(), 1):
        print(f"[{i}] {info['nombre']} ({codigo}) - {info['tipo']}")

def seleccionar_cripto():
    """Permite al usuario seleccionar una cripto."""
    listar_criptos()
    while True:
        try:
            opcion = int(input("\nSelecciona una opción: "))
            if 1 <= opcion <= len(CRIPTOS_DISPONIBLES):
                cripto_codigo = list(CRIPTOS_DISPONIBLES.keys())[opcion - 1]
                return cripto_codigo
            else:
                print("❌ Opción inválida.")
        except ValueError:
            print("❌ Ingresa un número válido.")

def obtener_info_cripto(codigo):
    """Obtiene información de una cripto."""
    return CRIPTOS_DISPONIBLES.get(codigo.upper())
```

### **2. Módulo de APIs (apis.py)**

```python
# apis.py
import sqlite3
import requests
from datetime import datetime

class GestorAPIs:
    def __init__(self):
        self.conn = sqlite3.connect('arbitraje.db')
    
    def agregar_api(self, plataforma, cripto, api_key, api_secret, 
                    comision_compra, comision_venta):
        """Agrega o actualiza configuración de API."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO apis_config 
            (plataforma, cripto, api_key, api_secret, comision_compra, comision_venta, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (plataforma, cripto, api_key, api_secret, comision_compra, comision_venta))
        self.conn.commit()
        print(f"✅ API de {plataforma} para {cripto} configurada.")
    
    def obtener_api(self, plataforma, cripto):
        """Obtiene configuración de una API."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM apis_config 
            WHERE plataforma = ? AND cripto = ? AND activo = 1
        """, (plataforma, cripto))
        return cursor.fetchone()
    
    def listar_apis(self):
        """Lista todas las APIs configuradas."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM apis_config WHERE activo = 1")
        return cursor.fetchall()
    
    def consultar_tasa_binance(self, cripto):
        """Consulta tasa actual desde Binance API (ejemplo)."""
        try:
            # API pública de Binance (no requiere autenticación)
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={cripto}USDT"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                precio = float(data['price'])
                return precio
            else:
                print(f"⚠️  Error al consultar API: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return None
    
    def probar_conexion(self, plataforma, cripto):
        """Prueba la conexión con una API."""
        print(f"\n🔍 Probando conexión con {plataforma} para {cripto}...")
        
        if plataforma.lower() == 'binance':
            tasa = self.consultar_tasa_binance(cripto)
            if tasa:
                print(f"✅ Conexión exitosa!")
                print(f"💱 Precio actual de {cripto}: ${tasa:.4f}")
                return True
            else:
                print(f"❌ No se pudo conectar con {plataforma}")
                return False
        else:
            print(f"⚠️  Plataforma {plataforma} aún no implementada.")
            return False
    
    def actualizar_todas_tasas(self):
        """Actualiza tasas de todas las APIs configuradas."""
        apis = self.listar_apis()
        
        if not apis:
            print("\n⚠️  No hay APIs configuradas.")
            return
        
        print("\n🔄 Actualizando tasas desde APIs...")
        
        for api in apis:
            plataforma = api[1]
            cripto = api[2]
            
            if plataforma.lower() == 'binance':
                tasa = self.consultar_tasa_binance(cripto)
                if tasa:
                    print(f"✅ {cripto} en {plataforma}: ${tasa:.4f}")
                else:
                    print(f"❌ {cripto} en {plataforma}: Error")
        
        print("\n✅ Actualización completada.")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def menu_apis():
    """Menú de gestión de APIs."""
    gestor = GestorAPIs()
    
    while True:
        print("\n" + "=" * 60)
        print("CONFIGURACIÓN DE APIs Y PLATAFORMAS")
        print("=" * 60)
        print("[1] Agregar/Editar API de Plataforma")
        print("[2] Ver APIs Configuradas")
        print("[3] Probar Conexión con API")
        print("[4] Actualizar Tasas desde APIs")
        print("[5] Eliminar API")
        print("[6] Volver al Menú Principal")
        print("=" * 60)
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == '1':
            agregar_api_interactivo(gestor)
        elif opcion == '2':
            listar_apis_configuradas(gestor)
        elif opcion == '3':
            probar_conexion_interactivo(gestor)
        elif opcion == '4':
            gestor.actualizar_todas_tasas()
            input("\nPresiona Enter para continuar...")
        elif opcion == '5':
            eliminar_api_interactivo(gestor)
        elif opcion == '6':
            break
        else:
            print("\n❌ Opción no válida.")

def agregar_api_interactivo(gestor):
    """Interfaz para agregar API."""
    print("\n" + "=" * 60)
    print("AGREGAR/EDITAR CONFIGURACIÓN DE API")
    print("=" * 60)
    
    print("\nPlataformas disponibles:")
    print("[1] Binance")
    print("[2] Kraken")
    print("[3] Coinbase")
    print("[4] Otra (manual)")
    
    opcion_plat = input("\nSelecciona plataforma: ")
    
    plataformas = {
        '1': 'Binance',
        '2': 'Kraken',
        '3': 'Coinbase',
        '4': input("  Nombre de la plataforma: ")
    }
    
    plataforma = plataformas.get(opcion_plat, 'Desconocida')
    
    cripto = input("Cripto (ej: USDT, BTC): ").upper()
    
    print("\n💡 Puedes dejar en blanco si la API es pública.")
    api_key = input("API Key (opcional): ")
    api_secret = input("API Secret (opcional): ")
    
    try:
        comision_compra = float(input("Comisión de compra % (ej: 0.35): "))
        comision_venta = float(input("Comisión de venta % (ej: 0.35): "))
        
        gestor.agregar_api(plataforma, cripto, api_key, api_secret, 
                          comision_compra, comision_venta)
        
        # Probar conexión inmediatamente
        if input("\n¿Deseas probar la conexión ahora? (s/n): ").lower() in ['s', 'si', 'sí']:
            gestor.probar_conexion(plataforma, cripto)
        
    except ValueError:
        print("❌ Error: Las comisiones deben ser números.")
    
    input("\nPresiona Enter para continuar...")

def listar_apis_configuradas(gestor):
    """Muestra todas las APIs configuradas."""
    apis = gestor.listar_apis()
    
    if not apis:
        print("\n⚠️  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n" + "=" * 60)
    print("APIs CONFIGURADAS")
    print("=" * 60)
    
    for api in apis:
        print(f"\n🔧 {api[1]} - {api[2]}")
        print(f"   API Key: {'*' * 20 if api[3] else 'No configurada'}")
        print(f"   Comisión compra: {api[5]}%")
        print(f"   Comisión venta: {api[6]}%")
        print(f"   Estado: {'✅ Activa' if api[7] else '❌ Inactiva'}")
    
    print("=" * 60)
    input("\nPresiona Enter para continuar...")

def probar_conexion_interactivo(gestor):
    """Interfaz para probar conexión."""
    apis = gestor.listar_apis()
    
    if not apis:
        print("\n⚠️  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n" + "=" * 60)
    print("PROBAR CONEXIÓN CON API")
    print("=" * 60)
    
    for i, api in enumerate(apis, 1):
        print(f"[{i}] {api[1]} - {api[2]}")
    
    try:
        opcion = int(input("\nSelecciona API a probar: "))
        if 1 <= opcion <= len(apis):
            api_seleccionada = apis[opcion - 1]
            gestor.probar_conexion(api_seleccionada[1], api_seleccionada[2])
        else:
            print("❌ Opción inválida.")
    except ValueError:
        print("❌ Debes ingresar un número.")
    
    input("\nPresiona Enter para continuar...")

def eliminar_api_interactivo(gestor):
    """Interfaz para eliminar API."""
    apis = gestor.listar_apis()
    
    if not apis:
        print("\n⚠️  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n" + "=" * 60)
    print("ELIMINAR CONFIGURACIÓN DE API")
    print("=" * 60)
    
    for i, api in enumerate(apis, 1):
        print(f"[{i}] {api[1]} - {api[2]}")
    
    try:
        opcion = int(input("\nSelecciona API a eliminar (0 para cancelar): "))
        
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(apis):
            api_seleccionada = apis[opcion - 1]
            confirmacion = input(f"\n¿Eliminar {api_seleccionada[1]} - {api_seleccionada[2]}? (s/n): ")
            
            if confirmacion.lower() in ['s', 'si', 'sí']:
                cursor = gestor.conn.cursor()
                cursor.execute("""
                    UPDATE apis_config SET activo = 0 
                    WHERE id = ?
                """, (api_seleccionada[0],))
                gestor.conn.commit()
                print("✅ API eliminada (desactivada).")
        else:
            print("❌ Opción inválida.")
    except ValueError:
        print("❌ Debes ingresar un número.")
    
    input("\nPresiona Enter para continuar...")
```

---

## 🔥 IMPLEMENTACIÓN INMEDIATA

Dado tu análisis detallado, te propongo implementar en este orden:

### **AHORA MISMO (30 min):**
1. ✅ Completar operador.py - **HECHO**
2. ✅ Database con backups y restauración - **HECHO**
3. ✅ Exports en carpeta separada - **HECHO**

### **SIGUIENTE (1-2 horas):**
4. 🔄 Crear `criptomonedas.py` con catálogo
5. 🔄 Actualizar `boveda.py` con fondeo mejorado
6. 🔄 Actualizar `operador.py` para multi-cripto

### **DESPUÉS (2-3 horas):**
7. ⏳ Crear `apis.py` completo
8. ⏳ Agregar opción [6] en `main.py`
9. ⏳ Testing completo

### **FINALMENTE (1-2 horas):**
10. ⏳ Mejorar consultas en `estadisticas.py`
11. ⏳ Agregar filtros avanzados
12. ⏳ Documentación final

---

## ❓ PRÓXIMA DECISIÓN

**¿Qué prefieres que hagamos ahora?**

**Opción A:** Implemento el fondeo mejorado (FIAT → Cripto) y el selector de criptomonedas

**Opción B:** Creo el módulo completo de APIs (apis.py) con Binance de ejemplo

**Opción C:** Me enfoco en mejorar las consultas y filtros en estadísticas

**Opción D:** Hago todo paso a paso en el orden recomendado

---

**Dime qué opción prefieres y continúo con la implementación completa** 🚀
