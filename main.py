from typing import Any
from fastapi import FastAPI
from mapper import Mapper
from models import Property, ValuationResponse
from models_dto import PropertyDTO, ValuationResponseDTO
from agent import Agent

app = FastAPI(title="Price Estimation Agent API")

@app.post("/estimate-price", response_model=ValuationResponseDTO)
async def estimate_price(requestDto: PropertyDTO):

    property : Property = Mapper.to_property(requestDto)

    message : Any = "invocacion del agente ia"
    
    # Creamos el agente
    agent = Agent()
    # 👇 Esperamos a la inicialización del agente
    await agent.setup()

    # Invocamos al Agente para que calcule la valoracion del inmueble
    # Esta invocacion ejecuta el super-step del agente
    retornoValuation : ValuationResponse = await agent.estimate_prices(message, property)

    responseDto : ValuationResponseDTO = Mapper.to_valuation_response_dto(retornoValuation)

    return responseDto
