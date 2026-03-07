"""
Repository para operações com Turmas.

Orquestra o acesso a dados da entidade Turma, delegando
operações SQL ao TurmaModel (camada de modelo) e aplicando
validações de entrada e conversões necessárias.

Segue o padrão Repository: isola a lógica de acesso a dados
do restante da aplicação, facilitando testes e futuras trocas
de mecanismo de persistência
"""

from __future__ import annotations

import sqlite3
from typing import Optional

from .turma_models import TurmaModel


class TurmaRepository:
    """
    Repositório para operação CRUD de turmas e gestão de matrículas.

    Coordena criação, busca e manipulação de turmas e seus
    relacionamentos com alunos (N:N via tabela ``turma_alunos``).
    Toda lógica SQL é delegada a ``TurmaModel``; este repositório
    cuida de validações de entrada, tratamento de erros e conversão
    entre dicts (interface da API/serviços) e objetos de modelo.

    Attributes:
        _conn (sqlite3.Connection): Conexão ativa com o banco de dados.

    Examples:
        >>> from educalin.repositories import get_connection
        >>> from educalin.repositories.turma_repository import TurmaRepository
        >>> conn = get_connection()
        >>> repo = TurmaRepository(conn)
        >>> turma_id = repo.criar({'codigo': 'ES006', 'disciplina': 'POO', 'semestre': '2025.2'})
    """

    def __init__(self, conn: sqlite3.Connection):
        """
        Inicializa o repositório com uma conexão SQLite.

        Args:
            conn: Conexão SQLite ativa. Deve ter ``row_factory = sqlite3.Row``
                e ``PRAGMA foreign_keys = ON`` habilitado para garantir 
                integridade referencial e acesso por nome de coluna.

        Raises:
            TypeError: Se ``conn`` não for uma instância de ``sqlite3.Connection``.
        """
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("conn deve ser uma instância sqlite3.Connection")
        self._conn = conn

    # Interface pública

    def criar(self, turma_data: dict) -> int:
        """
        Cria uma nova turma a partir de um dicionário de dados.

        Valida os campos obrigatórios antes de delegar a persistência
        ao ``TurmaModel``. A chave ``professor_id`` é opcional; se ausente
        ou ``None``, a turma é criada sem professor responsável.

        Args:
            turma_data: Dicionário com os campos da turma. Campos
                obrigatórios: ``'codigo'``, ``'disciplina'``, ``'semestre'``.
                Campo opcional: ``'professor_id'`` (int).

        Returns:
            ID (int) da turma recém-criada.

        Raises:
            ValueError: Se algum campo obrigatório estiver ausente ou vazio,
                ou se ``'professor_id'`` não corresponder a um professor existente.

        Examples:
            >>> turma_id = repo.criar({
            ...     'codigo': 'ES006',
            ...     'disciplina': 'Programação Orientada a Objetos',
            ...     'semestre': '2025.2',
            ...     'professor_id': 1,
            ... })
        """
        self._validar_campos_obrigatorios(turma_data)

        try:
            return TurmaModel.criar(
                conn=self._conn,
                codigo=turma_data['codigo'],
                disciplina=turma_data['disciplina'],
                semestre=turma_data['semestre'],
                professor_id=turma_data.get('professor_id'),
            )
        except sqlite3.IntegrityError as exc:
            # Normaliza erros de integridade do banco em ValueError,
            # conforme contrato deste repositório.
            msg = str(exc)
            if "UNIQUE" in msg.upper():
                raise ValueError(
                    "Já existe uma turma com o mesmo código ou combinação de dados fornecida."
                ) from exc
            raise ValueError(
                "Não foi possível criar a turma devido a uma violação de integridade no banco de dados."
            ) from exc

    def buscar_por_id(self, turma_id: int) -> Optional[TurmaModel]:
        """
        Busca uma turma pelo seu ID.

        Args:
            turma_id: Identificador da turma
        
        Returns:
            Instância de ``TurmaModel`` se encontrado, ``None`` caso contrário

        Examples:
            >>> turma = repo.buscar_por_id(1)
            >>> turma.codigo
            'ES006'
        """
        return TurmaModel.buscar_por_id(self._conn, turma_id)

    def listar_por_professor(self, professor_id: int) -> list[TurmaModel]:
        """
        Lista todas as turmas associadas a um professor.

        Se o professor não existir ou não tiver turmas, retorna lista vazia
        sem lançar erro - comportamento adequado para consulta de listagem.

        Args:
            professor_id: ID do professor cujas turmas devem ser listadas
        
        Returns:
            Lista de instâncias de ``TurmaModel``, possivelmente vazia.
            As turmas são ordenadas por código (ordem do modelo).

        Examples:
            >>> turmas = repo.listar_por_professor(1)
            >>> [t.codigo for t in turmas]
            ['ES003', 'ES006']
        """
        if not isinstance(professor_id, int) or professor_id <= 0:
            return []
        return TurmaModel.listar_todas(self._conn, professor_id=professor_id)

    def adicionar_aluno(self, turma_id: int, aluno_id: int) -> bool:
        """
        Matricula um aluno em uma turma (relacionamento N:N).

        Verifica a existência da turma antes de delegar ao modelo,
        lançando ``ValueError`` com mensagem clara se não encontrada.
        A verificação de existência e tipo do aluno é realizada por
        ``TurmaModel.adicionar_aluno()``, que consulta a tabela de
        usuários e lança ``ValueError`` se o ``aluno_id`` não for válido.

        Args:
            turma_id: ID da turma onde o aluno será matriculado.
            aluno_id: ID do aluno (deve existir na tabela ``usuarios``
                com ``tipo_usuario = 'aluno'``).

        Returns:
            ``True`` se o aluno já foi matriculado com sucesso.
            ``False`` se o aluno já estava matriculado nesta turma.

        Raises:
            ValueError: Se ``turma_id`` não corresponder a uma turma existente,
                 ou se ``aluno_id`` não corresponder a um aluno válido.

        Examples:
            >>> repo.adicionar_aluno(turma_id=1, aluno_id=5)
            True
            >>> repo.adicionar_aluno(turma_id=1, aluno_id=5)
            False
        """
        turma = self._garantir_turma_existe(turma_id)
        return turma.adicionar_aluno(self._conn, aluno_id)

    def remover_aluno(self, turma_id: int, aluno_id: int) -> bool:
        """
        Remove a matrícula de um aluno em uma turma.

        Se a turma não existir, retorna ``False`` sem lançar erro -
        o estado desejado (aluno não matriculado) já está satisfeito.
        O mesmo vale se o aluno não estiver matriculado.

        Args:
            turma_id: ID da turma
            aluno_id: ID do aluno a ser removido.

        Returns:
            ``True`` se a matrícula foi removida
            ``False`` se o aluno não estava matriculado ou a turma não existe

        Examples:
            >>> repo.remover_aluno(turma_id=1, aluno_id=5)
            True
            >>> repo.remover_aluno(turma_id=1, aluno_id=5)
            False
        """
        turma = TurmaModel.buscar_por_id(self._conn, turma_id)
        if turma is None:
            return False
        return turma.remover_aluno(self._conn, aluno_id)

    def listar_alunos(self, turma_id: int) -> list[dict]:
        """
        Lista todos os alunos matriculados em uma turma.

        Retorna lista vazia (sem erro) se a turma não existir, comportamento
        consistente com o princípio de que consultas de leitura não devem
        lançar erros por ausência de dados.

        Args:
            turma_id: ID da turma.

        Returns:
            Lista de dicts com dados dos alunos matriculados.
            Cada dict contém ao menos ``id``, ``nome``, ``email``,
            ``matricula`` e ``data_matricula``. Lista vazia se a turma
            não existir ou não tiver alunos.

        Examples:
            >>> alunos = repo.listar_alunos(1)
            >>> alunos[0]['nome']
            'Fulano de Tal'
        """
        turma = TurmaModel.buscar_por_id(self._conn, turma_id)
        if turma is None:
            return []
        return turma.listar_alunos(self._conn)


    # Métodos auxiliares privados

    def _validar_campos_obrigatorios(self, turma_data: dict) -> None:
        """
        Valida que os campos obrigatórios estão presentes e não-vazios.

        Args:
            turma_data: Dicionário de dados da turma a validar

        Raises:
            ValueError: Se algum campo obrigatório estiver ausente ou vazio
        """
        campos_obrigatorios = ('codigo', 'disciplina', 'semestre')
        for campo in campos_obrigatorios:
            valor = turma_data.get(campo)
            if not valor or not str(valor).strip():
                raise ValueError(f"Campo obrigatório ausente ou vazio: '{campo}'")

    def _garantir_turma_existe(self, turma_id: int) -> TurmaModel:
        """
        Busca uma turma e lança ValueError se não for encontrada.

        Usado em operações de escrita onde a ausência da turma é
        um erro de entrada, não um resultado esperado de consulta.

        Args:
            turma_id: ID da turma a verificar

        Returns:
            Instância de ``TurmaModel`` se existir

        Raises:
            ValueError: Se a turma não for encontrada
        """
        turma = TurmaModel.buscar_por_id(self._conn, turma_id)
        if turma is None:
            raise ValueError(f"Turma com id {turma_id} não encontrada")
        return turma
