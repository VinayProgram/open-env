from typing import Optional

from ..sql.db import create_chat, get_chat_by_key
from .customer_chat_schema import CustomerChatCreateRequest, CustomerChatResponse


class CustomerChatService:
    """Customer chat service with DB-backed operations."""

    @staticmethod
    def create_chat(request: CustomerChatCreateRequest) -> CustomerChatResponse:
        existing = get_chat_by_key(request.chat_key)
        if existing:
            # If chat exists, return existing data as idempotent behavior
            return CustomerChatResponse(
                id=existing["id"],
                customer_name=existing["customer_name"],
                chat_key=existing["chat_key"],
                created_at=existing["created_at"],
            )

        new_id = create_chat(request.customer_name, request.chat_key)

        created = get_chat_by_key(request.chat_key)
        assert created is not None

        return CustomerChatResponse(
            id=created["id"],
            customer_name=created["customer_name"],
            chat_key=created["chat_key"],
            created_at=created["created_at"],
        )

    @staticmethod
    def get_chat(chat_key: str) -> Optional[CustomerChatResponse]:
        existing = get_chat_by_key(chat_key)
        if not existing:
            return None
        return CustomerChatResponse(
            id=existing["id"],
            customer_name=existing["customer_name"],
            chat_key=existing["chat_key"],
            created_at=existing["created_at"],
        )
