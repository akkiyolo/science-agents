"""
Groq Client
------------
Wraps Groq chat completion calls for the LangGraph conversation nodes.

Will be fully implemented in Step 3.
"""

from __future__ import annotations

from science_agents.config.settings import GROQ_API_KEY, GROQ_MODEL, logger


def get_groq_llm():
    """Return a configured LangChain-Groq ChatGroq instance."""
    from langchain_groq import ChatGroq

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

    logger.info("Initializing Groq LLM client with model=%s", GROQ_MODEL)
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0.7,
        max_tokens=1024,
        streaming=True,
    )
