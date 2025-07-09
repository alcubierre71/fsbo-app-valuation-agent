from pydantic import BaseModel, Field
from datetime import datetime

class PropertyDTO(BaseModel):
    built_area: int = Field(..., alias="builtArea")
    bedrooms: int
    bathrooms: int
    floor: int
    condition: str
    region: str
    city: str
    property_type: str = Field(..., alias="propertyType")
    description: str
    exterior: bool
    has_elevator: bool = Field(..., alias="hasElevator")
    has_parking: bool = Field(..., alias="hasParking")
    has_storage_room: bool = Field(..., alias="hasStorageRoom")
    has_air_conditioning: bool = Field(..., alias="hasAirConditioning")
    has_balcony_or_terrace: bool = Field(..., alias="hasBalconyOrTerrace")
    has_pool: bool = Field(..., alias="hasPool")
    country: str
    region: str = Field(..., alias="region")
    province: str
    city: str
    district: str
    neighborhood: str

    class Config:
        allow_population_by_field_name = True


class UserDTO(BaseModel):
    id: str
    alias: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: str
    phone_number: str = Field(..., alias="phoneNumber")
    preferred_lang: str = Field(..., alias="preferredLang")
    account_type: str = Field(..., alias="accountType")

    class Config:
        allow_population_by_field_name = True


class ValuationRequest(BaseModel):
    property: PropertyDTO
    user: UserDTO


class ValuationResponse(BaseModel):
    min_sale_price: float = Field(..., alias="minSalePrice")
    max_sale_price: float = Field(..., alias="maxSalePrice")
    min_rental_price: float = Field(..., alias="minRentalPrice")
    max_rental_price: float = Field(..., alias="maxRentalPrice")
    valuation_date: datetime = Field(..., alias="valuationDate")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True  # para que la respuesta use los alias si se usa `.model_dump(by_alias=True)`
