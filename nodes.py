from datetime import datetime
from valuation_state import ValuationState
from models import GeneratedResponse

# --- Master -----------------------------------------------------------
def master_node(state: ValuationState) -> ValuationState:
    """El nodo master no altera el estado: solo lo re-envía al router."""
    return state


def master_router(state: ValuationState) -> str:               # <- router
    if state.get("is_valid"):
        return "end"
    if state.get("attempts", 0) >= state.get("max_attempts", 3):
        return "end"
    if "generated_response" in state:
        return "evaluator"
    return "generator"

# --- Generator --------------------------------------------------------
def generator_node(state: ValuationState) -> ValuationState:
    prop = state.get("request_data", {})
    area       = prop.get("builtArea", 100)
    base_price = area * 2_800
    variation  = base_price * 0.10

    generated_response = GeneratedResponse(
        min_sale_price   = base_price - variation,
        max_sale_price   = base_price + variation,
        min_rental_price = base_price * 0.003,
        max_rental_price = base_price * 0.004,
        valuation_date   = datetime.now().isoformat(),
    )

    return {
        **state,
        "generated_response": generated_response,
        "attempts": state.get("attempts", 0) + 1,
    }

# --- Evaluator --------------------------------------------------------
def evaluator_node(state: ValuationState) -> ValuationState:
    resp = state.get("generated_response", GeneratedResponse(
        min_sale_price=0, max_sale_price=0,
        min_rental_price=0, max_rental_price=0,
        valuation_date=""
    ))

    ok = all([
        resp.min_sale_price   > 20_000,
        resp.max_sale_price   > resp.min_sale_price,
        resp.min_rental_price > 100,
        resp.max_rental_price > resp.min_rental_price,
    ])

    return {
        **state,
        "is_valid": ok,
        "evaluation_feedback": (
            "Validación satisfactoria" if ok
            else "La respuesta generada no cumple los requisitos mínimos."
        ),
    }
