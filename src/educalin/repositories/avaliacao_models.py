"""
Modelo de Avaliação com relacionamentos.

AvaliacaoModel representa uma avaliação (prova, trabalho, etc) de uma turma.
"""

import sqlite3
from typing import Optional, List
from datetime import date, datetime
from .base_model import BaseModel


class AvaliacaoModel(BaseModel):
    """
    Modelo de Avaliação.

    Relacionamentos:
    - turma_id -> turmas(id)
    - Relacionamento 1:N com NotaModel
    """

    def __init__(
        self,
        id: int,
        titulo: str,
        data: date,
        valor_maximo: float,
        peso: float,
        turma_id: int,
        topico = None,
        criada_em: Optional[datetime] = None,
    ):
        self.id = id
        self.titulo = titulo
        self.data = data
        self.valor_maximo = valor_maximo
        self.peso = peso
        self.turma_id = turma_id
        self.topico = topico
        self.criada_em = criada_em or datetime.now()

    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        titulo: str,
        data: date,
        valor_maximo: float,
        peso: float,
        turma_id: int,
        topico = None
    ) -> int:
        """
        Cria uma nova avaliação.

        Args:
            conn: Conexão SQLite
            titulo: Título da avaliação
            data: Data de realização
            valor_maximo: Valor máximo da avaliação
            peso: Peso da avaliação (0 a 1)
            turma_id: ID da turma
            topico: Tópico da avaliação (opcional)

        Returns:
            int: ID da avaliação criada

        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Validações
        titulo = cls._validate_not_empty(titulo, "Título")

        if not isinstance(data, date):
            raise ValueError("Data deve ser um objeto date.")

        if not isinstance(valor_maximo, (int, float)) or valor_maximo <= 0:
            raise ValueError("Valor máximo deve ser um número positivo.")

        if not isinstance(peso, (int, float)) or not (0 <= peso <= 1):
            raise ValueError("Peso deve estar no intervalo de 0 a 1.")

        cursor = conn.execute(
            """
            INSERT INTO avaliacoes (titulo, data, valor_maximo, peso, turma_id, topico)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (titulo, data.isoformat(), valor_maximo, peso, turma_id, topico)
        )
        conn.commit()
        return cursor.lastrowid

    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, avaliacao_id: int) -> Optional['AvaliacaoModel']:
        """Busca avaliação por ID."""
        cursor = conn.execute(
            "SELECT * FROM avaliacoes WHERE id = ?",
            (avaliacao_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return cls(
            id=row['id'],
            titulo=row['titulo'],
            data=date.fromisoformat(row['data']),
            valor_maximo=row['valor_maximo'],
            peso=row['peso'],
            turma_id=row['turma_id'],
            topico=row['topico'],
            criada_em=datetime.fromisoformat(row['criada_em'])
        )

    @classmethod
    def listar_por_turma(cls, conn: sqlite3.Connection, turma_id: int) -> List['AvaliacaoModel']:
        """Lista todas as avaliações de uma turma."""
        cursor = conn.execute(
            "SELECT * FROM avaliacoes WHERE turma_id = ? ORDER BY data DESC",
            (turma_id,)
        )

        avaliacoes = []
        for row in cursor.fetchall():
            avaliacoes.append(cls(
                id=row['id'],
                titulo=row['titulo'],
                data=date.fromisoformat(row['data']),
                valor_maximo=row['valor_maximo'],
                peso=row['peso'],
                turma_id=row['turma_id'],
                criada_em=datetime.fromisoformat(row['criada_em'])
            ))
        return avaliacoes

    def atualizar(self, conn: sqlite3.Connection, **campos) -> None:
        """
        Atualiza campos da avaliação.

        Args:
            conn: Conexão SQLite
            **campos: Campos a atualizar (titulo, data, valor_maximo, peso)
        """
        # Validações
        if 'titulo' in campos:
            campos['titulo'] = self._validate_not_empty(campos['titulo'], "Título")

        if 'data' in campos:
            if not isinstance(campos['data'], date):
                raise ValueError("Data deve ser um objeto date.")
            campos['data'] = campos['data'].isoformat()

        if 'valor_maximo' in campos:
            if not isinstance(campos['valor_maximo'], (int, float)) or campos['valor_maximo'] <= 0:
                raise ValueError("Valor máximo deve ser um número positivo.")

        if 'peso' in campos:
            if not isinstance(campos['peso'], (int, float)) or not (0 <= campos['peso'] <= 1):
                raise ValueError("Peso deve estar no intervalo de 0 a 1.")

        # Monta query dinamicamente
        sets = ', '.join(f"{campo} = ?" for campo in campos.keys())
        valores = list(campos.values()) + [self.id]

        conn.execute(
            f"UPDATE avaliacoes SET {sets} WHERE id = ?",
            valores
        )
        conn.commit()

        # Atualiza instância local
        for campo, valor in campos.items():
            if campo == 'data' and isinstance(valor, str):
                valor = date.fromisoformat(valor)
            setattr(self, campo, valor)

    def deletar(self, conn: sqlite3.Connection) -> None:
        """Deleta a avaliação do banco de dados."""
        conn.execute("DELETE FROM avaliacoes WHERE id = ?", (self.id,))
        conn.commit()

    def calcular_media_turma(self, conn: sqlite3.Connection) -> Optional[float]:
        """Calcula a média da turma nesta avaliação."""
        cursor = conn.execute(
            """
            SELECT AVG(valor) as media
            FROM notas
            WHERE avaliacao_id = ?
            """,
            (self.id,)
        )
        row = cursor.fetchone()
        return row['media'] if row['media'] is not None else None
