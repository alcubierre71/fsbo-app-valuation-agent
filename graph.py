# Graph del agente 

# graph.py  – definición y compilación del flujo LangGraph
from langgraph.graph import StateGraph, START, END
from state import ValuationState
from nodes import (
    master_node,
    master_router,
    generator_node,
    evaluator_node,
)

# 1) Crear el builder para nuestro estado
builder: StateGraph[ValuationState] = StateGraph(ValuationState)

# 2) Crear los nodos del grafo
builder.add_node("master",     master_node)        # type: ignore[arg-type]
builder.add_node("generator",  generator_node)     # type: ignore[arg-type]
builder.add_node("evaluator",  evaluator_node)     # type: ignore[arg-type]

# 3) Crear los edges fijos y condicionales del grafo
builder.add_edge(START, "master")

# Crear el edge condicional con su router 
# Conectar master → (generator | evaluator | END) según el router
builder.add_conditional_edges(                      # type: ignore[arg-type]
    "master",
    master_router,
    {
        "generator": "generator",
        "evaluator": "evaluator",
        "end":       END,
    },
)

# Conexion de los demas flujos (vuelta al master)
builder.add_edge("generator",  "master")
builder.add_edge("evaluator",  "master")
builder.add_edge("master", END)

# 4) Compilar el grafo
graph = builder.compile()   # type: ignore[call-overload]
