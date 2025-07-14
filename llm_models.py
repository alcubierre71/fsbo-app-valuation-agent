#from tools import other_tools
from datetime import datetime
#from email import message
from langchain_openai import ChatOpenAI

class LlmModels:

    # Inicializador
    def __init__(self) -> None:
        self.worker_llm_total = None 
        self.evaluator_llm_total = None 
        self.master_llm_total = None 
        #self.setup()

    def setup(self):
        # Creamos Modelo Worker Generator
        #self.tools = await other_tools()
        worker_llm = ChatOpenAI(model="gpt-4o-mini")
        self.worker_llm_total = worker_llm
        # Creamos Modelo Evaluator
        evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
        #self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        self.evaluator_llm_total = evaluator_llm.bind_tools(self.tools)   # type: ignore
        # Creamos el Modelo Master
        master_llm = ChatOpenAI(model="gpt-4o-mini")
        self.master_llm_total = master_llm

    def llm_master (self) -> str : 

        message_master = f"""
        Eres un asistente experto en valoración de bienes inmuebles. Tu responsabilidad no es realizar directamente las estimaciones de precio, sino **coordinar el flujo de trabajo** entre los distintos componentes del agente.

        Tu función consiste en:
        - Analizar la solicitud del usuario y determinar si cuentas con la información necesaria para iniciar la valoración.
        - Encargar al *generador* que elabore una estimación de precios (venta y alquiler) para el inmueble proporcionado.
        - Enviar el resultado al *evaluador* para verificar que cumple con los criterios de calidad establecidos.
        - Decidir si se puede finalizar el proceso o si se requiere iterar nuevamente (por ejemplo, solicitando una nueva estimación o más datos).

        El objetivo final es entregar una valoración precisa, justificada y verificable del inmueble, incluyendo rango de precios y un timestamp.

        Fecha y hora actuales: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        Criterios de éxito:
        - Se ha generado una valoración razonable basada en los datos disponibles del inmueble.
        - La evaluación de calidad ha confirmado que la valoración cumple los estándares establecidos.
        - Se ha producido una respuesta final clara con los precios mínimo y máximo para venta y alquiler.

        En cada paso, debes decidir cuál es el siguiente nodo que debe ejecutar el agente:
        - "generator" → si necesitas generar una nueva valoración.
        - "evaluator" → si quieres validar la calidad de una valoración ya generada.
        - "end" → si consideras que el proceso ha finalizado correctamente.

        No generes tú la valoración ni hagas la evaluación por tu cuenta. Solo toma decisiones de enrutamiento y termina la ejecución cuando todo esté en orden.

        Tu respuesta debe ser clara e indicar el siguiente paso que el agente debe ejecutar.
        """

        return message_master
    