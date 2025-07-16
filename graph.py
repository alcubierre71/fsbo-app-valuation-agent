# Graph del agente 

# graph.py  – definición y compilación del flujo LangGraph
from langgraph.graph import StateGraph, START, END
from state import ValuationState
from nodes import Nodes
#from langgraph.prebuilt import ToolNode

from tools import other_tools

class ValuationGraph:

    def __init__(self) -> None:
        self.graph = None                     # type: ignore[arg-type]

    async def build_graph(self):

        nodes = Nodes()
        await nodes.setup_llm( )
        self.tools = await other_tools()

        #tool_node = ToolNode(tools=self.tools)
        #tool_node = nodes.tool_node

        # 1) Crear el builder para nuestro estado
        builder: StateGraph[ValuationState] = StateGraph(ValuationState)

        # 2) Crear los nodos del grafo
        builder.add_node("master",     nodes.master_node)        # type: ignore
        builder.add_node("generator",  nodes.generator_node)     # type: ignore
        builder.add_node("gentools",   nodes.generator_toolnode) # type: ignore
        builder.add_node("evaluator",  nodes.evaluator_node)     # type: ignore

        # 3) Crear los edges fijos y condicionales del grafo
        builder.add_edge(START, "master")

        # Crear el edge condicional con su router 
        # Conectar master → (generator | evaluator | END) según el router
        builder.add_conditional_edges(                      
            "master",
            nodes.master_router,
            {
                "generator": "generator",
                "evaluator": "evaluator",
                "end":       END,
            },
        )

        # Conexion de los demas flujos (vuelta al master)
        #builder.add_edge("generator",  "master")
        builder.add_conditional_edges("generator", nodes.generator_router, {"gentools": "gentools", "master": "master"})
        builder.add_edge("gentools", "generator")
        builder.add_edge("evaluator",  "master")
        builder.add_edge("master", END)

        # 4) Compilar el grafo
        self.graph = builder.compile()   # type: ignore
