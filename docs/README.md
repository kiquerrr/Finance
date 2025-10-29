# 💰 Sistema de Arbitraje P2P - Versión 3.0

Sistema completo de gestión de operaciones de arbitraje de criptomonedas en plataformas P2P.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![SQLite](https://img.shields.io/badge/SQLite-3-green.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración Inicial](#-configuración-inicial)
- [Uso Básico](#-uso-básico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Módulos](#-módulos)
- [Glosario](#-glosario)
- [FAQ](#-faq)
- [Soporte](#-soporte)

---

## ✨ Características

### **Core del Sistema**
- ✅ Gestión completa de ciclos de operación
- ✅ Control de días operativos con múltiples ventas
- ✅ Cálculo automático de precios y ganancias
- ✅ Gestión de bóveda multi-cripto
- ✅ Sistema de logs detallado
- ✅ Base de datos SQLite con integridad referencial

### **Nuevas Funcionalidades v3.0**
- 🎯 **Proyecciones**: Simulador de escenarios futuros
- 📊 **Reportes**: Exportación a CSV y TXT
- 📝 **Notas**: Sistema de documentación de operaciones
- 🔔 **Alertas**: Notificaciones automáticas inteligentes
- 📈 **Gráficos**: Visualización de rendimiento (matplotlib)

### **Seguridad y Mantenimiento**
- 🔒 Validaciones en todas las operaciones críticas
- 💾 Sistema de backups automáticos
- 🔍 Verificación de integridad de BD
- 📁 Organización automática de archivos

---

## 🔧 Requisitos

### **Requisitos del Sistema**
- Python 3.7 o superior
- Sistema operativo: Windows, Linux o macOS
- ~50 MB de espacio en disco
- Terminal/Consola

### **Dependencias Opcionales**
```bash
# Para gráficos (recomendado)
matplotlib >= 3.5.0

# Para mejor manejo de fechas (opcional)
python-dateutil >= 2.8.0
```

---

## 🚀 Instalación

### **Opción 1: Instalación Automática (Recomendado)**
```bash
# 1. Clonar/descargar el repositorio
cd arbitraje/

# 2. Ejecutar script de instalación
python setup.py

# 3. Inicializar base de datos
python inicializar_bd.py

# 4. Iniciar el sistema
python main.py
```

### **Opción 2: Instalación Manual**
```bash
# 1. Instalar dependencias (opcional)
pip install matplotlib --break-system-packages

# En Windows:
pip install matplotlib

# 2. Inicializar base de datos
python inicializar_bd.py

# 3. Iniciar sistema
python main.py
```

---

## ⚙️ Configuración Inicial

### **Primera Vez**

1. **Configurar Parámetros**
```
   Main Menu > Gestión del Sistema > Configuración
```
   - Comisión de plataforma (default: 0.35%)
   - Ganancia objetivo por día (default: 2.0%)
   - Límites de ventas (3-5 ventas/día)

2. **Fondear la Bóveda**
```
   Main Menu > Gestión del Sistema > Gestión de Bóveda > Registrar Compra
```
   - Compra criptomonedas (USDT, USDC, etc.)
   - El sistema calcula automáticamente el precio promedio

3. **Iniciar Primer Ciclo**
   - Se crea automáticamente al iniciar el primer día
   - Define la duración (ej: 15 días)
   - El capital inicial se calcula automáticamente

---

## 📖 Uso Básico

### **Flujo de Operación Diaria**
```
┌─────────────────────────────────────────┐
│  1. INICIAR DÍA                         │
│     • Define precio de venta            │
│     • Sistema calcula ganancia estimada │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  2. REGISTRAR VENTAS                    │
│     • Ingresa datos de cada venta       │
│     • Sistema calcula ganancias reales  │
│     • Actualiza bóveda automáticamente  │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  3. CERRAR DÍA                          │
│     • Resumen del día                   │
│     • Opción de aplicar interés compuesto│
│     • Logs automáticos                  │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│  4. (OPCIONAL) ANÁLISIS                 │
│     • Ver reportes                      │
│     • Generar gráficos                  │
│     • Hacer proyecciones                │
└─────────────────────────────────────────┘
```

### **Comandos Rápidos**

| Acción | Ruta del Menú |
|--------|---------------|
| Operar | Operaciones > Iniciar Día |
| Ver estadísticas | Análisis > Estadísticas Generales |
| Generar reporte | Análisis > Generar Reportes |
| Ver alertas | Gestión > Sistema de Alertas |
| Backup | Gestión > Mantenimiento > Crear Backup |

---

## 📁 Estructura del Proyecto
```
arbitraje/
│
├── arbitraje.db              # Base de datos principal
├── main.py                   # Punto de entrada
├── setup.py                  # Script de instalación
├── requirements.txt          # Dependencias
│
├── CORE/                     # Módulos principales
│   ├── db_manager.py         # Gestor de base de datos
│   ├── logger.py             # Sistema de logs
│   ├── calculos.py           # Fórmulas y cálculos
│   ├── validaciones.py       # Validaciones centralizadas
│   └── queries.py            # Consultas reutilizables
│
├── MÓDULOS/                  # Funcionalidades base
│   ├── inicializar_bd.py     # Inicializador de BD
│   ├── operador.py           # Operación diaria
│   ├── boveda.py             # Gestión de bóveda
│   ├── ciclos.py             # Gestión de ciclos
│   ├── dias.py               # Gestión de días
│   ├── configuracion.py      # Configuración del sistema
│   └── mantenimiento.py      # Backups y optimización
│
├── FUNCIONALIDADES/          # Nuevas funcionalidades v3.0
│   ├── proyecciones.py       # Simulador de escenarios
│   ├── reportes.py           # Exportación de datos
│   ├── notas.py              # Sistema de notas
│   ├── alertas.py            # Sistema de alertas
│   └── graficos.py           # Visualización de datos
│
├── logs/                     # Logs del sistema
├── backups/                  # Backups automáticos
├── reportes/                 # Reportes exportados
└── graficos/                 # Gráficos generados
```

---

## 🔧 Módulos

### **Core**

#### **db_manager.py**
Gestor centralizado de conexiones a la base de datos.
- Context manager para transacciones seguras
- Manejo automático de errores
- Compatibilidad con todos los módulos

#### **logger.py**
Sistema de logging centralizado.
- Logs por categoría (operaciones, ciclos, bóveda, etc.)
- Rotación diaria automática
- Métodos específicos para cada tipo de operación

#### **calculos.py**
Todas las fórmulas matemáticas del sistema.
- Cálculo de precios sugeridos
- Cálculo de ganancias netas
- Validaciones de rentabilidad
- Cálculo de ROI

### **Módulos Principales**

#### **operador.py**
Flujo completo de operación diaria.
- Iniciar día
- Registrar ventas
- Cerrar día
- Aplicar interés compuesto

#### **boveda.py**
Gestión de capital en criptomonedas.
- Registrar compras
- Transferencias entre ciclos
- Consulta de inventario
- Cálculo de capital disponible

#### **ciclos.py**
Control de ciclos de operación.
- Crear ciclos
- Extender duración
- Cerrar con liquidación
- Historial completo

### **Funcionalidades Avanzadas**

#### **proyecciones.py**
Simulador de escenarios.
- Proyección lineal (ganancia constante)
- Proyección con interés compuesto
- Simulación Monte Carlo
- Análisis de escenarios

#### **reportes.py**
Exportación de datos.
- Reporte completo de ciclo (TXT)
- Exportación de días (CSV)
- Exportación de ventas (CSV)
- Reporte consolidado

#### **alertas.py**
Sistema de notificaciones.
- Día abierto largo (>24h)
- Límite de ventas alcanzado
- Capital bajo
- Ganancia negativa
- Ciclo por terminar
- Y más...

---

## 📚 Glosario

| Término | Definición |
|---------|------------|
| **Ciclo** | Período de operación definido (ej: 15 días) |
| **Día** | Jornada operativa dentro de un ciclo |
| **Bóveda** | Inventario de criptomonedas disponibles |
| **Capital Inicial** | Monto disponible al inicio del día |
| **Precio Publicado** | Precio al que vendes en P2P |
| **Comisión** | % que cobra la plataforma (default: 0.35%) |
| **Ganancia Neta** | Ganancia después de comisiones |
| **ROI** | Return on Investment (retorno de inversión) |
| **Interés Compuesto** | Reinversión de ganancias al capital |

---

## ❓ FAQ

### **Operación**

**P: ¿Cuántas ventas debo hacer por día?**
R: Entre 3-5 ventas diarias. Más puede generar bloqueos bancarios.

**P: ¿Puedo tener varios ciclos activos?**
R: No, el sistema permite solo un ciclo activo a la vez.

**P: ¿Qué hago si me equivoco al registrar una venta?**
R: No puedes eliminarla, pero puedes documentar el error en Notas para referencia futura.

**P: ¿Debo cerrar el día obligatoriamente?**
R: Sí, es importante cerrar cada día para mantener registros precisos.

### **Capital y Ganancias**

**P: ¿Cómo se calcula el precio sugerido?**
R: `precio_venta = costo / (1 - (comision + ganancia_objetivo)/100)`

**P: ¿Qué es el interés compuesto?**
R: Es sumar las ganancias del día al capital para el día siguiente, incrementando el potencial de ganancia.

**P: ¿Cómo afecta la comisión a mis ganancias?**
R: La comisión reduce el efectivo recibido. Con 0.35% de comisión, necesitas vender a un precio que compense esto más tu ganancia objetivo.

### **Técnicas**

**P: ¿Cómo hago un backup?**
R: Menú > Gestión > Mantenimiento > Crear Backup Manual

**P: ¿Los reportes incluyen todos los datos?**
R: Sí, puedes exportar reportes completos en TXT y CSV con todos los detalles.

**P: ¿Cómo interpreto las alertas?**
R: Las alertas te notifican sobre situaciones que requieren atención. Revisa regularmente el menú de alertas.

---

## 🐛 Solución de Problemas

### **Error: "No se pudo conectar a la base de datos"**
```bash
# Solución:
python inicializar_bd.py
```

### **Error: "matplotlib no instalado"**
```bash
# Linux/Mac:
pip install matplotlib --break-system-packages

# Windows:
pip install matplotlib
```

### **Datos corruptos o comportamiento extraño**
```bash
# 1. Crear backup
python main.py
# Ir a: Gestión > Mantenimiento > Backup

# 2. Verificar integridad
# Ir a: Gestión > Mantenimiento > Verificar Integridad

# 3. Si persiste, reinicializar BD
python inicializar_bd.py
# ADVERTENCIA: Esto borra todos los datos
```

### **Logs para debugging**
Los logs se encuentran en `logs/sistema_YYYY-MM-DD.log`

---

## 📊 Mejores Prácticas

### **Operación Diaria**
1. ✅ Revisa alertas al iniciar
2. ✅ Define precios conservadores
3. ✅ Registra ventas inmediatamente
4. ✅ Respeta límites de ventas (3-5/día)
5. ✅ Cierra el día siempre
6. ✅ Documenta incidentes en Notas

### **Mantenimiento**
1. ✅ Backups semanales
2. ✅ Optimización mensual de BD
3. ✅ Limpia logs antiguos (>90 días)
4. ✅ Revisa reportes periódicamente
5. ✅ Actualiza configuración según resultados

### **Análisis**
1. ✅ Genera reportes al finalizar ciclo
2. ✅ Usa proyecciones para planificar
3. ✅ Compara ciclos con gráficos
4. ✅ Documenta aprendizajes en Notas
5. ✅ Ajusta estrategia según datos

---

## 🔒 Seguridad

### **Datos Sensibles**
- ✅ La BD está en local, sin conexión externa
- ✅ No se almacenan contraseñas ni APIs por defecto
- ✅ Logs no contienen información bancaria
- ✅ Backups en directorio local

### **Recomendaciones**
- 🔐 Mantén backups en ubicación segura
- 🔐 No compartas el archivo `arbitraje.db`
- 🔐 Configura permisos restrictivos en el directorio
- 🔐 Considera encriptar backups importantes

---

## 🤝 Contribuciones

Este es un proyecto personal, pero sugerencias son bienvenidas.

Para reportar bugs:
1. Revisa los logs en `logs/`
2. Describe el problema detalladamente
3. Incluye pasos para reproducir
4. Indica tu versión de Python

---

## 📝 Changelog

### **v3.0 (2025)**
- ✨ Sistema de proyecciones y simulaciones
- ✨ Generador de reportes (CSV/TXT)
- ✨ Sistema de notas y observaciones
- ✨ Sistema de alertas inteligentes
- ✨ Gráficos de rendimiento (matplotlib)
- 🔧 Módulos centralizados (validaciones, queries)
- 🔧 Gestor de BD mejorado (db_manager)
- 🐛 Múltiples correcciones de bugs

### **v2.0**
- Sistema base funcional
- Gestión de ciclos y días
- Bóveda multi-cripto
- Sistema de logs

---

## 📄 Licencia

Este proyecto es de uso personal. Para uso comercial, contacta al autor.

---

## 👨‍💻 Autor

Sistema desarrollado para gestión personal de arbitraje P2P.

**Última actualización:** Octubre 2025
**Versión:** 3.0

---

## 🙏 Agradecimientos

- Python Software Foundation
- SQLite Development Team
- Matplotlib Development Team

---

**⚠️ DISCLAIMER**: Este software es una herramienta de gestión. El usuario es responsable de sus decisiones de inversión. No garantiza ganancias ni asume responsabilidad por pérdidas.
