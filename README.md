# 🚀 Sistema de Gestión de Arbitraje P2P v3.0

## 📋 Descripción

Sistema profesional y completo de gestión de operaciones de arbitraje P2P de criptomonedas con soporte multi-cripto, integración con APIs, backups automáticos y gestión inteligente de ciclos.

## ✨ Características Principales - Versión 3.0

### 🆕 **NUEVAS FUNCIONALIDADES:**

- **💰 Soporte Multi-Criptomonedas**: Opera con USDT, BTC, ETH, BNB, USDC, DAI
- **💵 Fondeo Intuitivo con FIAT**: Ingresa monto en USD y el sistema calcula la cripto
- **🌐 Integración con APIs**: Binance API funcional (más plataformas próximamente)
- **📦 Backups Automáticos**: Directorio dedicado con limpieza automática
- **♻️ Restauración de BD**: Recupera tu base de datos desde cualquier backup
- **📊 Exportación Organizada**: Archivos CSV en carpeta dedicada
- **🔍 Filtros Avanzados**: Búsquedas por cripto, tipo, fecha y más

### ⚡ **MEJORAS IMPLEMENTADAS:**

- **Gestión Inteligente de Ciclos**: El sistema detecta automáticamente situaciones ilógicas
- **Validaciones Adaptativas**: Opciones de cierre según el estado real del ciclo
- **Transferencia de Capital**: Mueve fondos entre ciclos fácilmente
- **Consultas Descriptivas**: Información más detallada en todas las vistas
- **Interfaz Mejorada**: Emojis, colores y mejor organización visual

## 📁 Estructura del Proyecto

```
Finance/
│
├── main.py                    # Programa principal (v3.0)
├── operador.py                # Operaciones diarias inteligentes
├── boveda.py                  # Gestión multi-cripto con FIAT
├── estadisticas.py            # Consultas con filtros avanzados
├── database.py                # BD con backups y restauración
├── criptomonedas.py          # Catálogo de criptomonedas (NUEVO)
├── apis.py                    # Gestión de APIs (NUEVO)
├── utils.py                   # Funciones auxiliares
│
├── arbitraje.db              # Base de datos principal
├── backups/                   # Backups automáticos (NUEVO)
│   └── arbitraje_backup_*.db
├── exports/                   # Exportaciones CSV (NUEVO)
│   └── transacciones_*.csv
│
└── README.md                  # Este archivo
```

## 🚀 Instalación

### Requisitos

- Python 3.7 o superior
- SQLite3 (incluido en Python)
- requests (opcional, para APIs): `pip install requests`

### Instalación

1. **Descargar todos los archivos:**
   - main.py
   - operador.py
   - boveda.py
   - estadisticas.py
   - database.py
   - criptomonedas.py (NUEVO)
   - apis.py (NUEVO)
   - utils.py

2. **Colocar todos los archivos en la misma carpeta**

3. **Ejecutar el programa:**
```bash
python main.py
```

4. **(Opcional) Instalar requests para usar APIs:**
```bash
pip install requests
```

## 🎯 Guía de Uso Rápida

### 1️⃣ **Primer Uso**

```
1. Ejecuta main.py
2. El sistema creará automáticamente:
   - arbitraje.db
   - backups/
   - exports/
3. Ir a [1] Operador → Crear nuevo ciclo
4. Ir a [2] Bóveda → Fondear con tu capital
5. ¡Listo para operar!
```

### 2️⃣ **Fondear con FIAT (Nuevo)**

```
[2] Gestión de Bóveda → [2] Fondear

1. Selecciona la criptomoneda (ej: USDT)
2. Ingresa monto en USD: $1000
3. Ingresa tasa de compra: 1.05
4. El sistema calcula: 952.38 USDT
5. Confirmar y listo!
```

### 3️⃣ **Configurar API de Binance**

```
[5] Configuración de APIs → [1] Agregar API

1. Seleccionar Binance
2. Ingresar cripto (ej: BTC)
3. Dejar API Key en blanco (API pública)
4. Ingresar comisiones
5. El sistema probará la conexión automáticamente
```

### 4️⃣ **Crear Backup**

```
[4] Configuración → [4] Crear Backup

✅ Backup guardado en: backups/arbitraje_backup_20251025_153045.db
🗑️ Solo se mantienen los últimos 10 backups
```

### 5️⃣ **Restaurar desde Backup**

```
[4] Configuración → [5] Restaurar Backup

1. Elige el backup de la lista
2. Confirma escribiendo 'RESTAURAR'
3. El sistema crea un backup de seguridad antes de restaurar
4. Reinicia el programa
```

## 📊 Funcionalidades Detalladas

### 🔄 **Módulo Operador**

**Flujo Inteligente:**
- Detecta ciclo activo automáticamente
- Alerta si hay capital en ciclos anteriores
- Opciones adaptativas según el estado
- Validación de precios con advertencias

**Cierre de Ciclos Inteligente:**
- ✅ Si hay ganancia Y capital → 4 opciones
- ✅ Si solo hay ganancia → 3 opciones
- ✅ Si solo hay capital → 3 opciones
- ✅ Si está vacío → 2 opciones

### 💰 **Módulo Bóveda**

**Consulta de Estado:**
- Vista global por criptomoneda
- Vista del ciclo activo
- Alertas de capital en otros ciclos
- Costo promedio por cripto

**Fondeo Mejorado:**
- Ingresa monto en FIAT (USD)
- Selecciona criptomoneda
- Ingresa tasa de compra
- El sistema calcula la cantidad automáticamente

**Historial con Filtros:**
- Todas las transacciones
- Solo del ciclo activo
- Por tipo (compra/venta)
- Por criptomoneda

**Transferencia de Capital:**
- Mueve capital de ciclos anteriores al activo
- Mantiene el costo promedio correcto
- Soporta múltiples criptos simultáneamente

### 📈 **Módulo Estadísticas**

**Resumen General:**
- Ciclos completados
- Ganancia histórica total
- Ganancia promedio por ciclo
- Mejor y peor ciclo

**Ciclo Activo:**
- Transacciones realizadas
- Capital disponible por cripto
- Inversión total
- Costo promedio

**Detalle de Ciclo:**
- Búsqueda por ID
- Información completa
- Todas las transacciones
- Métricas calculadas

**Exportación:**
- Formato CSV estándar
- Guardado en exports/
- Incluye todas las criptos
- Timestamp automático

### 🌐 **Módulo APIs (NUEVO)**

**Plataformas Soportadas:**
- ✅ Binance (API pública funcional)
- ⏳ Kraken (próximamente)
- ⏳ Coinbase (próximamente)

**Funciones:**
- Agregar/editar APIs
- Probar conexión
- Actualizar tasas en tiempo real
- Ver APIs configuradas
- Eliminar APIs

**Uso de Binance API:**
```
1. No requiere API Key (usa API pública)
2. Consulta precios en tiempo real
3. Funciona para BTC, ETH, BNB, USDT, etc.
4. Sin límite de consultas
```

### 💎 **Catálogo de Criptomonedas**

**Disponibles:**
- 🪙 USDT - Tether (Stablecoin)
- 🪙 USDC - USD Coin (Stablecoin)
- ₿ BTC - Bitcoin
- ₿ ETH - Ethereum
- ₿ BNB - Binance Coin
- 🪙 DAI - Dai (Stablecoin)

**Características:**
- Decimales configurados por cripto
- Información descriptiva
- Validación automática
- Formateo inteligente

## 🛠️ Configuración Avanzada

### Base de Datos

**Tablas:**
- `ciclos` - Ciclos de trabajo con soporte multi-cripto
- `transacciones` - Transacciones con cripto y monto FIAT
- `configuracion` - Parámetros del sistema
- `apis_config` - Configuración de APIs (NUEVA)

**Configuraciones:**
- `comision_defecto`: Comisión de la plataforma (%)
- `ganancia_defecto`: Meta de ganancia neta (%)
- `cripto_defecto`: Criptomoneda por defecto

### Backups

**Automáticos:**
- Máximo 10 backups guardados
- Los más antiguos se eliminan automáticamente
- Formato: `arbitraje_backup_YYYYMMDD_HHMMSS.db`

**Manuales:**
- Desde [4] Configuración → [4] Crear Backup
- Sin límite de cantidad
- Puedes mover los importantes a otra carpeta

### Exportaciones

**Formato CSV:**
- Encoding UTF-8
- Separador: coma (,)
- Todas las columnas incluidas
- Compatible con Excel/Google Sheets

## 💡 Casos de Uso

### Caso 1: Operar con Múltiples Criptos

```
DÍA 1:
- Fondear $500 en USDT
- Fondear $500 en BTC
- Operar con ambas

DÍA 2:
- El sistema separa automáticamente cada cripto
- Puedes vender USDT y mantener BTC
- Cada una con su costo promedio
```

### Caso 2: Usar API de Binance

```
1. Configurar API de Binance para BTC
2. Al fondear BTC, consultar tasa actual
3. El sistema muestra: "Precio BTC: $67,234.50"
4. Usar ese precio para el fondeo
5. Actualizar tasas cuando sea necesario
```

### Caso 3: Recuperación de Errores

```
PROBLEMA: Borraste una transacción por error

SOLUCIÓN:
1. Ir a [4] Configuración → [5] Restaurar Backup
2. Elegir el backup más reciente
3. El sistema crea backup de seguridad
4. Restaura el backup anterior
5. ¡Datos recuperados!
```

## 🐛 Solución de Problemas

### Error: "No module named 'criptomonedas'"

**Solución:** Asegúrate de tener todos los archivos en la misma carpeta:
- criptomonedas.py
- apis.py
- (todos los demás)

### Error: "No module named 'requests'"

**Solución:** 
```bash
pip install requests
```

**Alternativa:** Las APIs seguirán funcionando pero sin conexión real. Puedes ingresar tasas manualmente.

### Error: "database is locked"

**Solución:**
1. Cierra todas las instancias del programa
2. Reinicia
3. Si persiste, crea un backup y restaura

### Los backups ocupan mucho espacio

**Solución:** El sistema mantiene automáticamente solo los últimos 10. Puedes:
1. Eliminar manualmente backups antiguos de la carpeta `backups/`
2. Mover backups importantes a otra ubicación

## 📈 Mejoras Futuras (Roadmap)

### v3.1 (Próxima versión)
- [ ] Integración con Kraken API
- [ ] Integración con Coinbase API
- [ ] Actualización automática de tasas cada X minutos
- [ ] Alertas de precio por consola
- [ ] Más criptomonedas (SOL, ADA, DOT)

### v4.0 (Futuro)
- [ ] Interfaz gráfica (GUI)
- [ ] Gráficos de rendimiento
- [ ] Reportes PDF automáticos
- [ ] Dashboard web
- [ ] App móvil complementaria

## 📞 Soporte

### Reportar Bugs

Si encuentras algún error:
1. Anota el mensaje de error completo
2. Describe los pasos para reproducirlo
3. Indica tu versión de Python
4. Crea un issue en GitHub

### Contribuir

¿Quieres mejorar el sistema?
1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit (`git commit -m 'Añade nueva funcionalidad'`)
4. Push (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📜 Changelog

### v3.0 (Octubre 2025) - Multi-Cripto
- ✅ Soporte para múltiples criptomonedas
- ✅ Fondeo con monto en FIAT
- ✅ Módulo de APIs con Binance funcional
- ✅ Sistema de backups mejorado
- ✅ Restauración de BD desde backup
- ✅ Filtros avanzados en consultas
- ✅ Exportación organizada en carpeta dedicada
- ✅ Gestión inteligente de ciclos
- ✅ Validaciones adaptativas

### v2.0 (Octubre 2025) - Mejoras
- ✅ Gestión de ciclos mejorada
- ✅ Codificación UTF-8 corregida
- ✅ Manejo de errores robusto
- ✅ Interfaz visual mejorada
- ✅ Transferencia de capital entre ciclos

### v1.0 (Inicial)
- ✅ Gestión básica de ciclos
- ✅ Registro de transacciones
- ✅ Estadísticas simples

## ⚖️ Licencia

MIT License - Ver archivo LICENSE

## 🙏 Agradecimientos

- Comunidad de Python
- Binance por su API pública
- Todos los usuarios y contribuidores

## ⚠️ Disclaimer

Este software es una herramienta de gestión contable. NO es:
- Asesoramiento financiero
- Garantía de ganancias
- Responsable de pérdidas

Usa bajo tu propio riesgo. Las criptomonedas son volátiles.

---

## 🎉 ¡Listo para Usar!

**Versión 3.0 - Multi-Cripto**

✅ Todos los archivos listos para copiar y pegar
✅ Sistema completo y funcional
✅ Documentación completa
✅ APIs funcionales
✅ Backups automáticos

**¿Preguntas? Abre un issue en GitHub**

---

*Última actualización: Octubre 2025*
*Versión: 3.0*
*Autor: kiquerrr*
