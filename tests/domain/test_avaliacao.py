import pytest
from datetime import date

from educalin.domain.avaliacao import Avaliacao


def test_criar_avaliacao_com_sucesso():
    """
    Testa a criação de uma instância de Avaliacao com dados válidos.
    Good path
    """
    data_avaliacao = date(2026, 3, 15)
    avaliacao = Avaliacao(
        titulo="Prova 1 - Estrutura de Dados",
        data=data_avaliacao,
        valor_maximo=10.0,
        peso=0.4
    )
    assert avaliacao.titulo == "Prova 1 - Estrutura de Dados"
    assert avaliacao.data == data_avaliacao
    assert avaliacao.valor_maximo == 10.0
    assert avaliacao.peso == 0.4


def test_criar_avaliacao_titulo_vazio_lanca_erro():
    """
    Testa se um ValueError é lançado ao tentar criar uma avaliação com título vazio.
    """
    with pytest.raises(ValueError, match="O título não pode ser vazio."):
        Avaliacao(titulo="  ", data=date.today(), valor_maximo=10.0, peso=0.5)


def test_criar_avaliacao_valor_maximo_invalido_lanca_erro():
    """
    Testa se um ValueError é lançado para um valor_maximo não positivo.
    """
    with pytest.raises(ValueError, match="O valor máximo deve ser um número positivo."):
        Avaliacao(titulo="Prova", data=date.today(), valor_maximo=-5.0, peso=0.5)
    
    with pytest.raises(ValueError, match="O valor máximo deve ser um número positivo."):
        Avaliacao(titulo="Prova", data=date.today(), valor_maximo=0, peso=0.5)


def test_criar_avaliacao_peso_invalido_lanca_erro():
    """
    Testa se um ValueError é lançado para um peso fora do intervalo [0, 1].
    """
    with pytest.raises(ValueError, match="O peso deve estar no intervalo de 0 a 1."):
        Avaliacao(titulo="Prova", data=date.today(), valor_maximo=10.0, peso=-0.1)

    with pytest.raises(ValueError, match="O peso deve estar no intervalo de 0 a 1."):
        Avaliacao(titulo="Prova", data=date.today(), valor_maximo=10.0, peso=1.1)


def test_criar_avaliacao_com_tipo_data_invalido_lanca_erro():
    """
    Testa se um TypeError é lançado se a data não for um objeto date.
    """
    with pytest.raises(TypeError, match="O atributo data deve ser um objeto date."):
        Avaliacao(titulo="Prova", data="2026-03-15", valor_maximo=10.0, peso=0.5)
