# -*- coding: utf-8 -*-

CRIPTOS_DISPONIBLES = {
    'USDT': {
        'nombre': 'Tether',
        'simbolo': 'USDT',
        'decimales': 4,
        'tipo': 'Stablecoin',
        'descripcion': 'Moneda estable vinculada al dolar'
    },
    'USDC': {
        'nombre': 'USD Coin',
        'simbolo': 'USDC',
        'decimales': 4,
        'tipo': 'Stablecoin',
        'descripcion': 'Moneda estable respaldada por dolares'
    },
    'BTC': {
        'nombre': 'Bitcoin',
        'simbolo': 'BTC',
        'decimales': 8,
        'tipo': 'Criptomoneda',
        'descripcion': 'La primera y mas conocida criptomoneda'
    },
    'ETH': {
        'nombre': 'Ethereum',
        'simbolo': 'ETH',
        'decimales': 6,
        'tipo': 'Criptomoneda',
        'descripcion': 'Plataforma de contratos inteligentes'
    },
    'BNB': {
        'nombre': 'Binance Coin',
        'simbolo': 'BNB',
        'decimales': 6,
        'tipo': 'Criptomoneda',
        'descripcion': 'Token nativo de Binance'
    },
    'DAI': {
        'nombre': 'Dai',
        'simbolo': 'DAI',
        'decimales': 4,
        'tipo': 'Stablecoin',
        'descripcion': 'Stablecoin descentralizada'
    }
}

def listar_criptos():
    """Muestra lista de criptos disponibles."""
    print("\n" + "=" * 60)
    print("CRIPTOMONEDAS DISPONIBLES")
    print("=" * 60)
    
    for i, (codigo, info) in enumerate(CRIPTOS_DISPONIBLES.items(), 1):
        emoji = "$" if info['tipo'] == 'Stablecoin' else "B"
        print(f"\n{emoji} [{i}] {info['nombre']} ({codigo})")
        print(f"    Tipo: {info['tipo']}")
        print(f"    {info['descripcion']}")
    
    print("=" * 60)

def seleccionar_cripto():
    """Permite al usuario seleccionar una cripto."""
    listar_criptos()
    
    while True:
        try:
            opcion = int(input("\nSelecciona una opcion (numero): "))
            if 1 <= opcion <= len(CRIPTOS_DISPONIBLES):
                cripto_codigo = list(CRIPTOS_DISPONIBLES.keys())[opcion - 1]
                info = CRIPTOS_DISPONIBLES[cripto_codigo]
                print(f"\nSeleccionaste: {info['nombre']} ({cripto_codigo})")
                return cripto_codigo
            else:
                print(f"Opcion invalida. Elige entre 1 y {len(CRIPTOS_DISPONIBLES)}")
        except ValueError:
            print("Ingresa un numero valido.")

def obtener_info_cripto(codigo):
    """Obtiene informacion de una cripto."""
    return CRIPTOS_DISPONIBLES.get(codigo.upper())

def formatear_cantidad_cripto(cantidad, cripto):
    """Formatea cantidad segun los decimales de la cripto."""
    info = obtener_info_cripto(cripto)
    if info:
        decimales = info['decimales']
        return f"{cantidad:.{decimales}f}"
    return f"{cantidad:.4f}"

def validar_cripto(codigo):
    """Valida si un codigo de cripto existe."""
    return codigo.upper() in CRIPTOS_DISPONIBLES

def obtener_simbolo(cripto):
    """Obtiene el simbolo de una cripto."""
    info = obtener_info_cripto(cripto)
    return info['simbolo'] if info else cripto
