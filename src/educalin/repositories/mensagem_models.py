"""
Modelo de Mensagem para comunicação professor-aluno (US10).

MensagemModel representa uma mensagem privada entre usuários do sistema.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime
from .base_model import BaseModel


class MensagemModel(BaseModel):
    """
    Modelo de Mensagem.
    
    Relacionamentos:
    - remetente_id -> usuarios(id)
    - destinatario_id -> usuarios(id)
    
    Implementa US10: Sistema de mensagens privadas professor-aluno.
    """
    
    def __init__(
        self,
        id: int,
        remetente_id: int,
        destinatario_id: int,
        conteudo: str,
        lida: bool,
        data_envio: datetime,
        data_leitura: Optional[datetime] = None,
    ):
        self.id = id
        self.remetente_id = remetente_id
        self.destinatario_id = destinatario_id
        self.conteudo = conteudo
        self.lida = lida
        self.data_envio = data_envio
        self.data_leitura = data_leitura
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        remetente_id: int,
        destinatario_id: int,
        conteudo: str,
    ) -> int:
        """
        Cria uma nova mensagem.
        
        Args:
            conn: Conexão SQLite
            remetente_id: ID do remetente
            destinatario_id: ID do destinatário
            conteudo: Texto da mensagem
            
        Returns:
            ID da mensagem criada
            
        Raises:
            ValueError: Se dados forem inválidos
        """
        if remetente_id == destinatario_id:
            raise ValueError("Remetente e destinatário não podem ser o mesmo usuário")
        
        if not conteudo or not conteudo.strip():
            raise ValueError("Conteúdo da mensagem não pode ser vazio")
        
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO mensagens (
                remetente_id, destinatario_id, conteudo, lida, data_envio
            ) VALUES (?, ?, ?, 0, ?)
            """,
            (remetente_id, destinatario_id, conteudo.strip(), datetime.now())
        )
        conn.commit()
        return cursor.lastrowid
    
    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, mensagem_id: int) -> Optional['MensagemModel']:
        """
        Busca uma mensagem pelo ID.
        
        Args:
            conn: Conexão SQLite
            mensagem_id: ID da mensagem
            
        Returns:
            MensagemModel se encontrada, None caso contrário
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, remetente_id, destinatario_id, conteudo, lida, 
                   data_envio, data_leitura
            FROM mensagens
            WHERE id = ?
            """,
            (mensagem_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return cls(
            id=row['id'],
            remetente_id=row['remetente_id'],
            destinatario_id=row['destinatario_id'],
            conteudo=row['conteudo'],
            lida=bool(row['lida']),
            data_envio=datetime.fromisoformat(row['data_envio']),
            data_leitura=datetime.fromisoformat(row['data_leitura']) if row['data_leitura'] else None
        )
    
    @classmethod
    def listar_conversa(
        cls,
        conn: sqlite3.Connection,
        usuario_id: int,
        outro_usuario_id: int,
        limite: int = 50
    ) -> List['MensagemModel']:
        """
        Lista mensagens entre dois usuários ordenadas por data (mais recentes primeiro).
        
        Args:
            conn: Conexão SQLite
            usuario_id: ID de um dos usuários
            outro_usuario_id: ID do outro usuário
            limite: Número máximo de mensagens a retornar (default: 50)
            
        Returns:
            Lista de mensagens entre os dois usuários
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, remetente_id, destinatario_id, conteudo, lida,
                   data_envio, data_leitura
            FROM mensagens
            WHERE (remetente_id = ? AND destinatario_id = ?)
               OR (remetente_id = ? AND destinatario_id = ?)
            ORDER BY data_envio DESC
            LIMIT ?
            """,
            (usuario_id, outro_usuario_id, outro_usuario_id, usuario_id, limite)
        )
        rows = cursor.fetchall()
        
        mensagens = []
        for row in rows:
            mensagens.append(cls(
                id=row['id'],
                remetente_id=row['remetente_id'],
                destinatario_id=row['destinatario_id'],
                conteudo=row['conteudo'],
                lida=bool(row['lida']),
                data_envio=datetime.fromisoformat(row['data_envio']),
                data_leitura=datetime.fromisoformat(row['data_leitura']) if row['data_leitura'] else None
            ))
        
        return mensagens
    
    @classmethod
    def listar_recebidas(
        cls,
        conn: sqlite3.Connection,
        usuario_id: int,
        apenas_nao_lidas: bool = False,
        limite: int = 100
    ) -> List['MensagemModel']:
        """
        Lista mensagens recebidas por um usuário.
        
        Args:
            conn: Conexão SQLite
            usuario_id: ID do usuário destinatário
            apenas_nao_lidas: Se True, retorna apenas mensagens não lidas
            limite: Número máximo de mensagens (default: 100)
            
        Returns:
            Lista de mensagens recebidas
        """
        cursor = conn.cursor()
        
        sql = """
            SELECT id, remetente_id, destinatario_id, conteudo, lida,
                   data_envio, data_leitura
            FROM mensagens
            WHERE destinatario_id = ?
        """
        
        if apenas_nao_lidas:
            sql += " AND lida = 0"
        
        sql += " ORDER BY data_envio DESC LIMIT ?"
        
        cursor.execute(sql, (usuario_id, limite))
        rows = cursor.fetchall()
        
        mensagens = []
        for row in rows:
            mensagens.append(cls(
                id=row['id'],
                remetente_id=row['remetente_id'],
                destinatario_id=row['destinatario_id'],
                conteudo=row['conteudo'],
                lida=bool(row['lida']),
                data_envio=datetime.fromisoformat(row['data_envio']),
                data_leitura=datetime.fromisoformat(row['data_leitura']) if row['data_leitura'] else None
            ))
        
        return mensagens
    
    @classmethod
    def marcar_como_lida(cls, conn: sqlite3.Connection, mensagem_id: int) -> bool:
        """
        Marca uma mensagem como lida.
        
        Args:
            conn: Conexão SQLite
            mensagem_id: ID da mensagem
            
        Returns:
            True se atualizada com sucesso, False se não encontrada
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE mensagens
            SET lida = 1, data_leitura = ?
            WHERE id = ? AND lida = 0
            """,
            (datetime.now(), mensagem_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    
    @classmethod
    def contar_nao_lidas(cls, conn: sqlite3.Connection, usuario_id: int) -> int:
        """
        Conta mensagens não lidas de um usuário.
        
        Args:
            conn: Conexão SQLite
            usuario_id: ID do usuário
            
        Returns:
            Número de mensagens não lidas
        """
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM mensagens
            WHERE destinatario_id = ? AND lida = 0
            """,
            (usuario_id,)
        )
        row = cursor.fetchone()
        return row['total'] if row else 0
