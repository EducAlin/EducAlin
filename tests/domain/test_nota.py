import pytest
from datetime import datetime, date
from unittest.mock import Mock

from educalin.domain.nota import Nota
from educalin.domain.aluno import Aluno
from educalin.domain.avaliacao import Avaliacao


@pytest.fixture
def aluno_mock():
    """Fixture que cria um mock de Aluno."""
    aluno = Mock(spec=Aluno)
    aluno.nome = "João Teste"
    aluno.matricula = "2026001"
    return aluno


@pytest.fixture
def avaliacao_mock():
    """Fixture que cria um mock de Avaliacao com valor_maximo definido."""
    avaliacao = Mock(spec=Avaliacao)
    avaliacao.titulo = "Prova de TDD"
    avaliacao.valor_maximo = 10.0
    return avaliacao


def test_criar_nota_com_sucesso(aluno_mock, avaliacao_mock):
    """
    Testa a criação de uma instância de Nota com dados válidos (caminho feliz).
    """
    nota = Nota(aluno=aluno_mock, avaliacao=avaliacao_mock, valor=8.5)

    assert nota.aluno == aluno_mock
    assert nota.avaliacao == avaliacao_mock
    assert nota.valor == 8.5
    assert isinstance(nota.data_registro, datetime)


def test_criar_nota_com_valor_acima_do_maximo_lanca_erro(aluno_mock, avaliacao_mock):
    """
    Testa se um ValueError é lançado ao tentar criar uma nota com valor
    maior que o valor_maximo da avaliação.
    """
    with pytest.raises(ValueError, match="O valor da nota não pode ser maior que o valor máximo da avaliação."):
        Nota(aluno=aluno_mock, avaliacao=avaliacao_mock, valor=11.0)


def test_criar_nota_com_valor_negativo_lanca_erro(aluno_mock, avaliacao_mock):
    """
    Testa se um ValueError é lançado ao tentar criar uma nota com valor negativo.
    """
    with pytest.raises(ValueError, match="O valor da nota não pode ser negativo."):
        Nota(aluno=aluno_mock, avaliacao=avaliacao_mock, valor=-2.0)


def test_criar_nota_com_aluno_invalido_lanca_erro(avaliacao_mock):
    """
    Testa se um TypeError é lançado se o 'aluno' não for uma instância de Aluno.
    """
    with pytest.raises(TypeError, match="O aluno deve ser uma instância da classe Aluno."):
        Nota(aluno="não sou um aluno", avaliacao=avaliacao_mock, valor=7.0)


def test_criar_nota_com_avaliacao_invalida_lanca_erro(aluno_mock):
    """
    Testa se um TypeError é lançado se a 'avaliacao' não for uma instância de Avaliacao.
    """
    with pytest.raises(TypeError, match="A avaliação deve ser uma instância da classe Avaliacao."):
        Nota(aluno=aluno_mock, avaliacao="não sou uma avaliação", valor=7.0)


def test_calcular_percentual_da_nota(aluno_mock, avaliacao_mock):
    """
    Testa se o método calcular_percentual retorna o valor correto.
    """
    nota = Nota(aluno=aluno_mock, avaliacao=avaliacao_mock, valor=8.0)
    
    # A avaliação mock tem valor_maximo = 10.0, então 8.0 deve ser 80.0%
    assert nota.calcular_percentual() == 80.0