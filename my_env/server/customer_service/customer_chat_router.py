from fastapi import APIRouter, HTTPException

from .customer_chat_schema import CustomerChatCreateRequest, CustomerChatResponse
from .customer_chat_service import CustomerChatService

router = APIRouter(prefix="/customer-chat", tags=["Customer Chat"])


@router.post("/create", response_model=CustomerChatResponse)
def create_chat(request: CustomerChatCreateRequest) -> CustomerChatResponse:
    """Create a new chat session (idempotent by chat_key)."""
    return CustomerChatService.create_chat(request)


@router.get("/{chat_key}", response_model=CustomerChatResponse)
def get_chat(chat_key: str) -> CustomerChatResponse:
    item = CustomerChatService.get_chat(chat_key)
    if item is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return item
