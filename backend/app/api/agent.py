from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from openai import OpenAI
from app.agent.tools import get_available_tools, get_realtime_price, get_company_info, get_indian_stock_analysis
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4-turbo"

# Simple in-memory client setup (replace with Dependency Injection later)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-proj-placeholder")) # Will use placeholder if env not set

@router.post("/chat")
def chat_with_agent(request: ChatRequest):
    """
    Chat endpoint for the Financial Advisor Agent.
    Utilizes OpenAI function calling for financial tools.
    """
    try:
        # 1. First Call to LLM
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": "You are a highly intelligent financial advisor agent named SADA. You have access to real-time market data tools including a specialized tool for Indian Stocks (NSE/BSE). Always use these tools to provide accurate, data-driven advice. Be concise, professional, and helpful."},
                *[msg.dict(exclude_none=True) for msg in request.messages]
            ],
            tools=get_available_tools(),
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 2. Check if the model wants to call a function
        if tool_calls:
            messages = list(request.messages) # Copy existing messages
            messages.append(response_message) # Add the assistant's request to call a tool
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                tool_response = ""
                
                if function_name == "get_realtime_price":
                    tool_response = json.dumps(get_realtime_price(function_args.get("symbol")))
                elif function_name == "get_company_info":
                    tool_response = json.dumps(get_company_info(function_args.get("symbol")))
                elif function_name == "get_indian_stock_analysis":
                    tool_response = json.dumps(get_indian_stock_analysis(
                        function_args.get("symbol"), 
                        function_args.get("exchange", "NSE")
                    ))
                else:
                    tool_response = json.dumps({"error": "Unknown tool"})
                    
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": tool_response
                })
            
            # 3. Second Call to LLM with tool outputs
            second_response = client.chat.completions.create(
                model=request.model,
                messages=messages
            )
            
            return {"role": "assistant", "content": second_response.choices[0].message.content}
        
        return {"role": "assistant", "content": response_message.content}

    except Exception as e:
        # Fallback for when API Key is missing or invalid
        print(f"OpenAI Error: {e}")
        return {
            "role": "assistant", 
            "content": "I'm currently unable to connect to my AI brain (OpenAI API key missing or invalid). However, I can still simulate advice: Based on general market trends, diversifying your portfolio across tech and healthcare sectors is often recommended."
        }
