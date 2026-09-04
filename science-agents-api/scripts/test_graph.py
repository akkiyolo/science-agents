#!/usr/bin/env python3
"""
Test LangGraph Conversation Graph
----------------------------------
CLI script to test the LangGraph pipeline standalone (Step 3).
"""

import asyncio
import sys
from pathlib import Path

# Ensure the src directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from science_agents.config.settings import validate_settings, logger
from science_agents.application.conversation_service.graph import build_conversation_graph
from science_agents.application.conversation_service.state import ConversationState
from science_agents.application.conversation_service.memory import ConversationMemory


async def main():
    validate_settings()
    
    scientist_id = "einstein"
    player_id = "test_player_1"
    
    print(f"\n--- Testing LangGraph for {scientist_id} ---")
    
    # 1. Initialize Memory
    memory = ConversationMemory(player_id, scientist_id)
    chat_history = await memory.load_from_long_term()
    print(f"Loaded {len(chat_history)} past messages from MongoDB.")
    
    # 2. Build Graph
    graph = build_conversation_graph()
    
    # 3. Test loop
    queries = [
        "Hello Herr Einstein! What is your most famous equation?",
        "Could you explain it to me simply?",
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        
        # Prepare state
        state = ConversationState(
            scientist_id=scientist_id,
            player_id=player_id,
            user_message=query,
            chat_history=memory.get_history()
        )
        
        # Run graph
        result = await graph.ainvoke(state)
        
        response = result.get("response", "No response generated.")
        print(f"\nEinstein: {response}")
        
        # Save to memory
        memory.add_message("user", query)
        memory.add_message("assistant", response)
        
    # Save to MongoDB
    await memory.save_to_long_term()
    print("\nSaved conversation to long-term memory.")


if __name__ == "__main__":
    asyncio.run(main())
