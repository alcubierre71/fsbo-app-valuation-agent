# Clases de Modelos del Agente

from datetime import datetime

from pydantic import BaseModel

# Modelo interno del agente para representar una propiedad
class Property(BaseModel):
    built_area: int
    bedrooms: int
    bathrooms: int
    floor: int
    condition: str
    property_type: str
    description: str
    exterior: bool
    has_elevator: bool
    has_parking: bool
    has_storage_room: bool
    has_air_conditioning: bool
    has_balcony_or_terrace: bool
    has_pool: bool
    country: str
    region: str
    province: str
    city: str
    district: str
    neighborhood: str

# Modelo interno del agente para representar la respuesta de valoración
class ValuationResponse(BaseModel):
    min_sale_price: float
    max_sale_price: float
    min_rental_price: float
    max_rental_price: float
    valuation_date: datetime

# Modelo GeneratedReponse del Nodo Generator
class GeneratedResponse(BaseModel):
    min_sale_price: float
    max_sale_price: float
    min_rental_price: float
    max_rental_price: float
    valuation_date: str
