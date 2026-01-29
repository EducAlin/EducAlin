import pytest
from src.educalin.domain.aluno import Aluno

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