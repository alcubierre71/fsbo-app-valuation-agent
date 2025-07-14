from datetime import datetime
from typing import Any, List

from llm_models import LlmModels
from state import ValuationState
from models import GeneratedResponse, MasterOutput

from tools import other_tools
from langchain_openai import ChatOpenAI
from models import MasterOutput

class Nodes:

    # Inicializador
    def __init__(self):           # ← constructor sincrono
        self.indicador : bool = True
        self.models_llm = LlmModels()

    # Setup para realizar la construccion asincrona del Nodes 
    async def setup_llm(self):   
        self.tools = await other_tools()
        worker_llm = ChatOpenAI(model="gpt-4o-mini")
        self.worker_llm_total = worker_llm
        # Creamos Modelo Evaluator
        evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
        #self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        self.evaluator_llm_total = evaluator_llm.bind_tools(self.tools)   # type: ignore
        # Creamos el Modelo Master
        master_llm = ChatOpenAI(model="gpt-4o-mini")
        self.master_llm_total = master_llm.with_structured_output(MasterOutput) # type: ignore
       

    # --- Master -----------------------------------------------------------
    def master_node(self, state: ValuationState) -> ValuationState:
        """El nodo master no altera el estado: solo lo re-envía al router."""

        #state_response : ValuationState = state 
        prompt_master : str = self.models_llm.llm_master()

        messages: List[Any] = []
        #messages: List[Any] = state.get("messages", [])

        estado_valoracion : str = ""
        if state.get("generated_response"):
            estado_valoracion = "Realizada"
        else:
            estado_valoracion = "Pendiente" 

        estado_auditoria : str = ""
        if state.get("is_valid"):
            auditoria : bool | None = state.get("is_valid")
            if (auditoria):
                estado_auditoria = "Correcta"
            else:
                estado_auditoria = "Incorrecta"
        else:
            estado_auditoria = "Pendiente"

        prompt_master = prompt_master + f""" * Te indico el resultado de la valoracion realizada por el Generador: {estado_valoracion} """
        prompt_master = prompt_master + f""" * Te indico el resultado de la auditoria realizada por el Evaluator: {estado_auditoria} """

        messages.append(prompt_master)

        #sys_msg = SystemMessage(content=messages)

        # Invocamos al Modelo Master
        response : MasterOutput = self.master_llm_total.invoke(messages)   # type: ignore[assignment]

        # Actualizamos el estado inicial añadiendo el atributo worker_task
        state_response: ValuationState = {
            **state,
            "worker_task": response.worker_task if response.datos_entrada_valid else "end",
        } 

        return state_response


    def master_router(self, state: ValuationState) -> str:               # <- router
        if state.get("is_valid"):
            return "end"
        if state.get("attempts", 0) >= state.get("max_attempts", 3):
            return "end"
        if "generated_response" in state:
            return "evaluator"
        return "generator"

    # --- Generator --------------------------------------------------------
    def generator_node(self, state: ValuationState) -> ValuationState:
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
    def evaluator_node(self, state: ValuationState) -> ValuationState:
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
