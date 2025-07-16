from datetime import datetime
from typing import Any, Optional
import uuid

from dotenv import load_dotenv
from graph import ValuationGraph
#from models import GeneratedResponse, 
from models import Property, ValuationResponse
from state import ValuationState
#from tools import other_tools

#from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

load_dotenv(override=True)

class Agent:

    # Inicializador
    def __init__(self) -> None:
        self.agent_id = str(uuid.uuid4())
        #self.tools = None       
        #self.worker_llm_total = None 
        #self.evaluator_llm_total = None 
        #self.master_llm_total = None 
        self.valuation_graph: Optional[ValuationGraph] = None  # ➌ deja claro que puede ser None

    async def setup(self):
        # Creamos Modelo Worker Generator
        #self.tools = await other_tools()
        #worker_llm = ChatOpenAI(model="gpt-4o-mini")
        #self.worker_llm_total = worker_llm
        # Creamos Modelo Evaluator
        #evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
        #self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        #self.evaluator_llm_total = evaluator_llm.bind_tools(self.tools)   # type: ignore
        # Creamos el Modelo Master
        #master_llm = ChatOpenAI(model="gpt-4o-mini")
        #self.master_llm_total = master_llm

        self.valuation_graph = ValuationGraph() 

        await self.valuation_graph.build_graph()
        assert self.valuation_graph.graph is not None          # ➍ garantiza al type-checker

    # Wrapper para exponer la funcion Super-Step a la FastAPI
    async def estimate_prices(self, message: Any, request: Property) -> ValuationResponse: 
        #valuation : ValuationResponse = self.run_superstep_test(message, request)
        valuation : ValuationResponse = await self.run_superstep(message, request)
        return valuation

    # --------------------------------
    # Funcion Super-Step del agente
    # --------------------------------
    async def run_superstep(self, message: Any, request: Property) -> ValuationResponse: 

        prop = request
        # Creamos una configuracion para el grafo que incluye un ID de hilo unico para trazabilidad
        configuration: RunnableConfig = {"configurable": {"thread_id": self.agent_id}} 

        # Verificamos en tiempo de ejecucion que el grafo este correctamente inicializado
        if not self.valuation_graph or not self.valuation_graph.graph:   # ➎ protección en runtime
            raise RuntimeError("El grafo no está inicializado. Llama antes a setup().")
    
        #dummy = GeneratedResponse(min_sale_price   = 0, max_sale_price   = 0, min_rental_price = 0, max_rental_price = 0, valuation_date   = "")
    
        # Creamos el estado inicial que se va a pasar al grafo. Incluye:
        # - los mensajes del usuario,
        # - los datos del inmueble,
        # - la respuesta dummy,
        # - campos de evaluacion y control del flujo (feedback, intentos, validez, etc.)
        state = ValuationState(
            messages=message,
            request_data=prop.model_dump(by_alias=True),
            #generated_response=dummy,
            evaluation_feedback=None,
            is_valid=None,
            attempts=0,
            max_attempts=3,
            request_id=self.agent_id,
            timestamp=datetime.now()
        )

        # Ejecutamos asincronicamente el grafo LangGraph pasando el estado y la configuración
        result = await self.valuation_graph.graph.ainvoke(state, config=configuration)

        # Obtenemos la respuesta generada por el agente (tras pasar por el generador y evaluador)
        #valuation: ValuationResponse = ValuationResponse(0,0,0,0,datetime.now())
        valuation = result["generated_response"]

        # Devolvemos el objeto ValuationResponse al invocador externo (FastAPI)
        return valuation

    # Funcion Test que simula Super-Step del agente
    def run_superstep_test(self, message: Any, request: Property) -> ValuationResponse: 
        prop = request

        base_price = prop.built_area * 2_200
        bedrooms_factor = prop.bedrooms * 10_000
        floor_factor = prop.floor * 2_000

        min_sale = round(base_price + bedrooms_factor + floor_factor, 2)
        max_sale = round(min_sale * 1.20, 2)
        min_rent = round(min_sale * 0.004, 2)
        max_rent = round(min_sale * 0.0055, 2)

        # ✅  Usamos los alias camelCase para contentar a Pylance
        return ValuationResponse(
            min_sale_price=min_sale,
            max_sale_price=max_sale,
            min_rental_price=min_rent,
            max_rental_price=max_rent,
            valuation_date=datetime.now()
        )
