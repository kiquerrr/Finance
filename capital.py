# capital.py

from apis import obtener_precio_actual
from database import obtener_transacciones_por_ciclo
from utils import redondear

def calcular_capital_por_cripto(ciclo_id):
    transacciones = obtener_transacciones_por_ciclo(ciclo_id)
    capital = {}
    for tx in transacciones:
        cripto = tx['cripto']
        cantidad = tx['cantidad']
        capital[cripto] = capital.get(cripto, 0) + cantidad
    return capital

def convertir_a_usd(cantidad, cripto):
    precio = obtener_precio_actual(cripto)
    return redondear(cantidad * precio)

def resumen_por_ciclo(ciclo_id):
    capital = calcular_capital_por_cripto(ciclo_id)
    resumen = {}
    total_usd = 0
    for cripto, cantidad in capital.items():
        valor_usd = convertir_a_usd(cantidad, cripto)
        resumen[cripto] = {
            'cantidad': redondear(cantidad),
            'valor_usd': valor_usd
        }
        total_usd += valor_usd
    resumen['total_usd'] = redondear(total_usd)
    return resumen

def valor_total_en_usd(ciclo_id):
    resumen = resumen_por_ciclo(ciclo_id)
    return resumen.get('total_usd', 0)
