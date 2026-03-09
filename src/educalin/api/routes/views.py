"""
Rotas de interface web (views HTML) com Jinja2.

Serve as páginas de login, registro e redirecionamentos,
integradas com a API REST de autenticação existente.

Nota: as rotas de API (/auth/*) continuam ativas e são
chamadas pelo JavaScript do front-end via fetch().
Estas rotas servem apenas os templates HTML.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["views"])


def _find_project_root() -> Path:
    """Return the project root by locating the nearest ``pyproject.toml``."""
    here = Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise RuntimeError("Could not find project root (pyproject.toml not found)")


_TEMPLATES_DIR = _find_project_root() / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def _base_ctx(request: Request, **kwargs) -> dict:
    """
    Monta o contexto base compartilhado por todos os templates.

    Inclui o objeto ``request`` (obrigatório pelo Jinja2 do FastAPI),
    o ano atual para o footer e quaisquer parâmetros extras.

    Args:
        request: Objeto de requisição FastAPI.
        **kwargs: Pares chave-valor adicionais para o contexto.

    Returns:
        Dicionário de contexto pronto para passar ao template.
    """
    return {
        "request": request,
        "current_year": datetime.now().year,
        **kwargs,
    }


# Páginas públicas

@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(
    request: Request,
    error: Optional[str] = None,
    success: Optional[str] = None,
    email: Optional[str] = None,
):
    """
    Renderiza a página de login.

    Query params opcionais permitem exibir mensagens após redirecionamentos,
    como "cadastro realizado com sucesso" vindo da página de registro.

    Args:
        request: Objeto de requisição FastAPI.
        error: Mensagem de erro a exibir (ex.: credenciais inválidas).
        success: Mensagem de sucesso a exibir (ex.: cadastro concluído).
        email: E-mail para pré-preencher o campo (ex.: vindo do registro).

    Returns:
        HTMLResponse com o template ``login.html`` renderizado.
    """
    return templates.TemplateResponse(
        "login.html",
        _base_ctx(
            request,
            error=error,
            success=success,
            prefill_email=email or "",
        ),
    )


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
def register_page(
    request: Request,
    error: Optional[str] = None,
    tipo: Optional[str] = None,
):
    """
    Renderiza a página de cadastro de novo usuário.

    Args:
        request: Objeto de requisição FastAPI.
        error: Mensagem de erro a exibir após validação server-side.
        tipo: Tipo de usuário para pré-selecionar o campo de perfil
            (``'professor'``, ``'coordenador'`` ou ``'aluno'``).

    Returns:
        HTMLResponse com o template ``register.html`` renderizado.
    """
    return templates.TemplateResponse(
        "register.html",
        _base_ctx(
            request,
            error=error,
            prefill_tipo=tipo,
        ),
    )


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard_page(request: Request):
    """
    Renderiza o dashboard principal (placeholder).

    Em uma implementação completa, este endpoint extrairia o token JWT
    do cookie/sessão, validaria via ``get_current_user`` e popularia
    ``current_user`` no contexto.

    Returns:
        HTMLResponse com o template ``dashboard.html`` renderizado.
    """
    # TODO: validar JWT do cookie/session e popular current_user
    return templates.TemplateResponse(
        "dashboard.html",
        _base_ctx(request),
    )
