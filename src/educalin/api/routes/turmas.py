"""
Rotas para gestão de turmas e matrículas de alunos

Expõe os endpoints REST para criação e consulta de turmas,
gerenciamento de matrículas e resumo de desempenho.
Delega toda a lógica de dados ao TurmaRepository.
"""

from __future__ import annotations

import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from educalin.api.dependencies import get_current_user, get_db, require_role
from educalin.api.schemas import UsuarioSchema
from educalin.repositories.turma_repository import TurmaRepository

router = APIRouter(prefix="/turmas", tags=["turmas"])


# Schemas pydantic

class TurmaCreate(BaseModel):
    """Payload para criação de uma nova turma"""
    codigo: str
    disciplina: str
    semestre: str
    professor_id: Optional[int] = None

class TurmaResponse(BaseModel):
    """Representação de turma na resposta da API"""
    id: int
    codigo: str
    disciplina: str
    semestre: str
    professor_id: Optional[int] = None

class AlunoResumoResponse(BaseModel):
    """Resumo de um aluno matriculado em uma turma"""
    id: int
    nome: str
    email: str
    matricula: Optional[str] = None
    data_matricula: Optional[str] = None

class TurmaDetalheResponse(TurmaResponse):
    """Turma com lista de alunos matriculados"""
    alunos: list[AlunoResumoResponse] = []

class AdicionarAlunoPayload(BaseModel):
    """Payload para matricular um aluno em uma turma"""
    aluno_id: int

class MensagemResponse(BaseModel):
    """Resposta simples com mensagem de confirmação"""
    mensagem: str

class DesempenhoResponse(BaseModel):
    """Resumo de desempenho de uma turma"""
    turma_id: int
    total_alunos: int
    media_geral: float
    taxa_aprovacao: float


# Endpoints

@router.get(
    "",
    response_model=list[TurmaResponse],
    summary="Lista de turmas do professor",
)
def listar_turmas(
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(require_role("professor", "coordenador")),
):
    """
    Retorna todas as turmas associadas ao professor autenticado.

    Args:
        conn: Conexão com o banco de dados (injetada).
        current_user: Usuário autenticado (professor ou coordenador).

    Returns:
        Lista de turmas. Vazia se o professor não tiver turmas.
    """
    repo = TurmaRepository(conn)
    turmas = repo.listar_por_professor(current_user.id)
    return [
        TurmaResponse(
            id=t.id,
            codigo=t.codigo,
            disciplina=t.disciplina,
            semestre=t.semestre,
            professor_id=t.professor_id,
        )
        for t in turmas
    ]


@router.post(
    "",
    response_model=TurmaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova turma",
)
def criar_turma(
    payload: TurmaCreate,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(require_role("professor", "coordenador")),
):
    """
    Cria uma nova turma a partir dos dados fornecidos.

    O ``professor_id`` é opcional no payload; quando omitido, o ID do
    usuário autenticado é utilizado automaticamente.

    Args:
        payload: Dados da nova turma (código, disciplina, semestre
            e opcionalmente professor_id).
        conn: Conexão com o banco de dados (injetada).
        current_user: Usuário autenticado (professor ou coordenador).

    Returns:
        Dados da turma criada, incluindo o ID gerado.

    Raises:
        HTTPException 404: Se ``professor_id`` for informado mas não existir.
        HTTPException 409: Se já existir uma turma com o mesmo código.
        HTTPException 422: Se campos obrigatórios estiverem ausentes.
    """
    repo = TurmaRepository(conn)
    dados = payload.model_dump()
    if dados.get("professor_id") is None:
        dados["professor_id"] = current_user.id
    try:
        turma_id = repo.criar(dados)
    except ValueError as exc:
        msg = str(exc)
        if "não existe" in msg or "não encontrad" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        if "obrigatório" in msg or "vazio" in msg:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from exc

    turma = repo.buscar_por_id(turma_id)
    return TurmaResponse(
        id=turma.id,
        codigo=turma.codigo,
        disciplina=turma.disciplina,
        semestre=turma.semestre,
        professor_id=turma.professor_id
    )


@router.get(
    "/{turma_id}",
    response_model=TurmaDetalheResponse,
    summary="Detalhes de uma turma",
)
def detalhe_turma(
    turma_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(get_current_user),
):
    """
    Retorna os dados completos de uma turma, incluindo a lista de alunos.

    Args:
        turma_id: ID da turma a ser consultada.
        conn: Conexão com o banco de dados (injetada).
        current_user: Usuário autenticado (injetado).

    Returns:
        Dados da turma com a lista de alunos matriculados.

    Raises:
        HTTPException 404: Se a turma não for encontrada.
    """
    repo = TurmaRepository(conn)
    turma = repo.buscar_por_id(turma_id)

    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turma {turma_id} não encontrada",
        )

    alunos = repo.listar_alunos(turma_id)

    return TurmaDetalheResponse(
        id=turma.id,
        codigo=turma.codigo,
        disciplina=turma.disciplina,
        semestre=turma.semestre,
        professor_id=turma.professor_id,
        alunos=alunos
    )


@router.post(
    "/{turma_id}/alunos",
    response_model=MensagemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar aluno à turma",
)
def adicionar_aluno(
    turma_id: int,
    payload: AdicionarAlunoPayload,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(get_current_user),
):
    """
    Matricula um aluno em uma turma.

    Args:
        turma_id: ID da turma.
        payload: Corpo com ``aluno_id`` do aluno a matricular.
        conn: Conexão com o banco de dados (injetada).
        current_user: Usuário autenticado (injetado).

    Returns:
        Mensagem de confirmação.

    Raises:
        HTTPException 404: Se a turma ou o aluno não existirem.
        HTTPException 409: Se o aluno já estiver matriculado na turma.
    """
    repo = TurmaRepository(conn)
    try:
        adicionado = repo.adicionar_aluno(turma_id, payload.aluno_id)
    except ValueError as exc:
        msg = str(exc)
        if "não encontrad" in msg or "não existe" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from exc

    if not adicionado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Aluno {payload.aluno_id} já está matriculado nesta turma",
        )

    return MensagemResponse(mensagem=f"Aluno {payload.aluno_id} matriculado com sucesso")


@router.delete(
    "/{turma_id}/alunos/{aluno_id}",
    response_model=MensagemResponse,
    summary="Remover aluno da turma",
)
def remover_aluno(
    turma_id: int,
    aluno_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(get_current_user),
):
    """
    Remove a matrícula de um aluno em uma turma.

    Args:
        turma_id: ID da turma.
        aluno_id: ID do aluno a remover.
        conn: Conexão com o banco de dados (injetada).
        current_user: Usuário autenticado (injetado).

    Returns:
        Mensagem de confirmação.

    Raises:
        HTTPException 404: Se a turma não existir ou o aluno não estiver
            matriculado nela.
    """
    repo = TurmaRepository(conn)
    try:
        removido = repo.remover_aluno(turma_id, aluno_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if not removido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aluno {aluno_id} não está matriculado na turma {turma_id}",
        )

    return MensagemResponse(mensagem=f"Aluno {aluno_id} removido com sucesso")


@router.get(
    "/{turma_id}/desempenho",
    response_model=DesempenhoResponse,
    summary="Resumo de desempenho da turma",
)
def desempenho_turma(
    turma_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(get_current_user),
):
    """
    Retorna um resumo do desempenho da turma: total de alunos,
    média geral e taxa de aprovação.

    A média e a taxa de aprovação são calculadas diretamente sobre
    as notas registradas via SQL, sem instanciar entidades de domínio,
    mantendo a camada de API desacoplada dos serviços de relatório.

    Alunos sem notas são contabilizados com média 0.0 no cálculo da
    média geral da turma.

    Args:
        turma_id: ID da turma.
        conn: Conexão com o banco de dados (injetada).
        current_user: Usuário autenticado (injetado).

    Returns:
        Objeto com ``turma_id``, ``total_alunos``, ``media_geral``
        e ``taxa_aprovacao`` (percentual de alunos com média >= 6.0)

    Raises:
        HTTPException 404: Se a turma não for encontrada.
    """
    repo = TurmaRepository(conn)
    turma = repo.buscar_por_id(turma_id)
    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turma {turma_id} não encontrada",
        )

    cursor = conn.execute(
        """
        SELECT
            COUNT(DISTINCT ta.aluno_id)                                    AS total_alunos,
            -- Inner COALESCE: alunos sem notas contam como média 0.0.
            -- Outer COALESCE: retorna 0.0 quando não há alunos matriculados.
            COALESCE(AVG(COALESCE(medias.media, 0.0)), 0.0)               AS media_geral,
            COALESCE(
                100.0 * SUM(CASE WHEN COALESCE(medias.media, 0.0) >= 6.0 THEN 1 ELSE 0 END)
                      / NULLIF(COUNT(DISTINCT ta.aluno_id), 0),
                0.0
            )                                                              AS taxa_aprovacao
        FROM turma_alunos ta
        LEFT JOIN (
            SELECT n2.aluno_id, AVG(n2.valor) AS media
            FROM notas n2
            JOIN avaliacoes a2 ON n2.avaliacao_id = a2.id
            WHERE a2.turma_id = ?
            GROUP BY n2.aluno_id
        ) medias ON ta.aluno_id = medias.aluno_id
        WHERE ta.turma_id = ?
        """,
        (turma_id, turma_id),
    )
    row = cursor.fetchone()

    total = row['total_alunos'] if row else 0
    media = round(float(row['media_geral']), 2) if row else 0.0
    taxa = round(float(row['taxa_aprovacao']), 2) if row else 0.0

    return DesempenhoResponse(
        turma_id=turma_id,
        total_alunos=total,
        media_geral=media,
        taxa_aprovacao=taxa,
    )
