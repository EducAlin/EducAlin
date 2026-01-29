import pytest
from datetime import date
from unittest.mock import Mock
from src.educalin.domain.aluno import Aluno
from src.educalin.domain.nota import Nota
from src.educalin.domain.avaliacao import Avaliacao

def test_criar_aluno_com_sucesso():
    """
    Verifica se um objeto Aluno é instanciado corretamente e se a senha
    é armazenada como um hash.
    """
    aluno = Aluno(
        nome="João da Silva",
        email="joao.silva@email.com",
        senha="senhaSegura123",
        matricula="2024001"
    )
    assert aluno.nome == "João da Silva"
    assert aluno.email == "joao.silva@email.com"
    assert aluno.matricula == "2024001"
    assert isinstance(aluno.senha, bytes)
    assert aluno.senha != b"senhaSegura123"

def test_validar_credenciais_aluno():
    """
    Testa o método de validação de credenciais com senhas corretas e incorretas.
    """
    aluno = Aluno(
        nome="Maria Oliveira",
        email="maria.o@email.com",
        senha="outraSenha!@#",
        matricula="2024002"
    )
    # Teste good path
    assert aluno.validar_credenciais("maria.o@email.com", "outraSenha!@#") is True
    # Teste bad path com senha
    assert aluno.validar_credenciais("maria.o@email.com", "senhaErrada") is False
    # Teste bad path com email
    assert aluno.validar_credenciais("errado@email.com", "outraSenha!@#") is False

def test_resetar_senha_aluno():
    """
    Verifica se o método resetar_senha atualiza a senha corretamente.
    """
    aluno = Aluno(
        nome="Carlos Souza",
        email="carlos.s@email.com",
        senha="senhaAntiga456",
        matricula="2024003"
    )
    aluno.resetar_senha("novaSenhaSuperForteMegaTop")
    # A senha antiga pode funcionar
    assert aluno.validar_credenciais("carlos.s@email.com", "senhaAntiga456") is False
    # A nova senha deve funcionar
    assert aluno.validar_credenciais("carlos.s@email.com", "novaSenhaSuperForteMegaTop") is True

def test_email_invalido_aluno_lanca_erro():
    """
    Garante que um ValueError é lançado ao tentar atribuir um e-mail inválido.
    """
    aluno = Aluno("Teste", "email.valido@teste.com", "senha", "123")
    with pytest.raises(ValueError, match="Formato de e-mail inválido."):
        aluno.email = "emailinvalido"

def test_adicionar_nota_aluno():
    """Testa a adição de uma nota ao desempenho do aluno."""
    aluno = Aluno("Ana Lima", "ana.l@email.com", "senha", "2024004")
    avaliacao_mock = Mock(spec=Avaliacao, valor_maximo=10.0)
    
    nota = Nota(aluno=aluno, avaliacao=avaliacao_mock, valor=8.5)
    aluno.adicionar_nota(nota)
    
    assert len(aluno.desempenho) == 1
    assert aluno.desempenho[0] == nota

def test_adicionar_objeto_invalido_como_nota_lanca_erro():
    """Testa se um TypeError é lançado ao adicionar um objeto que não é Nota."""
    aluno = Aluno("Ana Lima", "ana.l@email.com", "senha", "2024004")
    with pytest.raises(TypeError, match="O objeto adicionado deve ser uma instância de Nota."):
        aluno.adicionar_nota("não é uma nota")

def test_adicionar_nota_de_outro_aluno_lanca_erro():
    """Testa se um ValueError é lançado ao adicionar uma nota que pertence a outro aluno."""
    aluno1 = Aluno("Ana Lima", "ana.l@email.com", "senha", "2024004")
    aluno2 = Aluno("Beto Costa", "beto.c@email.com", "senha", "2024005")
    avaliacao_mock = Mock(spec=Avaliacao, valor_maximo=10.0)
    
    nota_do_aluno2 = Nota(aluno=aluno2, avaliacao=avaliacao_mock, valor=9.0)
    
    with pytest.raises(ValueError, match="Esta nota pertence a outro aluno."):
        aluno1.adicionar_nota(nota_do_aluno2)

def test_calcular_media_aluno_com_notas():
    """
    Testa o cálculo da média de notas do aluno a partir de objetos Nota.
    """
    aluno = Aluno("Ana Lima", "ana.l@email.com", "senha", "2024004")
    
    # Teste com desempenho vazio
    assert aluno.calcular_media() == 0.0

    # Mock de avaliações
    av1 = Avaliacao(titulo="P1", data=date.today(), valor_maximo=10.0, peso=0.5)
    av2 = Avaliacao(titulo="T1", data=date.today(), valor_maximo=10.0, peso=0.5)
    av3 = Avaliacao(titulo="P2", data=date.today(), valor_maximo=10.0, peso=0.5)

    # Adiciona notas
    aluno.adicionar_nota(Nota(aluno=aluno, avaliacao=av1, valor=8.0))
    aluno.adicionar_nota(Nota(aluno=aluno, avaliacao=av2, valor=10.0))
    aluno.adicionar_nota(Nota(aluno=aluno, avaliacao=av3, valor=7.0))

    # Teste com notas válidas
    assert aluno.calcular_media() == (8.0 + 10.0 + 7.0) / 3