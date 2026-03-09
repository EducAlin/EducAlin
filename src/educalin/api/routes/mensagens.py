"""
Rotas de Mensagens da API FastAPI (US10).

Este módulo implementa endpoints para:
- Envio de mensagens privadas entre professor e aluno
- Listagem de conversas
- Listagem de mensagens recebidas
- Marcação de mensagens como lidas
- Contagem de mensagens não lidas
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status as http_status, Query
from pydantic import BaseModel, Field
from datetime import datetime

from ..dependencies import get_current_user
from ..schemas import UsuarioSchema, ErrorSchema
from educalin.repositories.mensagem_repository import MensagemRepository
from educalin.repositories.base import get_connection
import sqlite3


# Schemas específicos para mensagens
class MensagemEnviarSchema(BaseModel):
    """Schema para envio de mensagem"""
    destinatario_id: int = Field(..., gt=0, description="ID do destinatário")
    conteudo: str = Field(..., min_length=1, max_length=5000, description="Conteúdo da mensagem")


class MensagemResponseSchema(BaseModel):
    """Schema de resposta de mensagem"""
    id: int
    remetente_id: int
    destinatario_id: int
    conteudo: str
    lida: bool
    data_envio: datetime
    data_leitura: Optional[datetime] = None


class ConversaResponseSchema(BaseModel):
    """Schema de resposta de conversa"""
    mensagens: List[MensagemResponseSchema]
    total: int


class ContatoSchema(BaseModel):
    """Schema para contato recente"""
    contato_id: int
    contato_nome: str
    contato_tipo: str
    ultima_mensagem: datetime


class NaoLidasCountSchema(BaseModel):
    """Schema para contagem de mensagens não lidas"""
    total_nao_lidas: int


# Criar router para rotas de mensagens
router = APIRouter(
    prefix="/mensagens",
    tags=["Mensagens"],
    responses={
        401: {"model": ErrorSchema, "description": "Não autorizado"},
        400: {"model": ErrorSchema, "description": "Requisição inválida"},
        404: {"model": ErrorSchema, "description": "Mensagem não encontrada"},
    }
)


def get_db() -> sqlite3.Connection:
    """Dependency para obter conexão com o banco"""
    return get_connection()


@router.post(
    "/",
    response_model=MensagemResponseSchema,
    status_code=http_status.HTTP_201_CREATED,
    summary="Enviar mensagem",
    description="Envia uma nova mensagem privada (US10)"
)
def enviar_mensagem(
    mensagem: MensagemEnviarSchema,
    current_user: UsuarioSchema = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Envia uma nova mensagem privada.
    
    Implementa **US10**: "Como professor/aluno, quero enviar mensagens privadas
    para estabelecer comunicação direta."
    
    Args:
        mensagem: Dados da mensagem (destinatário e conteúdo)
        current_user: Usuário autenticado (remetente)
        conn: Conexão com o banco
        
    Returns:
        Dados da mensagem criada
        
    Raises:
        HTTPException 400: Se tentar enviar mensagem para si mesmo
        HTTPException 404: Se destinatário não existir
    """
    # Verificar se não está enviando para si mesmo
    if mensagem.destinatario_id == current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Não é possível enviar mensagem para si mesmo"
        )
    
    # Verificar se destinatário existe
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE id = ?", (mensagem.destinatario_id,))
    if not cursor.fetchone():
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Destinatário {mensagem.destinatario_id} não encontrado"
        )
    
    # Criar mensagem
    repo = MensagemRepository(conn)
    mensagem_id = repo.enviar_mensagem(
        remetente_id=current_user.id,
        destinatario_id=mensagem.destinatario_id,
        conteudo=mensagem.conteudo
    )
    
    # Buscar mensagem criada
    mensagem_criada = repo.buscar_por_id(mensagem_id)
    
    return MensagemResponseSchema(**mensagem_criada)


@router.get(
    "/conversa/{usuario_id}",
    response_model=ConversaResponseSchema,
    summary="Listar conversa",
    description="Lista mensagens entre o usuário atual e outro usuário (US10)"
)
def listar_conversa(
    usuario_id: int,
    limite: int = Query(50, ge=1, le=200, description="Número máximo de mensagens"),
    current_user: UsuarioSchema = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Lista mensagens trocadas entre o usuário atual e outro usuário.
    
    Args:
        usuario_id: ID do outro usuário
        limite: Número máximo de mensagens (default: 50)
        current_user: Usuário autenticado
        conn: Conexão com o banco
        
    Returns:
        Lista de mensagens entre os dois usuários
        
    Raises:
        HTTPException 400: Se tentar listar conversa consigo mesmo
    """
    if usuario_id == current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Não é possível listar conversa consigo mesmo"
        )
    
    repo = MensagemRepository(conn)
    mensagens = repo.listar_conversa(
        usuario_id=current_user.id,
        outro_usuario_id=usuario_id,
        limite=limite
    )
    
    return ConversaResponseSchema(
        mensagens=[MensagemResponseSchema(**m) for m in mensagens],
        total=len(mensagens)
    )


@router.get(
    "/recebidas",
    response_model=List[MensagemResponseSchema],
    summary="Listar mensagens recebidas",
    description="Lista mensagens recebidas pelo usuário autenticado (US10)"
)
def listar_recebidas(
    apenas_nao_lidas: bool = Query(False, description="Filtrar apenas mensagens não lidas"),
    limite: int = Query(100, ge=1, le=500, description="Número máximo de mensagens"),
    current_user: UsuarioSchema = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Lista mensagens recebidas pelo usuário autenticado.
    
    Args:
        apenas_nao_lidas: Se True, retorna apenas mensagens não lidas
        limite: Número máximo de mensagens (default: 100)
        current_user: Usuário autenticado
        conn: Conexão com o banco
        
    Returns:
        Lista de mensagens recebidas
    """
    repo = MensagemRepository(conn)
    mensagens = repo.listar_recebidas(
        usuario_id=current_user.id,
        apenas_nao_lidas=apenas_nao_lidas,
        limite=limite
    )
    
    return [MensagemResponseSchema(**m) for m in mensagens]


@router.patch(
    "/{mensagem_id}/lida",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Marcar mensagem como lida",
    description="Marca uma mensagem como lida (US10)"
)
def marcar_como_lida(
    mensagem_id: int,
    current_user: UsuarioSchema = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Marca uma mensagem como lida.
    
    Apenas o destinatário pode marcar sua mensagem como lida.
    
    Args:
        mensagem_id: ID da mensagem
        current_user: Usuário autenticado (deve ser o destinatário)
        conn: Conexão com o banco
        
    Raises:
        HTTPException 404: Se mensagem não for encontrada
        HTTPException 403: Se usuário não for o destinatário da mensagem
    """
    repo = MensagemRepository(conn)
    mensagem = repo.buscar_por_id(mensagem_id)
    
    if not mensagem:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Mensagem {mensagem_id} não encontrada"
        )
    
    # Verificar se é o destinatário
    if mensagem['destinatario_id'] != current_user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Apenas o destinatário pode marcar a mensagem como lida"
        )
    
    # Marcar como lida
    repo.marcar_como_lida(mensagem_id)
    return None


@router.get(
    "/nao-lidas/count",
    response_model=NaoLidasCountSchema,
    summary="Contar mensagens não lidas",
    description="Retorna o número de mensagens não lidas do usuário (US10)"
)
def contar_nao_lidas(
    current_user: UsuarioSchema = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Conta mensagens não lidas do usuário autenticado.
    
    Args:
        current_user: Usuário autenticado
        conn: Conexão com o banco
        
    Returns:
        Total de mensagens não lidas
    """
    repo = MensagemRepository(conn)
    total = repo.contar_nao_lidas(current_user.id)
    
    return NaoLidasCountSchema(total_nao_lidas=total)


@router.get(
    "/contatos",
    response_model=List[ContatoSchema],
    summary="Listar contatos recentes",
    description="Lista usuários com quem trocou mensagens recentemente (US10)"
)
def listar_contatos_recentes(
    limite: int = Query(10, ge=1, le=50, description="Número máximo de contatos"),
    current_user: UsuarioSchema = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    Lista usuários com quem o usuário autenticado trocou mensagens recentemente.
    
    Args:
        limite: Número máximo de contatos (default: 10)
        current_user: Usuário autenticado
        conn: Conexão com o banco
        
    Returns:
        Lista de contatos ordenada por última mensagem
    """
    repo = MensagemRepository(conn)
    contatos = repo.listar_contatos_recentes(
        usuario_id=current_user.id,
        limite=limite
    )
    
    return [ContatoSchema(**c) for c in contatos]
