"""
Rotas de criação e gestão de Planos de Ação da API FastAPI.

Este módulo implementa endpoints para:
- Criação de novos planos de ação
- Visualização de detalhes de um plano
- Adição de materiais a planos (composição)
- Atualização de status do plano
- Listagem de planos por aluno
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status as http_status

from ..schemas import (
    PlanoAcaoCreateSchema,
    PlanoAcaoResponseSchema,
    PlanoAcaoListSchema,
    PlanoAcaoMaterialSchema,
    PlanoAcaoStatusSchema,
    UsuarioSchema,
    ErrorSchema
)
from ..dependencies import get_current_user
from educalin.repositories.plano_acao_repository import PlanoAcaoRepository
from educalin.repositories.base import get_connection


# Criar router para rotas de planos de ação
router = APIRouter(
    prefix="/planos",
    tags=["Planos de Ação"],
    responses={
        401: {"model": ErrorSchema, "description": "Não autorizado"},
        400: {"model": ErrorSchema, "description": "Requisição inválida"},
        404: {"model": ErrorSchema, "description": "Plano não encontrado"},
    }
)

# Router separado para rotas de alunos relacionadas a planos
alunos_router = APIRouter(
    prefix="/alunos",
    tags=["Planos de Ação"],
    responses={
        401: {"model": ErrorSchema, "description": "Não autorizado"},
        400: {"model": ErrorSchema, "description": "Requisição inválida"},
        404: {"model": ErrorSchema, "description": "Aluno não encontrado"},
    }
)


def _criar_schema_resposta(plano, materiais_ids: list) -> PlanoAcaoResponseSchema:
    """
    Converte um PlanoAcaoModel em PlanoAcaoResponseSchema.

    Args:
        plano: Objeto PlanoAcaoModel
        materiais_ids: Lista de IDs de materiais do plano

    Returns:
        PlanoAcaoResponseSchema: Schema de resposta
    """
    return PlanoAcaoResponseSchema(
        id=plano.id,
        aluno_id=plano.aluno_id,
        objetivo=plano.objetivo,
        status=plano.status,
        data_criacao=plano.data_criacao,
        data_limite=plano.data_limite,
        observacoes=plano.observacoes,
        materiais=materiais_ids
    )


def _verificar_propriedade_plano(
    plano_id: int,
    current_user: UsuarioSchema,
    conn
) -> None:
    """
    Verifica se o usuário tem permissão para acessar o plano.

    Para alunos, pode acessar apenas seus planos.
    Para professores e coordenadores, pode acessar qualquer plano.

    Args:
        plano_id: ID do plano
        current_user: Usuário autenticado
        conn: Conexão com banco de dados

    Raises:
        HTTPException: Se o usuário não tem permissão
    """
    repo = PlanoAcaoRepository(conn)
    plano = repo.buscar_por_id(plano_id)

    if not plano:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Plano com ID {plano_id} não encontrado"
        )

    # Alunos só podem ver seus próprios planos
    if current_user.tipo_usuario == "aluno" and plano.aluno_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a este plano"
        )


@router.post(
    "",
    response_model=PlanoAcaoResponseSchema,
    status_code=http_status.HTTP_201_CREATED,
    summary="Criar novo Plano de Ação",
    description="Cria um novo plano de ação para o aluno.",
    responses={
        201: {"description": "Plano de ação criado com sucesso"},
        400: {"description": "Dados inválidos"},
        401: {"description": "Usuário não autenticado"},
        403: {"description": "Sem permissão para criar plano para este aluno"},
    }
)
def criar_plano(
    aluno_id: int,
    plano_data: PlanoAcaoCreateSchema,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> PlanoAcaoResponseSchema:
    """
    Cria um novo Plano de Ação para um aluno.

    O plano é criado com status 'rascunho'.

    **Permissões:**
    - Professores e coordenadores podem criar planos para qualquer aluno
    - Alunos só podem criar planos para si mesmos

    Args:
        aluno_id: ID do aluno destinatário (query parameter)
        plano_data: Dados do plano (objetivo, prazo_dias, observacoes)
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        PlanoAcaoResponseSchema: Dados do plano criado (vazio em materiais)

    Raises:
        HTTPException 400: Se dados forem inválidos
        HTTPException 403: Se sem permissão para criar para este aluno
        HTTPException 404: Se aluno não existe
    """
    # Validar permissões
    if current_user.tipo_usuario == "aluno" and aluno_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Alunos só podem criar planos para si mesmos"
        )

    if aluno_id <= 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="ID do aluno deve ser um número positivo"
        )

    try:
        conn = get_connection()
        try:
            # Criar o plano no repositório
            repo = PlanoAcaoRepository(conn)
            plano_id = repo.criar({
                'aluno_id': aluno_id,
                'objetivo': plano_data.objetivo,
                'prazo_dias': plano_data.prazo_dias,
                'observacoes': plano_data.observacoes
            })

            # Buscar plano criado
            plano = repo.buscar_por_id(plano_id)

            if not plano:
                raise HTTPException(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao criar plano de ação"
                )

            # Disparar Observer para notificações (futura integração)
            # TODO: Implementar notificação ao criar plano

            return _criar_schema_resposta(plano, [])

        finally:
            conn.close()

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar plano de ação: {str(e)}"
        )


@router.get(
    "/{plano_id}",
    response_model=PlanoAcaoResponseSchema,
    summary="Obter detalhes de um Plano de Ação",
    description="Retorna os detalhes completos de um plano de ação, incluindo materiais adicionados.",
    responses={
        200: {"description": "Detalhes do plano"},
        401: {"description": "Usuário não autenticado"},
        403: {"description": "Sem acesso a este plano"},
        404: {"description": "Plano não encontrado"},
    }
)
def obter_plano(
    plano_id: int,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> PlanoAcaoResponseSchema:
    """
    Obtém os detalhes completos de um plano de ação específico.

    **Permissões:**
    - Alunos podem ver apenas seus próprios planos
    - Professores e coordenadores podem ver todos os planos

    Args:
        plano_id: ID do plano
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        PlanoAcaoResponseSchema: Dados completos do plano incluindo materiais

    Raises:
        HTTPException 401: Se usuário não autenticado
        HTTPException 403: Se sem acesso
        HTTPException 404: Se plano não existe
    """
    if plano_id <= 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="ID do plano deve ser um número positivo"
        )

    try:
        conn = get_connection()
        try:
            # Verificar propriedade/acesso
            _verificar_propriedade_plano(plano_id, current_user, conn)

            repo = PlanoAcaoRepository(conn)
            plano = repo.buscar_por_id(plano_id)

            # Listar materiais do plano
            materiais_ids = repo.listar_materiais(plano_id)

            return _criar_schema_resposta(plano, materiais_ids)

        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar plano: {str(e)}"
        )


@router.put(
    "/{plano_id}/materiais",
    response_model=PlanoAcaoResponseSchema,
    summary="Adicionar material ao Plano de Ação",
    description="Adiciona um material de estudo ao plano (composição many-to-many).",
    responses={
        200: {"description": "Material adicionado com sucesso"},
        400: {"description": "Plano ou material inválido"},
        401: {"description": "Usuário não autenticado"},
        403: {"description": "Plano em status final, sem permissão de edição"},
        404: {"description": "Plano ou material não encontrado"},
    }
)
def adicionar_material_plano(
    plano_id: int,
    material_data: PlanoAcaoMaterialSchema,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> PlanoAcaoResponseSchema:
    """
    Adiciona um material de estudo a um plano de ação.

    Implementa a composição (relacionamento many-to-many) entre
    planos e materiais. Não é permitida adição a planos 'concluido' ou 'cancelado'.

    Args:
        plano_id: ID do plano
        material_data: Dados com ID do material a adicionar
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        PlanoAcaoResponseSchema: Plano atualizado com novos materiais

    Raises:
        HTTPException 400: Se plano ou material inválido
        HTTPException 403: Se plano em status final ou sem permissão
        HTTPException 404: Se plano ou material não encontrado
    """
    if plano_id <= 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="ID do plano deve ser um número positivo"
        )

    if material_data.material_id <= 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="ID do material deve ser um número positivo"
        )

    try:
        conn = get_connection()
        try:
            # Verificar propriedade/acesso
            _verificar_propriedade_plano(plano_id, current_user, conn)

            repo = PlanoAcaoRepository(conn)
            plano = repo.buscar_por_id(plano_id)

            # Validar status (não pode adicionar a planos finalizados)
            if plano.status in ['concluido', 'cancelado']:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail=f"Não é possível adicionar materiais a um plano {plano.status}"
                )

            # Adicionar material
            repo.adicionar_material(plano_id, material_data.material_id)

            # Buscar plano atualizado
            plano = repo.buscar_por_id(plano_id)
            materiais_ids = repo.listar_materiais(plano_id)

            return _criar_schema_resposta(plano, materiais_ids)

        finally:
            conn.close()

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar material: {str(e)}"
        )


@router.put(
    "/{plano_id}/status",
    response_model=PlanoAcaoResponseSchema,
    summary="Atualizar status do Plano de Ação",
    description="Muda o status do plano seguindo as transições de estado permitidas.",
    responses={
        200: {"description": "Status atualizado com sucesso"},
        400: {"description": "Transição de status inválida"},
        401: {"description": "Usuário não autenticado"},
        403: {"description": "Sem permissão para atualizar"},
        404: {"description": "Plano não encontrado"},
    }
)
def atualizar_status_plano(
    plano_id: int,
    status_data: PlanoAcaoStatusSchema,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> PlanoAcaoResponseSchema:
    """
    Atualiza o status de um plano de ação.

    **Transições permitidas:**
    - rascunho → enviado, cancelado
    - enviado → em_andamento, cancelado
    - em_andamento → concluido, cancelado
    - concluido → (sem transições)
    - cancelado → (sem transições)

    Args:
        plano_id: ID do plano
        status_data: Dados com novo status
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        PlanoAcaoResponseSchema: Plano com status atualizado

    Raises:
        HTTPException 400: Se transição de status inválida
        HTTPException 403: Se sem permissão
        HTTPException 404: Se plano não encontrado
    """
    if plano_id <= 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="ID do plano deve ser um número positivo"
        )

    try:
        conn = get_connection()
        try:
            # Verificar propriedade/acesso
            _verificar_propriedade_plano(plano_id, current_user, conn)

            repo = PlanoAcaoRepository(conn)
            plano = repo.buscar_por_id(plano_id)

            # Atualizar status (valida transições automaticamente)
            repo.atualizar_status(plano_id, status_data.status)

            # Buscar plano atualizado
            plano = repo.buscar_por_id(plano_id)
            materiais_ids = repo.listar_materiais(plano_id)

            return _criar_schema_resposta(plano, materiais_ids)

        finally:
            conn.close()

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar status: {str(e)}"
        )


@alunos_router.get(
    "/{aluno_id}/planos",
    response_model=PlanoAcaoListSchema,
    summary="Listar Planos de Ação de um aluno",
    description="Lista todos os planos de ação de um aluno específico.",
    responses={
        200: {"description": "Lista de planos"},
        401: {"description": "Usuário não autenticado"},
        403: {"description": "Sem acesso aos planos deste aluno"},
        404: {"description": "Aluno não encontrado"},
    }
)
def listar_planos_aluno(
    aluno_id: int,
    filtro_status: Optional[str] = None,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> PlanoAcaoListSchema:
    """
    Lista todos os planos de ação de um aluno.

    **Permissões:**
    - Alunos podem ver apenas seus próprios planos
    - Professores e coordenadores podem ver planos de qualquer aluno

    **Filtros:**
    - Opcionalmente filtrar por status (rascunho, enviado, em_andamento, concluido, cancelado)

    Args:
        aluno_id: ID do aluno
        filtro_status: (opcional) Filtrar por status
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        PlanoAcaoListSchema: Lista de planos do aluno

    Raises:
        HTTPException 400: Se parâmetros inválidos
        HTTPException 403: Se sem permissão
        HTTPException 404: Se aluno não encontrado
    """
    # Validar permissões
    if current_user.tipo_usuario == "aluno" and aluno_id != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Alunos só podem ver seus próprios planos"
        )

    if aluno_id <= 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="ID do aluno deve ser um número positivo"
        )

    try:
        conn = get_connection()
        try:
            repo = PlanoAcaoRepository(conn)

            # Listar planos do aluno
            planos = repo.listar_por_aluno(aluno_id, status=filtro_status)

            # Converter para schemas de resposta
            planos_response = []
            for plano in planos:
                materiais_ids = repo.listar_materiais(plano.id)
                planos_response.append(_criar_schema_resposta(plano, materiais_ids))

            return PlanoAcaoListSchema(
                total=len(planos_response),
                planos=planos_response
            )

        finally:
            conn.close()

    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar planos: {str(e)}"
        )
