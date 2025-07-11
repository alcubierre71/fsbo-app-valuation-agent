# Mapper para convertir entre DTO y Modelo

from models import Property, ValuationResponse
from models_dto import PropertyDTO, ValuationResponseDTO
from typing import Any

class Mapper:

    # Constructor para la instanciacion del objeto
    def __new__(cls, *args: Any, **kwargs: Any):
        raise TypeError("Mapper es una clase estática: no permitida la instanciacion")
    
    # Inicializador de atributos del objeto instanciado
    #def __init__(self) -> None:
    #    self.mapping = None       

    @staticmethod
    def to_property(dto: PropertyDTO) -> Property:
        return Property.model_validate(dto.model_dump())

    @staticmethod
    def to_property_dto(model: Property) -> PropertyDTO:
        return PropertyDTO.model_validate(model.model_dump())

    @staticmethod
    def to_valuation_response_dto(model: ValuationResponse) -> ValuationResponseDTO:
        return ValuationResponseDTO.model_validate(model.model_dump())

    @staticmethod
    def to_valuation_response(model_dto: ValuationResponseDTO) -> ValuationResponse:
        return ValuationResponse.model_validate(model_dto.model_dump())
