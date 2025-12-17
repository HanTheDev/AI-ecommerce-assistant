from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging
import json

from app.database import get_db, DATABASE_URL
from app.deps import get_current_user
from app import models

# Import LangChain components
from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Schemas
class QueryRequest(BaseModel):
    message: str

class QueryResponse(BaseModel):
    response: str
    sql_query: Optional[str] = None
    products: Optional[List[dict]] = None

# Initialize LangChain components
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")
db = SQLDatabase.from_uri(DATABASE_URL)

# Create agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
)

@router.post("/query", response_model=QueryResponse)
async def query_assistant(
    request: QueryRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Natural language query interface for products
    Examples:
    - "Show me laptops under $500"
    - "What electronics do you have in stock?"
    - "Find wireless headphones"
    """
    try:
        # Create a detailed prompt
        prompt = f"""
        You are a helpful shopping assistant. Answer the user's question about products.
        
        Database Schema:
        - products table: id, name, description, price, stock, category, created_at
        
        User Question: {request.message}
        
        Rules:
        1. Only query the 'products' table
        2. Always include product name, price, and stock in results
        3. Filter out products with stock = 0
        4. Limit results to 10 products max
        5. Format prices with 2 decimal places
        6. If asking about categories, use the category column
        7. Be conversational in your response
        
        Provide a helpful answer with specific product details.
        """
        
        # Execute query through agent
        response = agent_executor.invoke({"input": prompt})
        
        # Extract the response
        assistant_response = response.get("output", "I couldn't find any products matching your query.")
        
        # Try to extract product information from response
        # This is a simple approach - in production, you'd parse more carefully
        products = []
        
        return QueryResponse(
            response=assistant_response,
            products=products if products else None
        )
        
    except Exception as e:
        logger.error(f"Assistant error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/suggestions")
async def get_suggestions():
    """
    Get example queries users can try
    """
    return {
        "suggestions": [
            "Show me products under $50",
            "What laptops do you have?",
            "Find wireless headphones",
            "Show electronics in stock",
            "What's your cheapest product?",
            "Find products in the Electronics category",
            "Show me expensive items above $500"
        ]
    }