# 📦 Guía de Instalación Completa

Esta guía te llevará paso a paso en la instalación del Sistema de Arbitraje P2P v3.0.

---

## 📋 Requisitos Previos

### **1. Python**

**Verificar si tienes Python instalado:**
```bash
python --version
# o
python3 --version
```

**Si no tienes Python:**
- **Windows**: Descarga desde [python.org](https://www.python.org/downloads/)
- **Linux**: 
```bash
  sudo apt update
  sudo apt install python3 python3-pip
```
- **macOS**: 
```bash
  brew install python3
```

**Versión requerida:** Python 3.7 o superior

---

## 🚀 Instalación Paso a Paso

### **Método 1: Instalación Automática (Recomendado)**

#### **Paso 1: Descargar el proyecto**
```bash
# Si tienes git:
git clone [URL_DEL_REPO]
cd arbitraje/

# O descarga el ZIP y extráelo
```

#### **Paso 2: Ejecutar instalador**
```bash
python setup.py
```

Selecciona opción `[1] Instalación completa`

El script:
- ✅ Verificará Python
- ✅ Creará directorios necesarios
- ✅ Instalará dependencias (opcional)
- ✅ Verificará archivos

#### **Paso 3: Inicializar base de datos**
```bash
python inicializar_bd.py
```

Confirma escribiendo `CONFIRMAR` cuando se te pida.

#### **Paso 4: Iniciar el sistema**
```bash
python main.py
```

---

### **Método 2: Instalación Manual**

#### **Paso 1: Verificar archivos**

Asegúrate de tener estos archivos:

**Archivos obligatorios:**
```
✅ main.py
✅ inicializar_bd.py
✅ db_manager.py
✅ logger.py
✅ calculos.py
✅ operador.py
✅ boveda.py
✅ ciclos.py
✅ dias.py
✅ configuracion.py
✅ mantenimiento.py
```

**Archivos opcionales (funcionalidades v3.0):**
```
📦 proyecciones.py
📦 reportes.py
📦 notas.py
📦 alertas.py
📦 graficos.py
📦 validaciones.py
📦 queries.py
```

#### **Paso 2: Crear directorios**
```bash
mkdir logs backups reportes graficos
```

#### **Paso 3: Instalar dependencias opcionales**

**Para gráficos (recomendado):**
```bash
# Linux/macOS:
pip3 install matplotlib --break-system-packages

# Windows:
pip install matplotlib
```

**Para mejor manejo de fechas (opcional):**
```bash
# Linux/macOS:
pip3 install python-dateutil --break-system-packages

# Windows:
pip install python-dateutil
```

#### **Paso 4: Inicializar base de datos**
```bash
python inicializar_bd.py
```

Selecciona opción `[1]` y confirma con `CONFIRMAR`.

#### **Paso 5: Verificar instalación**
```bash
python setup.py
```

Selecciona opción `[3] Solo verificar sistema`

#### **Paso 6: Iniciar**
```bash
python main.py
```

---

## ⚙️ Configuración Post-Instalación

### **Primera Configuración**

1. **Acceder a Configuración**
```
   Menu Principal > [3] Gestión del Sistema > [3] Configuración
```

2. **Configurar parámetros básicos:**
   - **Comisión plataforma**: Default 0.35%
   - **Ganancia objetivo**: Default 2.0%
   - **Límites de ventas**: Min 3, Max 5

3. **Fondear la bóveda**
```
   Menu Principal > [3] Gestión > [1] Bóveda > [1] Registrar Compra
```
   
   Ejemplo:
```
   Cripto: USDT
   Cantidad: 1000
   Monto USD: 1000
   Tasa: 1.0000
```

---

## 🧪 Verificar que Todo Funciona

### **Test 1: Crear primer ciclo (automático)**
```
Menu Principal > [1] Operaciones > [1] Iniciar Día
```

El sistema creará automáticamente tu primer ciclo.

### **Test 2: Simular día completo**

1. **Iniciar día**
   - Define precio de venta
   
2. **Registrar venta ficticia**
   - Cantidad: 50 USDT
   - Precio: [El que hayas definido]
   
3. **Cerrar día**
   - Revisa resumen
   - No apliques interés compuesto por ahora

### **Test 3: Verificar logs**
```bash
# Linux/macOS:
cat logs/sistema_$(date +%Y-%m-%d).log

# Windows:
type logs\sistema_2025-10-28.log
```

Deberías ver registros de:
- Sistema iniciado
- Ciclo creado
- Día iniciado
- Venta registrada
- Día cerrado

### **Test 4: Generar reporte**
```
Menu Principal > [2] Análisis > [2] Generar Reportes > [1] Reporte de ciclo
```

---

## 🐛 Solución de Problemas Comunes

### **Error: "No se encuentra el módulo 'sqlite3'"**

**Python en Linux puede no incluir sqlite3 por defecto:**
```bash
sudo apt install libsqlite3-dev
pip3 install pysqlite3
```

### **Error: "Permission denied" (Linux/macOS)**

**Dale permisos de ejecución:**
```bash
chmod +x main.py
chmod +x setup.py
chmod +x inicializar_bd.py
```

### **Error: "pip no reconocido" (Windows)**

**Instala pip:**
```bash
python -m ensurepip --upgrade
```

O reinstala Python con la opción "Add Python to PATH".

### **matplotlib no se instala (Linux)**

**Instala dependencias del sistema:**
```bash
sudo apt install python3-tk
pip3 install matplotlib --break-system-packages
```

### **Base de datos corrupta**

**Reiniciar desde cero:**
```bash
# 1. Hacer backup si existe
cp arbitraje.db arbitraje_old.db

# 2. Reinicializar
python inicializar_bd.py
```

---

## 📱 Instalación en Diferentes Sistemas

### **Windows 10/11**
```bash
# 1. Abrir PowerShell o CMD
cd ruta\al\proyecto

# 2. Crear entorno virtual (opcional)
python -m venv venv
venv\Scripts\activate

# 3. Instalar
pip install matplotlib
python inicializar_bd.py
python main.py
```

### **Ubuntu/Debian**
```bash
# 1. Instalar Python y dependencias
sudo apt update
sudo apt install python3 python3-pip python3-tk

# 2. Instalar matplotlib
pip3 install matplotlib --break-system-packages

# 3. Inicializar
python3 inicializar_bd.py
python3 main.py
```

### **macOS**
```bash
# 1. Instalar Homebrew (si no lo tienes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalar Python
brew install python3

# 3. Instalar matplotlib
pip3 install matplotlib

# 4. Inicializar
python3 inicializar_bd.py
python3 main.py
```

### **Raspberry Pi**
```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade

# 2. Instalar dependencias
sudo apt install python3-pip python3-matplotlib

# 3. Configurar (mismo proceso)
python3 inicializar_bd.py
python3 main.py
```

---

## 🔄 Actualización de Versión Anterior

### **Desde v2.0 a v3.0**

**⚠️ IMPORTANTE: Hacer backup primero**
```bash
# 1. Backup de BD actual
cp arbitraje.db arbitraje_v2_backup.db

# 2. Backup de logs
cp -r logs/ logs_v2_backup/

# 3. Actualizar archivos
# (Reemplaza todos los archivos .py con las nuevas versiones)

# 4. Ejecutar migración (si aplica)
python setup.py

# 5. Verificar integridad
python main.py
# Ir a: Gestión > Mantenimiento > Verificar Integridad
```

---

## ✅ Checklist Final

Antes de empezar a operar, verifica:

- [ ] Python 3.7+ instalado
- [ ] Base de datos creada (`arbitraje.db` existe)
- [ ] Directorios creados (logs, backups, reportes, graficos)
- [ ] Configuración establecida (comisión, ganancia)
- [ ] Bóveda fondeada (al menos una cripto)
- [ ] Test de día completo exitoso
- [ ] Logs generándose correctamente
- [ ] Reportes exportables

---

## 📞 Soporte

Si tienes problemas:

1. **Revisa los logs**: `logs/sistema_YYYY-MM-DD.log`
2. **Verifica integridad**: Menu > Mantenimiento > Verificar Integridad
3. **Consulta FAQ**: Ver `README.md` sección FAQ
4. **Reinstala**: En último caso, reinicializa la BD

---

**¡Listo para operar! 🚀**

Continúa con el [README.md](README.md) para aprender a usar el sistema.
