# Graph del agente 

# graph.py  – definición y compilación del flujo LangGraph
from langgraph.graph import StateGraph, START, END
from state import ValuationState
from nodes import Nodes

class ValuationGraph:

    def __init__(self) -> None:
        self.graph = None                     # type: ignore[arg-type]

    async def build_graph(self):

        nodes = Nodes()

        # 1) Crear el builder para nuestro estado
        builder: StateGraph[ValuationState] = StateGraph(ValuationState)

        # 2) Crear los nodos del grafo
        builder.add_node("master",     nodes.master_node)        # type: ignore
        builder.add_node("generator",  nodes.generator_node)     # type: ignore
        builder.add_node("evaluator",  nodes.evaluator_node)     # type: ignore

        # 3) Crear los edges fijos y condicionales del grafo
        builder.add_edge(START, "master")

        # Crear el edge condicional con su router 
        # Conectar master → (generator | evaluator | END) según el router
        builder.add_conditional_edges(                      
            "master",
            Nodes.master_router,
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
        self.graph = builder.compile()   # type: ignore
