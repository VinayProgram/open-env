from pydantic import BaseModel


class CustomerChatCreateRequest(BaseModel):
    customer_name: str
    chat_key: str


class CustomerChatResponse(BaseModel):
    id: int
    customer_name: str
    chat_key: str
    created_at: str


class ConversionEntryRequest(BaseModel):
    chat_key: str
    customer_id: str
    customer_message: str
    agent_message: str
    reward: float = 0.0
    step_count: int = 0
    resolution_status: str | None = None
    customer_sentiment: str | None = None
    satisfaction_score: float | None = None
    done: bool = False
    metadata: str | None = None
