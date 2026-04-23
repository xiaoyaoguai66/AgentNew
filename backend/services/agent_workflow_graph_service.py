from config.settings import get_settings
from schemas.ai import AiWorkflowGraphEdge, AiWorkflowGraphNode
from services import agent_workflow_service, langgraph_agent_service


LEGACY_EDGES = [
    ("query-analysis", "retrieval-planner", False),
    ("retrieval-planner", "retrieval", False),
    ("retrieval", "route-filter", False),
    ("route-filter", "final-rerank", False),
    ("final-rerank", "generator", True),
    ("final-rerank", "no-evidence-response", True),
    ("generator", "verifier", False),
    ("verifier", "response-formatter", False),
]


def _build_legacy_mermaid(nodes: list[AiWorkflowGraphNode], edges: list[AiWorkflowGraphEdge]) -> str:
    lines = ["graph TD"]
    for node in nodes:
        if node.kind == "start":
            lines.append(f'    {node.id}(["{node.label}"])')
        elif node.kind == "end":
            lines.append(f'    {node.id}(["{node.label}"])')
        else:
            lines.append(f'    {node.id}["{node.label}"]')
    for edge in edges:
        connector = "-.->" if edge.conditional else "-->"
        lines.append(f"    {edge.source} {connector} {edge.target}")
    return "\n".join(lines)


def get_workflow_graph() -> dict:
    settings = get_settings()

    if settings.agent_workflow_engine == "legacy":
        status = agent_workflow_service.get_runtime_status()
        node_ids = ["__start__", *status.get("workflowNodes", []), "__end__"]
        nodes = [
            AiWorkflowGraphNode(
                id=node_id,
                label=node_id,
                kind="start" if node_id == "__start__" else "end" if node_id == "__end__" else "node",
            )
            for node_id in node_ids
        ]
        edges = [
            AiWorkflowGraphEdge(source="__start__", target="query-analysis", conditional=False),
            *[
                AiWorkflowGraphEdge(source=source, target=target, conditional=conditional)
                for source, target, conditional in LEGACY_EDGES
            ],
            AiWorkflowGraphEdge(source="response-formatter", target="__end__", conditional=False),
            AiWorkflowGraphEdge(source="no-evidence-response", target="__end__", conditional=False),
        ]
        return {
            "engine": "legacy",
            "style": status.get("workflowStyle", "stateful-node-pipeline"),
            "graphVisualizationReady": False,
            "nodes": nodes,
            "edges": edges,
            "mermaid": _build_legacy_mermaid(nodes, edges),
        }

    compiled = langgraph_agent_service._get_compiled_graph()
    graph = compiled.get_graph()
    nodes = []
    for node_id, node in graph.nodes.items():
        node_kind = "node"
        if node_id == "__start__":
            node_kind = "start"
        elif node_id == "__end__":
            node_kind = "end"
        nodes.append(AiWorkflowGraphNode(id=node_id, label=node.name, kind=node_kind))

    edges = [
        AiWorkflowGraphEdge(
            source=edge.source,
            target=edge.target,
            conditional=edge.conditional,
        )
        for edge in graph.edges
    ]

    return {
        "engine": "langgraph",
        "style": "langgraph-stategraph",
        "graphVisualizationReady": True,
        "nodes": nodes,
        "edges": edges,
        "mermaid": graph.draw_mermaid(),
    }
