from datetime import datetime
from models import PropertyDTO, ValuationResponse


def estimate_prices(request: PropertyDTO) -> ValuationResponse:
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
        minSalePrice=min_sale,
        maxSalePrice=max_sale,
        minRentalPrice=min_rent,
        maxRentalPrice=max_rent,
        valuationDate=datetime.now()
    )
