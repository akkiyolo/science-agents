"""
Graph Nodes
------------
Individual node functions for the LangGraph agentic RAG pipeline:
  retrieve → persona_filter → respond
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from science_agents.config.settings import logger
from science_agents.application.conversation_service.state import ConversationState
from science_agents.application.rag.retriever import retrieve
from science_agents.domain.scientist_factory import load_scientist
from science_agents.application.conversation_client.groq_client import get_groq_llm


async def retrieve_node(state: ConversationState) -> dict:
    """Query the scientist's vector store for relevant context."""
    logger.info("Node: retrieve for scientist '%s'", state.scientist_id)
    chunks = await retrieve(state.scientist_id, state.user_message, top_k=3)
    return {"retrieved_context": chunks}


async def persona_filter_node(state: ConversationState) -> dict:
    """Filter retrieved facts into the scientist's internal thoughts."""
    logger.info("Node: persona_filter for scientist '%s'", state.scientist_id)
    
    if not state.retrieved_context:
        return {"persona_filtered_context": "No specific memories retrieved."}
        
    # Just format them into a string block to ground the LLM
    context_str = "\n\n".join(state.retrieved_context)
    filtered = f"Recollections based on your life and work:\n{context_str}"
    
    return {"persona_filtered_context": filtered}


async def respond_node(state: ConversationState) -> dict:
    """Generate the final in-character response via Groq LLM."""
    logger.info("Node: respond for scientist '%s'", state.scientist_id)
    
    scientist = load_scientist(state.scientist_id)
    llm = get_groq_llm()
    
    # Build messages
    messages = [
        SystemMessage(content=scientist.system_prompt)
    ]
    
    # Add chat history
    for msg in state.chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
            
    # Prepare the latest user message with context
    prompt = f"""User message: {state.user_message}

Internal Context (use this to ground your answer if relevant, but do not break character):
{state.persona_filtered_context}
"""
    messages.append(HumanMessage(content=prompt))
    
    # Invoke LLM
    response = await llm.ainvoke(messages)
    
    return {"response": response.content}
