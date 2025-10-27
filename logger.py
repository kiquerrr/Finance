"""
=============================================================================
MÓDULO DE LOGGING - Sistema de Registro Completo
=============================================================================
Registra todas las operaciones, cálculos, errores y cambios de estado
"""

import os
from datetime import datetime
from pathlib import Path

class Logger:
    """Sistema de logging completo para el sistema de arbitraje"""
    
    def __init__(self, log_dir="logs"):
        """Inicializa el logger"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Archivos de log separados por categoría
        self.logs = {
            'general': self.log_dir / 'general.log',
            'operaciones': self.log_dir / 'operaciones.log',
            'calculos': self.log_dir / 'calculos.log',
            'errores': self.log_dir / 'errores.log',
            'boveda': self.log_dir / 'boveda.log',
            'ciclos': self.log_dir / 'ciclos.log'
        }
        
        # Crear archivos si no existen
        for log_file in self.logs.values():
            if not log_file.exists():
                log_file.touch()
    
    def _escribir(self, categoria, mensaje, nivel="INFO"):
        """Escribe un mensaje en el log correspondiente"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{timestamp}] [{nivel}] {mensaje}\n"
        
        # Escribir en el log específico
        if categoria in self.logs:
            with open(self.logs[categoria], 'a', encoding='utf-8') as f:
                f.write(linea)
        
        # También escribir en el log general
        with open(self.logs['general'], 'a', encoding='utf-8') as f:
            f.write(f"[{categoria.upper()}] {linea}")
    
    # ===================================================================
    # MÉTODOS ESPECÍFICOS POR CATEGORÍA
    # ===================================================================
    
    def info(self, mensaje, categoria='general'):
        """Registra información general"""
        self._escribir(categoria, mensaje, "INFO")
    
    def advertencia(self, mensaje, categoria='general'):
        """Registra advertencias"""
        self._escribir(categoria, mensaje, "WARNING")
    
    def error(self, mensaje, detalle="", categoria='errores'):
        """Registra errores con detalles"""
        msg = f"{mensaje}"
        if detalle:
            msg += f"\n    Detalle: {detalle}"
        self._escribir(categoria, msg, "ERROR")
    
    # ===================================================================
    # OPERACIONES DE BÓVEDA
    # ===================================================================
    
    def boveda_compra(self, cripto, cantidad, monto_usd, tasa, ciclo_id):
        """Registra una compra en la bóveda"""
        mensaje = f"""
    COMPRA REGISTRADA
    Ciclo: #{ciclo_id}
    Cripto: {cripto}
    Cantidad comprada: {cantidad}
    Monto invertido: ${monto_usd:.2f} USD
    Tasa de compra: 1 {cripto} = ${tasa:.4f} USD
    """
        self._escribir('boveda', mensaje, "INFO")
    
    def boveda_transferencia(self, cripto, cantidad, valor_usd, origen, destino):
        """Registra transferencias de capital"""
        mensaje = f"""
    TRANSFERENCIA
    Cripto: {cripto}
    Cantidad: {cantidad}
    Valor: ${valor_usd:.2f} USD
    Origen: {origen}
    Destino: {destino}
    """
        self._escribir('boveda', mensaje, "INFO")
    
    # ===================================================================
    # OPERACIONES DE CICLO
    # ===================================================================
    
    def ciclo_creado(self, ciclo_id, dias, capital_inicial, fecha_inicio, fecha_fin):
        """Registra la creación de un ciclo"""
        mensaje = f"""
    NUEVO CICLO CREADO
    ID: #{ciclo_id}
    Duración: {dias} días
    Capital inicial: ${capital_inicial:.2f} USD
    Fecha inicio: {fecha_inicio}
    Fecha fin estimada: {fecha_fin}
    """
        self._escribir('ciclos', mensaje, "INFO")
    
    def ciclo_cerrado(self, ciclo_id, dias_operados, inversion_inicial, ganancia_total, capital_final):
        """Registra el cierre de un ciclo"""
        roi = (ganancia_total / inversion_inicial * 100) if inversion_inicial > 0 else 0
        mensaje = f"""
    CICLO CERRADO
    ID: #{ciclo_id}
    Días operados: {dias_operados}
    Inversión inicial: ${inversion_inicial:.2f} USD
    Ganancia total: ${ganancia_total:.2f} USD
    Capital final: ${capital_final:.2f} USD
    ROI: {roi:.2f}%
    """
        self._escribir('ciclos', mensaje, "INFO")
    
    # ===================================================================
    # OPERACIONES DIARIAS
    # ===================================================================
    
    def dia_iniciado(self, ciclo_id, dia_num, capital_inicial, criptos_disponibles):
        """Registra el inicio de un día de operación"""
        cripto_detalle = "\n    ".join([f"{c}: {cant} ({val:.2f} USD)" 
                                        for c, cant, val in criptos_disponibles])
        mensaje = f"""
    DÍA INICIADO
    Ciclo: #{ciclo_id}
    Día: #{dia_num}
    Capital inicial: ${capital_inicial:.2f} USD
    Criptos disponibles:
    {cripto_detalle}
    """
        self._escribir('operaciones', mensaje, "INFO")
    
    def precio_definido(self, cripto, costo_promedio, comision, ganancia_objetivo, precio_publicado, ganancia_neta_estimada):
        """Registra la definición de precio de venta"""
        mensaje = f"""
    PRECIO DE VENTA DEFINIDO
    Cripto: {cripto}
    Costo promedio: ${costo_promedio:.4f}
    Comisión: {comision:.2f}%
    Ganancia objetivo: {ganancia_objetivo:.2f}%
    Precio publicado: ${precio_publicado:.4f}
    Ganancia neta estimada: {ganancia_neta_estimada:.2f}%
    """
        self._escribir('operaciones', mensaje, "INFO")
    
    def venta_registrada(self, venta_num, cripto, cantidad_vendida, precio_unitario, monto_total, comision_pagada, ganancia_neta):
        """Registra una venta individual"""
        mensaje = f"""
    VENTA #{venta_num} REGISTRADA
    Cripto: {cripto}
    Cantidad vendida: {cantidad_vendida}
    Precio unitario: ${precio_unitario:.4f}
    Monto total recibido: ${monto_total:.2f} USD
    Comisión pagada: ${comision_pagada:.2f} USD
    Ganancia neta: ${ganancia_neta:.2f} USD
    """
        self._escribir('operaciones', mensaje, "INFO")
    
    def dia_cerrado(self, ciclo_id, dia_num, capital_inicial, capital_final, ganancia_dia, ventas_realizadas):
        """Registra el cierre de un día"""
        mensaje = f"""
    DÍA CERRADO
    Ciclo: #{ciclo_id}
    Día: #{dia_num}
    Capital inicial: ${capital_inicial:.2f} USD
    Capital final: ${capital_final:.2f} USD
    Ganancia del día: ${ganancia_dia:.2f} USD
    Ventas realizadas: {ventas_realizadas}
    """
        self._escribir('operaciones', mensaje, "INFO")
    
    # ===================================================================
    # CÁLCULOS DETALLADOS
    # ===================================================================
    
    def calculo_venta(self, cripto, cantidad, costo_unitario, precio_venta, comision_pct):
        """Registra el detalle de cálculo de una venta"""
        costo_total = cantidad * costo_unitario
        monto_venta = cantidad * precio_venta
        comision = monto_venta * (comision_pct / 100)
        ganancia_bruta = monto_venta - costo_total
        ganancia_neta = ganancia_bruta - comision
        
        mensaje = f"""
    CÁLCULO DE VENTA
    ─────────────────────────────────────────────
    Cripto: {cripto}
    Cantidad: {cantidad}
    
    COSTOS:
    - Costo unitario: ${costo_unitario:.4f}
    - Costo total: ${costo_total:.2f} USD
    
    VENTA:
    - Precio venta: ${precio_venta:.4f}
    - Monto total: ${monto_venta:.2f} USD
    
    COMISIONES:
    - Porcentaje: {comision_pct:.2f}%
    - Monto: ${comision:.2f} USD
    
    GANANCIAS:
    - Ganancia bruta: ${ganancia_bruta:.2f} USD
    - Ganancia neta: ${ganancia_neta:.2f} USD
    - ROI: {(ganancia_neta/costo_total*100):.2f}%
    ─────────────────────────────────────────────
    """
        self._escribir('calculos', mensaje, "INFO")
        
        return {
            'costo_total': costo_total,
            'monto_venta': monto_venta,
            'comision': comision,
            'ganancia_bruta': ganancia_bruta,
            'ganancia_neta': ganancia_neta
        }
    
    def calculo_capital_dia(self, capital_inicial, ventas, capital_final):
        """Registra el cálculo del capital al final del día"""
        total_vendido = sum(v['monto_venta'] for v in ventas)
        total_comisiones = sum(v['comision'] for v in ventas)
        total_ganancias = sum(v['ganancia_neta'] for v in ventas)
        
        mensaje = f"""
    CÁLCULO CAPITAL DEL DÍA
    ─────────────────────────────────────────────
    Capital inicial: ${capital_inicial:.2f} USD
    
    RESUMEN DE VENTAS:
    - Total vendido: ${total_vendido:.2f} USD
    - Total comisiones: ${total_comisiones:.2f} USD
    - Total ganancias: ${total_ganancias:.2f} USD
    
    Capital final: ${capital_final:.2f} USD
    Diferencia: ${capital_final - capital_inicial:.2f} USD
    ─────────────────────────────────────────────
    """
        self._escribir('calculos', mensaje, "INFO")
    
    # ===================================================================
    # UTILIDADES
    # ===================================================================
    
    def separador(self, categoria='general'):
        """Agrega un separador visual en el log"""
        self._escribir(categoria, "="*60, "INFO")
    
    def limpiar_logs_antiguos(self, dias=30):
        """Limpia logs más antiguos que X días"""
        # Implementar si es necesario
        pass
    
    def generar_reporte_dia(self, ciclo_id, dia_num):
        """Genera un reporte del día en formato legible"""
        reporte_path = self.log_dir / f"reporte_ciclo_{ciclo_id}_dia_{dia_num}.txt"
        # Implementar generación de reporte
        pass


# ===================================================================
# INSTANCIA GLOBAL
# ===================================================================
log = Logger()


# ===================================================================
# FUNCIONES DE UTILIDAD
# ===================================================================

def ver_log(categoria='general', ultimas_lineas=50):
    """Muestra las últimas líneas de un log"""
    logger = Logger()
    if categoria in logger.logs:
        with open(logger.logs[categoria], 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            return ''.join(lineas[-ultimas_lineas:])
    return "Categoría de log no encontrada"

def buscar_en_logs(texto, categoria='general'):
    """Busca un texto en los logs"""
    logger = Logger()
    resultados = []
    if categoria in logger.logs:
        with open(logger.logs[categoria], 'r', encoding='utf-8') as f:
            for num_linea, linea in enumerate(f, 1):
                if texto.lower() in linea.lower():
                    resultados.append(f"Línea {num_linea}: {linea.strip()}")
    return resultados
