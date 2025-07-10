from fastapi import FastAPI
from mapper import to_property, to_valuation_response_dto
from models import Property, ValuationResponse
from models_dto import PropertyDTO, ValuationResponseDTO
from agent import estimate_prices

app = FastAPI(title="Price Estimation Agent API")

@app.post("/estimate-price", response_model=ValuationResponseDTO)
def estimate_price(requestDto: PropertyDTO):

    property : Property = to_property(requestDto)

    # Invocamos al Agente para que calcule la valoracion del inmueble
    retornoValuation : ValuationResponse = estimate_prices(property)

    responseDto : ValuationResponseDTO = to_valuation_response_dto(retornoValuation)

    return responseDto
