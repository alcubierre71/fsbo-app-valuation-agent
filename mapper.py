# Mapper para convertir entre DTO y Modelo

from models import Property, ValuationResponse
from models_dto import PropertyDTO, ValuationResponseDTO


def to_property(dto: PropertyDTO) -> Property:
    return Property.model_validate(dto.model_dump(by_alias=True))


def to_property_dto(model: Property) -> PropertyDTO:
    return PropertyDTO.model_validate(model.model_dump())


def to_valuation_response_dto(model: ValuationResponse) -> ValuationResponseDTO:
    return ValuationResponseDTO.model_validate(model.model_dump())


def to_valuation_response(model_dto: ValuationResponseDTO) -> ValuationResponse:
    return ValuationResponse.model_validate(model_dto.model_dump(by_alias=True))
