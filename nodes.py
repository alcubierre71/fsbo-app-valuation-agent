from typing import Any, Dict, List

from llm_models import LlmModels
from state import ValuationState
from models import EvaluatorOutput, GeneratedResponse, GeneratorOutput, MasterOutput

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
        generator_llm = ChatOpenAI(model="gpt-4o-mini")
        #self.generator_llm_total = generator_llm.bind_tools(self.tools)   # type: ignore
        self.generator_llm_total = generator_llm.with_structured_output(GeneratorOutput) # type: ignore
        # Creamos Modelo Evaluator
        evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
        #self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        self.evaluator_llm_total = evaluator_llm.with_structured_output(EvaluatorOutput) # type: ignore
        # Creamos el Modelo Master
        master_llm = ChatOpenAI(model="gpt-4o-mini")
        self.master_llm_total = master_llm.with_structured_output(MasterOutput) # type: ignore
       
    # ----------------------------------------------------------------------
    # --- Master -----------------------------------------------------------
    # ----------------------------------------------------------------------
    def master_node(self, state: ValuationState) -> ValuationState:
        """El nodo master no altera el estado: solo lo re-envía al router."""

        #state_response : ValuationState = state 
        prompt_master : str = self.models_llm.llm_master()

        messages: List[Any] = []
        #messages: List[Any] = state.get("messages", [])

        #if state.get("request_data"):
        datos_inmueble : Dict[str, Any] | None = state.get("request_data")

        estado_valoracion : str = ""
        if state.get("generated_response"):
            estado_valoracion = "Realizada"
        else:
            estado_valoracion = "Pendiente" 

        # Valor puede ser True, False o None (o clave ausente)
        is_valid = state.get("is_valid")

        if is_valid is True:
            estado_auditoria = "Correcta"
        elif is_valid is False:
            estado_auditoria = "Incorrecta"
        else:                       # None o no evaluado todavía
            estado_auditoria = "Pendiente"

        prompt_master = prompt_master + f""" \n* Te indico los datos del inmueble enviados por el Usuario: {datos_inmueble} """
        prompt_master = prompt_master + f""" \n* Te indico el resultado de la valoracion realizada por el Generador: {estado_valoracion} """
        prompt_master = prompt_master + f""" \n* Te indico el resultado de la auditoria realizada por el Evaluator: {estado_auditoria} """

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

        response = "generator"

        if state.get("is_valid"):
            return "end"
        
        if state.get("attempts", 0) >= state.get("max_attempts", 5):
            return "end"
        
        #if "generated_response" in state:
        #    return "evaluator"

        # Enrutado de tarea segun la decision del Nodo Master        
        task = state.get("worker_task")

        if task == "generator":
            response = "generator"
        elif task == "evaluator": 
            response = "evaluator"
        elif task == "end":
            response = "end"
        
        return response 

    # ----------------------------------------------------------------------
    # --- Generator --------------------------------------------------------
    # ----------------------------------------------------------------------
    def generator_node(self, state: ValuationState) -> ValuationState:

        prompt_generator : str = self.models_llm.llm_generator()

        messages: List[Any] = []        

        datos_inmueble : Dict[str, Any] | None = state.get("request_data")

        valuation = GeneratedResponse(
            min_sale_price   = 0,
            max_sale_price   = 0,
            min_rental_price = 0,
            max_rental_price = 0,
            valuation_date   = "",
        )

        prompt_generator = prompt_generator + f""" \n* Te indico los datos del inmueble request_data enviados por el Usuario: {datos_inmueble} """


        messages.append(prompt_generator)

        #sys_msg = SystemMessage(content=messages)

        # Invocamos al Modelo Generator
        response : GeneratorOutput = self.generator_llm_total.invoke(messages)   # type: ignore[assignment]

        # Si el calculo se ha podido realizar, recogemos la valoracion del inmueble
        if response.valuation_ok:
            valuation = response.valuation_generated

        # Actualizamos el estado inicial añadiendo el atributo generated_response
        state_response: ValuationState = {
            **state,
            "generated_response": valuation,
            "attempts": state.get("attempts", 0) + 1,
            "is_valid": None   # queda pendiente ser auditado por el Evaluator 
        }

        return state_response

    # ----------------------------------------------------------------------
    # --- Evaluator --------------------------------------------------------
    # ----------------------------------------------------------------------
    def evaluator_node(self, state: ValuationState) -> ValuationState:

        prompt_evaluator : str = self.models_llm.llm_evaluator()

        messages: List[Any] = []

        #sys_msg = SystemMessage(content=messages)

        # Extraermos del State los datos del inmueble y los datos de la valoracion del Generator
        datos_inmueble : Dict[str, Any] | None = state.get("request_data")
        valoracion_generator : GeneratedResponse | None = state.get("generated_response")

        prompt_evaluator = prompt_evaluator + f""" \n* Te indico los datos del inmueble enviados por el Usuario: {datos_inmueble} """
        prompt_evaluator = prompt_evaluator + f""" \n* Te indico la valoracion realizada por el Generator: {valoracion_generator} """

        messages.append(prompt_evaluator)

        # Invocamos al Modelo Master
        response : EvaluatorOutput = self.evaluator_llm_total.invoke(messages)   # type: ignore[assignment]

        # Actualizamos el estado inicial añadiendo el atributo worker_task
        state_response: ValuationState = {
            **state,
            "is_valid": response.success_criteria_met, 
            "evaluation_feedback": response.evaluation_feedback
        } 

        return state_response
