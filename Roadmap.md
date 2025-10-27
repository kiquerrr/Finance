# üìã ROADMAP DE MEJORAS - Sistema Arbitraje P2P

## ‚úÖ COMPLETADO (En esta sesi√≥n)

1. ‚úÖ Operador.py arreglado (c√≥digo completo)
2. ‚úÖ Directorios `backups/` y `exports/` creados autom√°ticamente
3. ‚úÖ Sistema de backups mejorado con limpieza autom√°tica
4. ‚úÖ Funci√≥n de restaurar BD desde backup
5. ‚úÖ Base de datos preparada para multi-cripto
6. ‚úÖ Exportaci√≥n CSV a carpeta `exports/`

---

## üîÑ EN PROGRESO (Siguiente fase)

### **PRIORIDAD ALTA** üî¥

#### 1. **Sistema de Criptomonedas M√∫ltiples**
**Estado:** Base de datos lista, falta implementaci√≥n

**Archivos a modificar:**
- `boveda.py` - Agregar selector de cripto en fondeo
- `operador.py` - Trabajar con cripto espec√≠fica
- `estadisticas.py` - Filtrar por cripto

**Cambios necesarios:**
```python
# En fondeo:
- Preguntar: ¬øQu√© cripto vas a fondear? (USDT, BTC, ETH, etc.)
- Calcular cantidad seg√∫n tasa de compra
```

#### 2. **Fondeo Mejorado con FIAT**
**Estado:** Pendiente

**L√≥gica nueva:**
```
Usuario ingresa: $100 USD
Sistema pregunta: ¬øQu√© cripto comprar? ‚Üí USDT
Sistema consulta tasa: 1 USDT = $1.05
Sistema calcula: 100 / 1.05 = 95.238 USDT
Sistema registra: 95.238 USDT comprados por $100
```

**Archivos:**
- `boveda.py` - Reescribir funci√≥n `fondear_boveda()`

#### 3. **Configuraci√≥n de APIs** (NUEVA OPCI√ìN [6])
**Estado:** Tabla creada, falta interfaz

**Men√∫ nuevo en main.py:**
```
[6] ‚öôÔ∏è  Configuraci√≥n de APIs y Plataformas
    [1] Agregar/Editar API de Plataforma
    [2] Ver APIs Configuradas
    [3] Probar Conexi√≥n API
    [4] Actualizar Tasas desde API
    [5] Volver
```

**Datos a guardar:**
- Plataforma (Binance, Kraken, etc.)
- Cripto (USDT, BTC, ETH, etc.)
- API Key
- API Secret
- Comisi√≥n de compra
- Comisi√≥n de venta

---

### **PRIORIDAD MEDIA** üü°

#### 4. **Consultas Mejoradas en Estad√≠sticas**

**Opci√≥n 1 - Ver Resumen General:**
```
Agregar:
- Total invertido hist√≥rico
- ROI promedio
- Mejor mes/semana
- Gr√°fico ASCII de ganancias
```

**Opci√≥n 2 - Listar Ciclos:**
```
Agregar filtros:
- Por fecha (rango)
- Por cripto
- Por monto m√≠nimo de ganancia
- Ordenar por ganancia/fecha
```

**Opci√≥n 3 - Ver Ciclo Activo:**
```
Agregar:
- Cripto operada
- Tasa promedio de compra
- Tasa promedio de venta
- Hora de inicio del ciclo
- Tiempo transcurrido
- Proyecci√≥n de ganancia
```

**Opci√≥n 4 - Ver Detalle de Ciclo:**
```
Mejorar:
- B√∫squeda por ID, fecha o rango
- Mostrar todas las transacciones
- Calcular m√©tricas del ciclo
```

#### 5. **Ver Historial de Transacciones (B√≥veda)**

**Agregar filtros:**
- Por tipo (compra/venta)
- Por cripto
- Por fecha (d√≠a espec√≠fico, rango)
- Por monto m√≠nimo
- Paginaci√≥n (10, 25, 50 resultados)

---

### **PRIORIDAD BAJA** üü¢

#### 6. **Integraci√≥n con APIs Reales**
**Estado:** Futuro

**APIs a integrar:**
- Binance API
- Kraken API  
- Coinbase API

**Funcionalidades:**
- Consultar tasas en tiempo real
- Actualizar comisiones autom√°ticamente
- Sincronizar transacciones (opcional)

#### 7. **Dashboard Visual**
**Estado:** Futuro lejano

- Gr√°ficos con matplotlib
- Reportes PDF
- Interfaz gr√°fica (Tkinter/PyQt)

---

## üìù DETALLE DE IMPLEMENTACI√ìN

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
¬øQu√© cripto vas a comprar?
[1] USDT (Tether)
[2] BTC (Bitcoin)
[3] ETH (Ethereum)
Selecciona: 1

Ingresa el monto en USD que vas a invertir: 1000

üîç Consultando tasa de compra para USDT...
üí± Tasa actual: 1 USDT = $1.0520 USD
üìä Con $1000 comprar√°s: 950.57 USDT

¬øConfirmar compra? (s/n):
```

#### Paso 2: Agregar selector de cripto en operador

```python
def analizar_mercado(costo_promedio, cripto):
    # A√±adir el s√≠mbolo de la cripto en mensajes
    print(f"Operando con {cripto}")
    print(f"Precio sugerido de {cripto}: ${precio:.4f}")
```

#### Paso 3: Actualizar estad√≠sticas con filtros

```python
def listar_ciclos_con_filtros():
    print("Filtrar por:")
    print("[1] Todos los ciclos")
    print("[2] Por cripto")
    print("[3] Por rango de fechas")
    print("[4] Por ganancia m√≠nima")
    
    # Implementar l√≥gica de filtros
```

---

### **FASE 2: Configuraci√≥n de APIs** (3-4 horas)

#### Crear nuevo m√≥dulo: `apis.py`

```python
# apis.py
import sqlite3

def agregar_api():
    """Agrega configuraci√≥n de API."""
    plataforma = input("Plataforma (ej: Binance): ")
    cripto = input("Cripto (ej: USDT): ")
    api_key = input("API Key: ")
    api_secret = input("API Secret (oculto): ")
    comision_compra = float(input("Comisi√≥n de compra %: "))
    comision_venta = float(input("Comisi√≥n de venta %: "))
    
    # Guardar en BD
    
def consultar_tasa_api(plataforma, cripto):
    """Consulta tasa desde API configurada."""
    # Implementar llamada a API
    pass

def actualizar_tasas():
    """Actualiza todas las tasas desde APIs."""
    # Para cada API configurada:
    #   - Consultar tasa actual
    #   - Actualizar en configuraci√≥n
    pass
```

#### Integrar en `main.py`:

```python
def modulo_apis():
    while True:
        print("==== Configuraci√≥n de APIs ====")
        print("[1] Agregar/Editar API")
        print("[2] Ver APIs Configuradas")
        print("[3] Probar Conexi√≥n")
        print("[4] Actualizar Tasas")
        print("[5] Volver")
        
        # Llamar funciones de apis.py
```

---

### **FASE 3: Mejoras en Consultas** (2 horas)

#### Actualizar `estadisticas.py`:

1. **Consultar estad√≠sticas generales:**
```python
# Agregar:
- Total invertido hist√≥rico
- ROI = (ganancia_total / inversion_total) * 100
- Ciclo m√°s rentable (por ROI, no solo por monto)
- Promedio de d√≠as por ciclo
```

2. **Ver ciclo activo:**
```python
# Agregar:
- Hora de inicio (extraer de fecha_inicio)
- Tiempo transcurrido en d√≠as/horas
- Proyecci√≥n: "Si cierras ahora ganar√≠as $X"
- Cripto principal operada
```

3. **Ver detalle de ciclo:**
```python
# Mejorar b√∫squeda:
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

## üéØ PLAN DE EJECUCI√ìN RECOMENDADO

### **Semana 1: Fundamentos Multi-Cripto**
- ‚úÖ D√≠a 1-2: Database actualizada (HECHO)
- üîÑ D√≠a 3: Fondeo mejorado con FIAT
- üîÑ D√≠a 4: Selector de cripto en operador
- üîÑ D√≠a 5: Testing y correcciones

### **Semana 2: APIs y Automatizaci√≥n**
- ‚è≥ D√≠a 1-2: M√≥dulo apis.py b√°sico
- ‚è≥ D√≠a 3: Integraci√≥n con Binance API (ejemplo)
- ‚è≥ D√≠a 4: Actualizaci√≥n autom√°tica de tasas
- ‚è≥ D√≠a 5: Testing de APIs

### **Semana 3: Mejoras en Consultas**
- ‚è≥ D√≠a 1: Filtros en estad√≠sticas
- ‚è≥ D√≠a 2: B√∫squedas avanzadas
- ‚è≥ D√≠a 3: Consultas m√°s descriptivas
- ‚è≥ D√≠a 4-5: Testing y documentaci√≥n

---

## üì¶ ARCHIVOS A CREAR/MODIFICAR

### **Archivos Nuevos:**
1. ‚úÖ `backups/` (directorio) - CREADO
2. ‚úÖ `exports/` (directorio) - CREADO
3. ‚è≥ `apis.py` - Gesti√≥n de APIs - **PENDIENTE**
4. ‚è≥ `criptomonedas.py` - Cat√°logo de criptos - **PENDIENTE**

### **Archivos a Modificar:**

#### **ALTA PRIORIDAD:**
1. ‚úÖ `database.py` - Base multi-cripto - **COMPLETADO**
2. üîÑ `boveda.py` - Fondeo mejorado - **EN PROGRESO**
3. üîÑ `operador.py` - Multi-cripto - **EN PROGRESO**
4. ‚è≥ `main.py` - Agregar opci√≥n [6] APIs - **PENDIENTE**

#### **MEDIA PRIORIDAD:**
5. ‚è≥ `estadisticas.py` - Filtros y consultas - **PENDIENTE**
6. ‚è≥ `utils.py` - Funciones para APIs - **PENDIENTE**

---

## üí° SUGERENCIAS DE IMPLEMENTACI√ìN

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
    print("\nüí∞ CRIPTOMONEDAS DISPONIBLES:")
    for i, (codigo, info) in enumerate(CRIPTOS_DISPONIBLES.items(), 1):
        print(f"[{i}] {info['nombre']} ({codigo}) - {info['tipo']}")

def seleccionar_cripto():
    """Permite al usuario seleccionar una cripto."""
    listar_criptos()
    while True:
        try:
            opcion = int(input("\nSelecciona una opci√≥n: "))
            if 1 <= opcion <= len(CRIPTOS_DISPONIBLES):
                cripto_codigo = list(CRIPTOS_DISPONIBLES.keys())[opcion - 1]
                return cripto_codigo
            else:
                print("‚ùå Opci√≥n inv√°lida.")
        except ValueError:
            print("‚ùå Ingresa un n√∫mero v√°lido.")

def obtener_info_cripto(codigo):
    """Obtiene informaci√≥n de una cripto."""
    return CRIPTOS_DISPONIBLES.get(codigo.upper())
```

### **2. M√≥dulo de APIs (apis.py)**

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
        """Agrega o actualiza configuraci√≥n de API."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO apis_config 
            (plataforma, cripto, api_key, api_secret, comision_compra, comision_venta, activo)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (plataforma, cripto, api_key, api_secret, comision_compra, comision_venta))
        self.conn.commit()
        print(f"‚úÖ API de {plataforma} para {cripto} configurada.")
    
    def obtener_api(self, plataforma, cripto):
        """Obtiene configuraci√≥n de una API."""
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
            # API p√∫blica de Binance (no requiere autenticaci√≥n)
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={cripto}USDT"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                precio = float(data['price'])
                return precio
            else:
                print(f"‚ö†Ô∏è  Error al consultar API: {response.status_code}")
                return None
        except Exception as e:
            print(f"‚ùå Error de conexi√≥n: {e}")
            return None
    
    def probar_conexion(self, plataforma, cripto):
        """Prueba la conexi√≥n con una API."""
        print(f"\nüîç Probando conexi√≥n con {plataforma} para {cripto}...")
        
        if plataforma.lower() == 'binance':
            tasa = self.consultar_tasa_binance(cripto)
            if tasa:
                print(f"‚úÖ Conexi√≥n exitosa!")
                print(f"üí± Precio actual de {cripto}: ${tasa:.4f}")
                return True
            else:
                print(f"‚ùå No se pudo conectar con {plataforma}")
                return False
        else:
            print(f"‚ö†Ô∏è  Plataforma {plataforma} a√∫n no implementada.")
            return False
    
    def actualizar_todas_tasas(self):
        """Actualiza tasas de todas las APIs configuradas."""
        apis = self.listar_apis()
        
        if not apis:
            print("\n‚ö†Ô∏è  No hay APIs configuradas.")
            return
        
        print("\nüîÑ Actualizando tasas desde APIs...")
        
        for api in apis:
            plataforma = api[1]
            cripto = api[2]
            
            if plataforma.lower() == 'binance':
                tasa = self.consultar_tasa_binance(cripto)
                if tasa:
                    print(f"‚úÖ {cripto} en {plataforma}: ${tasa:.4f}")
                else:
                    print(f"‚ùå {cripto} en {plataforma}: Error")
        
        print("\n‚úÖ Actualizaci√≥n completada.")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def menu_apis():
    """Men√∫ de gesti√≥n de APIs."""
    gestor = GestorAPIs()
    
    while True:
        print("\n" + "=" * 60)
        print("CONFIGURACI√ìN DE APIs Y PLATAFORMAS")
        print("=" * 60)
        print("[1] Agregar/Editar API de Plataforma")
        print("[2] Ver APIs Configuradas")
        print("[3] Probar Conexi√≥n con API")
        print("[4] Actualizar Tasas desde APIs")
        print("[5] Eliminar API")
        print("[6] Volver al Men√∫ Principal")
        print("=" * 60)
        
        opcion = input("Selecciona una opci√≥n: ")
        
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
            print("\n‚ùå Opci√≥n no v√°lida.")

def agregar_api_interactivo(gestor):
    """Interfaz para agregar API."""
    print("\n" + "=" * 60)
    print("AGREGAR/EDITAR CONFIGURACI√ìN DE API")
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
    
    print("\nüí° Puedes dejar en blanco si la API es p√∫blica.")
    api_key = input("API Key (opcional): ")
    api_secret = input("API Secret (opcional): ")
    
    try:
        comision_compra = float(input("Comisi√≥n de compra % (ej: 0.35): "))
        comision_venta = float(input("Comisi√≥n de venta % (ej: 0.35): "))
        
        gestor.agregar_api(plataforma, cripto, api_key, api_secret, 
                          comision_compra, comision_venta)
        
        # Probar conexi√≥n inmediatamente
        if input("\n¬øDeseas probar la conexi√≥n ahora? (s/n): ").lower() in ['s', 'si', 's√≠']:
            gestor.probar_conexion(plataforma, cripto)
        
    except ValueError:
        print("‚ùå Error: Las comisiones deben ser n√∫meros.")
    
    input("\nPresiona Enter para continuar...")

def listar_apis_configuradas(gestor):
    """Muestra todas las APIs configuradas."""
    apis = gestor.listar_apis()
    
    if not apis:
        print("\n‚ö†Ô∏è  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n" + "=" * 60)
    print("APIs CONFIGURADAS")
    print("=" * 60)
    
    for api in apis:
        print(f"\nüîß {api[1]} - {api[2]}")
        print(f"   API Key: {'*' * 20 if api[3] else 'No configurada'}")
        print(f"   Comisi√≥n compra: {api[5]}%")
        print(f"   Comisi√≥n venta: {api[6]}%")
        print(f"   Estado: {'‚úÖ Activa' if api[7] else '‚ùå Inactiva'}")
    
    print("=" * 60)
    input("\nPresiona Enter para continuar...")

def probar_conexion_interactivo(gestor):
    """Interfaz para probar conexi√≥n."""
    apis = gestor.listar_apis()
    
    if not apis:
        print("\n‚ö†Ô∏è  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n" + "=" * 60)
    print("PROBAR CONEXI√ìN CON API")
    print("=" * 60)
    
    for i, api in enumerate(apis, 1):
        print(f"[{i}] {api[1]} - {api[2]}")
    
    try:
        opcion = int(input("\nSelecciona API a probar: "))
        if 1 <= opcion <= len(apis):
            api_seleccionada = apis[opcion - 1]
            gestor.probar_conexion(api_seleccionada[1], api_seleccionada[2])
        else:
            print("‚ùå Opci√≥n inv√°lida.")
    except ValueError:
        print("‚ùå Debes ingresar un n√∫mero.")
    
    input("\nPresiona Enter para continuar...")

def eliminar_api_interactivo(gestor):
    """Interfaz para eliminar API."""
    apis = gestor.listar_apis()
    
    if not apis:
        print("\n‚ö†Ô∏è  No hay APIs configuradas.")
        input("\nPresiona Enter para continuar...")
        return
    
    print("\n" + "=" * 60)
    print("ELIMINAR CONFIGURACI√ìN DE API")
    print("=" * 60)
    
    for i, api in enumerate(apis, 1):
        print(f"[{i}] {api[1]} - {api[2]}")
    
    try:
        opcion = int(input("\nSelecciona API a eliminar (0 para cancelar): "))
        
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(apis):
            api_seleccionada = apis[opcion - 1]
            confirmacion = input(f"\n¬øEliminar {api_seleccionada[1]} - {api_seleccionada[2]}? (s/n): ")
            
            if confirmacion.lower() in ['s', 'si', 's√≠']:
                cursor = gestor.conn.cursor()
                cursor.execute("""
                    UPDATE apis_config SET activo = 0 
                    WHERE id = ?
                """, (api_seleccionada[0],))
                gestor.conn.commit()
                print("‚úÖ API eliminada (desactivada).")
        else:
            print("‚ùå Opci√≥n inv√°lida.")
    except ValueError:
        print("‚ùå Debes ingresar un n√∫mero.")
    
    input("\nPresiona Enter para continuar...")
```

---

## üî• IMPLEMENTACI√ìN INMEDIATA

Dado tu an√°lisis detallado, te propongo implementar en este orden:

### **AHORA MISMO (30 min):**
1. ‚úÖ Completar operador.py - **HECHO**
2. ‚úÖ Database con backups y restauraci√≥n - **HECHO**
3. ‚úÖ Exports en carpeta separada - **HECHO**

### **SIGUIENTE (1-2 horas):**
4. üîÑ Crear `criptomonedas.py` con cat√°logo
5. üîÑ Actualizar `boveda.py` con fondeo mejorado
6. üîÑ Actualizar `operador.py` para multi-cripto

### **DESPU√âS (2-3 horas):**
7. ‚è≥ Crear `apis.py` completo
8. ‚è≥ Agregar opci√≥n [6] en `main.py`
9. ‚è≥ Testing completo

### **FINALMENTE (1-2 horas):**
10. ‚è≥ Mejorar consultas en `estadisticas.py`
11. ‚è≥ Agregar filtros avanzados
12. ‚è≥ Documentaci√≥n final

---

## ‚ùì PR√ìXIMA DECISI√ìN

**¬øQu√© prefieres que hagamos ahora?**

**Opci√≥n A:** Implemento el fondeo mejorado (FIAT ‚Üí Cripto) y el selector de criptomonedas

**Opci√≥n B:** Creo el m√≥dulo completo de APIs (apis.py) con Binance de ejemplo

**Opci√≥n C:** Me enfoco en mejorar las consultas y filtros en estad√≠sticas

**Opci√≥n D:** Hago todo paso a paso en el orden recomendado

---

**Dime qu√© opci√≥n prefieres y contin√∫o con la implementaci√≥n completa** üöÄ

# ?? RESUMEN COMPLETO DE CORRECCIONES Y MEJORAS

## ? M”DULOS CREADOS Y CORREGIDOS

### 1. **logger.py** - Sistema de Logging Completo ? NUEVO
- Registra TODAS las operaciones del sistema
- Logs separados por categorÌa (general, operaciones, c·lculos, errores, bÛveda, ciclos)
- Formatos estandarizados con timestamps
- Funciones especÌficas para cada tipo de operaciÛn
- **UbicaciÛn:** `/logs/` (se crea autom·ticamente)

### 2. **calculos.py** - Calculadora con FÛrmulas Corregidas ? NUEVO
- ? FÛrmulas matem·ticas verificadas y documentadas
- ? C·lculo correcto de comisiones
- ? Ganancia bruta y neta calculadas correctamente
- ? ROI calculado con precisiÛn
- ? Todos los c·lculos registrados en logs

### 3. **configuracion.py** - MÛdulo de ConfiguraciÛn ? NUEVO
**Separado del mantenimiento, incluye:**
- ConfiguraciÛn de comisiones (manual o por API)
- ConfiguraciÛn de ganancia objetivo
- GestiÛn de APIs de plataformas
- LÌmites de ventas diarias
- Exportar/Importar configuraciones

### 4. **mantenimiento.py** - MÛdulo de Mantenimiento ? NUEVO
**Funciones completas de mantenimiento:**
- Backups y restauraciÛn autom·tica
- VerificaciÛn de integridad de BD
- ReparaciÛn de problemas
- Limpieza de datos antiguos
- OptimizaciÛn de base de datos
- GestiÛn de logs
- ExportaciÛn de datos a CSV

### 5. **dias.py** - MÛdulo Corregido ??
**Correcciones aplicadas:**
- ? IntegraciÛn con logger y calculadora
- ? C·lculos de ventas corregidos
- ? Sistema de "Pool de ReinversiÛn" (InterÈs Compuesto)
- ? Registro dual: Cripto + Efectivo en banco
- ? Resumen de dÌa con todos los datos correctos
- ? M˙ltiples criptos operables por dÌa

### 6. **ciclos.py** - MÛdulo Corregido ??
**Correcciones aplicadas:**
- ? Registro correcto de inversiÛn inicial
- ? ValidaciÛn de ciclos completados
- ? OpciÛn de extender o cerrar al completar dÌas planificados
- ? No permite operar dÌas adicionales sin autorizaciÛn
- ? C·lculo correcto de dÌas transcurridos/restantes
- ? ROI y estadÌsticas precisas

---

## ?? PROBLEMAS CRÕTICOS RESUELTOS

### ? PROBLEMA 1: Errores de C·lculo
**SÌntoma:** Capital final incorrecto, ganancias que no cuadraban
**Causa:** FÛrmulas mal implementadas, variables con nombres confusos
**SoluciÛn:**
```python
# ANTES (incorrecto)
ganancia = monto_venta - costo_total

# AHORA (correcto)
costo_total = cantidad * costo_unitario
monto_venta = cantidad * precio_venta
comision = monto_venta * (comision_pct / 100)
efectivo_recibido = monto_venta - comision
ganancia_bruta = monto_venta - costo_total
ganancia_neta = ganancia_bruta - comision
```

### ? PROBLEMA 2: Falta de Registro de Efectivo
**SÌntoma:** Vender 100 USDT mostraba menos capital
**SoluciÛn:** Nueva tabla `efectivo_banco` + Pool de reinversiÛn
```python
# Ahora se registra:
1. Cripto vendida (sale de bÛveda)
2. Efectivo recibido (entra a banco)
3. Pool de reinversiÛn (para interÈs compuesto)
```

### ? PROBLEMA 3: Ciclos sin Control
**SÌntoma:** PodÌa operar dÌa 4 en ciclo de 3 dÌas
**SoluciÛn:**
```python
# Ahora verifica:
- Si el ciclo completÛ sus dÌas planificados
- Si debe cerrarse o extenderse
- No permite operar sin autorizaciÛn
```

### ? PROBLEMA 4: InversiÛn Inicial en $0.00
**SÌntoma:** Siempre mostraba $0.00 de inversiÛn
**SoluciÛn:**
```python
# Al crear ciclo, calcula inversiÛn inicial:
inversion_inicial = SUM(cantidad * precio_promedio) FROM boveda_ciclo
```

### ? PROBLEMA 5: MÛdulo dias.py no encontrado
**SÌntoma:** `module 'dias' has no attribute 'obtener_dia_actual'`
**SoluciÛn:** Archivo dias.py completamente reescrito con todas las funciones

### ? PROBLEMA 6: Fondear requerÌa ciclo activo
**SÌntoma:** No podÌa fondear sin ciclo
**SoluciÛn:** Ya NO requiere ciclo activo para fondear

---

## ?? NUEVA ESTRUCTURA DE BASE DE DATOS

### Tablas Nuevas/Modificadas:

```sql
-- Nueva tabla: Efectivo en banco
CREATE TABLE efectivo_banco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ciclo_id INTEGER NOT NULL,
    dia_id INTEGER,
    monto REAL NOT NULL,
    concepto TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nueva tabla: ConfiguraciÛn de APIs
CREATE TABLE apis_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    plataforma TEXT NOT NULL,
    api_key TEXT,
    api_secret TEXT,
    activa INTEGER DEFAULT 1,
    tipo TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Columnas aÒadidas a tabla 'dias'
ALTER TABLE dias ADD COLUMN efectivo_recibido REAL DEFAULT 0;
ALTER TABLE dias ADD COLUMN comisiones_pagadas REAL DEFAULT 0;
ALTER TABLE dias ADD COLUMN ganancia_bruta REAL DEFAULT 0;

-- Columnas aÒadidas a tabla 'ventas'
ALTER TABLE ventas ADD COLUMN efectivo_recibido REAL DEFAULT 0;
ALTER TABLE ventas ADD COLUMN ganancia_bruta REAL DEFAULT 0;

-- Columnas corregidas en tabla 'ciclos'
-- La inversiÛn_inicial ahora se calcula correctamente
```

---

## ?? FLUJO CORREGIDO DEL SISTEMA

### Flujo Normal de OperaciÛn:

```
1. FONDEAR B”VEDA (sin necesidad de ciclo)
   +-> Registra compra en boveda_ciclo
   +-> Log: boveda_compra()

2. CREAR CICLO GLOBAL
   +-> Calcula inversiÛn_inicial desde bÛveda
   +-> Define duraciÛn (dÌas planificados)
   +-> Log: ciclo_creado()

3. INICIAR DÕA
   +-> Verifica que ciclo estÈ activo
   +-> Verifica dÌas restantes
   +-> Calcula capital inicial del dÌa
   +-> Log: dia_iniciado()

4. DEFINIR PRECIO DE VENTA
   +-> Calcula precio sugerido con calc.py
   +-> Usuario define precio real
   +-> Calcula ganancia estimada
   +-> Log: precio_definido()

5. REGISTRAR VENTAS (3-5 por dÌa)
   +-> Para cada venta:
       +-> Calcula con calc.calcular_venta()
       +-> Descuenta cripto de bÛveda
       +-> Registra efectivo en banco
       +-> Log: venta_registrada()
       +-> Log: calculo_venta()

6. CERRAR DÕA
   +-> Calcula resumen con calc.calcular_resumen_dia()
   +-> Muestra capital en criptos + efectivo
   +-> Registra ganancia del dÌa
   +-> Log: dia_cerrado()

7. APLICAR INTER…S COMPUESTO (opcional)
   +-> Convierte efectivo del pool en cripto
   +-> Aumenta capital para dÌa siguiente
   +-> Log: boveda_compra() + reinversiÛn

8. VERIFICAR CICLO COMPLETADO
   +-> Si dÌas_transcurridos >= dÌas_planificados:
       +-> Ofrece EXTENDER o CERRAR
       +-> No permite operar sin decisiÛn

9. CERRAR CICLO
   +-> Calcula estadÌsticas finales
   +-> Muestra ROI y ganancias
   +-> Cambia estado a 'cerrado'
   +-> Log: ciclo_cerrado()
```

---

## ?? PLAN DE INTEGRACI”N - PASO A PASO

### FASE 1: PreparaciÛn (5 minutos)
```bash
# 1. Hacer backup completo
cp arbitraje.db arbitraje_backup_manual.db

# 2. Crear directorios necesarios
mkdir -p logs backups exports

# 3. Copiar nuevos mÛdulos al proyecto
# - logger.py
# - calculos.py
# - configuracion.py
# - mantenimiento.py
```

### FASE 2: Actualizar Base de Datos (3 minutos)
```sql
-- Ejecutar estos comandos en SQLite:

-- Crear tabla de efectivo
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

-- Agregar columnas a dias
ALTER TABLE dias ADD COLUMN efectivo_recibido REAL DEFAULT 0;
ALTER TABLE dias ADD COLUMN comisiones_pagadas REAL DEFAULT 0;
ALTER TABLE dias ADD COLUMN ganancia_bruta REAL DEFAULT 0;

-- Agregar columnas a ventas
ALTER TABLE ventas ADD COLUMN efectivo_recibido REAL DEFAULT 0;
ALTER TABLE ventas ADD COLUMN ganancia_bruta REAL DEFAULT 0;
```

### FASE 3: Reemplazar MÛdulos (10 minutos)
1. **Reemplazar dias.py** con la versiÛn corregida
2. **Reemplazar ciclos.py** con la versiÛn corregida
3. **Actualizar boveda.py** agregando imports:
   ```python
   from logger import log
   from calculos import calc
   ```
4. **Actualizar operador.py** para usar nuevos mÛdulos

### FASE 4: Actualizar main.py (5 minutos)
```python
# Modificar men˙ principal para separar opciones:

# ANTES:
# [4] ConfiguraciÛn y Mantenimiento

# AHORA:
# [4] ??  ConfiguraciÛn
# [5] ?? Mantenimiento
# [6] ?? Salir
```

### FASE 5: Testing (20 minutos)
```
? Test 1: Crear ciclo nuevo
? Test 2: Fondear con 2 criptos diferentes
? Test 3: Operar dÌa completo (3-5 ventas)
? Test 4: Verificar c·lculos en logs
? Test 5: Cerrar dÌa y revisar n˙meros
? Test 6: Aplicar interÈs compuesto
? Test 7: Completar ciclo y cerrar
? Test 8: Crear backup
? Test 9: Ver todos los logs
? Test 10: Exportar datos
```

---

## ?? CHECKLIST FINAL

### Antes de Lanzar VersiÛn 1 Beta:

- [ ] Todos los mÛdulos nuevos copiados
- [ ] Base de datos actualizada
- [ ] Imports corregidos en todos los archivos
- [ ] Men˙ principal actualizado
- [ ] Tests b·sicos ejecutados
- [ ] Backup creado
- [ ] Logs funcionando
- [ ] C·lculos verificados manualmente
- [ ] Ciclo completo probado
- [ ] Pool de reinversiÛn probado
- [ ] DocumentaciÛn actualizada

---

## ?? CARACTERÕSTICAS NUEVAS

### 1. Sistema de Logging Avanzado
- Cada acciÛn queda registrada
- F·cil debugging
- AuditorÌa completa
- Logs por categorÌa

### 2. Pool de ReinversiÛn (InterÈs Compuesto)
- Efectivo de ventas va al pool
- Se puede reinvertir en cripto
- Capital crece autom·ticamente
- Maximiza ganancias

### 3. ConfiguraciÛn Modular
- APIs configurables
- Comisiones din·micas
- Par·metros personalizables
- Import/Export de config

### 4. Mantenimiento Profesional
- Backups autom·ticos
- VerificaciÛn de integridad
- OptimizaciÛn de BD
- Limpieza programada

### 5. Validaciones Inteligentes
- No operar dÌas extra sin autorizaciÛn
- Verificar capital disponible
- Validar lÌmites de ventas
- Prevenir errores

---

## ?? PR”XIMOS PASOS RECOMENDADOS

1. **Implementar los mÛdulos** siguiendo el plan de integraciÛn
2. **Ejecutar tests completos** con datos reales pequeÒos
3. **Revisar logs generados** para verificar todo funciona
4. **Hacer pruebas de estrÈs** con m˙ltiples ciclos
5. **Documentar casos de uso** especÌficos de tu operaciÛn
6. **Crear manual de usuario** simple
7. **Preparar versiÛn 1.0 Beta** para testing real

---

## ?? TIPS IMPORTANTES

- **SIEMPRE** crear backup antes de operar
- **REVISAR** los logs despuÈs de cada dÌa
- **VERIFICAR** c·lculos manualmente los primeros dÌas
- **USAR** el pool de reinversiÛn para maximizar ganancias
- **CONFIGURAR** lÌmites de ventas seg˙n tu banco
- **MANTENER** la BD optimizada semanalmente

---

## ?? C”MO DETECTAR PROBLEMAS

Si algo no cuadra, revisa:
1. **Logs de c·lculos** ? `/logs/calculos.log`
2. **Logs de operaciones** ? `/logs/operaciones.log`
3. **Logs de errores** ? `/logs/errores.log`
4. **Verificar integridad** ? Mantenimiento > OpciÛn 5
5. **Generar reporte** ? Mantenimiento > OpciÛn 11

---

°SISTEMA LISTO PARA FASE DE TESTING! ??
