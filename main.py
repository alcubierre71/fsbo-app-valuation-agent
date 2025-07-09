from fastapi import FastAPI
from models import PropertyDTO, ValuationResponse
from agent import estimate_prices

app = FastAPI(title="Price Estimation Agent API")

@app.post("/estimate-price", response_model=ValuationResponse)
def estimate_price(request: PropertyDTO):

    retornoValuation = estimate_prices(request)

    return retornoValuation
