"""
Repository para operações de banco de dados com Mensagens (US10).

Implementa o padrão Repository para abstrair operações de persistência
de mensagens privadas entre professor e aluno usando SQL puro (SQLite3).
"""

import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime

from .base_model import BaseModel
from .mensagem_models import MensagemModel
from .base import get_connection


class MensagemRepository:
    """
    Repository para operações CRUD de mensagens.
    
    Utiliza SQL puro para interagir com a tabela 'mensagens'.
    Implementa US10: Sistema de mensagens privadas professor-aluno.
    
    Example:
        >>> repo = MensagemRepository()
        >>> mensagem_id = repo.enviar_mensagem(
        ...     remetente_id=1,
        ...     destinatario_id=2,
        ...     conteudo="Olá, preciso de ajuda"
        ... )
        >>> mensagens = repo.listar_conversa(usuario_id=1, outro_usuario_id=2)
        >>> repo.marcar_como_lida(mensagem_id)
    """
    
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        """
        Inicializa o repository.
        
        Args:
            conn: Conexão SQLite opcional. Se não fornecida, cria uma nova.
        """
        self.conn = conn or get_connection()
        self._own_connection = conn is None
    
    def __enter__(self):
        """Suporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão ao sair do context manager (se for própria)."""
        if self._own_connection:
            self.conn.close()
    
    def enviar_mensagem(
        self,
        remetente_id: int,
        destinatario_id: int,
        conteudo: str
    ) -> int:
        """
        Envia uma nova mensagem.
        
        Args:
            remetente_id: ID do usuário remetente
            destinatario_id: ID do usuário destinatário
            conteudo: Texto da mensagem
            
        Returns:
            ID da mensagem criada
            
        Raises:
            ValueError: Se dados forem inválidos
        """
        return MensagemModel.criar(
            conn=self.conn,
            remetente_id=remetente_id,
            destinatario_id=destinatario_id,
            conteudo=conteudo
        )
    
    def buscar_por_id(self, mensagem_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca uma mensagem pelo ID.
        
        Args:
            mensagem_id: ID da mensagem
            
        Returns:
            Dicionário com dados da mensagem ou None se não encontrada
        """
        model = MensagemModel.buscar_por_id(self.conn, mensagem_id)
        
        if not model:
            return None
        
        return {
            'id': model.id,
            'remetente_id': model.remetente_id,
            'destinatario_id': model.destinatario_id,
            'conteudo': model.conteudo,
            'lida': model.lida,
            'data_envio': model.data_envio,
            'data_leitura': model.data_leitura
        }
    
    def listar_conversa(
        self,
        usuario_id: int,
        outro_usuario_id: int,
        limite: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Lista mensagens entre dois usuários.
        
        Args:
            usuario_id: ID de um dos usuários
            outro_usuario_id: ID do outro usuário
            limite: Número máximo de mensagens (default: 50)
            
        Returns:
            Lista de mensagens ordenadas por data (mais recentes primeiro)
        """
        models = MensagemModel.listar_conversa(
            conn=self.conn,
            usuario_id=usuario_id,
            outro_usuario_id=outro_usuario_id,
            limite=limite
        )
        
        return [
            {
                'id': m.id,
                'remetente_id': m.remetente_id,
                'destinatario_id': m.destinatario_id,
                'conteudo': m.conteudo,
                'lida': m.lida,
                'data_envio': m.data_envio,
                'data_leitura': m.data_leitura
            }
            for m in models
        ]
    
    def listar_recebidas(
        self,
        usuario_id: int,
        apenas_nao_lidas: bool = False,
        limite: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Lista mensagens recebidas por um usuário.
        
        Args:
            usuario_id: ID do usuário destinatário
            apenas_nao_lidas: Se True, retorna apenas não lidas
            limite: Número máximo de mensagens (default: 100)
            
        Returns:
            Lista de mensagens recebidas
        """
        models = MensagemModel.listar_recebidas(
            conn=self.conn,
            usuario_id=usuario_id,
            apenas_nao_lidas=apenas_nao_lidas,
            limite=limite
        )
        
        return [
            {
                'id': m.id,
                'remetente_id': m.remetente_id,
                'destinatario_id': m.destinatario_id,
                'conteudo': m.conteudo,
                'lida': m.lida,
                'data_envio': m.data_envio,
                'data_leitura': m.data_leitura
            }
            for m in models
        ]
    
    def marcar_como_lida(self, mensagem_id: int) -> bool:
        """
        Marca mensagem como lida.
        
        Args:
            mensagem_id: ID da mensagem
            
        Returns:
            True se atualizada, False se não encontrada ou já lida
        """
        return MensagemModel.marcar_como_lida(self.conn, mensagem_id)
    
    def contar_nao_lidas(self, usuario_id: int) -> int:
        """
        Conta mensagens não lidas de um usuário.
        
        Args:
            usuario_id: ID do usuário
            
        Returns:
            Número de mensagens não lidas
        """
        return MensagemModel.contar_nao_lidas(self.conn, usuario_id)
    
    def listar_contatos_recentes(
        self,
        usuario_id: int,
        limite: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Lista usuários com quem o usuário trocou mensagens recentemente.
        
        Args:
            usuario_id: ID do usuário
            limite: Número máximo de contatos (default: 10)
            
        Returns:
            Lista com IDs e informações dos contatos
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT
                CASE
                    WHEN m.remetente_id = ? THEN m.destinatario_id
                    ELSE m.remetente_id
                END as contato_id,
                u.nome as contato_nome,
                u.tipo_usuario as contato_tipo,
                MAX(m.data_envio) as ultima_mensagem
            FROM mensagens m
            INNER JOIN usuarios u ON u.id = CASE
                WHEN m.remetente_id = ? THEN m.destinatario_id
                ELSE m.remetente_id
            END
            WHERE m.remetente_id = ? OR m.destinatario_id = ?
            GROUP BY contato_id, contato_nome, contato_tipo
            ORDER BY ultima_mensagem DESC
            LIMIT ?
            """,
            (usuario_id, usuario_id, usuario_id, usuario_id, limite)
        )
        
        rows = cursor.fetchall()
        
        return [
            {
                'contato_id': row['contato_id'],
                'contato_nome': row['contato_nome'],
                'contato_tipo': row['contato_tipo'],
                'ultima_mensagem': datetime.fromisoformat(row['ultima_mensagem'])
            }
            for row in rows
        ]
