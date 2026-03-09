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


# --- US06: Análise de tópicos/assuntos ---

class TopicoAnaliseItem(BaseModel):
    """Análise de desempenho em um tópico específico"""
    topico: str
    total_avaliacoes: int
    media_geral: float
    total_alunos_com_dificuldade: int  # alunos com média < 6.0 no tópico
    percentual_dificuldade: float


class TopicoAnaliseResponse(BaseModel):
    """Lista de tópicos ordenados por dificuldade"""
    turma_id: int
    topicos: list[TopicoAnaliseItem]


@router.get(
    "/{turma_id}/topicos/analise",
    response_model=TopicoAnaliseResponse,
    summary="Análise de desempenho por tópico (US06)",
    description="Retorna análise detalhada dos tópicos da turma ordenados por dificuldade (US06)",
)
def analise_topicos_turma(
    turma_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(get_current_user),
):
    """
    Retorna análise de desempenho por tópico/assunto da matéria.
    
    Implementa **US06**: "Como professor, eu quero associar as notas a assuntos 
    específicos da matéria, para que o sistema me mostre quais tópicos são mais 
    difíceis para a turma."
    
    Para cada tópico, calcula:
    - Média geral das notas
    - Total de alunos com dificuldade (média < 6.0 no tópico)
    - Percentual de alunos com dificuldade
    
    Tópicos sem nome (NULL) são agrupados como "Sem tópico definido".
    
    Args:
        turma_id: ID da turma
        conn: Conexão com o banco (injetada)
        current_user: Usuário autenticado (injetado)
        
    Returns:
        Lista de tópicos ordenados por percentual de dificuldade (decrescente)
        
    Raises:
        HTTPException 404: Se a turma não for encontrada
    """
    repo = TurmaRepository(conn)
    turma = repo.buscar_por_id(turma_id)
    if turma is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turma {turma_id} não encontrada",
        )
    
    # Query para análise por tópico
    cursor = conn.execute("""
        WITH media_por_aluno_topico AS (
            SELECT 
                COALESCE(a.topico, 'Sem tópico definido') as topico,
                n.aluno_id,
                AVG(n.valor) as media_aluno
            FROM avaliacoes a
            INNER JOIN notas n ON a.id = n.avaliacao_id
            WHERE a.turma_id = ?
            GROUP BY COALESCE(a.topico, 'Sem tópico definido'), n.aluno_id
        ),
        total_alunos_turma AS (
            SELECT COUNT(DISTINCT aluno_id) as total
            FROM turma_alunos
            WHERE turma_id = ?
        )
        SELECT 
            mpt.topico,
            COUNT(DISTINCT a2.id) as total_avaliacoes,
            ROUND(AVG(mpt.media_aluno), 2) as media_geral,
            SUM(CASE WHEN mpt.media_aluno < 6.0 THEN 1 ELSE 0 END) as alunos_com_dificuldade,
            ROUND(
                100.0 * SUM(CASE WHEN mpt.media_aluno < 6.0 THEN 1 ELSE 0 END) / 
                NULLIF((SELECT total FROM total_alunos_turma), 0),
                2
            ) as percentual_dificuldade
        FROM media_por_aluno_topico mpt
        INNER JOIN avaliacoes a2 ON COALESCE(a2.topico, 'Sem tópico definido') = mpt.topico
        WHERE a2.turma_id = ?
        GROUP BY mpt.topico
        ORDER BY percentual_dificuldade DESC, media_geral ASC
    """, (turma_id, turma_id, turma_id))
    
    rows = cursor.fetchall()
    
    topicos = []
    for row in rows:
        topicos.append(TopicoAnaliseItem(
            topico=row['topico'],
            total_avaliacoes=row['total_avaliacoes'],
            media_geral=float(row['media_geral']),
            total_alunos_com_dificuldade=row['alunos_com_dificuldade'],
            percentual_dificuldade=float(row['percentual_dificuldade'])
        ))
    
    return TopicoAnaliseResponse(
        turma_id=turma_id,
        topicos=topicos
    )


# --- US12: Sugerir materiais personalizados ---

class MaterialSugestaoItem(BaseModel):
    """Material sugerido para um aluno"""
    material_id: int
    titulo: str
    descricao: Optional[str]
    topico_relacionado: str
    desempenho_no_topico: float  # Média do aluno neste tópico
    url: Optional[str] = None


class MaterialSugestaoResponse(BaseModel):
    """Lista de materiais sugeridos personalizados"""
    aluno_id: int
    aluno_nome: str
    topicos_com_dificuldade: List[str]
    materiais_sugeridos: List[MaterialSugestaoItem]
    total_sugestoes: int


@router.get(
    "/alunos/{aluno_id}/materiais/sugestoes",
    response_model=MaterialSugestaoResponse,
    summary="Sugerir materiais personalizados (US12)",
    description="Sugere materiais de reforço baseados em tópicos com desempenho < 60% nas últimas 3 avaliações (US12)",
)
def sugerir_materiais_aluno(
    aluno_id: int,
    conn: sqlite3.Connection = Depends(get_db),
    current_user: UsuarioSchema = Depends(get_current_user),
):
    """
    Sugere materiais personalizados para um aluno com dificuldades.
    
    Implementa **US12**: "Como professor, eu quero sugerir materiais de reforço
    personalizados para um aluno com base nos tópicos com desempenho inferior
    a 60% nas últimas 3 avaliações, para ajudá-lo a superar os desafios."
    
    Critérios:
    - Identifica tópicos onde a média do aluno < 6.0 nas últimas 3 avaliações
    - Busca materiais relacionados aos tópicos identificados
    - Retorna materiais ordenados por relevância (menor desempenho primeiro)
    
    Args:
        aluno_id: ID do aluno
        conn: Conexão com o banco
        current_user: Usuário autenticado (professor)
        
    Returns:
        Lista de materiais sugeridos com justificativa
        
    Raises:
        HTTPException 404: Se aluno não for encontrado
        HTTPException 403: Se usuário não for professor
    """
    # Verificar se é professor
    if current_user.tipo_usuario != 'professor':
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Apenas professores podem sugerir materiais"
        )
    
    # Buscar nome do aluno
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome FROM usuarios WHERE id = ? AND tipo_usuario = 'aluno'",
        (aluno_id,)
    )
    aluno_row = cursor.fetchone()
    
    if not aluno_row:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Aluno {aluno_id} não encontrado"
        )
    
    aluno_nome = aluno_row['nome']
    
    # Identificar tópicos com dificuldade (média < 6.0 nas últimas 3 avaliações)
    cursor.execute("""
        WITH ultimas_avaliacoes AS (
            SELECT DISTINCT a.id, a.topico, a.data, a.turma_id
            FROM avaliacoes a
            INNER JOIN notas n ON a.id = n.avaliacao_id
            WHERE n.aluno_id = ?
                AND a.topico IS NOT NULL
                AND a.topico != ''
            ORDER BY a.data DESC
            LIMIT 3
        ),
        desempenho_topicos AS (
            SELECT 
                COALESCE(a.topico, 'Sem tópico') as topico,
                AVG(n.valor) as media_topico,
                a.turma_id
            FROM ultimas_avaliacoes ua
            INNER JOIN avaliacoes a ON ua.id = a.id
            INNER JOIN notas n ON a.id = n.avaliacao_id
            WHERE n.aluno_id = ?
            GROUP BY topico, a.turma_id
            HAVING media_topico < 6.0
        )
        SELECT 
            dt.topico,
            dt.media_topico,
            dt.turma_id,
            t.nome as turma_nome
        FROM desempenho_topicos dt
        LEFT JOIN turmas t ON dt.turma_id = t.id
        ORDER BY dt.media_topico ASC
    """, (aluno_id, aluno_id))
    
    topicos_dificuldade = cursor.fetchall()
    
    if not topicos_dificuldade:
        # Aluno não tem dificuldades identificadas
        return MaterialSugestaoResponse(
            aluno_id=aluno_id,
            aluno_nome=aluno_nome,
            topicos_com_dificuldade=[],
            materiais_sugeridos=[],
            total_sugestoes=0
        )
    
    # Buscar materiais relacionados aos tópicos identificados
    topicos_lista = [t['topico'] for t in topicos_dificuldade]
    topicos_map = {t['topico']: t['media_topico'] for t in topicos_dificuldade}
    
    # Query para materiais - busca por palavra-chave no título ou descrição
    placeholders = ','.join('?' * len(topicos_lista))
    
    materiais_sugeridos = []
    
    for topico in topicos_lista:
        cursor.execute(f"""
            SELECT 
                m.id,
                m.titulo,
                m.descricao,
                m.arquivo_url
            FROM materiais m
            WHERE (
                LOWER(m.titulo) LIKE LOWER(?) 
                OR LOWER(m.descricao) LIKE LOWER(?)
            )
            LIMIT 5
        """, (f'%{topico}%', f'%{topico}%'))
        
        rows = cursor.fetchall()
        
        for row in rows:
            materiais_sugeridos.append(MaterialSugestaoItem(
                material_id=row['id'],
                titulo=row['titulo'],
                descricao=row['descricao'],
                topico_relacionado=topico,
                desempenho_no_topico=topicos_map[topico],
                url=row['arquivo_url'] if row['arquivo_url'] else None
            ))
    
    # Se não encontrou materiais específicos, buscar materiais gerais das turmas do aluno
    if not materiais_sugeridos:
        turmas_ids = list(set([t['turma_id'] for t in topicos_dificuldade]))
        placeholders_turmas = ','.join('?' * len(turmas_ids))
        
        cursor.execute(f"""
            SELECT 
                m.id,
                m.titulo,
                m.descricao,
                m.arquivo_url,
                t.nome as turma_nome
            FROM materiais m
            INNER JOIN turmas t ON m.turma_id = t.id
            WHERE m.turma_id IN ({placeholders_turmas})
            ORDER BY m.data_upload DESC
            LIMIT 10
        """, turmas_ids)
        
        rows = cursor.fetchall()
        
        for row in rows:
            materiais_sugeridos.append(MaterialSugestaoItem(
                material_id=row['id'],
                titulo=row['titulo'],
                descricao=row['descricao'],
                topico_relacionado=f"Material geral - {row['turma_nome']}",
                desempenho_no_topico=min(topicos_map.values()),
                url=row['arquivo_url'] if row['arquivo_url'] else None
            ))
    
    return MaterialSugestaoResponse(
        aluno_id=aluno_id,
        aluno_nome=aluno_nome,
        topicos_com_dificuldade=topicos_lista,
        materiais_sugeridos=materiais_sugeridos,
        total_sugestoes=len(materiais_sugeridos)
    )

