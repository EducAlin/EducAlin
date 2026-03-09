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
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["views"])

templates = Jinja2Templates(directory="templates")


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

@router.get("/", response_class=RedirectResponse, include_in_schema=False)
def root_redirect():
    """
    Redireciona a raiz para a página de login.

    Returns:
        Redirecionamento 302 para ``/login``.
    """
    return RedirectResponse(url="/login", status_code=302)


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
        HTMLResponse com mensagem de boas-vindas temporária.
    """
    # TODO: validar JWT do cookie/session e popular current_user
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard — EducAlin</title>
        <link rel="stylesheet"
              href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
                    background:var(--cream)">
            <div style="text-align:center;max-width:480px;padding:2rem">
                <div class="auth-logo" style="justify-content:center;margin-bottom:1rem">
                    <span class="brand-dot"></span>EducAlin
                </div>
                <h2 style="font-family:var(--font-display);color:var(--petroleum)">
                    Login realizado com sucesso!
                </h2>
                <p style="color:var(--slate);margin:1rem 0 1.5rem">
                    Dashboard em construção. O token JWT está armazenado
                    em <code>sessionStorage</code>.
                </p>
                <a href="/login" class="btn-edu-primary" style="display:inline-block;width:auto;padding:.65rem 1.5rem">
                    Voltar ao Login
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
