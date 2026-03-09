"""
Testes para AvaliacaoRepository

Cobre criação de avaliações, registro de notas e consultas
agregadas, usando banco SQLite em memória para isolamento.
"""
# pylint: disable=redefined-outer-name
import sqlite3
from datetime import date
import pytest

from educalin.repositories.avaliacao_repository import AvaliacaoRepository
from educalin.repositories.schemas import create_all_tables
from educalin.repositories.usuario_models import ProfessorModel, AlunoModel
from educalin.repositories.turma_models import TurmaModel


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
    return AvaliacaoRepository(conn)

@pytest.fixture
def professor_id(conn):
    """Cria e retorna ID de um professor de suporte"""
    return ProfessorModel.criar(
        conn, "Dr. Exemplo", "prof@edu.br", "senha123", "PROF001"
    )

@pytest.fixture
def turma_id(conn, professor_id):
    """Cria uma turma e retorna seu ID"""
    return TurmaModel.criar(conn, "ES006", "POO", "2025.2", professor_id)

@pytest.fixture
def aluno_id(conn):
    """Cria e retorna ID de um aluno de suporte"""
    return AlunoModel.criar(
        conn, "Aluno Um", "aluno@edu.br", "senha123", "MAT001"
    )

@pytest.fixture
def outro_aluno_id(conn):
    """Cria e retorna ID de um segundo aluno de suporte"""
    return AlunoModel.criar(
        conn, "Aluno Dois", "aluno2@edu.br", "senha456", "MAT002"
    )

@pytest.fixture
def avaliacao_data(turma_id):
    """Dados mínimos válidos para uma avaliação"""
    return {
        'titulo': 'Prova 1',
        'data': date(2026, 2, 10),
        'valor_maximo': 10.0,
        'peso': 0.4,
        'turma_id': turma_id
    }

@pytest.fixture
def avaliacao_id(repo, avaliacao_data):
    """Cria uma avaliação e retorna seu ID"""
    return repo.criar_avaliacao(avaliacao_data)

@pytest.fixture
def nota_data(aluno_id, avaliacao_id):
    """Dados mínimos válidos para uma nota"""
    return {
        'aluno_id': aluno_id,
        'avaliacao_id': avaliacao_id,
        'valor': 7.5
    }


class TestAvaliacaoRepositoryEstrutura:
    """Testa que o repositório existe e tem a interface correta"""

    def test_instancia_com_conexao(self, conn):
        """Deve inicializar com uma conexão SQLite"""
        repo = AvaliacaoRepository(conn)

        assert repo is not None

    def test_conexao_invalida_lanca_erro(self):
        """Deve lançar TypeError ao tentar inicializar sem conexão válida"""
        with pytest.raises(TypeError):
            AvaliacaoRepository("não é conexão")

    def test_possui_metodo_criar_avaliacao(self, repo):
        """Deve possuir o método criar_avaliacao()"""
        assert callable(getattr(repo, 'criar_avaliacao', None))

    def test_possui_metodo_registrar_nota(self, repo):
        """Deve possuir o método registrar_nota()"""
        assert callable(getattr(repo, 'registrar_nota', None))

    def test_possui_metodo_buscar_notas_aluno(self, repo):
        """Deve possuir o método buscar_notas_aluno()"""
        assert callable(getattr(repo, 'buscar_notas_aluno', None))

    def test_possui_metodo_buscar_notas_turma(self, repo):
        """Deve possuir o método buscar_notas_turma()"""
        assert callable(getattr(repo, 'buscar_notas_turma', None))

    def test_possui_metodo_calcular_media_aluno(self, repo):
        """Deve possuir o método calcular_media_aluno()"""
        assert callable(getattr(repo, 'calcular_media_aluno', None))


class TestAvaliacaoRepositoryCriarAvaliacao:
    """Testes do método criar_avaliacao()"""

    def test_retorna_inteiro(self, repo, avaliacao_data):
        """Deve retornar o ID da avaliação criada"""
        assert isinstance(repo.criar_avaliacao(avaliacao_data), int)

    def test_id_positivo(self, repo, avaliacao_data):
        """ID retornado deve ser positivo"""
        assert repo.criar_avaliacao(avaliacao_data) > 0

    def test_avaliacao_persistida(self, repo, avaliacao_data, conn):
        """Avaliação criada deve ser encontrável por ID"""
        id_avaliacao = repo.criar_avaliacao(avaliacao_data)

        cursor = conn.execute("SELECT id FROM avaliacoes WHERE id = ?", (id_avaliacao,))

        assert cursor.fetchone() is not None

    def test_ids_unicos(self, repo, avaliacao_data):
        """IDs devem ser únicos e crescentes"""
        id1 = repo.criar_avaliacao(avaliacao_data)
        id2 = repo.criar_avaliacao({**avaliacao_data, 'titulo': 'Prova 2'})

        assert id1 != id2
        assert id2 > id1

    def test_titulo_vazio_lanca_erro(self, repo, avaliacao_data):
        """Deve lançar ValueError quando título está vazio"""
        with pytest.raises(ValueError):
            repo.criar_avaliacao({**avaliacao_data, 'titulo': ''})

    def test_valor_maximo_zero_lanca_erro(self, repo, avaliacao_data):
        """Deve lançar ValueError quando valor máximo é zero"""
        with pytest.raises(ValueError):
            repo.criar_avaliacao({**avaliacao_data, 'valor_maximo': 0})

    def test_valor_maximo_negativo_lanca_erro(self, repo, avaliacao_data):
        """Deve lançar ValueError quando valor máximo é negativo"""
        with pytest.raises(ValueError):
            repo.criar_avaliacao({**avaliacao_data, 'valor_maximo': -1.0})

    def test_peso_fora_do_intervalo_lanca_erro(self, repo, avaliacao_data):
        """Deve lançar ValueError quando peso está fora do intervalo [0, 1]"""
        with pytest.raises(ValueError):
            repo.criar_avaliacao({**avaliacao_data, 'peso': 1.5})

    def test_turma_inexistente_lanca_erro(self, repo, avaliacao_data):
        """Deve lançar ValueError quando turma_id não existe no banco"""
        with pytest.raises(ValueError):
            repo.criar_avaliacao({**avaliacao_data, 'turma_id': 99999})

    def test_campos_obrigatorios_ausentes_lancam_erro(self, repo):
        """Dados incompletos devem lançar ValueError"""
        with pytest.raises(ValueError):
            repo.criar_avaliacao({'titulo': 'Sem turma'})

    def test_data_invalida_lanca_erro(self, repo, avaliacao_data):
        """Deve lançar ValueError ou TypeError quando data é string ao invés de date"""
        with pytest.raises((ValueError, TypeError)):
            repo.criar_avaliacao({**avaliacao_data, 'data': '2026-03-06'})


class TestAvaliacaoRepositoryRegistrarNota:
    """Testes do método registrar_nota()"""

    def test_retorna_inteiro(self, repo, nota_data):
        """Deve retornar o ID da nota criada"""
        assert isinstance(repo.registrar_nota(nota_data), int)

    def test_id_positivo(self, repo, nota_data):
        """ID retornado deve ser positivo"""
        assert repo.registrar_nota(nota_data) > 0

    def test_nota_persistida(self, repo, nota_data, conn):
        """Nota criada deve ser encontrável por ID"""
        nota_id = repo.registrar_nota(nota_data)

        cursor = conn.execute("SELECT id FROM notas WHERE id = ?", (nota_id,))

        assert cursor.fetchone() is not None

    def test_valor_correto_persistido(self, repo, nota_data, conn):
        """Valor da nota deve ser persistido corretamente no banco"""
        nota_id = repo.registrar_nota(nota_data)

        cursor = conn.execute("SELECT valor FROM notas WHERE id = ?", (nota_id,))

        assert cursor.fetchone()['valor'] == nota_data['valor']

    def test_nota_duplicada_lanca_erro(self, repo, nota_data):
        """Mesmo aluno na mesma avaliação não pode ter duas notas"""
        repo.registrar_nota(nota_data)

        with pytest.raises(ValueError):
            repo.registrar_nota(nota_data)

    def test_valor_negativo_lanca_erro(self, repo, nota_data):
        """Deve lançar ValueError quando valor da nota é negativo"""
        with pytest.raises(ValueError):
            repo.registrar_nota({**nota_data, 'valor': -1.0})

    def test_valor_acima_do_maximo_lanca_erro(self, repo, nota_data):
        """Valor acima de valor_maximo da avaliação deve lançar erro"""
        with pytest.raises(ValueError):
            repo.registrar_nota({**nota_data, 'valor': 11.0})

    def test_aluno_inexistente_lanca_erro(self, repo, nota_data):
        """Deve lançar ValueError quando aluno_id não existe no banco"""
        with pytest.raises(ValueError):
            repo.registrar_nota({**nota_data, 'aluno_id': 9999})

    def test_avaliacao_inexistente_lanca_erro(self, repo, nota_data):
        """Deve lançar ValueError quando avaliacao_id não existe no banco"""
        with pytest.raises(ValueError):
            repo.registrar_nota({**nota_data, 'avaliacao_id': 99999})

    def test_campos_obrigatorios_ausentes_lancam_erro(self, repo):
        """Dados incompletos devem lançar ValueError"""
        with pytest.raises(ValueError):
            repo.registrar_nota({'Valor': 8.0})

    def test_valor_zero_valido(self, repo, nota_data):
        """Nota zero é válida"""
        nota_id = repo.registrar_nota({**nota_data, 'valor': 0.0})
        assert nota_id > 0

    def test_valor_igual_ao_maximo_valido(self, repo, nota_data):
        """Nota igual ao valor máximo é válida"""
        nota_id = repo.registrar_nota({**nota_data, 'valor': 10.0})
        assert nota_id > 0


class TestAvaliacaoRepositoryBuscarNotasAluno:
    """Testes do método buscar_notas_aluno()"""

    def test_retorna_lista(self, repo, aluno_id, turma_id):
        """Deve retornar uma lista de notas"""
        assert isinstance(repo.buscar_notas_aluno(aluno_id, turma_id), list)

    def test_lista_vazia_sem_notas(self, repo, aluno_id, turma_id):
        """Deve retornar lista vazia quando aluno não possui notas"""
        assert repo.buscar_notas_aluno(aluno_id, turma_id) == []

    def test_retorna_nota_registrada(self, repo, nota_data, aluno_id, turma_id):
        """Nota registrada deve ser retornada na busca do aluno"""
        repo.registrar_nota(nota_data)
        notas = repo.buscar_notas_aluno(aluno_id, turma_id)
        assert len(notas) == 1

    def test_cada_nota_tem_campos_obrigatorios(self, repo, nota_data, aluno_id, turma_id):
        """Cada nota retornada deve ter os campos obrigatórios"""
        repo.registrar_nota(nota_data)
        nota = repo.buscar_notas_aluno(aluno_id, turma_id)[0]

        assert 'valor' in nota
        assert 'avaliacao_id' in nota
        assert 'aluno_id' in nota

    def test_multiplas_avaliacoes(self, repo, aluno_id, turma_id, avaliacao_data, avaliacao_id):
        """Aluno com notas em duas avaliações diferentes deve retornar exatamente 2 notas"""
        av2_id = repo.criar_avaliacao({**avaliacao_data, 'titulo': 'Prova 2'})
        repo.registrar_nota({
            'aluno_id': aluno_id,
            'avaliacao_id': avaliacao_id,
            'valor': 6.0
        })

        repo.registrar_nota({
            'aluno_id': aluno_id,
            'avaliacao_id': av2_id,
            'valor': 8.0
        })

        notas = repo.buscar_notas_aluno(aluno_id, turma_id)

        assert len(notas) == 2

    def test_isola_notas_entre_alunos(self, repo, nota_data, outro_aluno_id, turma_id):
        """Nota de um aluno não deve aparecer na busca de outro aluno"""
        repo.registrar_nota(nota_data)

        notas_outro = repo.buscar_notas_aluno(outro_aluno_id, turma_id)
        notas_dono = repo.buscar_notas_aluno(nota_data['aluno_id'], turma_id)

        assert notas_outro == []
        assert len(notas_dono) == 1

    def test_aluno_inexistente_retorna_lista_vazia(self, repo, turma_id):
        """Aluno inexistente deve retornar lista vazia"""
        assert repo.buscar_notas_aluno(9999, turma_id) == []

    def test_turma_inexistente_retorna_lista_vazia(self, repo, aluno_id):
        """Turma inexistente deve retornar lista vazia"""
        assert repo.buscar_notas_aluno(aluno_id, 9999) == []


class TestAvaliacaoRepositoryBuscarNotasTurma:
    """Testes do método buscar_notas_turma()"""

    def test_retorna_lista(self, repo, turma_id):
        """Deve retornar uma lista de notas"""
        assert isinstance(repo.buscar_notas_turma(turma_id), list)

    def test_lista_vazia_sem_notas(self, repo, turma_id):
        """Deve retornar lista vazia quando turma não possui notas"""
        assert repo.buscar_notas_turma(turma_id) == []

    def test_retorna_nota_registrada(self, repo, nota_data, turma_id):
        """Nota registrada deve ser retornada na busca da turma"""
        repo.registrar_nota(nota_data)
        assert len(repo.buscar_notas_turma(turma_id)) == 1

    def test_cada_nota_tem_campos_obrigatorios(self, repo, nota_data, turma_id):
        """Cada nota retornada deve ter os campos obrigatórios"""
        repo.registrar_nota(nota_data)
        nota = repo.buscar_notas_turma(turma_id)[0]

        assert 'valor' in nota
        assert 'aluno_id' in nota
        assert 'avaliacao_id' in nota

    def test_multiplas_notas_de_alunos_diferentes(self, repo, turma_id, avaliacao_id,
                                                   aluno_id, outro_aluno_id):
        """Deve retornar múltiplas notas de alunos diferentes na mesma turma"""
        repo.registrar_nota({
            'aluno_id': aluno_id,
            'avaliacao_id': avaliacao_id,
            'valor': 7.0,
        })

        repo.registrar_nota({
            'aluno_id': outro_aluno_id,
            'avaliacao_id': avaliacao_id,
            'valor': 8.0,
        })

        assert len(repo.buscar_notas_turma(turma_id)) == 2

    def test_isola_notas_entre_turmas(self, repo, conn, professor_id, aluno_id, avaliacao_data):
        """Não deve retornar notas de outras turmas"""
        outra_turma_id = TurmaModel.criar(conn, "ES001", "Matemática", "2025.2", professor_id)
        outra_av_id = repo.criar_avaliacao({**avaliacao_data, 'turma_id': outra_turma_id})

        repo.registrar_nota({
            'aluno_id': aluno_id,
            'avaliacao_id': outra_av_id,
            'valor': 5.0
        })

        assert repo.buscar_notas_turma(avaliacao_data['turma_id']) == []

    def test_turma_inexistente_retorna_lista_vazia(self, repo):
        """Turma inexistente deve retornar lista vazia"""
        assert repo.buscar_notas_turma(99999) == []


class TestAvaliacaoRepositoryCalcularMediaAluno:
    """Testes do método calcular_media_aluno()"""

    def test_retorna_float(self, repo, nota_data, aluno_id, turma_id):
        """Deve retornar um float representando a média"""
        repo.registrar_nota(nota_data)
        resultado = repo.calcular_media_aluno(aluno_id, turma_id)
        assert isinstance(resultado, float)

    def test_sem_notas_retorna_none(self, repo, aluno_id, turma_id):
        """Deve retornar None quando aluno não possui notas"""
        assert repo.calcular_media_aluno(aluno_id, turma_id) is None

    def test_media_nota_unica(self, repo, nota_data, aluno_id, turma_id):
        """Média com uma única nota deve ser igual àquela nota"""
        repo.registrar_nota(nota_data)

        media = repo.calcular_media_aluno(aluno_id, turma_id)

        assert media == pytest.approx(7.5, abs=0.01)

    def test_media_multiplas_notas(self, repo, aluno_id, turma_id, avaliacao_data):
        """Média de [6.0, 8.0] deve ser 7.0"""
        av1_id = repo.criar_avaliacao({**avaliacao_data, 'titulo': 'Prova 1'})
        av2_id = repo.criar_avaliacao({**avaliacao_data, 'titulo': 'Prova 2'})

        repo.registrar_nota({'aluno_id': aluno_id, 'avaliacao_id': av1_id, 'valor': 6.0})
        repo.registrar_nota({'aluno_id': aluno_id, 'avaliacao_id': av2_id, 'valor': 8.0})

        media = repo.calcular_media_aluno(aluno_id, turma_id)

        assert media == pytest.approx(7.0, abs=0.01)

    def test_isola_media_entre_alunos(self, repo, aluno_id, outro_aluno_id,
                                       turma_id, avaliacao_id):
        """Média calculada deve ser apenas do aluno especificado"""
        repo.registrar_nota({'aluno_id': aluno_id, 'avaliacao_id': avaliacao_id, 'valor': 9.0})
        repo.registrar_nota({'aluno_id': outro_aluno_id, 'avaliacao_id': avaliacao_id, 'valor': 3.0})

        media = repo.calcular_media_aluno(aluno_id, turma_id)

        assert media == pytest.approx(9.0, abs=0.01)

    def test_filtro_por_topico(self, repo, aluno_id, turma_id, avaliacao_data):
        """Com tópico informado, deve considerar apenas avaliações daquele tópico"""
        av_poo_id = repo.criar_avaliacao({**avaliacao_data, 'titulo': 'P1 POO', 'topico': 'heranca'})
        av_bd_id = repo.criar_avaliacao({**avaliacao_data, 'titulo': 'P1 BD', 'topico': 'sql'})

        repo.registrar_nota({'aluno_id': aluno_id, 'avaliacao_id': av_poo_id, 'valor': 9.0})
        repo.registrar_nota({'aluno_id': aluno_id, 'avaliacao_id': av_bd_id, 'valor': 8.0})

        media = repo.calcular_media_aluno(aluno_id, turma_id, topico='heranca')

        assert media == pytest.approx(9.0, abs=0.01)

    def test_topico_sem_notas_retorna_none(self, repo, nota_data, aluno_id, turma_id):
        """Tópico sem notas registradas deve retornar None"""
        repo.registrar_nota(nota_data)

        assert repo.calcular_media_aluno(aluno_id, turma_id, topico='topico_inexistente') is None

    def test_aluno_inexistente_retorna_none(self, repo, turma_id):
        """Aluno inexistente deve retornar None"""
        assert repo.calcular_media_aluno(9999, turma_id) is None


class TestAvaliacaoRepositoryCriarAvaliacaoPesosLimite:
    """Testa os limites do intervalo de peso em criar_avaliacao()"""

    def test_peso_zero_valido(self, repo, avaliacao_data):
        """Peso zero deve ser aceito (limite inferior do intervalo [0, 1])"""
        av_id = repo.criar_avaliacao({**avaliacao_data, 'peso': 0.0})
        assert av_id > 0

    def test_peso_um_valido(self, repo, avaliacao_data):
        """Peso máximo (1.0) deve ser aceito (limite superior do intervalo [0, 1])"""
        av_id = repo.criar_avaliacao({**avaliacao_data, 'peso': 1.0})
        assert av_id > 0


class TestAvaliacaoRepositoryRegistrarNotaValorNone:
    """Testa comportamento de registrar_nota() com valor=None explícito"""

    def test_valor_none_explicito_lanca_erro(self, repo, nota_data):
        """Passar valor=None explicitamente deve lançar ValueError"""
        with pytest.raises(ValueError):
            repo.registrar_nota({**nota_data, 'valor': None})
