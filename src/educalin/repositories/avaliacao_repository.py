"""
Repository para operações com Avaliações e Notas.

Orquestra criação de avaliações, registro de notas e consultas
agregadas, delegando SQL aos modelos AvaliacaoModel e NotaModel.
"""

from __future__ import annotations

import sqlite3
from datetime import date

from .avaliacao_models import AvaliacaoModel
from .nota_models import NotaModel


class AvaliacaoRepository:
    """
    Repository para CRUD de avaliação e notas de turmas.

    Coordena as operações entre AvaliacaoModel e NotaModel,
    aplicando validações de entrada e expondo uma interface
    orientada a casos de uso - não a tabelas.

    Attributes:
        _conn (sqlite3.Connection): Conexão ativa com o banco de dados.
    
    Examples:
        >>> from educalin.repositories import get_connection
        >>> from educalin.repositories.avaliacao_repository import AvaliacaoRepository
        >>> repo = AvaliacaoRepository(get_connection())
        >>> av_id = repo.criar_avaliacao({
        ...     'titulo': 'Prova 1', 'data': date.today(),
        ...     'valor_maximo': 10.0, 'peso': 0.4, 'turma_id': 1,
        ... })
    """

    def __init__(self, conn: sqlite3.Connection):
        """
        Inicializa o repositório com uma conexão SQLite.

        Args:
            conn: Conexão SQLite ativa. Se ``row_factory`` for ``None``,
                será configurado automaticamente para ``sqlite3.Row``.
                Recomenda-se também ``PRAGMA foreign_keys = ON``.

        Raises:
            TypeError: Se ``conn`` não for uma instância ``sqlite3.Connection``
                ou se ``conn.row_factory`` estiver configurado para um valor
                diferente de ``sqlite3.Row``.
        """
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("conn deve ser uma instância de sqlite3.Connection")

        if conn.row_factory is None:
            conn.row_factory = sqlite3.Row
        elif conn.row_factory is not sqlite3.Row:
            raise TypeError(
                "conn.row_factory deve ser sqlite3.Row para uso com AvaliacaoRepository"
            )

        self._conn = conn

    # Interface pública

    def criar_avaliacao(self, avaliacao_data: dict) -> int:
        """
        Cria uma nova avaliação a partir de um dicionário de dados.

        Args:
            avaliacao_data: Campos obrigatórios: ``titulo`` (str),
                ``data`` (``datetime.date``), ``valor_maximo`` (float > 0),
                ``peso`` (float entre 0 e 1), ``turma_id`` (int).
                Campo opcional: ``topico`` (str).

        Returns:
            ID (int) da avaliação criada.

        Raises:
            ValueError: Se os campos obrigatórios estiverem ausentes, inválidos,
                ou se a turma referência não existir.
            TypeError: Se ``data`` não for um objeto ``datetime.date``.

        Examples:
            >>> av_id = repo.criar_avaliacao({
            ...     'titulo': 'Prova 1', 'data': date(2026, 2, 10),
            ...     'valor_maximo': 10.0, 'peso': 0.4, 'turma_id': 1,
            ... })
        """
        self._validar_avaliacao_data(avaliacao_data)
        self._garantir_turma_existe(avaliacao_data['turma_id'])

        return AvaliacaoModel.criar(
            conn=self._conn,
            titulo=avaliacao_data['titulo'],
            data=avaliacao_data['data'],
            valor_maximo=avaliacao_data['valor_maximo'],
            peso=avaliacao_data['peso'],
            turma_id=avaliacao_data['turma_id'],
            topico=avaliacao_data.get('topico'),
        )

    def registrar_nota(self, nota_data: dict) -> int:
        """
        Registra a nota de um aluno em uma avaliação.

        Args:
            nota_data: Campos obrigatórios: ``aluno_id`` (int),
                ``avaliacao_id`` (int), ``valor`` (float >= 0).

        Returns:
            ID (int) da nota criada.

        Raises:
            ValueError: Se campos obrigatórios estiverem ausentes, se o valor
                for negativo ou superior ao ``valor_maximo`` da avaliação,
                se o aluno ou a avaliação não existirem, ou se já existir
                nota para este aluno nesta avaliação.

        Examples:
            >>> nota_id = repo.registrar_nota({
            ...     'aluno_id': 5, 'avaliacao_id': 2, 'valor': 8.5,
            ... })
        """
        self._validar_nota_data(nota_data)

        return NotaModel.criar(
            conn=self._conn,
            aluno_id=nota_data['aluno_id'],
            avaliacao_id=nota_data['avaliacao_id'],
            valor=nota_data['valor']
        )

    def buscar_notas_aluno(self, aluno_id: int, turma_id: int) -> list[dict]:
        """
        Retorna todas as notas de um aluno nas avaliações de uma turma.

        A consulta cruza ``notas`` com ``avaliacoes`` para filtrar apenas
        avaliações que pertencem à turma especificada.

        Args:
            aluno_id: ID do aluno.
            turma_id: ID da turma cujas avaliações serão consideradas.

        Returns:
            Lista de dicts com campos ``id``, ``aluno_id``,
            ``avaliacao_id``, ``valor`` e ``data_registro``.
            Lista vazia se o aluno ou turma não existirem ou não houver notas.

        Examples:
            >>> notas = repo.buscar_notas_aluno(aluno_id=5, turma_id=1)
            >>> [n['valor'] for n in notas]
            [7.5, 8.0]
        """
        cursor = self._conn.execute(
            """
            SELECT n.id, n.aluno_id, n.avaliacao_id, n.valor, n.data_registro
            FROM notas n
            JOIN avaliacoes a ON n.avaliacao_id = a.id
            WHERE n.aluno_id = ?
              AND a.turma_id = ?
            ORDER BY a.data ASC
            """,
            (aluno_id, turma_id)
        )
        return [dict(row) for row in cursor.fetchall()]

    def buscar_notas_turma(self, turma_id: int) -> list[dict]:
        """
        Retorna todas as notas registradas nas avaliações de uma turma.

        Útil para geração de relatórios consolidados (ex.: RelatorioTurma).

        Args:
            turma_id: ID da turma.

        Returns:
            Lista de dicts com campos ``id``, ``aluno_id``,
            ``avaliacao_id``, ``valor`` e ``data_registro``,
            ordenados por avaliação e nome do aluno.
            Lista vazia se a turma não existir ou não houver notas.

        Examples:
            >>> notas = repo.buscar_notas_turma(turma_id=1)
            >>> len(notas)
            12
        """
        cursor = self._conn.execute(
            """
            SELECT n.id, n.aluno_id, n.avaliacao_id, n.valor, n.data_registro
            FROM notas n
            JOIN avaliacoes a ON n.avaliacao_id = a.id
            JOIN usuarios u ON n.aluno_id = u.id
            WHERE a.turma_id = ?
            ORDER BY a.data ASC, u.nome ASC
            """,
            (turma_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def calcular_media_aluno(
        self,
        aluno_id: int,
        turma_id: int,
        topico: str | None = None,
    ) -> float | None:
        """
        Calcula a média das notas de um aluno em uma turma.

        Quando ``topico`` é informado, considera apenas avaliações
        cujo campo ``topico`` corresponde exatamente ao valor passado.
        Quando omitido, considera todas as avaliações da turma.

        A média é simples (aritmética), sem ponderação de peso.

        Args:
            aluno_id: ID do aluno.
            turma_id: ID da turma.
            topico: Tópico específico para filtrar avaliações (opcional).

        Returns:
            Média aritmética (float) arredondada em 2 casas decimais,
            ou ``None`` se o aluno não tiver notas no filtro especificado.

        Examples:
            >>> repo.calcular_media_aluno(aluno_id=5, turma_id=1)
            7.75 
            >>> repo.calcular_media_aluno(aluno_id=5, turma_id=1, topico='heranca')
            9.0
        """
        cursor = self._conn.execute(
            """
            SELECT AVG(n.valor) as media
            FROM notas n
            JOIN avaliacoes a ON n.avaliacao_id = a.id
            WHERE n.aluno_id = ?
              AND a.turma_id = ?
              AND (? IS NULL OR a.topico = ?)
            """,
            (aluno_id, turma_id, topico, topico),
        )

        row = cursor.fetchone()
        if row is None or row['media'] is None:
            return None
        return round(float(row['media']), 2)

    # Métodos auxiliares privados

    def _validar_avaliacao_data(self, avaliacao_data: dict) -> None:
        """
        Valida os campos obrigatórios do dicionário de avaliação.

        Raises:
            ValueError: Se algum campo obrigatório estiver ausente, vazio
                ou com valor fora dos limites esperados.
            TypeError: Se ``data`` não for ``datetime.date``.
        """
        campos_obrigatorios = ('titulo', 'data', 'valor_maximo', 'peso', 'turma_id')
        for campo in campos_obrigatorios:
            if campo not in avaliacao_data or avaliacao_data[campo] is None:
                raise ValueError(f"Campo obrigatório ausente: '{campo}'")

        titulo = avaliacao_data['titulo']
        if not isinstance(titulo, str) or not titulo.strip():
            raise ValueError("Título não pode ser vazio")

        if not isinstance(avaliacao_data['data'], date):
            raise TypeError("'data' deve ser um objeto datetime.date")

        valor_maximo = avaliacao_data['valor_maximo']
        if not isinstance(valor_maximo, (int, float)) or valor_maximo <= 0:
            raise ValueError("'valor_maximo' deve ser um número positivo")

        peso = avaliacao_data['peso']
        if not isinstance(peso, (int, float)) or not (0 <= peso <= 1):
            raise ValueError("'peso' deve estar no intervalo [0, 1]")

        turma_id = avaliacao_data['turma_id']
        if not isinstance(turma_id, int) or turma_id <= 0:
            raise ValueError("'turma_id' deve ser um inteiro positivo")

        if 'topico' in avaliacao_data:
            topico = avaliacao_data['topico']
            if topico is not None:
                if not isinstance(topico, str) or not topico.strip():
                    raise ValueError("'topico' deve ser uma string não-vazia ou None")
                avaliacao_data['topico'] = topico.strip()

    def _validar_nota_data(self, nota_data: dict) -> None:
        """
        Valida os campos obrigatórios do dicionário de nota.

        Raises:
            ValueError: Se algum campo obrigatório estiver ausente ou inválido,
                se ``valor`` for negativo, ou se ``aluno_id``/``avaliacao_id``
                não forem inteiros positivos.
        """
        for campo in ('aluno_id', 'avaliacao_id', 'valor'):
            if campo not in nota_data or nota_data[campo] is None:
                raise ValueError(f"Campo obrigatório ausente: '{campo}'")

        for campo in ('aluno_id', 'avaliacao_id'):
            val = nota_data[campo]
            if not isinstance(val, int) or val <= 0:
                raise ValueError(f"'{campo}' deve ser um inteiro positivo")

        valor = nota_data['valor']
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("'valor' deve ser um número não-negativo")

    def _garantir_turma_existe(self, turma_id: int) -> None:
        """
        Verifica se a turma existe, lançando ValueError se não.

        Raises:
            ValueError: Se a turma não for encontrada.
        """
        cursor = self._conn.execute(
            "SELECT id FROM turmas WHERE id = ?", (turma_id,)
        )
        if cursor.fetchone() is None:
            raise ValueError(f"Turma com id {turma_id} não encontrada")
