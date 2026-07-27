"""Módulo de Roteamento de Endpoints HTTP da API."""

from api.routes.datasets import router as datasets_router
from api.routes.query import router as query_router
from api.routes.upload import router as upload_router

__all__ = ["datasets_router", "query_router", "upload_router"]

