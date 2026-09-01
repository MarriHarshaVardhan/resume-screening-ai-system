import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.resume_tables import User, Resume, ScreeningResult
from app.services.recent_screening import get_recent_screenings
from app.services.screening_history import get_screening_history
from app.services.ai_screening import execute_ai_screening, search_knowledge_base_rag

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/mcp",
    tags=["MCP Server Protocol Integration"],
    include_in_schema=False
)

MCP_TOOLS = [
    {
        "name": "screen_resume",
        "description": "Run AI RAG screening agent on candidate resume against target job description.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "Target User ID"},
                "resume_id": {"type": "integer", "description": "Target Resume ID"},
                "job_id": {"type": "integer", "description": "Target Job ID"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_screening_history",
        "description": "Retrieve dynamic AI screening history for a specific candidate user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "Target User ID"}
            }
        }
    },
    {
        "name": "search_knowledge_base",
        "description": "Perform RAG vector similarity search over indexed resume text in the Knowledge Base.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query or required skills"}
            },
            "required": ["query"]
        }
    }
]


@router.get("/tools")
def list_mcp_tools():
    """
    List available MCP tools for external AI clients.
    """
    return {
        "protocolVersion": "2024-11-05",
        "tools": MCP_TOOLS
    }


@router.post("/call")
def call_mcp_tool(
    name: str = Body(..., embed=True),
    arguments: Dict[str, Any] = Body(default={}, embed=True),
    db: Session = Depends(get_db)
):
    """
    Execute an MCP tool call from external AI agent context.
    """
    logger.info("MCP Tool called: %s with arguments: %s", name, arguments)

    if name == "screen_resume":
        user_id = arguments.get("user_id")
        resume_id = arguments.get("resume_id")
        job_id = arguments.get("job_id")

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        result = execute_ai_screening(db=db, user=user, resume_id=resume_id, job_id=job_id)
        return {"content": [{"type": "text", "text": str(result.model_dump())}]}

    elif name == "get_screening_history":
        user_id = arguments.get("user_id")
        result = get_screening_history(db=db, user_id=user_id)
        return {"content": [{"type": "text", "text": str(result)}]}

    elif name == "search_knowledge_base":
        query = arguments.get("query", "")
        result = search_knowledge_base_rag(query=query, db=db)
        return {"content": [{"type": "text", "text": str(result)}]}

    else:
        raise HTTPException(status_code=404, detail=f"MCP Tool '{name}' not found")
