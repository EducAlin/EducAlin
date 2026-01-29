import pytest
from src.educalin.domain.professor import Professor

# mock de uma classe ainda nao implementada
class DummyTurma:
    def __init__(self, codigo):
        self.codigo = codigo

@pytest.fixture
def professor_exemplo():
    """Cria uma instância de Professor para ser usada nos testes."""
    return Professor(
        nome="Dr. Arnaldo",
        email="arnaldo.prof@educalin.com",
        senha="senhaDoProfessor",
        registro_funcional="RF12345"
    )

def test_criar_professor_com_sucesso(professor_exemplo):
    """
    Verifica a instanciação correta de um Professor.
    """
    assert professor_exemplo.nome == "Dr. Arnaldo"
    assert professor_exemplo.email == "arnaldo.prof@educalin.com"
    assert professor_exemplo.registro_funcional == "RF12345"
    assert isinstance(professor_exemplo.senha, bytes)
    assert professor_exemplo.turmas == []

def test_validar_credenciais_professor(professor_exemplo):
    """
    Testa a lógica de autenticação do Professor.
    """
    assert professor_exemplo.validar_credenciais("arnaldo.prof@educalin.com", "senhaDoProfessor") is True
    assert professor_exemplo.validar_credenciais("arnaldo.prof@educalin.com", "senhaErrada") is False

def test_adicionar_turma_professor(professor_exemplo):
    """Testa a adição de uma turma usando mock com dummy à lista do professor."""
    turma_a = DummyTurma("T1A")
    professor_exemplo.adicionar_turma(turma_a)
    
    assert len(professor_exemplo.turmas) == 1
    assert turma_a in professor_exemplo.turmas