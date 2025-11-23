"""LangChain SQL Agent for querying employee database."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine, text
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Custom prompt to ensure markdown table output with smart field selection
CUSTOM_AGENT_PROMPT = """You are an SQL expert assistant. When answering questions about data, you MUST format your response as a markdown table.

FIELD SELECTION RULES - SMART CONTEXT-AWARE FIELDS:
1. ALWAYS include: first_name, last_name (employee identity is essential)
2. IF query mentions SKILLS or PROFICIENCY: Include skill name and proficiency level
3. IF query mentions HIRE DATE, DATE RANGE, or TIMING: Include hire_date column
4. IF query mentions DEPARTMENT: Include department_name
5. IF query mentions SALARY, PAY, or COMPENSATION: Include salary column
6. IF query mentions PROJECTS or WORK: Include project names/details
7. IF query mentions MANAGER or REPORTS: Include manager information
8. IF query mentions EXPERIENCE, LEVEL, or SENIORITY: Include any relevant proficiency/level data

GENERAL RULES:
- Always format query results as a markdown table with pipe delimiters (|)
- Include column headers separated by |
- Add a separator row with dashes (---) after headers
- Return ALL matching results in table format
- Do NOT return plain text lists or natural language responses - ONLY tables
- Include relevant contextual fields based on the query intent
- Provide a brief title/explanation BEFORE the table if helpful
- Ensure all column values are present in each row

EXAMPLE SMART RESPONSES:
- Query: "employees with python skills" → Return: first_name | last_name | skill | proficiency
- Query: "engineers hired in last 2 years" → Return: first_name | last_name | hire_date | department_name
- Query: "senior managers and their salary" → Return: first_name | last_name | department_name | salary

Always use SELECT * to get all available data, then extract only the relevant columns for the table."""


def get_sql_agent(api_key: str):
    """
    Create and return a SQL agent configured with Gemini API.
    
    Args:
        api_key: Google API key for Gemini
        
    Returns:
        SQL agent ready to query the database
    """
    # Set the API key
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Create SQLAlchemy engine for the SQLite database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "employee_database.db")
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Create SQLDatabase instance
    db = SQLDatabase(engine)
    
    # Create LLM instance
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    
    # Create SQL agent
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    return agent


def query_database(query: str, api_key: str) -> dict:
    """
    Execute a natural language query against the employee database.
    
    Args:
        query: Natural language query
        api_key: Google API key for Gemini
        
    Returns:
        Dictionary with result and status
    """
    logger.info("=" * 80)
    logger.info("NEW QUERY RECEIVED")
    logger.info(f"Query: {query}")
    logger.info("=" * 80)
    
    try:
        # Set the API key
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Create SQLAlchemy engine for the SQLite database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "employee_database.db")
        engine = create_engine(f"sqlite:///{db_path}")
        
        # Create SQLDatabase instance
        logger.info("📊 Initializing SQLDatabase connection")
        db = SQLDatabase(engine)
        
        # Create LLM instance
        logger.info("🤖 Initializing Gemma-3-27b-it LLM")
        llm = ChatGoogleGenerativeAI(model="gemma-3-27b-it", temperature=0)
        
        # Create SQL agent
        logger.info("🔧 Creating SQL Agent")
        agent = create_sql_agent(
            llm=llm,
            db=db,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=10
        )
        
        logger.info("🚀 Executing agent with natural language query")
        # Add custom prompt to encourage markdown table output
        enhanced_query = f"{CUSTOM_AGENT_PROMPT}\n\nUser query: {query}"
        
        try:
            result = agent.invoke({"input": enhanced_query})
            output = result.get("output", str(result))
        except Exception as agent_error:
            # Extract markdown table from error message if present
            error_str = str(agent_error)
            logger.info(f"🔍 Agent parsing error detected, attempting markdown extraction")
            
            # Try to extract markdown table from the error message
            if "Could not parse LLM output:" in error_str:
                # Extract the markdown content between backticks
                import re
                match = re.search(r"Could not parse LLM output:\s*`([^`]*)`", error_str, re.DOTALL)
                if match:
                    output = match.group(1).strip()
                    logger.info(f"✅ Successfully extracted markdown from error (length: {len(output)} chars)")
                else:
                    raise agent_error
            else:
                raise agent_error
        
        logger.info(f"✅ Agent output received (length: {len(output)} chars)")
        logger.info(f"📄 Output preview: {output[:300]}...")
        
        return {
            "success": True,
            "result": output,
            "error": None,
            "formatted": False
        }
        
    except Exception as e:
        logger.error(f"❌ ERROR occurred: {str(e)}", exc_info=True)
        return {
            "success": False,
            "result": None,
            "error": str(e),
            "formatted": False
        }
