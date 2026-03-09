"""
Modelo de Turma com relacionamentos Many-to-Many para alunos.

TurmaModel gerencia turmas escolares com:
- Relacionamento N:1 com Professor (usuario)
- Relacionamento N:N com Alunos (usuarios) via tabela intermediária
"""

import sqlite3
from typing import Optional, List, Dict
from datetime import datetime


class TurmaModel:
    """
    Modelo de Turma escolar com relacionamentos.

    Relacionamentos:
    - professor_id -> usuarios(id) onde tipo_usuario='professor'
    - alunos -> N:N via tabela turma_alunos
    """

    def __init__(
        self,
        id: int,
        codigo: str,
        disciplina: str,
        semestre: str,
        professor_id: Optional[int] = None,
        data_criacao: Optional[datetime] = None,
    ):
        self.id = id
        self.codigo = codigo
        self.disciplina = disciplina
        self.semestre = semestre
        self.professor_id = professor_id
        self.data_criacao = data_criacao or datetime.now()
        self._conn: Optional[sqlite3.Connection] = None

    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        codigo: str,
        disciplina: str,
        semestre: str,
        professor_id: Optional[int] = None,
    ) -> int:
        """
        Cria uma nova turma.

        Args:
            conn: Conexão SQLite
            codigo: Código único da turma (ex: "POO-2026.1")
            disciplina: Nome da disciplina
            semestre: Período letivo (ex: "2026.1")
            professor_id: ID do professor responsável (opcional)

        Returns:
            ID da turma criada

        Raises:
            ValueError: Se campos obrigatórios estiverem vazios
            sqlite3.IntegrityError: Se código duplicado ou professor_id inválido
        """
        # Validações
        if not codigo or not codigo.strip():
            raise ValueError("Código da turma não pode ser vazio")
        if not disciplina or not disciplina.strip():
            raise ValueError("Disciplina não pode ser vazia")
        if not semestre or not semestre.strip():
            raise ValueError("Semestre não pode ser vazio")

        # Valida se professor existe (se fornecido)
        if professor_id:
            cursor = conn.execute(
                "SELECT id FROM usuarios WHERE id = ? AND tipo_usuario = 'professor'",
                (professor_id,)
            )
            if not cursor.fetchone():
                raise ValueError(f"Professor com ID {professor_id} não existe")

        cursor = conn.execute(
            """
            INSERT INTO turmas (codigo, disciplina, semestre, professor_id)
            VALUES (?, ?, ?, ?)
            """,
            (codigo.strip(), disciplina.strip(), semestre.strip(), professor_id)
        )
        conn.commit()
        return cursor.lastrowid

    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, turma_id: int) -> Optional['TurmaModel']:
        """Busca turma por ID."""
        cursor = conn.execute(
            "SELECT * FROM turmas WHERE id = ?",
            (turma_id,)
        )
        row = cursor.fetchone()
        return cls._from_row(row) if row else None

    @classmethod
    def buscar_por_codigo(cls, conn: sqlite3.Connection, codigo: str) -> Optional['TurmaModel']:
        """Busca turma por código."""
        cursor = conn.execute(
            "SELECT * FROM turmas WHERE codigo = ?",
            (codigo,)
        )
        row = cursor.fetchone()
        return cls._from_row(row) if row else None

    @classmethod
    def listar_todas(cls, conn: sqlite3.Connection, professor_id: Optional[int] = None) -> List['TurmaModel']:
        """
        Lista todas as turmas, opcionalmente filtradas por professor.

        Args:
            conn: Conexão SQLite
            professor_id: Se fornecido, filtra turmas deste professor
        """
        if professor_id:
            cursor = conn.execute(
                "SELECT * FROM turmas WHERE professor_id = ? ORDER BY codigo",
                (professor_id,)
            )
        else:
            cursor = conn.execute("SELECT * FROM turmas ORDER BY codigo")

        return [cls._from_row(row) for row in cursor.fetchall()]

    @classmethod
    def _from_row(cls, row: sqlite3.Row) -> 'TurmaModel':
        """Converte Row do SQLite para TurmaModel."""
        return cls(
            id=row['id'],
            codigo=row['codigo'],
            disciplina=row['disciplina'],
            semestre=row['semestre'],
            professor_id=row['professor_id'],
            data_criacao=datetime.fromisoformat(row['data_criacao']) if row['data_criacao'] else None,
        )

    def atualizar(self, conn: sqlite3.Connection, **campos) -> None:
        """
        Atualiza campos da turma.

        Args:
            **campos: Campos a atualizar (disciplina, semestre, professor_id)
        """
        if not campos:
            return

        # Validações
        if 'codigo' in campos:
            raise ValueError("Código da turma não pode ser alterado")

        if 'professor_id' in campos and campos['professor_id']:
            cursor = conn.execute(
                "SELECT id FROM usuarios WHERE id = ? AND tipo_usuario = 'professor'",
                (campos['professor_id'],)
            )
            if not cursor.fetchone():
                raise ValueError(f"Professor com ID {campos['professor_id']} não existe")

        sets = ', '.join(f"{campo} = ?" for campo in campos.keys())
        valores = list(campos.values()) + [self.id]

        conn.execute(
            f"UPDATE turmas SET {sets} WHERE id = ?",
            valores
        )
        conn.commit()

        # Atualiza instância local
        for campo, valor in campos.items():
            setattr(self, campo, valor)

    def deletar(self, conn: sqlite3.Connection) -> None:
        """
        Remove turma do banco.

        Note: Alunos são removidos automaticamente via CASCADE em turma_alunos.
        """
        conn.execute("DELETE FROM turmas WHERE id = ?", (self.id,))
        conn.commit()

    # ==========================
    # Relacionamento Many-to-Many com Alunos
    # ==========================

    def adicionar_aluno(self, conn: sqlite3.Connection, aluno_id: int) -> bool:
        """
        Adiciona um aluno à turma (relacionamento N:N).

        Args:
            conn: Conexão SQLite
            aluno_id: ID do aluno (usuario com tipo_usuario='aluno')

        Returns:
            True se adicionado, False se já estava na turma

        Raises:
            ValueError: Se aluno_id não existe ou não é tipo 'aluno'
        """
        # Verifica se é um aluno válido
        cursor = conn.execute(
            "SELECT id FROM usuarios WHERE id = ? AND tipo_usuario = 'aluno'",
            (aluno_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Aluno com ID {aluno_id} não existe")

        # Verifica se já está matriculado
        cursor = conn.execute(
            "SELECT 1 FROM turma_alunos WHERE turma_id = ? AND aluno_id = ?",
            (self.id, aluno_id)
        )
        if cursor.fetchone():
            return False  # Já matriculado

        # Adiciona matrícula
        conn.execute(
            "INSERT INTO turma_alunos (turma_id, aluno_id) VALUES (?, ?)",
            (self.id, aluno_id)
        )
        conn.commit()
        return True

    def remover_aluno(self, conn: sqlite3.Connection, aluno_id: int) -> bool:
        """
        Remove um aluno da turma.

        Returns:
            True se removido, False se não estava na turma
        """
        cursor = conn.execute(
            "DELETE FROM turma_alunos WHERE turma_id = ? AND aluno_id = ?",
            (self.id, aluno_id)
        )
        conn.commit()
        return cursor.rowcount > 0

    def listar_alunos(self, conn: sqlite3.Connection) -> List[dict]:
        """
        Lista todos os alunos matriculados na turma.

        Returns:
            Lista de dicts com dados dos alunos e data de matrícula
        """
        cursor = conn.execute(
            """
            SELECT
                u.id, u.nome, u.email, u.matricula,
                ta.data_matricula
            FROM turma_alunos ta
            JOIN usuarios u ON ta.aluno_id = u.id
            WHERE ta.turma_id = ?
            ORDER BY u.nome
            """,
            (self.id,)
        )

        return [dict(row) for row in cursor.fetchall()]

    def contar_alunos(self, conn: sqlite3.Connection) -> int:
        """Retorna o número de alunos matriculados na turma."""
        cursor = conn.execute(
            "SELECT COUNT(*) as total FROM turma_alunos WHERE turma_id = ?",
            (self.id,)
        )
        return cursor.fetchone()['total']

    # Interface de injeção de conexão

    def conectar(self, conn: sqlite3.Connection) -> "TurmaModel":
        """
        Injeta a conexão SQLite necessária para operações que dependem
        do banco (``alunos``, ``obter_desempenho_geral``).

        Método público que substitui o acesso direto ao atributo privado
        ``_conn`` a partir de camadas externas.

        Args:
            conn: Conexão SQLite ativa.

        Returns:
            A própria instância (fluent interface), permitindo encadeamento:
            ``RelatorioTurma(turma.conectar(conn))``.

        Examples:
            >>> relatorio = RelatorioTurma(turma.conectar(conn))
            >>> conteudo = relatorio.gerar()
        """
        self._conn = conn
        return self

    # Interface para RelatorioTurma (Template Method)

    @property
    def alunos(self) -> List['_AlunoProxy']:
        """
        Retorna lista de proxies de alunos para uso no RelatorioTurma.

        Cada item expõe ``nome``, ``matricula`` e ``calcular_media()``.
        Requer que ``self._conn`` esteja definido (injetado pelo endpoint).

        Returns:
            Lista de _AlunoProxy, vazia se _conn não estiver disponível.
        """
        if self._conn is None:
            return []
        cursor = self._conn.execute(
            """
            SELECT u.id, u.nome, u.matricula
            FROM turma_alunos ta
            JOIN usuarios u ON ta.aluno_id = u.id
            WHERE ta.turma_id = ?
            ORDER BY u.nome
            """,
            (self.id,),
        )
        return [
            _AlunoProxy(row['id'], row['nome'], row['matricula'], self.id, self._conn)
            for row in cursor.fetchall()
        ]

    def obter_desempenho_geral(self) -> Dict:
        """
        Calcula estatísticas gerais de desempenho da turma.

        Compatível com a interface esperada por RelatorioTurma.
        Requer que ``self._conn`` esteja definido.

        Returns:
            Dicionário com ``media_geral``, ``total_alunos`` e
            ``taxa_aprovacao``.
        """
        if self._conn is None:
            return {'media_geral': 0.0, 'total_alunos': 0, 'taxa_aprovacao': 0.0}

        alunos = self.alunos
        if not alunos:
            return {'media_geral': 0.0, 'total_alunos': 0, 'taxa_aprovacao': 0.0}

        medias = [a.calcular_media() for a in alunos]
        medias_validas = [m for m in medias if m is not None]

        if not medias_validas:
            return {
                'media_geral': 0.0,
                'total_alunos': len(alunos),
                'taxa_aprovacao': 0.0,
            }

        media_geral = sum(medias_validas) / len(medias_validas)
        aprovados = sum(1 for m in medias_validas if m >= 6.0)
        taxa_aprovacao = (aprovados / len(medias_validas)) * 100

        return {
            'media_geral': round(media_geral, 2),
            'total_alunos': len(alunos),
            'taxa_aprovacao': round(taxa_aprovacao, 2),
        }

    def __repr__(self) -> str:
        return f"<TurmaModel(id={self.id}, codigo='{self.codigo}', disciplina='{self.disciplina}')>"


class _AlunoProxy:
    """
    Proxy leve de aluno para uso exclusivo no RelatorioTurma.

    Expõe ``nome``, ``matricula`` e ``calcular_media()`` sem depender
    da classe de domínio ``Aluno``.
    """

    def __init__(
        self,
        aluno_id: int,
        nome: str,
        matricula: str,
        turma_id: int,
        conn: sqlite3.Connection,
    ):
        self.nome = nome
        self.matricula = matricula
        self._aluno_id = aluno_id
        self._turma_id = turma_id
        self._conn = conn

    def calcular_media(self) -> Optional[float]:
        """Calcula a média do aluno nas avaliações da turma."""
        cursor = self._conn.execute(
            """
            SELECT AVG(n.valor) AS media
            FROM notas n
            JOIN avaliacoes a ON n.avaliacao_id = a.id
            WHERE n.aluno_id = ? AND a.turma_id = ?
            """,
            (self._aluno_id, self._turma_id),
        )
        row = cursor.fetchone()
        if row is None or row['media'] is None:
            return 0.0
        return round(float(row['media']), 2)
