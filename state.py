from typing import TypedDict, Optional, Dict, Any, List, Annotated
from datetime import datetime
from langgraph.graph import add_messages

from models import GeneratedResponse

# State --> define el estado actual del agente
# Contiene todos los atributos que se van pasando de un Nodo a otro dentro del super-step
class ValuationState(TypedDict, total=False):
    # Entrada del usuario (PropertyDTO como dict plano)
    request_data: Dict[str, Any]

    # Tarea worker a ejecutar
    # Tarea del Generator / Tarea del Evaluator
    worker_task: str 

    # Respuesta generada por el modelo generador
    #generated_response: Optional[Dict[str, Any]]
    generated_response: GeneratedResponse

    # Feedback textual del evaluador
    evaluation_feedback: Optional[str]

    # Resultado de la evaluación (True si es válida, False si se rechaza)
    is_valid: Optional[bool]

    # Control de intentos de iteración
    attempts: int
    max_attempts: int

    # Para trazabilidad
    request_id: Optional[str]
    timestamp: Optional[datetime]

    # Mensajes acumulados durante la conversación (langgraph)
    messages: Annotated[List[Any], add_messages]
