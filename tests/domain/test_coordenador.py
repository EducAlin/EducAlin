import pytest
from educalin.domain.coordenador import Coordenador
from educalin.domain.turma import Turma

def test_criar_coordenador_com_sucesso():
    """
    Verifica a instanciação correta de um Coordenador.
    """
    coordenador = Coordenador(
        nome="Sra. Carla",
        email="carla.coord@educalin.com",
        senha="senhaDaCoordenacao",
        codigo_coordenacao="COORD-001"
    )
    assert coordenador.nome == "Sra. Carla"
    assert coordenador.email == "carla.coord@educalin.com"
    assert coordenador.codigo_coordenacao == "COORD-001"
    assert isinstance(coordenador.senha, bytes)

def test_validar_credenciais_coordenador():
    """
    Testa a lógica de autenticação do Coordenador.
    """
    coordenador = Coordenador(
        nome="Sr. Daniel",
        email="daniel.coord@educalin.com",
        senha="senhaDoCoordenador123",
        codigo_coordenacao="COORD-002"
    )
    assert coordenador.validar_credenciais("daniel.coord@educalin.com", "senhaDoCoordenador123") is True
    assert coordenador.validar_credenciais("daniel.coord@educalin.com", "senhaErrada") is False

def test_comparar_turmas_coordenador():
    """
    Testa o método que compara duas turmas pelo código.
    """
    turma1 = Turma(codigo="T1A", disciplina="POO", semestre="2026.1")
    turma2 = Turma(codigo="T1A", disciplina="Algoritmos", semestre="2026.1")
    turma3 = Turma(codigo="T1B", disciplina="POO", semestre="2026.1")
    
    assert Coordenador.comparar_turmas(turma1, turma2) is True
    assert Coordenador.comparar_turmas(turma1, turma3) is False
