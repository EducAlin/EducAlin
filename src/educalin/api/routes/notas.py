"""
Rotas para registro e consulta de avaliações e notas.

Expõe endpoints REST para criação de avaliações em turmas,
registro de notas de alunos, consulta do histórico individual
e geração de relatório de turma via Template Method.

Delega persistência ao AvaliacaoRepository e geração de
relatório ao RelatorioTurma.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from educalin.repositories.avaliacao_repository import AvaliacaoRepository
from educalin.repositories.avaliacao_models import AvaliacaoModel
from educalin.repositories.turma_models import TurmaModel
from educalin.repositories.usuario_models import UsuarioModel
from educalin.repositories.base import get_connection
from educalin.services.relatorios.turma import RelatorioTurma

router = APIRouter(tags=["notas"])

FORMATOS_VALIDOS = ("txt",)


def get_db():
    """
    Dependência local de conexão para uso nas rotas de notas.

    Yields:
        sqlite3.Connection: Conexão ativa com o banco de dados.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


# Schemas Pydantic
class AvaliacaoCreate(BaseModel):
    """Payload para criação de uma avaliação em uma turma."""

    titulo: str = Field(..., min_length=1)
    data: date
    valor_maximo: float = Field(..., gt=0)
    peso: float = Field(..., ge=0, le=1)
    topico: Optional[str] = None


class AvaliacaoResponse(BaseModel):
    """Representação de uma avaliação na resposta da API."""

    id: int
    titulo: str
    data: date
    valor_maximo: float
    peso: float
    turma_id: int
    topico: Optional[str] = None


class NotaCreate(BaseModel):
    """
    Payload para registro de nota de um aluno em uma avaliação.

    A validação de ``valor <= valor_maximo`` é feita na camada
    de serviço, pois depende de consulta ao banco. A validação
    ``valor >= 0`` é feita aqui via Field.
    """

    aluno_id: int
    valor: float = Field(..., ge=0)


class NotaCreateComAvaliacao(NotaCreate):
    """Payload com avaliacao_id explícito, usado internamente."""

    avaliacao_id: int


class NotaResponse(BaseModel):
    """Representação de uma nota na resposta da API."""

    id: int
    aluno_id: int
    avaliacao_id: int
    valor: float


class RelatorioResponse(BaseModel):
    """Resposta do endpoint de relatório de turma."""

    turma_id: int
    conteudo: str


# Endpoints
@router.post(
    "/turmas/{turma_id}/avaliacoes",
    response_model=AvaliacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar avaliação em uma turma",
)
def criar_avaliacao(
    turma_id: int,
    payload: AvaliacaoCreate,
    conn: sqlite3.Connection = Depends(get_db),
):
    """
    Cria uma nova avaliação associada à turma especificada.

    Args:
        turma_id: ID da turma onde a avaliação será criada.
        payload: Dados da avaliação (título, data, valor máximo,
            peso e tópico opcional).
        conn: Conexão com o banco de dados (injetada).

    Returns:
        Dados da avaliação criada, incluindo o ID gerado.

    Raises:
        HTTPException 404: Se a turma não for encontrada.
        HTTPException 422: Se os dados forem inválidos
            (título vazio, valor_maximo <= 0, peso fora de [0,1]).
    """
    turma = TurmaModel.buscar_por_id(conn, turma_id)
    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turma {turma_id} não encontrada",
        )

    repo = AvaliacaoRepository(conn)
    avaliacao_data = payload.model_dump()
    avaliacao_data['turma_id'] = turma_id

    try:
        avaliacao_id = repo.criar_avaliacao(avaliacao_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    avaliacao = AvaliacaoModel.buscar_por_id(conn, avaliacao_id)
    return AvaliacaoResponse(
        id=avaliacao.id,
        titulo=avaliacao.titulo,
        data=avaliacao.data,
        valor_maximo=avaliacao.valor_maximo,
        peso=avaliacao.peso,
        turma_id=avaliacao.turma_id,
        topico=getattr(avaliacao, 'topico', None),
    )


@router.post(
    "/avaliacoes/{avaliacao_id}/notas",
    response_model=NotaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nota de um aluno",
)
def registrar_nota(
    avaliacao_id: int,
    payload: NotaCreate,
    conn: sqlite3.Connection = Depends(get_db),
):
    """
    Registra a nota de um aluno em uma avaliação.

    Valida que o valor não excede o ``valor_maximo`` da avaliação
    antes de persistir. O disparo de notificações via Observer
    ocorre dentro do ``NotaModel.criar()``.

    Args:
        avaliacao_id: ID da avaliação onde a nota será registrada.
        payload: Dados da nota (aluno_id e valor).
        conn: Conexão com o banco de dados (injetada).

    Returns:
        Dados da nota criada.

    Raises:
        HTTPException 404: Se a avaliação ou o aluno não existirem.
        HTTPException 409: Se já existir nota para este aluno
            nesta avaliação.
        HTTPException 422: Se o valor exceder o valor_maximo
            da avaliação.
    """
    avaliacao = AvaliacaoModel.buscar_por_id(conn, avaliacao_id)
    if avaliacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avaliação {avaliacao_id} não encontrada",
        )

    aluno = UsuarioModel.buscar_por_id(conn, payload.aluno_id)
    if aluno is None or aluno.tipo_usuario != 'aluno':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aluno {payload.aluno_id} não encontrado",
        )

    if payload.valor > avaliacao.valor_maximo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Valor {payload.valor} excede o valor máximo "
                f"da avaliação ({avaliacao.valor_maximo})"
            ),
        )

    repo = AvaliacaoRepository(conn)
    try:
        nota_id = repo.registrar_nota({
            'aluno_id': payload.aluno_id,
            'avaliacao_id': avaliacao_id,
            'valor': payload.valor,
        })
    except ValueError as exc:
        msg = str(exc)
        if "já existe" in msg.lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg
        ) from exc

    return NotaResponse(
        id=nota_id,
        aluno_id=payload.aluno_id,
        avaliacao_id=avaliacao_id,
        valor=payload.valor,
    )


@router.get(
    "/alunos/{aluno_id}/notas",
    response_model=list[NotaResponse],
    summary="Histórico de notas do aluno",
)
def historico_aluno(
    aluno_id: int,
    turma_id: Optional[int] = Query(default=None),
    conn: sqlite3.Connection = Depends(get_db),
):
    """
    Retorna o histórico de notas de um aluno.

    Quando ``turma_id`` é informado como query parameter, filtra
    apenas as notas das avaliações daquela turma. Caso contrário,
    retorna todas as notas do aluno em todas as turmas.

    Args:
        aluno_id: ID do aluno cujo histórico será consultado.
        turma_id: ID da turma para filtrar (opcional).
        conn: Conexão com o banco de dados (injetada).

    Returns:
        Lista de notas. Vazia se o aluno não tiver notas.

    Raises:
        HTTPException 404: Se o aluno não for encontrado.
    """
    aluno = UsuarioModel.buscar_por_id(conn, aluno_id)
    if aluno is None or aluno.tipo_usuario != 'aluno':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aluno {aluno_id} não encontrado",
        )

    repo = AvaliacaoRepository(conn)

    if turma_id is not None:
        notas = repo.buscar_notas_aluno(aluno_id, turma_id)
    else:
        notas = _buscar_todas_notas_aluno(conn, aluno_id)

    return [
        NotaResponse(
            id=n['id'],
            aluno_id=n['aluno_id'],
            avaliacao_id=n['avaliacao_id'],
            valor=n['valor'],
        )
        for n in notas
    ]


@router.get(
    "/turmas/{turma_id}/relatorio",
    response_model=RelatorioResponse,
    summary="Gerar relatório de desempenho da turma",
)
def relatorio_turma(
    turma_id: int,
    formato: Annotated[
        str,
        Query(description="Formato de saída. Aceito: 'txt'"),
    ] = "txt",
    conn: sqlite3.Connection = Depends(get_db),
):
    """
    Gera o relatório de desempenho da turma usando o Template Method
    implementado em ``RelatorioTurma``.

    O fluxo ``coletar_dados() → processar_dados() → formatar_saida()``
    é disparado pelo método ``gerar()`` da classe base, garantindo que
    toda a lógica de relatório fique na camada de serviço, não na API.

    Args:
        turma_id: ID da turma para gerar o relatório.
        formato: Formato de saída desejado. Atualmente apenas ``'txt'``
            é suportado.
        conn: Conexão com o banco de dados (injetada).

    Returns:
        Objeto com ``turma_id`` e ``conteudo`` (string formatada do relatório).

    Raises:
        HTTPException 404: Se a turma não for encontrada.
        HTTPException 422: Se o formato solicitado não for suportado.
    """
    if formato not in FORMATOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Formato '{formato}' não suportado. Use: {FORMATOS_VALIDOS}",
        )

    turma = TurmaModel.buscar_por_id(conn, turma_id)
    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turma {turma_id} não encontrada",
        )

    # Injeta a conexão na turma para que obter_desempenho_geral()
    # e a iteração sobre alunos funcionem com dados reais do banco.
    turma._conn = conn

    relatorio = RelatorioTurma(turma)
    conteudo = relatorio.gerar()

    return RelatorioResponse(turma_id=turma_id, conteudo=conteudo)


# Helpers privados
def _buscar_todas_notas_aluno(conn: sqlite3.Connection, aluno_id: int) -> list[dict]:
    """
    Busca todas as notas de um aluno em todas as turmas.

    Consulta auxiliar usada quando ``turma_id`` não é fornecido
    no endpoint de histórico. Não está no ``AvaliacaoRepository``
    pois não pertence ao escopo da issue #61.

    Args:
        conn: Conexão SQLite ativa.
        aluno_id: ID do aluno.

    Returns:
        Lista de dicts com ``id``, ``aluno_id``, ``avaliacao_id``,
        ``valor`` e ``data_registro``, ordenados por data da avaliação.
    """
    cursor = conn.execute(
        """
        SELECT n.id, n.aluno_id, n.avaliacao_id, n.valor, n.data_registro
        FROM notas n
        JOIN avaliacoes a ON n.avaliacao_id = a.id
        WHERE n.aluno_id = ?
        ORDER BY a.data ASC
        """,
        (aluno_id,),
    )
    return [dict(row) for row in cursor.fetchall()]
