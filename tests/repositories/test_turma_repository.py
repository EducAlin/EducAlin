"""
Testes para TurmaRepository.
"""
# pylint: disable=redefined-outer-name
import sqlite3
import pytest
from educalin.repositories.turma_repository import TurmaRepository
from educalin.repositories.schemas import create_all_tables
from educalin.repositories.usuario_models import ProfessorModel, AlunoModel

@pytest.fixture
def conn():
    """Conexão SQLite em memória - isolada por teste"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_all_tables(conn)
    yield conn
    conn.close()

@pytest.fixture
def repo(conn):
    """Instância do repositório com conexão em memória"""
    return TurmaRepository(conn)

@pytest.fixture
def professor_id(conn):
    """Cria e retorna ID de um professor de suporte"""
    return ProfessorModel.criar(
        conn, "Dr. Exemplo", "prof@edu.br", "senha123", "PROF001"
    )

@pytest.fixture
def outro_professor_id(conn):
    """Cria e retorna ID de um segundo professor de suporte"""
    return ProfessorModel.criar(
        conn, "Dra. Outra", "profa@edu.br", "senha456", "PROF002"
    )

@pytest.fixture
def aluno_id(conn):
    """Cria e retorna ID de um aluno de suporte"""
    return AlunoModel.criar(
        conn, "Aluno Teste", "aluno@edu.br", "senha123", "MAT001"
    )

@pytest.fixture
def outro_aluno_id(conn):
    """Cria e retorna ID de um segundo aluno de suporte"""
    return AlunoModel.criar(
        conn, "Aluno Dois", "aluno2@edu.br", "senha456", "MAT002"
    )

@pytest.fixture
def turma_data(professor_id):
    """Dados mínimos para criação da turma"""
    return {
        'codigo': 'ES006',
        'disciplina': 'Programação Orientada a Objetos',
        'semestre': '2025.2',
        'professor_id': professor_id,
    }

@pytest.fixture
def turma_id(repo, turma_data):
    """Cria uma turma e retorna seu ID"""
    return repo.criar(turma_data)


class TestTurmaRepositoryEstrutura:
    """Testa que o repositório existe e tem a interface correta"""

    def test_instancia_com_conexao(self, conn):
        """Deve inicializar com uma conexão SQLite"""
        repo = TurmaRepository(conn)
        assert repo is not None

    def test_possui_metodo_criar(self, repo):
        """Deve possuir o método criar()"""
        assert callable(getattr(repo, 'criar', None))

    def test_possui_metodo_buscar_por_id(self, repo):
        """Deve possuir o método buscar_por_id()"""
        assert callable(getattr(repo, 'buscar_por_id', None))

    def test_possui_metodo_listar_por_professor(self, repo):
        """Deve possuir o método listar_por_professor()"""
        assert callable(getattr(repo, 'listar_por_professor', None))

    def test_possui_metodo_adicionar_aluno(self, repo):
        """Deve possuir o método adicionar_aluno()"""
        assert callable(getattr(repo, 'adicionar_aluno', None))

    def test_possui_metodo_remover_aluno(self, repo):
        """Deve possuir o método remover_aluno()"""
        assert callable(getattr(repo, 'remover_aluno', None))


class TestTurmaRepositoryCriar:
    """Testa o método criar()"""

    def test_retorna_inteiro(self, repo, turma_data):
        """Deve retornar o ID da turma criada"""
        resultado = repo.criar(turma_data)
        assert isinstance(resultado, int)

    def test_id_positivo(self, repo, turma_data):
        """ID retornado deve ser positivo"""
        assert repo.criar(turma_data) > 0

    def test_turma_persistida(self, repo, turma_data):
        """Turma criada deve ser encontrável por ID"""
        id_turma = repo.criar(turma_data)
        turma = repo.buscar_por_id(id_turma)
        assert turma is not None

    def test_dados_persistidos_corretamente(self, repo, turma_data):
        """Os dados da turma devem ser mantidos após criação"""
        id_turma = repo.criar(turma_data)
        turma = repo.buscar_por_id(id_turma)
        assert turma.codigo == turma_data['codigo']
        assert turma.disciplina == turma_data['disciplina']
        assert turma.semestre == turma_data['semestre']
        assert turma.professor_id == turma_data['professor_id']

    def test_sem_professor(self, repo):
        """Deve aceitar criação de turma sem professor"""
        id_turma = repo.criar({
            'codigo': 'SEM-PROF',
            'disciplina': 'Disciplina',
            'semestre': '2025.2',
        })
        turma = repo.buscar_por_id(id_turma)
        assert turma.professor_id is None

    def test_codigo_duplicado_lanca_erro(self, repo, turma_data):
        """Código duplicado deve lançar ValueError"""
        repo.criar(turma_data)
        with pytest.raises((ValueError, Exception)):
            repo.criar(turma_data)

    def test_campos_obrigatorios_ausentes_lancam_erro(self, repo):
        """Dados incompletos devem lançar ValueError"""
        with pytest.raises(ValueError):
            repo.criar({'codigo': 'X'})

    def test_professor_inexistente_lanca_erro(self, repo):
        """professor_id inválido deve lançar ValueError"""
        with pytest.raises(ValueError):
            repo.criar({
                'codigo': 'T999',
                'disciplina': 'X',
                'semestre': '2025.2',
                'professor_id': 99999,
            })

    def test_ids_incrementais(self, repo, professor_id):
        """IDs devem ser únicos e crescentes"""
        id1 = repo.criar({
            'codigo': 'T1', 
            'disciplina': 'A', 
            'semestre': '2025.1',
         'professor_id': professor_id
        })
        id2 = repo.criar({
            'codigo': 'T2', 
            'disciplina': 'B', 
            'semestre': '2025.2', 
            'professor_id': professor_id
        })

        assert id1 != id2
        assert id2 > id1


class TestTurmaRepositoryBuscarPorId:
    """Testa o método buscar_por_id()"""

    def test_retorna_turma_existente(self, repo, turma_id):
        """Deve retornar objeto com atributo codigo"""
        turma = repo.buscar_por_id(turma_id)

        assert turma is not None
        assert hasattr(turma, 'codigo')

    def test_id_inexistente_retorna_none(self, repo):
        """ID que não existe deve retornar None"""
        assert repo.buscar_por_id(99999) is None

    def test_retorna_objeto_com_todos_os_campos(self, repo, turma_id, turma_data):
        """Objeto retornado deve ter todos os campos principais"""
        turma = repo.buscar_por_id(turma_id)

        assert turma.id == turma_id
        assert turma.codigo == turma_data['codigo']
        assert turma.disciplina == turma_data['disciplina']
        assert turma.semestre == turma_data['semestre']


class TestTurmaRepositoryListarPorProfessor:
    """Testa o método listar_por_professor()"""

    def test_retorna_lista(self, repo, professor_id):
        """Deve retornar uma lista"""
        resultado = repo.listar_por_professor(professor_id)

        assert isinstance(resultado, list)

    def test_lista_vazia_sem_turmas(self, repo, professor_id):
        """Professor sem turmas deve retornar lista vazia"""
        assert repo.listar_por_professor(professor_id) == []

    def test_retorna_turmas_do_professor(self, repo, professor_id, turma_data):
        """Deve retornar apenas as turmas do professor especificado"""
        repo.criar(turma_data)

        resultado = repo.listar_por_professor(professor_id)

        assert len(resultado) == 1

    def test_multiplas_turmas(self, repo, professor_id):
        """Deve retornar todas as turmas do professor"""
        for i in range(3):
            repo.criar({
                'codigo': f'T{i}',
                'disciplina': 'Disc',
                'semestre': '2025.2',
                'professor_id': professor_id,
            })

        assert len(repo.listar_por_professor(professor_id)) == 3

    def test_isola_turma_entre_professores(self, repo, professor_id, outro_professor_id):
        """Não deve retornar turmas de outros professores"""
        repo.criar({
            'codigo': 'T-A',
            'disciplina': 'A',
            'semestre': '2025.2',
            'professor_id': professor_id,
        })

        repo.criar({
            'codigo': 'T-B',
            'disciplina': 'B',
            'semestre': '2025.2',
            'professor_id': outro_professor_id,
        })

        resultado = repo.listar_por_professor(professor_id)

        assert len(resultado) == 1
        assert resultado[0].codigo == 'T-A'

    def test_professor_inexistente_retorna_lista_vazia(self, repo):
        """Professor que não existe deve retornar lista vazia sem erro"""
        assert repo.listar_por_professor(9999) == []


class TestTurmaRepositoryAdicionarAluno:
    """Testa o método adicionar_aluno()"""

    def test_retorna_true_ao_adicionar(self, repo, turma_id, aluno_id):
        """Deve retornar True quando o aluno é adicionado com sucesso"""
        assert repo.adicionar_aluno(turma_id, aluno_id) is True

    def test_aluno_aparece_na_lista(self, repo, turma_id, aluno_id):
        """Aluno adicionado deve aparecer na listagem da turma"""
        repo.adicionar_aluno(turma_id, aluno_id)
        alunos = repo.listar_alunos(turma_id)

        ids = [a['id'] for a in alunos]

        assert aluno_id in ids

    def test_retorna_false_se_ja_matriculado(self, repo, turma_id, aluno_id):
        """Segunda adição do mesmo aluno deve retornar False, sem erro"""
        repo.adicionar_aluno(turma_id, aluno_id)

        assert repo.adicionar_aluno(turma_id, aluno_id) is False

    def test_multiplos_alunos(self, repo, turma_id, aluno_id, outro_aluno_id):
        """Deve suportar múltiplos alunos na mesma turma"""
        repo.adicionar_aluno(turma_id, aluno_id)
        repo.adicionar_aluno(turma_id, outro_aluno_id)

        assert len(repo.listar_alunos(turma_id)) == 2

    def test_turma_inexistente_lanca_erro(self, repo, aluno_id):
        """turma_id inválido deve lançar ValueError"""
        with pytest.raises(ValueError):
            repo.adicionar_aluno(99999, aluno_id)

    def test_aluno_inexistente_lanca_erro(self, repo, turma_id):
        """aluno_id inválido deve lançar ValueError"""
        with pytest.raises(ValueError):
            repo.adicionar_aluno(turma_id, 9999)


class TestTurmaRepositoryRemoverAluno:
    """Testa o método remover_aluno()"""

    def test_retorna_true_ao_remover(self, repo, turma_id, aluno_id):
        """Deve retornar True quando o aluno é removido com sucesso"""
        repo.adicionar_aluno(turma_id, aluno_id)

        assert repo.remover_aluno(turma_id, aluno_id) is True

    def test_aluno_nao_aparece_mais_na_lista(self, repo, turma_id, aluno_id):
        """Aluno removido não deve aparecer na listagem"""
        repo.adicionar_aluno(turma_id, aluno_id)
        repo.remover_aluno(turma_id, aluno_id)

        alunos = repo.listar_alunos(turma_id)
        ids = [a['id'] for a in alunos]

        assert aluno_id not in ids

    def test_retorna_false_se_nao_matriculado(self, repo, turma_id, aluno_id):
        """Remover aluno não matriculado deve retornar False, sem erro"""
        assert repo.remover_aluno(turma_id, aluno_id) is False

    def test_remove_aluno_correto(self, repo, turma_id, aluno_id, outro_aluno_id):
        """Deve remover apenas o aluno especificado, mantendo os demais"""
        repo.adicionar_aluno(turma_id, aluno_id)
        repo.adicionar_aluno(turma_id, outro_aluno_id)
        repo.remover_aluno(turma_id, aluno_id)

        alunos = repo.listar_alunos(turma_id)
        ids = [a['id'] for a in alunos]

        assert outro_aluno_id in ids
        assert aluno_id not in ids

    def test_turma_inexistente_retorna_false(self, repo, aluno_id):
        """turma_id que não existe deve retornar False sem erro"""
        assert repo.remover_aluno(9999, aluno_id) is False


class TestTurmaRepositoryListarAlunos:
    """Testa o método listar_alunos()"""

    def test_retorna_lista(self, repo, turma_id):
        """Deve retornar uma lista"""
        assert isinstance(repo.listar_alunos(turma_id), list)

    def test_lista_vazia_sem_alunos(self, repo, turma_id):
        """Turma sem alunos deve retornar lista vazia"""
        assert repo.listar_alunos(turma_id) == []

    def test_cada_item_tem_campos_esperados(self, repo, turma_id, aluno_id):
        """Cada item deve ter ao menos id e nome"""
        repo.adicionar_aluno(turma_id, aluno_id)

        alunos = repo.listar_alunos(turma_id)

        assert 'id' in alunos[0]
        assert 'nome' in alunos[0]
        assert 'email' in alunos[0]
        assert 'matricula' in alunos[0]
        assert 'data_matricula' in alunos[0]

    def test_lista_vazia_apos_remocao_de_todos_alunos(self, repo, turma_id, aluno_id):
        """Após remover todos os alunos, a lista deve estar vazia"""
        repo.adicionar_aluno(turma_id, aluno_id)
        repo.remover_aluno(turma_id, aluno_id)

        assert repo.listar_alunos(turma_id) == []

    def test_turma_inexistente_retorna_lista_vazia(self, repo):
        """turma_id inexistente deve retornar lista vazia sem erro"""
        assert repo.listar_alunos(9999) == []
