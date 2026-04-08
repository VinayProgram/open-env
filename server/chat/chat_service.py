"""Business logic for chat message persistence."""

from __future__ import annotations

from typing import Any, Mapping

from ..sql.db import add_message, get_chat_by_key, get_messages_by_chat_key
from .chat_schema import ChatMessage, ChatMessageResponse


class ChatService:
    """Service layer for storing chat messages."""

    @staticmethod
    def _to_message_response(row: Mapping[str, Any]) -> ChatMessageResponse:
        return ChatMessageResponse(
            id=int(row["id"]),
            chat_key=str(row["chat_key"]),
            sender=str(row["sender"]),
            message=str(row["message"]),
            reward=float(row["reward"]),
            resolution_status=str(row["resolution_status"]),
            customer_sentiment=str(row["customer_sentiment"]),
            satisfaction_score=float(row["satisfaction_score"]),
            awaiting_customer_response=bool(row["awaiting_customer_response"]),
            done=bool(row["done"]),
            created_at=str(row["created_at"]),
        )

    @staticmethod
    def store_message(
        chat_key: str,
        message: ChatMessage,
        *,
        reward: float = 0.0,
        resolution_status: str = "in_progress",
        customer_sentiment: str = "negative",
        satisfaction_score: float = 0.0,
        awaiting_customer_response: bool = True,
        done: bool = False,
    ) -> ChatMessageResponse:
        existing_chat = get_chat_by_key(chat_key)
        if existing_chat is None:
            raise ValueError(f"Chat '{chat_key}' does not exist")

        stored = add_message(
            chat_key=chat_key,
            sender=message.sender.strip(),
            message=message.message.strip(),
            reward=reward,
            resolution_status=resolution_status,
            customer_sentiment=customer_sentiment,
            satisfaction_score=satisfaction_score,
            awaiting_customer_response=awaiting_customer_response,
            done=done,
        )
        return ChatService._to_message_response(stored)

    @staticmethod
    def get_messages(chat_key: str) -> list[ChatMessageResponse]:
        existing_chat = get_chat_by_key(chat_key)
        if existing_chat is None:
            raise ValueError(f"Chat '{chat_key}' does not exist")

        rows = get_messages_by_chat_key(chat_key)
        return [ChatService._to_message_response(row) for row in rows]

