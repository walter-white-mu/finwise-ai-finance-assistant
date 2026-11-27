from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)


class ChatToolResult(BaseModel):
    name: str
    data: dict | list


class ChatResponse(BaseModel):
    conversation_id: str
    assistant_message: str
    tool_results: list[ChatToolResult] = Field(default_factory=list)
