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

    # -----------------------------------------------------------
    # Prompt del Modelo Master
    # -----------------------------------------------------------
    def llm_master (self) -> str : 

        message_master = f"""
        Eres un asistente experto en valoración de bienes inmuebles. Tu responsabilidad no es realizar directamente las estimaciones de precio, sino **coordinar el flujo de trabajo** entre los distintos componentes del agente.

        Tu función consiste en:
        - Analizar la solicitud del usuario y determinar si cuentas con la información necesaria para iniciar la valoración.
        - Encargar al *generador* que elabore una estimación de precios (venta y alquiler) para el inmueble proporcionado.
        - Enviar el resultado al *evaluador* para verificar que cumple con los criterios de calidad establecidos.
        - Decidir si se puede finalizar el proceso o si se requiere iterar nuevamente (por ejemplo, solicitando una nueva estimación o más datos).
        - Si la auditoria realizada por el evaluator no se ha superado, hay que volver a indicarle al generator que realice otra valoracion.

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

    # -----------------------------------------------------------
    # Prompt del Modelo Evaluator
    # -----------------------------------------------------------
    def llm_evaluator (self) -> str : 

        message_evaluator = f"""Eres un asistente especializado en auditoría de valoraciones inmobiliarias generadas por modelos de lenguaje.

        Tu función es revisar las valoraciones de inmuebles generadas por otro agente (el Generador) y determinar si cumplen con los criterios de calidad requeridos para ser entregadas al usuario final.

        El objetivo es asegurar que la valoración es coherente, razonable, útil y basada adecuadamente en los datos del inmueble proporcionados. 

        Debes revisar:

        1. Si los precios estimados (venta y alquiler) son consistentes con las características del inmueble.
        2. Si la valoración evita exageraciones, imprecisiones o respuestas vagas.
        3. Si hay errores evidentes, contradicciones o señales de que el Generador ha fallado.
        4. Si los precios minimos realmente son inferiores a los precios maximos
        5. Si los precios minimos son exageradamente bajos. Por ejemplo, el precio minimo de venta no puede ser 
           inferior a 20.000 euros y el precio minimo de alquiler no puede ser inferior a 100 euros.
        6. Si el formato de salida es claro, completo y profesional.

        Fecha y hora actuales: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        Debes responder **solo** de una de las siguientes dos formas:

        - Si la valoración es correcta y puede ser enviada al usuario final, responde con:

        ```json
        {{
        "success_criteria_met": true,
        "evaluation_feedback": "Valoración adecuada para su entrega. [Puedes añadir aquí observaciones opcionales]."
        }}

        Si la valoración es deficiente o necesita ser corregida, responde con:

        ```json
        {{
        "success_criteria_met": false,
        "evaluation_feedback": "La valoración no es válida porque [indica brevemente el motivo o sugerencias de mejora]."
        }}  

        No realices la valoración tú mismo. Limítate a auditar la generada por el otro agente. 
        No inventes datos adicionales. Solo valida lo que te han entregado.

        """

        return message_evaluator

    # -----------------------------------------------------------
    # Prompt del Modelo Generator
    # -----------------------------------------------------------
    def llm_generator (self) -> str : 

        message_generator = f"""Eres un asistente en encargado de generar la valoracion de un inmueble a partir 
        de los datos proporcinoados por el usuario.

        La valoracion la debes calcular teniendo en cuenta este calculo:

        1. Se obtienen los datos de la propiedad del request_data de entrada
        2. Se extrae el area mediante el builtArea de la propiedad
        3. Se calcula el base_price multiplicando el area por el valor 2.800
        4. Se calcula la variation dividiendo el base_price entre 10
        
        La salida se calcula del siguiente modo:

        generated_response = GeneratedResponse(
            min_sale_price   = base_price - variation,
            max_sale_price   = base_price + variation,
            min_rental_price = base_price * 0.003,
            max_rental_price = base_price * 0.004,
            valuation_date   = datetime.now().isoformat(),
        )

        Fecha y hora actuales: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        Debes responder indicando si has podido realizar la valoracion o no y el resultado de dicha valoracion. 
        Puedes añadir un feedback sobre la valoracion realizada o sobre los problemas que te has encontrado
        a la hora de realizar dicha valoracion. 

        La respuesta debe rellenar los campos de salida
        * valuation_ok: Indica si se ha podido realizar la valoracion del inmueble con los datos proporcionados (true / false)
        * valuation_feedback: Comentarios acerca de la valoracion realizada (positivos o negativos)
        * valuation_generated: Se indican los datos de la valoracion del inmueble realizada 
          (min_sale_price, max_sale_price, min_rental_price, max_rental_price, valuation_date)

        La respuesta debe ser en formato

        ```json
        {{
        "valuation_ok": [valuation_ok],
        "evaluation_feedback": [evaluation_feedback],
        "valuation_generated": [valuation_generated]
        }}  

       """

        return message_generator 
            