"""
Modelo de Plano de Ação com composição de materiais.

PlanoAcaoModel representa um plano personalizado para um aluno.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime, timedelta
from .base_model import BaseModel


class PlanoAcaoModel(BaseModel):
    """
    Modelo de Plano de Ação.
    
    Relacionamentos:
    - aluno_id -> usuarios(id) onde tipo_usuario='aluno'
    - Composição com MaterialModel via tabela plano_materiais (many-to-many)
    
    Status possíveis: rascunho, enviado, em_andamento, concluido, cancelado
    """
    
    STATUS_VALIDOS = ['rascunho', 'enviado', 'em_andamento', 'concluido', 'cancelado']
    
    def __init__(
        self,
        id: int,
        aluno_id: int,
        objetivo: str,
        data_criacao: datetime,
        data_limite: datetime,
        status: str = 'rascunho',
        observacoes: Optional[str] = None,
    ):
        self.id = id
        self.aluno_id = aluno_id
        self.objetivo = objetivo
        self.data_criacao = data_criacao
        self.data_limite = data_limite
        self.status = status
        self.observacoes = observacoes
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        aluno_id: int,
        objetivo: str,
        prazo_dias: int,
        observacoes: Optional[str] = None,
    ) -> int:
        """
        Cria um novo plano de ação.
        
        Args:
            conn: Conexão SQLite
            aluno_id: ID do aluno destinatário
            objetivo: Objetivo/descrição do plano
            prazo_dias: Número de dias até a data limite
            observacoes: Observações adicionais (opcional)
        
        Returns:
            int: ID do plano criado
        
        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Validações
        objetivo = cls._validate_not_empty(objetivo, "Objetivo")
        
        if not isinstance(prazo_dias, int) or prazo_dias <= 0:
            raise ValueError("Prazo em dias deve ser um inteiro positivo.")
        
        # Verificar se o aluno existe
        cursor = conn.execute(
            "SELECT id FROM usuarios WHERE id = ? AND tipo_usuario = 'aluno'",
            (aluno_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Aluno com id {aluno_id} não existe.")
        
        data_criacao = datetime.now()
        data_limite = data_criacao + timedelta(days=prazo_dias)
        
        cursor = conn.execute(
            """
            INSERT INTO planos_acao (aluno_id, objetivo, data_criacao, data_limite, status, observacoes)
            VALUES (?, ?, ?, ?, 'rascunho', ?)
            """,
            (aluno_id, objetivo, data_criacao.isoformat(), data_limite.isoformat(), observacoes)
        )
        conn.commit()
        return cursor.lastrowid
    
    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, plano_id: int) -> Optional['PlanoAcaoModel']:
        """Busca plano de ação por ID."""
        cursor = conn.execute(
            "SELECT * FROM planos_acao WHERE id = ?",
            (plano_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return cls(
            id=row['id'],
            aluno_id=row['aluno_id'],
            objetivo=row['objetivo'],
            data_criacao=datetime.fromisoformat(row['data_criacao']),
            data_limite=datetime.fromisoformat(row['data_limite']),
            status=row['status'],
            observacoes=row['observacoes']
        )
    
    @classmethod
    def listar_por_aluno(
        cls,
        conn: sqlite3.Connection,
        aluno_id: int,
        status: Optional[str] = None
    ) -> List['PlanoAcaoModel']:
        """
        Lista todos os planos de ação de um aluno.
        
        Args:
            conn: Conexão SQLite
            aluno_id: ID do aluno
            status: Filtrar por status (opcional)
        """
        if status:
            if status not in cls.STATUS_VALIDOS:
                raise ValueError(f"Status inválido. Use um de: {cls.STATUS_VALIDOS}")
            query = "SELECT * FROM planos_acao WHERE aluno_id = ? AND status = ? ORDER BY data_criacao DESC"
            cursor = conn.execute(query, (aluno_id, status))
        else:
            query = "SELECT * FROM planos_acao WHERE aluno_id = ? ORDER BY data_criacao DESC"
            cursor = conn.execute(query, (aluno_id,))
        
        planos = []
        for row in cursor.fetchall():
            planos.append(cls(
                id=row['id'],
                aluno_id=row['aluno_id'],
                objetivo=row['objetivo'],
                data_criacao=datetime.fromisoformat(row['data_criacao']),
                data_limite=datetime.fromisoformat(row['data_limite']),
                status=row['status'],
                observacoes=row['observacoes']
            ))
        return planos
    
    def adicionar_material(self, conn: sqlite3.Connection, material_id: int) -> None:
        """
        Adiciona um material ao plano de ação (composição).
        
        Args:
            conn: Conexão SQLite
            material_id: ID do material a adicionar
        
        Raises:
            ValueError: Se o plano já está concluído ou cancelado
            sqlite3.IntegrityError: Se o material já está no plano
        """
        if self.status in ['concluido', 'cancelado']:
            raise ValueError(f"Não é possível adicionar materiais a um plano {self.status}.")
        
        # Verificar se o material existe
        cursor = conn.execute("SELECT id FROM materiais WHERE id = ?", (material_id,))
        if not cursor.fetchone():
            raise ValueError(f"Material com id {material_id} não existe.")
        
        try:
            conn.execute(
                """
                INSERT INTO plano_materiais (plano_id, material_id)
                VALUES (?, ?)
                """,
                (self.id, material_id)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Material já está adicionado a este plano.")
    
    def remover_material(self, conn: sqlite3.Connection, material_id: int) -> None:
        """
        Remove um material do plano de ação.
        
        Args:
            conn: Conexão SQLite
            material_id: ID do material a remover
        
        Raises:
            ValueError: Se o plano já está concluído ou cancelado
        """
        if self.status in ['concluido', 'cancelado']:
            raise ValueError(f"Não é possível remover materiais de um plano {self.status}.")
        
        conn.execute(
            "DELETE FROM plano_materiais WHERE plano_id = ? AND material_id = ?",
            (self.id, material_id)
        )
        conn.commit()
    
    def listar_materiais(self, conn: sqlite3.Connection) -> List[int]:
        """
        Lista os IDs de todos os materiais do plano.
        
        Returns:
            List[int]: Lista de IDs de materiais
        """
        cursor = conn.execute(
            "SELECT material_id FROM plano_materiais WHERE plano_id = ? ORDER BY data_adicao",
            (self.id,)
        )
        return [row['material_id'] for row in cursor.fetchall()]
    
    def atualizar_status(self, conn: sqlite3.Connection, novo_status: str) -> None:
        """
        Atualiza o status do plano de ação.
        
        Args:
            conn: Conexão SQLite
            novo_status: Novo status do plano
        
        Raises:
            ValueError: Se o novo status for inválido ou a transição não for permitida
        """
        if novo_status not in self.STATUS_VALIDOS:
            raise ValueError(f"Status inválido. Use um de: {self.STATUS_VALIDOS}")
        
        # Validar transições de status
        transicoes_validas = {
            'rascunho': ['enviado', 'cancelado'],
            'enviado': ['em_andamento', 'cancelado'],
            'em_andamento': ['concluido', 'cancelado'],
            'concluido': [],  # Status final
            'cancelado': [],  # Status final
        }
        
        if novo_status not in transicoes_validas.get(self.status, []):
            raise ValueError(f"Transição inválida de '{self.status}' para '{novo_status}'.")
        
        # Validar que há materiais antes de enviar
        if novo_status == 'enviado':
            cursor = conn.execute(
                "SELECT COUNT(*) as total FROM plano_materiais WHERE plano_id = ?",
                (self.id,)
            )
            if cursor.fetchone()['total'] == 0:
                raise ValueError("Não é possível enviar um plano sem materiais.")
        
        conn.execute(
            "UPDATE planos_acao SET status = ? WHERE id = ?",
            (novo_status, self.id)
        )
        conn.commit()
        self.status = novo_status
    
    def atualizar(self, conn: sqlite3.Connection, **campos) -> None:
        """
        Atualiza campos do plano de ação.
        
        Args:
            conn: Conexão SQLite
            **campos: Campos a atualizar (objetivo, data_limite, observacoes)
        
        Raises:
            ValueError: Se o plano já está concluído ou cancelado
        """
        if self.status in ['concluido', 'cancelado']:
            raise ValueError(f"Não é possível atualizar um plano {self.status}.")
        
        # Validações
        if 'objetivo' in campos:
            campos['objetivo'] = self._validate_not_empty(campos['objetivo'], "Objetivo")
        
        if 'data_limite' in campos:
            if not isinstance(campos['data_limite'], datetime):
                raise ValueError("Data limite deve ser um objeto datetime.")
            if campos['data_limite'] < self.data_criacao:
                raise ValueError("Data limite não pode ser anterior à data de criação.")
            campos['data_limite'] = campos['data_limite'].isoformat()
        
        # Monta query dinamicamente
        sets = ', '.join(f"{campo} = ?" for campo in campos.keys())
        valores = list(campos.values()) + [self.id]
        
        conn.execute(
            f"UPDATE planos_acao SET {sets} WHERE id = ?",
            valores
        )
        conn.commit()
        
        # Atualiza instância local
        for campo, valor in campos.items():
            if campo == 'data_limite' and isinstance(valor, str):
                valor = datetime.fromisoformat(valor)
            setattr(self, campo, valor)
    
    def deletar(self, conn: sqlite3.Connection) -> None:
        """
        Deleta o plano de ação do banco de dados.
        Os materiais associados são removidos automaticamente (CASCADE).
        """
        conn.execute("DELETE FROM planos_acao WHERE id = ?", (self.id,))
        conn.commit()
    
    def esta_vencido(self) -> bool:
        """Verifica se o prazo do plano já passou."""
        return datetime.now() > self.data_limite and self.status not in ['concluido', 'cancelado']
