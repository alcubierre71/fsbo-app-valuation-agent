from datetime import datetime
from models import Property, ValuationResponse

def estimate_prices(request: Property) -> ValuationResponse: 
    prop = request

    base_price = prop.built_area * 2_200
    bedrooms_factor = prop.bedrooms * 10_000
    floor_factor = prop.floor * 2_000

    min_sale = round(base_price + bedrooms_factor + floor_factor, 2)
    max_sale = round(min_sale * 1.20, 2)
    min_rent = round(min_sale * 0.004, 2)
    max_rent = round(min_sale * 0.0055, 2)

    # ✅  Usamos los alias camelCase para contentar a Pylance
    return ValuationResponse(
        min_sale_price=min_sale,
        max_sale_price=max_sale,
        min_rental_price=min_rent,
        max_rental_price=max_rent,
        valuation_date=datetime.now()
    )
