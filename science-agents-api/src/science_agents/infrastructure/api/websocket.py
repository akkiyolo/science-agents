"""
WebSocket Endpoint
-------------------
/ws/dialogue/{scientist_id} — accepts player messages, streams AI responses.

Will be fully implemented in Step 4.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from science_agents.config.settings import logger

ws_router = APIRouter()


@ws_router.websocket("/ws/dialogue/{scientist_id}")
async def dialogue_websocket(websocket: WebSocket, scientist_id: str):
    """
    WebSocket endpoint for real-time dialogue with a scientist NPC.
    
    Expected incoming message format:
        {"player_id": "...", "message": "..."}
    
    Outgoing stream format:
        {"type": "token", "content": "..."}
        {"type": "end"}
        {"type": "error", "content": "..."}
    """
    await websocket.accept()
    logger.info("WebSocket connected for scientist=%s", scientist_id)
    
    # 1. Initialize Memory and Graph
    # Use a default player_id if none provided later, but ideally it comes in connection or first message
    # For simplicity, we'll initialize it per message if player_id changes, or assume it's sent in the first message.
    # To keep it robust, we'll initialize memory when we receive the message.
    graph = None
    memory = None
    current_player_id = None

    try:
        from science_agents.application.conversation_service.graph import build_conversation_graph
        from science_agents.application.conversation_service.memory import ConversationMemory
        from science_agents.application.conversation_service.state import ConversationState
        
        graph = build_conversation_graph()
        
        while True:
            data = await websocket.receive_json()
            player_id = data.get("player_id", "anonymous")
            message = data.get("message", "")

            logger.info("Message from player=%s to scientist=%s: %s", player_id, scientist_id, message[:100])
            
            # Re-init memory if player changes (or first time)
            if memory is None or current_player_id != player_id:
                memory = ConversationMemory(player_id, scientist_id)
                await memory.load_from_long_term()
                current_player_id = player_id

            # Prepare state
            state = ConversationState(
                scientist_id=scientist_id,
                player_id=player_id,
                user_message=message,
                chat_history=memory.get_history()
            )
            
            # Invoke Graph
            try:
                result = await graph.ainvoke(state)
                response_text = result.get("response", "I'm sorry, my mind wandered.")
                
                # Send the response back
                # (For now, we stream the whole token since ainvoke is used. True streaming can be added later)
                await websocket.send_json({
                    "type": "token",
                    "content": response_text
                })
                await websocket.send_json({"type": "end"})
                
                # Save to memory
                memory.add_message("user", message)
                memory.add_message("assistant", response_text)
                await memory.save_to_long_term()
                
            except Exception as e:
                logger.error("Error generating response: %s", e)
                await websocket.send_json({"type": "error", "content": "The scientist is currently deep in thought (error)."})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for scientist=%s", scientist_id)
    except Exception as e:
        logger.error("WebSocket error for scientist=%s: %s", scientist_id, e)
        try:
            await websocket.send_json({"type": "error", "content": str(e)})
        except Exception:
            pass
