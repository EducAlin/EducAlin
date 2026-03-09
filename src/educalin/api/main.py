"""
Aplicação principal FastAPI do EducAlin.

Este módulo configura a aplicação FastAPI, incluindo:
- Configuração de CORS
- Registro de routers
- Tratamento de exceções
- Documentação da API
"""


import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
load_dotenv()

from educalin.repositories.base import init_db
from .routes import auth, turmas, notas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco de dados na startup da aplicação."""
    init_db()
    yield


# Criar aplicação FastAPI
app = FastAPI(
    title="EducAlin API",
    description="API REST para o sistema de gestão educacional EducAlin",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# Configurar CORS
_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #TODO especificar origens permitidas em produção
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registrar routers
app.include_router(auth.router)
app.include_router(turmas.router)
app.include_router(notas.router)


# Rota raiz
@app.get("/", tags=["Info"])
async def root():
    """
    Endpoint raiz da API.


    Returns:
        Informações básicas sobre a API
    """
    return {
        "message": "Bem-vindo à API EducAlin",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Rota de health check
@app.get("/health", tags=["Info"])
async def health_check():
    """
    Verifica o status da API.


    Returns:
        Status da aplicação
    """
    return {
        "status": "healthy",
        "message": "API está funcionando corretamente"
    }


# Handler global para exceções não tratadas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Trata exceções não capturadas para evitar vazamento de informações sensíveis.
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor. Por favor, tente novamente mais tarde."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "educalin.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
