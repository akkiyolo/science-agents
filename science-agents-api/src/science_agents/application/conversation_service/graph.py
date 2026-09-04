"""
LangGraph Conversation Graph
------------------------------
Compiles the agentic RAG graph: retrieve → persona_filter → respond.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, END

from science_agents.config.settings import logger
from science_agents.application.conversation_service.state import ConversationState
from science_agents.application.conversation_service.nodes import (
    retrieve_node,
    persona_filter_node,
    respond_node,
)


def build_conversation_graph():
    """Build and compile the LangGraph conversation graph."""
    logger.info("Building LangGraph conversation graph...")
    
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("persona_filter", persona_filter_node)
    workflow.add_node("respond", respond_node)
    
    # Define edges
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "persona_filter")
    workflow.add_edge("persona_filter", "respond")
    workflow.add_edge("respond", END)
    
    # Compile the graph
    app = workflow.compile()
    return app
