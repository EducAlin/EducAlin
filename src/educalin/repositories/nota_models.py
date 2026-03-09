"""
Modelo de Nota - Classe de Associação entre Aluno e Avaliação.

NotaModel representa a nota de um aluno em uma avaliação específica.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime
from .base_model import BaseModel
from .exceptions import NotaDuplicadaError


class NotaModel(BaseModel):
    """
    Modelo de Nota - Associação entre Aluno e Avaliação.

    Relacionamentos:
    - aluno_id -> usuarios(id) onde tipo_usuario='aluno'
    - avaliacao_id -> avaliacoes(id)

    Esta é uma classe de associação que armazena a relação many-to-many
    entre alunos e avaliações, com o atributo adicional 'valor'.
    """

    def __init__(
        self,
        id: int,
        aluno_id: int,
        avaliacao_id: int,
        valor: float,
        data_registro: Optional[datetime] = None,
    ):
        self.id = id
        self.aluno_id = aluno_id
        self.avaliacao_id = avaliacao_id
        self.valor = valor
        self.data_registro = data_registro or datetime.now()

    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        aluno_id: int,
        avaliacao_id: int,
        valor: float,
    ) -> int:
        """
        Cria uma nova nota.

        Args:
            conn: Conexão SQLite
            aluno_id: ID do aluno
            avaliacao_id: ID da avaliação
            valor: Valor numérico da nota

        Returns:
            int: ID da nota criada

        Raises:
            ValueError: Se os dados forem inválidos
            sqlite3.IntegrityError: Se já existe nota para este aluno nesta avaliação
        """
        # Validações
        if not isinstance(valor, (int, float)):
            raise ValueError("Valor da nota deve ser um número.")

        if valor < 0:
            raise ValueError("Valor da nota não pode ser negativo.")

        # Verificar se a avaliação existe e obter valor_maximo
        cursor = conn.execute(
            "SELECT valor_maximo FROM avaliacoes WHERE id = ?",
            (avaliacao_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Avaliação com id {avaliacao_id} não existe.")

        valor_maximo = row['valor_maximo']
        if valor > valor_maximo:
            raise ValueError(f"Valor da nota ({valor}) não pode ser maior que o valor máximo da avaliação ({valor_maximo}).")

        # Verificar se o aluno existe
        cursor = conn.execute(
            "SELECT id FROM usuarios WHERE id = ? AND tipo_usuario = 'aluno'",
            (aluno_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Aluno com id {aluno_id} não existe.")

        try:
            cursor = conn.execute(
                """
                INSERT INTO notas (aluno_id, avaliacao_id, valor)
                VALUES (?, ?, ?)
                """,
                (aluno_id, avaliacao_id, valor)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise NotaDuplicadaError(
                f"Já existe nota para o aluno {aluno_id} na avaliação {avaliacao_id}."
            )

    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, nota_id: int) -> Optional['NotaModel']:
        """Busca nota por ID."""
        cursor = conn.execute(
            "SELECT * FROM notas WHERE id = ?",
            (nota_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return cls(
            id=row['id'],
            aluno_id=row['aluno_id'],
            avaliacao_id=row['avaliacao_id'],
            valor=row['valor'],
            data_registro=datetime.fromisoformat(row['data_registro'])
        )

    @classmethod
    def buscar_por_aluno_avaliacao(
        cls,
        conn: sqlite3.Connection,
        aluno_id: int,
        avaliacao_id: int
    ) -> Optional['NotaModel']:
        """Busca nota específica de um aluno em uma avaliação."""
        cursor = conn.execute(
            "SELECT * FROM notas WHERE aluno_id = ? AND avaliacao_id = ?",
            (aluno_id, avaliacao_id)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return cls(
            id=row['id'],
            aluno_id=row['aluno_id'],
            avaliacao_id=row['avaliacao_id'],
            valor=row['valor'],
            data_registro=datetime.fromisoformat(row['data_registro'])
        )

    @classmethod
    def listar_por_aluno(cls, conn: sqlite3.Connection, aluno_id: int) -> List['NotaModel']:
        """Lista todas as notas de um aluno."""
        cursor = conn.execute(
            """
            SELECT n.*
            FROM notas n
            JOIN avaliacoes a ON n.avaliacao_id = a.id
            WHERE n.aluno_id = ?
            ORDER BY a.data DESC
            """,
            (aluno_id,)
        )

        notas = []
        for row in cursor.fetchall():
            notas.append(cls(
                id=row['id'],
                aluno_id=row['aluno_id'],
                avaliacao_id=row['avaliacao_id'],
                valor=row['valor'],
                data_registro=datetime.fromisoformat(row['data_registro'])
            ))
        return notas

    @classmethod
    def listar_por_avaliacao(cls, conn: sqlite3.Connection, avaliacao_id: int) -> List['NotaModel']:
        """Lista todas as notas de uma avaliação."""
        cursor = conn.execute(
            """
            SELECT n.*
            FROM notas n
            JOIN usuarios u ON n.aluno_id = u.id
            WHERE n.avaliacao_id = ?
            ORDER BY u.nome
            """,
            (avaliacao_id,)
        )

        notas = []
        for row in cursor.fetchall():
            notas.append(cls(
                id=row['id'],
                aluno_id=row['aluno_id'],
                avaliacao_id=row['avaliacao_id'],
                valor=row['valor'],
                data_registro=datetime.fromisoformat(row['data_registro'])
            ))
        return notas

    def atualizar_valor(self, conn: sqlite3.Connection, novo_valor: float) -> None:
        """
        Atualiza o valor da nota.

        Args:
            conn: Conexão SQLite
            novo_valor: Novo valor da nota

        Raises:
            ValueError: Se o novo valor for inválido
        """
        # Validações
        if not isinstance(novo_valor, (int, float)):
            raise ValueError("Valor da nota deve ser um número.")

        if novo_valor < 0:
            raise ValueError("Valor da nota não pode ser negativo.")

        # Verificar valor_maximo da avaliação
        cursor = conn.execute(
            "SELECT valor_maximo FROM avaliacoes WHERE id = ?",
            (self.avaliacao_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError("Avaliação não encontrada.")

        valor_maximo = row['valor_maximo']
        if novo_valor > valor_maximo:
            raise ValueError(f"Valor da nota ({novo_valor}) não pode ser maior que o valor máximo da avaliação ({valor_maximo}).")

        conn.execute(
            "UPDATE notas SET valor = ? WHERE id = ?",
            (novo_valor, self.id)
        )
        conn.commit()
        self.valor = novo_valor

    def deletar(self, conn: sqlite3.Connection) -> None:
        """Deleta a nota do banco de dados."""
        conn.execute("DELETE FROM notas WHERE id = ?", (self.id,))
        conn.commit()

    def calcular_percentual(self, conn: sqlite3.Connection) -> float:
        """
        Calcula o percentual da nota em relação ao valor máximo da avaliação.

        Returns:
            float: Percentual entre 0 e 100
        """
        cursor = conn.execute(
            "SELECT valor_maximo FROM avaliacoes WHERE id = ?",
            (self.avaliacao_id,)
        )
        row = cursor.fetchone()
        if not row or row['valor_maximo'] == 0:
            return 0.0

        return (self.valor / row['valor_maximo']) * 100
