from pydantic import BaseModel


class PromptRequest(BaseModel):
    prompt: str
    model_name: str
    max_new_tokens: int


class PromptResponse(BaseModel):
    thinking: str
    final: str

