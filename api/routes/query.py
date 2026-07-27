"""Endpoint de consulta em linguagem natural POST /ask."""

from fastapi import APIRouter
from loguru import logger

from agents.orchestrator import OrchestratorAgent
from api.contracts import QuestionRequest, QuestionResponse
from services.deps import get_catalog_service, get_duckdb_service

router = APIRouter(tags=["Query"])


@router.post("/ask", response_model=QuestionResponse, status_code=200)
async def ask_question(request: QuestionRequest) -> QuestionResponse:
    """Recebe uma pergunta em linguagem natural sobre um dataset_id e retorna a resposta formatada."""
    logger.info(
        f"Recebida pergunta no /ask (dataset_id='{request.dataset_id}'): '{request.question}'"
    )


    orchestrator = OrchestratorAgent(
        catalog_service=get_catalog_service(),
        duckdb_service=get_duckdb_service(),
    )

    response = await orchestrator.run_async(question=request.question, dataset_id=request.dataset_id)
    return response
