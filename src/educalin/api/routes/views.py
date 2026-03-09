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

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..dependencies import get_current_user, get_current_user_flexible
from ..schemas import UsuarioSchema

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


@router.get("/dashboard/professor", response_class=HTMLResponse, include_in_schema=False)
def dashboard_professor_page(
    request: Request,
    current_user: UsuarioSchema = Depends(get_current_user_flexible)
):
    """
    Renderiza o dashboard específico para professores.

    Exibe:
    - Lista de turmas do professor
    - Formulário de registro de notas
    - Botões para criar plano de ação
    - Acesso a relatórios de desempenho

    Requer autenticação JWT válida e tipo de usuário 'professor'.

    Args:
        request: Objeto de requisição FastAPI.
        current_user: Usuário autenticado via JWT.

    Returns:
        HTMLResponse com o template ``dashboard/professor.html`` renderizado.
        
    Raises:
        HTTPException: 403 se o usuário não for professor.
    """
    # Validar tipo de usuário
    if current_user.tipo_usuario != 'professor':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas professores podem acessar este dashboard."
        )
    
    import json
    import sqlite3
    from educalin.repositories.base import get_connection
    from educalin.repositories.turma_repository import TurmaRepository
    from educalin.repositories.plano_acao_repository import PlanoAcaoRepository
    
    professor_id = current_user.id
    
    try:
        conn = get_connection()
        turma_repo = TurmaRepository(conn)
        plano_repo = PlanoAcaoRepository(conn)
        
        # Buscar turmas do professor autenticado
        turmas = turma_repo.listar_por_professor(professor_id)
        
        # Calcular estatísticas REAIS
        total_alunos = 0
        turmas_data = []
        alunos_ids = set()
        
        for turma in turmas:
            alunos = turma_repo.listar_alunos(turma.id)
            num_alunos = len(alunos)
            total_alunos += num_alunos
            
            # Coletar IDs únicos de alunos para contar planos depois
            for aluno in alunos:
                alunos_ids.add(aluno['id'])
            
            turmas_data.append({
                'id': turma.id,
                'codigo': turma.codigo,
                'disciplina': turma.disciplina,
                'semestre': turma.semestre,
                'total_alunos': num_alunos
            })
        
        # Contar planos ATIVOS dos alunos dessas turmas
        planos_ativos = 0
        for aluno_id in alunos_ids:
            planos_ativos += plano_repo.contar(aluno_id=aluno_id, status='em_andamento')
            planos_ativos += plano_repo.contar(aluno_id=aluno_id, status='enviado')
        
        # Converter current_user UsuarioSchema para dict para o template
        current_user_dict = {
            'id': current_user.id,
            'nome': current_user.nome,
            'email': current_user.email,
            'tipo_usuario': current_user.tipo_usuario
        }
        
        conn.close()
        
        return templates.TemplateResponse(
            "dashboard/professor.html",
            _base_ctx(
                request,
                current_user=current_user_dict,
                turmas=turmas_data,
                turmas_json=json.dumps(turmas_data),
                total_alunos=total_alunos,
                planos_ativos=planos_ativos,
            ),
        )
    except Exception as e:
        # Em caso de erro, retornar página com dados vazios
        current_user_dict = {
            'id': current_user.id,
            'nome': current_user.nome,
            'tipo_usuario': current_user.tipo_usuario
        }
        return templates.TemplateResponse(
            "dashboard/professor.html",
            _base_ctx(
                request,
                current_user=current_user_dict,
                turmas=[],
                turmas_json='[]',
                total_alunos=0,
                planos_ativos=0,
                error=str(e)
            ),
        )


@router.get("/dashboard/aluno", response_class=HTMLResponse, include_in_schema=False)
def dashboard_aluno_page(
    request: Request,
    current_user: UsuarioSchema = Depends(get_current_user_flexible)
):
    """
    Renderiza o dashboard específico para alunos.

    Exibe:
    - Notas por turma com médias
    - Desempenho geral do aluno
    - Materiais disponíveis
    - Planos de ação criados para o aluno

    Requer autenticação JWT válida e tipo de usuário 'aluno'.

    Args:
        request: Objeto de requisição FastAPI.
        current_user: Usuário autenticado via JWT.

    Returns:
        HTMLResponse com o template ``dashboard/aluno.html`` renderizado.
        
    Raises:
        HTTPException: 403 se o usuário não for aluno.
    """
    # Validar tipo de usuário
    if current_user.tipo_usuario != 'aluno':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas alunos podem acessar este dashboard."
        )
    
    import sqlite3
    from educalin.repositories.base import get_connection
    from educalin.repositories.plano_acao_repository import PlanoAcaoRepository
    from educalin.repositories.material_repository import MaterialRepository
    
    aluno_id = current_user.id
    
    try:
        conn = get_connection()
        plano_repo = PlanoAcaoRepository(conn)
        material_repo = MaterialRepository(conn)
        
        # Buscar turmas do aluno autenticado com notas
        cursor = conn.execute("""
            SELECT 
                t.id, t.codigo, t.disciplina, t.semestre,
                COUNT(DISTINCT a.id) as total_avaliacoes,
                AVG(n.valor) as media
            FROM turmas t
            INNER JOIN turma_alunos ta ON t.id = ta.turma_id
            LEFT JOIN avaliacoes a ON t.id = a.turma_id
            LEFT JOIN notas n ON a.id = n.avaliacao_id AND n.aluno_id = ta.aluno_id
            WHERE ta.aluno_id = ?
            GROUP BY t.id, t.codigo, t.disciplina, t.semestre
            ORDER BY t.codigo
        """, (aluno_id,))
        
        turmas = []
        soma_medias = 0
        total_turmas_com_media = 0
        
        for row in cursor.fetchall():
            media = row['media']
            if media is not None:
                soma_medias += media
                total_turmas_com_media += 1
            
            turmas.append({
                'id': row['id'],
                'codigo': row['codigo'],
                'disciplina': row['disciplina'],
                'semestre': row['semestre'],
                'total_avaliacoes': row['total_avaliacoes'] or 0,
                'media': media
            })
        
        # Calcular média geral
        if total_turmas_com_media > 0:
            media_geral = round(soma_medias / total_turmas_com_media, 2)
        else:
            media_geral = "N/A"
        
        # Buscar materiais disponíveis para o aluno autenticado
        cursor = conn.execute("""
            SELECT 
                m.id, m.titulo, m.tipo,
                t.codigo as turma_nome,
                u.nome as professor_nome
            FROM materiais m
            INNER JOIN turmas t ON m.turma_id = t.id
            INNER JOIN usuarios u ON t.professor_id = u.id
            INNER JOIN turma_alunos ta ON t.id = ta.turma_id
            WHERE ta.aluno_id = ?
            ORDER BY m.data_upload DESC
            LIMIT 10
        """, (aluno_id,))
        
        materiais = []
        for row in cursor.fetchall():
            materiais.append({
                'id': row['id'],
                'titulo': row['titulo'],
                'tipo': row['tipo'],
                'turma_nome': row['turma_nome'],
                'professor_nome': row['professor_nome']
            })
        
        # Buscar planos de ação do aluno autenticado
        planos_models = plano_repo.listar_por_aluno(aluno_id)
        planos = []
        for plano in planos_models:
            planos.append({
                'id': plano.id,
                'objetivo': plano.objetivo,
                'status': plano.status,
                'data_limite': plano.data_limite.strftime('%d/%m/%Y') if plano.data_limite else 'N/A',
                'observacoes': plano.observacoes
            })
        
        # Converter current_user UsuarioSchema para dict para o template
        current_user_dict = {
            'id': current_user.id,
            'nome': current_user.nome,
            'email': current_user.email,
            'tipo_usuario': current_user.tipo_usuario
        }
        
        conn.close()
        
        return templates.TemplateResponse(
            "dashboard/aluno.html",
            _base_ctx(
                request,
                current_user=current_user_dict,
                aluno=current_user_dict,
                turmas=turmas,
                total_turmas=len(turmas),
                media_geral=media_geral,
                materiais=materiais,
                total_materiais=len(materiais),
                planos=planos,
                total_planos=len(planos),
            ),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Em caso de erro, retornar página com dados vazios
        return templates.TemplateResponse(
            "dashboard/aluno.html",
            _base_ctx(
                request,
                current_user={'nome': 'Aluno', 'tipo_usuario': 'aluno'},
                aluno={'nome': 'Aluno'},
                turmas=[],
                total_turmas=0,
                media_geral="N/A",
                materiais=[],
                total_materiais=0,
                planos=[],
                total_planos=0,
                error=str(e)
            ),
        )
