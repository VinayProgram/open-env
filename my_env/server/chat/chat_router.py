"""WebSocket chat endpoint with persistent message storage."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from .ai_model import AIModelSession
from .chat_schema import ChatMessage, ChatMessageResponse, ChatTurnResponse
from .chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/{chat_key}/messages", response_model=List[ChatMessageResponse])
def list_chat_messages(chat_key: str) -> List[ChatMessageResponse]:
    """Return all persisted messages for a chat session by chat_key."""
    try:
        return ChatService.get_messages(chat_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.websocket("/ws/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: str) -> None:
    """Accept websocket chat messages, store them, and reply with AI output."""

    await websocket.accept()
    ai_session = AIModelSession(chat_key=chat_id)

    try:
        while True:
            try:
                payload = await websocket.receive_json()
                message = ChatMessage.model_validate(payload)
                stored_customer = ChatService.store_message(chat_id, message)

                if message.sender.strip().lower() not in {"customer", "user"}:
                    await websocket.send_json(
                        ChatTurnResponse(
                            chat_key=chat_id,
                            customer_message=stored_customer,
                            assistant_message=None,
                            reward=0.0,
                            resolution_status="open",
                            customer_sentiment="neutral",
                            satisfaction_score=0.0,
                            awaiting_customer_response=False,
                            done=False,
                        ).model_dump()
                    )
                    continue

                ai_result = await ai_session.step(message.message)
                stored_assistant = ChatService.store_message(
                    chat_id,
                    ChatMessage(sender="assistant", message=ai_result.assistant_text),
                    reward=ai_result.reward,
                    resolution_status=ai_result.resolution_status,
                    customer_sentiment=ai_result.customer_sentiment,
                    satisfaction_score=ai_result.satisfaction_score,
                    awaiting_customer_response=ai_result.awaiting_customer_response,
                    done=ai_result.done,
                )
                await websocket.send_json(
                    ChatTurnResponse(
                        chat_key=chat_id,
                        customer_message=stored_customer,
                        assistant_message=stored_assistant,
                        reward=ai_result.reward,
                        resolution_status=ai_result.resolution_status,
                        customer_sentiment=ai_result.customer_sentiment,
                        satisfaction_score=ai_result.satisfaction_score,
                        awaiting_customer_response=ai_result.awaiting_customer_response,
                        done=ai_result.done,
                    ).model_dump()
                )
            except ValueError as exc:
                await websocket.send_json(
                    {
                        "error": "chat_not_found",
                        "detail": str(exc),
                    }
                )
            except ValidationError as exc:
                await websocket.send_json(
                    {
                        "error": "invalid_message",
                        "detail": exc.errors(),
                    }
                )
            except Exception as exc:
                await websocket.send_json(
                    {
                        "error": "invalid_payload",
                        "detail": str(exc),
                    }
                )
    except WebSocketDisconnect:
        return
    finally:
        await ai_session.close()



