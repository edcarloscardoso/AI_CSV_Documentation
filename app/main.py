"""Aplicação FastAPI backend do AI CSV Query."""

from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from api.exceptions import AppBaseError
from api.routes import datasets_router, upload_router

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(
    title="AI CSV Query API",
    description="Interface inteligente de consulta de CSVs em linguagem natural via Agentes de IA",
    version="0.1.0",
)

# Registra os roteadores de endpoints da API
app.include_router(upload_router)
app.include_router(datasets_router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redireciona a raiz para a documentação interativa OpenAPI (/docs)."""
    return RedirectResponse(url="/docs")


# Middleware CORS (seguro para dev/prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir às origens autorizadas
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(AppBaseError)
async def app_error_handler(request: Request, exc: AppBaseError) -> JSONResponse:
    """Handler global para exceções da aplicação."""
    logger.warning(f"[{exc.code}] {exc.message} (Path: {request.url.path})")
    return JSONResponse(
        status_code=exc.http_status,
        content={"error": type(exc).__name__, "detail": exc.message, "code": exc.code},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler global para erros não capturados."""
    logger.exception(f"Erro não tratado na requisição {request.url.path}: {exc!s}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalError",
            "detail": "Ocorreu um erro interno imprevisto. Tente novamente mais tarde.",
            "code": "INTERNAL_ERROR",
        },
    )


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Endpoint de verificação de integridade (Health Check)."""
    return {
        "status": "ok",
        "service": "AI CSV Query API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
