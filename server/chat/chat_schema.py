"""Pydantic schemas for websocket chat messages."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Incoming websocket message payload."""

    sender: str = Field(..., description="Message sender, e.g. customer or agent")
    message: str = Field(..., min_length=1, description="Text content for the message")


class ChatMessageResponse(BaseModel):
    """Stored chat message returned to websocket clients."""

    id: int
    chat_key: str
    sender: str
    message: str
    reward: float = 0.0
    resolution_status: str = "in_progress"
    customer_sentiment: str = "negative"
    satisfaction_score: float = 0.0
    awaiting_customer_response: bool = True
    done: bool = False
    created_at: str


class ChatTurnResponse(BaseModel):
    """WebSocket response containing stored customer/assistant messages and env info."""

    chat_key: str
    customer_message: ChatMessageResponse
    assistant_message: ChatMessageResponse | None = None
    reward: float = 0.0
    resolution_status: str = "open"
    customer_sentiment: str = "neutral"
    satisfaction_score: float = 0.0
    awaiting_customer_response: bool = False
    done: bool = False
