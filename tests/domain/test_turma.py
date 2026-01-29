import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from educalin.domain.turma import Turma, Observer, AlunoDuplicadoException, AlunoNaoEncontradoException

class TestTurmaInicializacao:
    """Testes de criação e inicialização da Turma"""

    def test_turma_inicializacao_valida(self):
        """Deve criar uma turma com os atributos obrigatórios corretos"""
        # Arrange
        dados = {
            "codigo": "ES-2025.2",
            "disciplina": "Programação Orientada à Objetos",
            "semestre": "2025.2"
        }

        # Act
        turma = Turma(**dados)

        # Assert
        assert turma.codigo == "ES-2025.2"
        assert turma.disciplina == "Programação Orientada à Objetos"
        assert turma.semestre == "2025.2"
        assert turma.alunos == []
        assert turma.total_alunos == 0
        assert isinstance(turma.data_criacao, datetime)

    def test_turma_com_professor(self):
        """Deve criar turma com professor atribuído"""
        professor_mock = Mock()
        professor_mock.nome = "Prof. Fulano"

        turma = Turma("ES-01", "POO", "2025.2", professor=professor_mock)

        assert turma.professor == professor_mock

    def test_turma_codigo_vazio_deve_falhar(self):
        """Deve lançar ValueError se código for vazio"""
        with pytest.raises(ValueError, match="Código da turma não pode ser vazio"):
            Turma("", "POO", "2025.2")
    
    def test_turma_disciplina_vazia_deve_falhar(self):
        """Deve lançar ValueError se disciplina for vazio"""
        with pytest.raises(ValueError, match="Disciplina da turma não pode ser vazia"):
            Turma("ES-01", "", "2025.2")
    
    def test_turma_semestre_vazio_deve_falhar(self):
        """Deve lançar ValueError se semestre for vazio"""
        with pytest.raises(ValueError, match="Semestre da turma não pode ser vazio"):
            Turma("ES-01", "POO", "")

    def test_turma_normaliza_espacos(self):
        """Deve remover espaços extras dos atributos"""
        turma = Turma("    ES-01    ", "    POO    ", "    2025.2    ")

        assert turma.codigo == "ES-01"
        assert turma.disciplina == "POO"
        assert turma.semestre == "2025.2"
            


class TestTurmaGestaoAlunos:
    """Testes de adição e remoção de alunos"""

    @pytest.fixture
    def turma(self):
        """Fixture com turma padrão"""
        return Turma("ES-01", "POO", "2025.2")
    
    @pytest.fixture
    def aluno_mock(self):
        """Fixture com mock de aluno"""
        aluno = Mock()
        aluno.matricula = "12345"
        aluno.nome = "Fulano de Tal da Silva"
        return aluno

    def test_adicionar_aluno_com_sucesso(self, turma, aluno_mock):
        """Deve adicionar um objeto aluno à lista da turma"""
        resultado = turma.adicionar_aluno(aluno_mock)

        assert resultado is True
        assert len(turma.alunos) == 1
        assert aluno_mock in turma.alunos
        assert turma.total_alunos == 1

    def test_nao_deve_adicionar_aluno_duplicado(self, turma, aluno_mock):
        """Deve ignorar ou impedir a adição do mesmo aluno duas vezes"""
        turma.adicionar_aluno(aluno_mock)
        resultado = turma.adicionar_aluno(aluno_mock) # Tentativa duplicada

        assert resultado is False
        assert len(turma.alunos) == 1

    def test_adicionar_nao_aluno_deve_falhar(self, turma):
        """Deve lançar TypeError se tentar adicionar algo que não é Aluno"""
        with pytest.raises(TypeError, match="Esperado instância de Aluno"):
            turma.adicionar_aluno("não é um aluno")

    def test_remover_aluno_existente(self, turma, aluno_mock):
        """Deve remover um aluno que está na lista"""
        turma.adicionar_aluno(aluno_mock)

        resultado = turma.remover_aluno(aluno_mock)

        assert resultado is True
        assert len(turma.alunos) == 0

    def test_remover_aluno_inexistente(self, turma, aluno_mock):
        """Deve retornar erro ao tentar remover um aluno inexistente"""
        resultado = turma.remover_aluno(aluno_mock)

        assert resultado is False

    def test_buscar_aluno_por_matricula_existente(self, turma, aluno_mock):
        """Deve encontrar aluno pela matrícula"""
        turma.adicionar_aluno(aluno_mock)

        aluno_encontrado = turma.buscar_aluno_por_matricula("12345")

        assert aluno_encontrado == aluno_mock

    def test_buscar_aluno_por_matricula_inexistente(self, turma):
        """Deve retornar None se matrícula não existe"""
        aluno_encontrado = turma.buscar_aluno_por_matricula("11111")

        assert aluno_encontrado is None



class TestTurmaDesempenho:
    """Testes de cálculo de desempenho"""

    @pytest.fixture
    def turma_com_alunos(self):
        """Fixture com turma contendo alunos mock"""
        turma = Turma("ES-01", "POO", "2025.2")

        aluno1 = Mock()
        aluno1.matricula = "001"
        aluno1.calcular_media = Mock(return_value=8.5)
        
        aluno2 = Mock()
        aluno2.matricula = "002"
        aluno2.calcular_media = Mock(return_value=5.0)
        
        aluno3 = Mock()
        aluno3.matricula = "003"
        aluno3.calcular_media = Mock(return_value=7.0)

        turma.adicionar_aluno(aluno1)
        turma.adicionar_aluno(aluno2)
        turma.adicionar_aluno(aluno3)

        return turma
    
    def test_obter_desempenho_geral_turma_vazia(self):
        """Deve retornar estatísticas zeradas para turma vazia"""
        turma = Turma("ES-01", "POO", "2025.2")

        desempenho = turma.obter_desempenho_geral()

        assert desempenho == {
            'media_geral': 0.0,
            'total_alunos': 0,
            'alunos_com_dificuldade': 0,
            'taxa_aprovacao': 0.0
        }

    def test_obter_desempenho_geral_com_alunos(self, turma_com_alunos):
        """Deve calcular estatísticas corretas da turma"""
        desempenho = turma_com_alunos.obter_desempenho_geral()

        assert desempenho['media_geral'] == pytest.approx(6.83, abs=0.01)
        assert desempenho['total_alunos'] == 3
        assert desempenho['alunos_com_dificuldade'] == 1
        assert desempenho['taxa_aprovacao'] == pytest.approx(66.67, abs=0.01)

    def test_obter_alunos_com_dificuldade(self, turma_com_alunos):
        """Deve retornar apenas alunos com média < 6.0"""
        alunos_dificuldade = turma_com_alunos.obter_alunos_com_dificuldade()

        assert len(alunos_dificuldade) == 1
        assert alunos_dificuldade[0].matricula == "002"



class TestTurmaObserverPattern:
    """Testes do padrão Observer"""

    @pytest.fixture
    def turma(self):
        return Turma("ES-01", "POO", "2025.2")
    
    @pytest.fixture
    def observer_mock(self):
        observer = Mock(spec=Observer)
        return observer
    
    def test_implementa_interface_subject(self, turma):
        """Verifica se a Turma tem os métodos do padrão Observer (Subject)"""
        assert hasattr(turma, 'adicionar_observer')
        assert hasattr(turma, 'remover_observer')
        assert hasattr(turma, 'notificar_observers')

    def test_adicionar_observer(self, turma, observer_mock):
        """Deve adicionar observer à lista"""
        turma.adicionar_observer(observer_mock)

        turma.notificar_observers({'teste': 'evento'})
        observer_mock.atualizar.assert_called_once_with({'teste': 'evento'})

    def test_remover_observer(self, turma, observer_mock):
        """Deve remover observer da lista"""
        turma.adicionar_observer(observer_mock)
        turma.remover_observer(observer_mock)

        turma.notificar_observers({'teste': 'evento'})
        observer_mock.atualizar.asser_not_called()

    def test_notificar_multiplos_observers(self, turma):
        """Deve notificar todos os observers"""
        obs1 = Mock(spec=Observer)
        obs2 = Mock(spec=Observer)

        turma.adicionar_observer(obs1)
        turma.adicionar_observer(obs2)

        turma.notificar_observers({'evento': 'teste'})

        obs1.atualizar.assert_called_once()
        obs2.atualizar.assert_called_once()

    def test_adicionar_aluno_notifica_observers(self, turma, observer_mock):
        """Deve notificar observers quando aluno é adicionado"""
        turma.adicionar_observer(observer_mock)

        aluno_mock = Mock()
        aluno_mock.matricula = "12345"
        aluno_mock.nome = "Fulano de Tal"

        turma.adicionar_aluno(aluno_mock)

        observer_mock.atualizar.assert_called_once()

        evento = observer_mock.atualizar.call_args[0][0]
        assert evento['evento'] == 'aluno_adicionado'
        assert evento['aluno_matricula'] == "12345"



class TestTurmaMetodosEspeciais:
    """Testes de métodos especiais"""

    def test_repr(self):
        """Deve retornar representação oficial"""
        turma = Turma("ES-01", "POO", "2025.2")

        repr_str = repr(turma)

        assert "Turma(codigo='ES-01'" in repr_str
        assert "disciplina='POO'" in repr_str
        assert "alunos=0" in repr_str

    def test_str(self):
        """Deve retornar representação amigável"""
        turma = Turma("ES-01", "POO", "2025.2")

        str_repr = str(turma)

        assert "Turma ES-01 - POO (2025.2) - 0 alunos" == str_repr

    def test_igualdade_turmas_mesmo_codigo(self):
        """Turmas com mesmo código devem ser iguais"""
        turma1 = Turma("ES-01", "POO", "2025.2")
        turma2 = Turma("ES-01", "Algoritmos", "2026.2")

        assert turma1 == turma2

    def test_igualdade_turmas_codigos_diferentes(self):
        """Turmas com códigos diferentes não devem ser iguais"""
        turma1 = Turma("ES-01", "POO", "2025.2")
        turma2 = Turma("ES-02", "Algoritmos", "2026.2")
        
        assert turma1 != turma2

    def test_hash_permite_uso_em_set(self):
        """Deve poder usar Turma em sets/dicts"""
        turma1 = Turma("ES-01", "POO", "2025.2")
        turma2 = Turma("ES-02", "Algoritmos", "2026.2")

        turmas_set = {turma1, turma2}

        assert len(turmas_set) == 2
        assert turma1 in turmas_set