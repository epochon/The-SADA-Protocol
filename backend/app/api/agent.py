from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4-turbo"

@router.post("/chat")
def chat_with_agent(request: ChatRequest):
    """
    Chat endpoint for the Financial Advisor Agent.
    """
    user_message = request.messages[-1].content
    
    # Placeholder for LLM logic
    # TODO: Integrate LangChain or OpenAI Client
    
    response = f"I am a financial advisor agent. You asked: '{user_message}'. I am currently in development mode, but soon I will be able to analyze your portfolio and give advice."
    
    return {"role": "assistant", "content": response}
