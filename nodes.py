import json
from typing import Any, Dict, List

from llm_models import LlmModels
from state import ValuationState
from models import EvaluatorOutput, GeneratedResponse, GeneratorOutput, MasterOutput

from tools import other_tools
from langchain_openai import ChatOpenAI
from models import MasterOutput
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class Nodes:

    # Inicializador
    def __init__(self):           # ← constructor sincrono
        self.indicador : bool = True
        self.models_llm = LlmModels()

    # Setup para realizar la construccion asincrona del Nodes 
    async def setup_llm(self):   
        self.tools = await other_tools()
        generator_llm = ChatOpenAI(model="gpt-4o-mini")   # type: ignore 
        self.generator_llm_total = generator_llm.bind_tools(self.tools)    # type: ignore 
        #self.generator_llm_total = generator_llm.with_structured_output(GeneratorOutput) # type: ignore   
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

    # Router del nodo Master
    def master_router(self, state: ValuationState) -> str:               # <- router

        response = "generator"

        if state.get("is_valid"):
            return "end"
        
        # Limite de ejecuciones en bucle indefinido 
        if state.get("attempts", 0) >= state.get("max_attempts", 3):
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

        #messages: List[Any] = []        

        datos_inmueble : Dict[str, Any] | None = state.get("request_data")

        valuation = GeneratedResponse(min_sale_price = 0, max_sale_price = 0, min_rental_price = 0, max_rental_price = 0, valuation_date   = "")

        prompt_generator = prompt_generator + f""" \n* Te indico los datos del inmueble request_data enviados por el Usuario: {datos_inmueble} """

        # Recuperamos los mensajes del state antes de enviarlos al LLM
        # Esto es importante hacerlo porque pueden venir mensajes de las Tools
        found_system_message = False
        messages = state["messages"]   # type: ignore

        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = prompt_generator
                found_system_message = True
        
        # Preparamos el prompt del Generator junto con los mensajes del State
        if not found_system_message:
            messages = [SystemMessage(content=prompt_generator)] + messages

        print("messages_input_generator: ", messages)

        #messages.append(prompt_generator)

        #sys_msg = SystemMessage(content=messages)

        # Invocamos al Modelo Generator
        #response : GeneratorOutput = self.generator_llm_total.invoke(messages)   # type: ignore[assignment]
        response_msg : BaseMessage = self.generator_llm_total.invoke(messages)   # type: ignore[assignment]

        # Paso 1: Extraer el contenido
        content_str: str = response_msg.content  # type: ignore

        print("content_str: ", content_str)

        if "```json" in content_str:
            # Paso 2: Eliminar delimitadores ```json ... ```
            if content_str.strip().startswith("```json"):
                content_str = content_str.strip()[7:-3].strip()

            # Paso 3: Parsear como JSON
            content_json = json.loads(content_str)

            print("content_json: ", content_json)
             
            # Paso 4: Convertir a GeneratorOutput (esto valida y deserializa)
            generator_output = GeneratorOutput(**content_json)

            # Paso 5: Extraer la valoración generada
            valuation = generator_output.valuation_generated
        else:
            print("⚠️ No se encontró el bloque ```json en el mensaje.")

        # Si el calculo se ha podido realizar, recogemos la valoracion del inmueble
        #if response.valuation_ok:
        #    valuation = response.valuation_generated

        # Actualizamos el estado inicial añadiendo el atributo generated_response
        state_response: ValuationState = {
            **state,
            "generated_response": valuation,
            "attempts": state.get("attempts", 0) + 1,
            "is_valid": None,   # queda pendiente ser auditado por el Evaluator 
            "messages": [response_msg]
        }

        return state_response

    # ToolNode con las Tools disponibles para el nodo Generator 
    def generator_toolnode(self, state: ValuationState) -> ToolNode:

        tool_node = ToolNode(tools=self.tools)

        return tool_node 

    # Router del nodo Generator
    def generator_router(self, state: ValuationState) -> str:
        last_message = state["messages"][-1]   # type: ignore[assignment]
        
        # Si el ultimo mensaje tiene tool_calls, se devuelve "tools"
        # "tool_calls" es un mensaje estandar de tipo AIMessage devuelto por el LLM
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "gentools"
        else:
            return "master"

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
