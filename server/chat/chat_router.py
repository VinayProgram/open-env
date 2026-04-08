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


from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

@router.websocket("/ws/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: str) -> None:
    """Accept websocket chat messages, store them, and reply with AI output."""

    await websocket.accept()
    ai_session = AIModelSession(chat_key=chat_id)

    async def safe_send(data):
        """Send data safely without crashing if socket is closed."""
        try:
            await websocket.send_json(data)
        except Exception:
            # socket already closed → ignore
            pass

    try:
        while True:
            # 🔹 STEP 1: Receive message safely
            try:
                payload = await websocket.receive_json()
            except WebSocketDisconnect:
                print("Client disconnected")
                break  # ✅ EXIT LOOP IMMEDIATELY
            except Exception as exc:
                await safe_send({
                    "error": "invalid_payload",
                    "detail": str(exc),
                })
                continue

            # 🔹 STEP 2: Validate message
            try:
                message = ChatMessage.model_validate(payload)
            except ValidationError as exc:
                await safe_send({
                    "error": "invalid_message",
                    "detail": exc.errors(),
                })
                continue

            # 🔹 STEP 3: Store customer message
            try:
                stored_customer = ChatService.store_message(chat_id, message)
            except ValueError as exc:
                await safe_send({
                    "error": "chat_not_found",
                    "detail": str(exc),
                })
                continue

            # 🔹 STEP 4: If not customer → just echo metadata
            if message.sender.strip().lower() not in {"customer", "user"}:
                await safe_send(
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

            # 🔹 STEP 5: AI processing
            try:
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

                await safe_send(
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

            except Exception as exc:
                await safe_send({
                    "error": "ai_processing_error",
                    "detail": str(exc),
                })

    finally:
        # 🔹 Always cleanup session
        await ai_session.close()
        print(f"WebSocket closed for chat_id={chat_id}")
