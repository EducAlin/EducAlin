"""
Modelo de Meta de aprendizado.

MetaModel representa uma meta de aprendizado de um aluno.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime
from .base_model import BaseModel


class MetaModel(BaseModel):
    """
    Modelo de Meta de aprendizado.
    
    Relacionamentos:
    - aluno_id -> usuarios(id) onde tipo_usuario='aluno'
    
    Uma meta tem descrição, valor alvo, prazo, e progresso atual.
    """
    
    def __init__(
        self,
        id: int,
        aluno_id: int,
        descricao: str,
        valor_alvo: float,
        prazo: datetime,
        progresso_atual: float = 0.0,
        meta_atingida_em: Optional[datetime] = None,
        criada_em: Optional[datetime] = None,
    ):
        self.id = id
        self.aluno_id = aluno_id
        self.descricao = descricao
        self.valor_alvo = valor_alvo
        self.prazo = prazo
        self.progresso_atual = progresso_atual
        self.meta_atingida_em = meta_atingida_em
        self.criada_em = criada_em or datetime.now()
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        aluno_id: int,
        descricao: str,
        valor_alvo: float,
        prazo: datetime,
        progresso_atual: float = 0.0,
    ) -> int:
        """
        Cria uma nova meta.
        
        Args:
            conn: Conexão SQLite
            aluno_id: ID do aluno
            descricao: Descrição da meta
            valor_alvo: Valor alvo a ser atingido
            prazo: Data e hora limite
            progresso_atual: Progresso inicial (padrão 0.0)
        
        Returns:
            int: ID da meta criada
        
        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Validações
        descricao = cls._validate_not_empty(descricao, "Descrição")
        
        if not isinstance(valor_alvo, (int, float)) or valor_alvo <= 0:
            raise ValueError("Valor alvo deve ser um número positivo.")
        
        if not isinstance(prazo, datetime):
            raise ValueError("Prazo deve ser um objeto datetime.")
        
        if not isinstance(progresso_atual, (int, float)) or progresso_atual < 0:
            raise ValueError("Progresso atual deve ser um número não-negativo.")
        
        if progresso_atual > valor_alvo:
            raise ValueError("Progresso atual não pode ser maior que o valor alvo.")
        
        # Verificar se o aluno existe
        cursor = conn.execute(
            "SELECT id FROM usuarios WHERE id = ? AND tipo_usuario = 'aluno'",
            (aluno_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Aluno com id {aluno_id} não existe.")
        
        # Definir meta_atingida_em se progresso >= valor_alvo
        meta_atingida_em = None
        if progresso_atual >= valor_alvo:
            meta_atingida_em = datetime.now().isoformat()
        
        cursor = conn.execute(
            """
            INSERT INTO metas (aluno_id, descricao, valor_alvo, prazo, progresso_atual, meta_atingida_em)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (aluno_id, descricao, valor_alvo, prazo.isoformat(), progresso_atual, meta_atingida_em)
        )
        conn.commit()
        return cursor.lastrowid
    
    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, meta_id: int) -> Optional['MetaModel']:
        """Busca meta por ID."""
        cursor = conn.execute(
            "SELECT * FROM metas WHERE id = ?",
            (meta_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return cls(
            id=row['id'],
            aluno_id=row['aluno_id'],
            descricao=row['descricao'],
            valor_alvo=row['valor_alvo'],
            prazo=datetime.fromisoformat(row['prazo']),
            progresso_atual=row['progresso_atual'],
            meta_atingida_em=datetime.fromisoformat(row['meta_atingida_em']) if row['meta_atingida_em'] else None,
            criada_em=datetime.fromisoformat(row['criada_em'])
        )
    
    @classmethod
    def listar_por_aluno(
        cls,
        conn: sqlite3.Connection,
        aluno_id: int,
        apenas_ativas: bool = False
    ) -> List['MetaModel']:
        """
        Lista todas as metas de um aluno.
        
        Args:
            conn: Conexão SQLite
            aluno_id: ID do aluno
            apenas_ativas: Se True, retorna apenas metas não atingidas
        """
        if apenas_ativas:
            query = """
                SELECT * FROM metas 
                WHERE aluno_id = ? AND meta_atingida_em IS NULL
                ORDER BY prazo ASC
            """
        else:
            query = "SELECT * FROM metas WHERE aluno_id = ? ORDER BY prazo DESC"
        
        cursor = conn.execute(query, (aluno_id,))
        
        metas = []
        for row in cursor.fetchall():
            metas.append(cls(
                id=row['id'],
                aluno_id=row['aluno_id'],
                descricao=row['descricao'],
                valor_alvo=row['valor_alvo'],
                prazo=datetime.fromisoformat(row['prazo']),
                progresso_atual=row['progresso_atual'],
                meta_atingida_em=datetime.fromisoformat(row['meta_atingida_em']) if row['meta_atingida_em'] else None,
                criada_em=datetime.fromisoformat(row['criada_em'])
            ))
        return metas
    
    def atualizar_progresso(self, conn: sqlite3.Connection, novo_progresso: float) -> bool:
        """
        Atualiza o progresso da meta.
        
        Args:
            conn: Conexão SQLite
            novo_progresso: Novo valor de progresso
        
        Returns:
            bool: True se a meta foi atingida com esta atualização
        
        Raises:
            ValueError: Se o novo progresso for inválido
        """
        # Validações
        if not isinstance(novo_progresso, (int, float)) or novo_progresso < 0:
            raise ValueError("Progresso deve ser um número não-negativo.")
        
        if novo_progresso > self.valor_alvo:
            raise ValueError(f"Progresso ({novo_progresso}) não pode ser maior que o valor alvo ({self.valor_alvo}).")
        
        # Verificar se meta foi atingida
        meta_atingida = novo_progresso >= self.valor_alvo
        meta_atingida_em = None
        
        if meta_atingida and not self.meta_atingida_em:
            # Meta acabou de ser atingida
            meta_atingida_em = datetime.now().isoformat()
        elif not meta_atingida:
            # Meta ainda não foi atingida (pode ter sido revertida)
            meta_atingida_em = None
        else:
            # Meta já estava atingida, mantém a data original
            meta_atingida_em = self.meta_atingida_em.isoformat() if self.meta_atingida_em else None
        
        conn.execute(
            "UPDATE metas SET progresso_atual = ?, meta_atingida_em = ? WHERE id = ?",
            (novo_progresso, meta_atingida_em, self.id)
        )
        conn.commit()
        
        self.progresso_atual = novo_progresso
        if meta_atingida_em:
            self.meta_atingida_em = datetime.fromisoformat(meta_atingida_em)
        else:
            self.meta_atingida_em = None
        
        return meta_atingida and not self.meta_atingida_em
    
    def atualizar(self, conn: sqlite3.Connection, **campos) -> None:
        """
        Atualiza campos da meta.
        
        Args:
            conn: Conexão SQLite
            **campos: Campos a atualizar (descricao, valor_alvo, prazo)
        """
        # Validações
        if 'descricao' in campos:
            campos['descricao'] = self._validate_not_empty(campos['descricao'], "Descrição")
        
        if 'valor_alvo' in campos:
            if not isinstance(campos['valor_alvo'], (int, float)) or campos['valor_alvo'] <= 0:
                raise ValueError("Valor alvo deve ser um número positivo.")
            if campos['valor_alvo'] < self.progresso_atual:
                raise ValueError("Valor alvo não pode ser menor que o progresso atual.")
        
        if 'prazo' in campos:
            if not isinstance(campos['prazo'], datetime):
                raise ValueError("Prazo deve ser um objeto datetime.")
            campos['prazo'] = campos['prazo'].isoformat()
        
        # Monta query dinamicamente
        sets = ', '.join(f"{campo} = ?" for campo in campos.keys())
        valores = list(campos.values()) + [self.id]
        
        conn.execute(
            f"UPDATE metas SET {sets} WHERE id = ?",
            valores
        )
        conn.commit()
        
        # Atualiza instância local
        for campo, valor in campos.items():
            if campo == 'prazo' and isinstance(valor, str):
                valor = datetime.fromisoformat(valor)
            setattr(self, campo, valor)
    
    def deletar(self, conn: sqlite3.Connection) -> None:
        """Deleta a meta do banco de dados."""
        conn.execute("DELETE FROM metas WHERE id = ?", (self.id,))
        conn.commit()
    
    def calcular_percentual_progresso(self) -> float:
        """
        Calcula o percentual de progresso da meta.
        
        Returns:
            float: Percentual entre 0 e 100
        """
        if self.valor_alvo == 0:
            return 0.0
        return (self.progresso_atual / self.valor_alvo) * 100
    
    def esta_atingida(self) -> bool:
        """Verifica se a meta foi atingida."""
        return self.meta_atingida_em is not None
    
    def esta_vencida(self) -> bool:
        """Verifica se o prazo da meta já passou."""
        return datetime.now() > self.prazo and not self.esta_atingida()
