"""
=============================================================================
MÓDULO DE CÁLCULOS - Fórmulas Corregidas y Verificadas
=============================================================================
Todas las fórmulas están documentadas y registradas en el logger
"""

from logger import log

class CalculadoraArbitraje:
    """Maneja todos los cálculos del sistema con precisión"""
    
    def __init__(self, comision_default=0.35):
        """
        Inicializa la calculadora
        
        Args:
            comision_default: Porcentaje de comisión por defecto (ej: 0.35 para 0.35%)
        """
        self.comision_pct = comision_default
    
    # ===================================================================
    # CÁLCULOS DE PRECIO
    # ===================================================================
    
    def calcular_precio_sugerido(self, costo_promedio, ganancia_objetivo_pct):
        """
        Calcula el precio de venta sugerido para alcanzar la ganancia objetivo
        
        Fórmula:
        precio_sugerido = costo_promedio * (1 + (comision + ganancia_objetivo) / 100)
        
        Args:
            costo_promedio: Costo promedio de compra por unidad
            ganancia_objetivo_pct: Ganancia neta objetivo (ej: 2.0 para 2%)
        
        Returns:
            float: Precio de venta sugerido
        """
        margen_total = self.comision_pct + ganancia_objetivo_pct
        precio_sugerido = costo_promedio * (1 + (margen_total / 100))
        
        log.info(
            f"Cálculo precio sugerido: Costo={costo_promedio:.4f}, "
            f"Comisión={self.comision_pct}%, Ganancia objetivo={ganancia_objetivo_pct}%, "
            f"Precio sugerido={precio_sugerido:.4f}",
            categoria='calculos'
        )
        
        return precio_sugerido
    
    def calcular_ganancia_neta_estimada(self, costo_promedio, precio_venta):
        """
        Calcula la ganancia neta estimada dado un precio de venta
        
        Fórmula:
        ganancia_bruta_pct = ((precio_venta - costo_promedio) / costo_promedio) * 100
        ganancia_neta_pct = ganancia_bruta_pct - comision_pct
        
        Args:
            costo_promedio: Costo promedio de compra
            precio_venta: Precio al que se planea vender
        
        Returns:
            float: Ganancia neta estimada en porcentaje
        """
        if costo_promedio == 0:
            log.error("Costo promedio es cero", "No se puede calcular ganancia")
            return 0
        
        ganancia_bruta_pct = ((precio_venta - costo_promedio) / costo_promedio) * 100
        ganancia_neta_pct = ganancia_bruta_pct - self.comision_pct
        
        log.info(
            f"Ganancia estimada: Costo={costo_promedio:.4f}, "
            f"Precio venta={precio_venta:.4f}, "
            f"Ganancia bruta={ganancia_bruta_pct:.2f}%, "
            f"Ganancia neta={ganancia_neta_pct:.2f}%",
            categoria='calculos'
        )
        
        return ganancia_neta_pct
    
    # ===================================================================
    # CÁLCULOS DE VENTA
    # ===================================================================
    
    def calcular_venta(self, cantidad, costo_unitario, precio_venta):
        """
        Calcula todos los valores de una venta
        
        Args:
            cantidad: Cantidad de cripto vendida
            costo_unitario: Costo promedio unitario de compra
            precio_venta: Precio unitario de venta
        
        Returns:
            dict: Todos los valores de la venta
        """
        # Validaciones
        if cantidad <= 0:
            log.error("Cantidad inválida", f"Cantidad={cantidad}")
            return None
        
        if costo_unitario <= 0:
            log.error("Costo unitario inválido", f"Costo={costo_unitario}")
            return None
        
        if precio_venta <= 0:
            log.error("Precio de venta inválido", f"Precio={precio_venta}")
            return None
        
        # Cálculos
        costo_total = cantidad * costo_unitario
        monto_venta = cantidad * precio_venta
        comision = monto_venta * (self.comision_pct / 100)
        efectivo_recibido = monto_venta - comision
        ganancia_bruta = monto_venta - costo_total
        ganancia_neta = ganancia_bruta - comision
        
        # ROI
        roi_pct = (ganancia_neta / costo_total * 100) if costo_total > 0 else 0
        
        resultado = {
            'cantidad': cantidad,
            'costo_unitario': costo_unitario,
            'precio_venta': precio_venta,
            'costo_total': costo_total,
            'monto_venta': monto_venta,
            'comision_pct': self.comision_pct,
            'comision': comision,
            'efectivo_recibido': efectivo_recibido,
            'ganancia_bruta': ganancia_bruta,
            'ganancia_neta': ganancia_neta,
            'roi_pct': roi_pct
        }
        
        # Registrar en log con detalle
        log.calculo_venta(
            cripto="",  # Se pasa desde donde se llame
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            precio_venta=precio_venta,
            comision_pct=self.comision_pct
        )
        
        return resultado
    
    # ===================================================================
    # CÁLCULOS DE CAPITAL
    # ===================================================================
    
    def calcular_capital_cripto(self, cantidad, precio_actual):
        """
        Calcula el valor en USD de una cantidad de cripto
        
        Args:
            cantidad: Cantidad de cripto
            precio_actual: Precio actual por unidad
        
        Returns:
            float: Valor en USD
        """
        valor = cantidad * precio_actual
        log.info(
            f"Capital cripto: {cantidad} x ${precio_actual:.4f} = ${valor:.2f} USD",
            categoria='calculos'
        )
        return valor
    
    def calcular_capital_total(self, criptos):
        """
        Calcula el capital total sumando todas las criptos
        
        Args:
            criptos: Lista de tuplas (nombre, cantidad, precio_unitario)
        
        Returns:
            float: Capital total en USD
        """
        total = 0
        detalle = []
        
        for nombre, cantidad, precio in criptos:
            valor = cantidad * precio
            total += valor
            detalle.append(f"{nombre}: {cantidad} x ${precio:.4f} = ${valor:.2f}")
        
        log.info(
            f"Capital total calculado:\n" + "\n".join(detalle) + f"\nTOTAL: ${total:.2f} USD",
            categoria='calculos'
        )
        
        return total
    
    def calcular_costo_promedio(self, compras):
        """
        Calcula el costo promedio ponderado de compra
        
        Args:
            compras: Lista de tuplas (cantidad, precio_unitario)
        
        Returns:
            float: Costo promedio por unidad
        """
        if not compras:
            return 0
        
        costo_total = sum(cantidad * precio for cantidad, precio in compras)
        cantidad_total = sum(cantidad for cantidad, precio in compras)
        
        if cantidad_total == 0:
            return 0
        
        costo_promedio = costo_total / cantidad_total
        
        log.info(
            f"Costo promedio: ${costo_total:.2f} / {cantidad_total} = ${costo_promedio:.4f}",
            categoria='calculos'
        )
        
        return costo_promedio
    
    # ===================================================================
    # CÁLCULOS DE DÍA
    # ===================================================================
    
    def calcular_resumen_dia(self, capital_inicial, ventas, capital_final_criptos):
        """
        Calcula el resumen completo de un día de operación
        
        Args:
            capital_inicial: Capital al inicio del día
            ventas: Lista de ventas realizadas (cada una con su dict de cálculo)
            capital_final_criptos: Capital que queda en criptos
        
        Returns:
            dict: Resumen del día
        """
        # Ventas del día
        total_vendido_cripto = sum(v['cantidad'] for v in ventas)
        total_monto_ventas = sum(v['monto_venta'] for v in ventas)
        total_comisiones = sum(v['comision'] for v in ventas)
        total_efectivo_recibido = sum(v['efectivo_recibido'] for v in ventas)
        total_ganancia_bruta = sum(v['ganancia_bruta'] for v in ventas)
        total_ganancia_neta = sum(v['ganancia_neta'] for v in ventas)
        
        # Capital final total
        capital_final_total = capital_final_criptos + total_efectivo_recibido
        
        # Balance del día
        balance = capital_final_total - capital_inicial
        
        resumen = {
            'capital_inicial': capital_inicial,
            'capital_final_criptos': capital_final_criptos,
            'efectivo_recibido': total_efectivo_recibido,
            'capital_final_total': capital_final_total,
            'total_vendido_cripto': total_vendido_cripto,
            'total_monto_ventas': total_monto_ventas,
            'total_comisiones': total_comisiones,
            'total_ganancia_bruta': total_ganancia_bruta,
            'total_ganancia_neta': total_ganancia_neta,
            'balance': balance,
            'num_ventas': len(ventas)
        }
        
        # Registrar en log
        log.calculo_capital_dia(
            capital_inicial=capital_inicial,
            ventas=ventas,
            capital_final=capital_final_total
        )
        
        return resumen
    
    # ===================================================================
    # CÁLCULOS DE CICLO
    # ===================================================================
    
    def calcular_resumen_ciclo(self, inversion_inicial, dias_operados, ganancias_dias, capital_final):
        """
        Calcula el resumen completo de un ciclo
        
        Args:
            inversion_inicial: Inversión inicial del ciclo
            dias_operados: Número de días operados
            ganancias_dias: Lista de ganancias por día
            capital_final: Capital final al cerrar el ciclo
        
        Returns:
            dict: Resumen del ciclo
        """
        ganancia_total = sum(ganancias_dias)
        
        # ROI del ciclo
        if inversion_inicial > 0:
            roi_total = (ganancia_total / inversion_inicial) * 100
            roi_diario_promedio = roi_total / dias_operados if dias_operados > 0 else 0
        else:
            roi_total = 0
            roi_diario_promedio = 0
        
        # Ganancia diaria promedio
        ganancia_promedio_dia = ganancia_total / dias_operados if dias_operados > 0 else 0
        
        resumen = {
            'inversion_inicial': inversion_inicial,
            'dias_operados': dias_operados,
            'ganancia_total': ganancia_total,
            'ganancia_promedio_dia': ganancia_promedio_dia,
            'capital_final': capital_final,
            'roi_total_pct': roi_total,
            'roi_diario_promedio_pct': roi_diario_promedio
        }
        
        log.info(
            f"Resumen ciclo: Inversión=${inversion_inicial:.2f}, "
            f"Días={dias_operados}, Ganancia=${ganancia_total:.2f}, "
            f"Capital final=${capital_final:.2f}, ROI={roi_total:.2f}%",
            categoria='calculos'
        )
        
        return resumen
    
    # ===================================================================
    # UTILIDADES
    # ===================================================================
    
    def formatear_moneda(self, valor):
        """Formatea un valor como moneda"""
        return f"${valor:,.2f}"
    
    def formatear_cripto(self, valor, decimales=8):
        """Formatea una cantidad de cripto"""
        return f"{valor:.{decimales}f}"
    
    def formatear_porcentaje(self, valor):
        """Formatea un porcentaje"""
        return f"{valor:.2f}%"


# ===================================================================
# INSTANCIA GLOBAL
# ===================================================================
calc = CalculadoraArbitraje()


# ===================================================================
# FUNCIONES DE UTILIDAD PARA TESTING
# ===================================================================

def test_calculo_venta():
    """Prueba el cálculo de una venta"""
    print("\n=== TEST: Cálculo de Venta ===")
    
    # Caso: Vender 100 USDT comprados a $1.00, vendidos a $1.05
    resultado = calc.calcular_venta(
        cantidad=100,
        costo_unitario=1.00,
        precio_venta=1.05
    )
    
    print(f"\nCantidad vendida: {resultado['cantidad']} USDT")
    print(f"Costo unitario: ${resultado['costo_unitario']:.4f}")
    print(f"Precio venta: ${resultado['precio_venta']:.4f}")
    print(f"─────────────────────────────")
    print(f"Costo total: ${resultado['costo_total']:.2f}")
    print(f"Monto venta: ${resultado['monto_venta']:.2f}")
    print(f"Comisión ({resultado['comision_pct']}%): ${resultado['comision']:.2f}")
    print(f"Efectivo recibido: ${resultado['efectivo_recibido']:.2f}")
    print(f"─────────────────────────────")
    print(f"Ganancia bruta: ${resultado['ganancia_bruta']:.2f}")
    print(f"Ganancia neta: ${resultado['ganancia_neta']:.2f}")
    print(f"ROI: {resultado['roi_pct']:.2f}%")
    
    # Verificación
    esperado_ganancia_neta = 100 * 1.05 - 100 * 1.05 * 0.0035 - 100
    print(f"\n✓ Ganancia neta esperada: ${esperado_ganancia_neta:.2f}")
    print(f"✓ Ganancia neta calculada: ${resultado['ganancia_neta']:.2f}")
    print(f"✓ Diferencia: ${abs(esperado_ganancia_neta - resultado['ganancia_neta']):.6f}")


if __name__ == "__main__":
    test_calculo_venta()
