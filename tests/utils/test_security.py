"""Testes para o módulo de segurança (utils/security.py)."""

import os
import time

import pytest


# Garante que JWT_SECRET_KEY está definida antes de importar o módulo
os.environ.setdefault("JWT_SECRET_KEY", "chave-secreta-de-teste-para-unit-tests")

from educalin.utils.security import (
    criar_token_jwt,
    decodificar_token_jwt,
    hash_senha,
    verificar_senha,
)


class TestHashSenha:
    """Testes para a função hash_senha."""

    def test_retorna_string(self):
        """Deve retornar uma string."""
        resultado = hash_senha("minha_senha")
        assert isinstance(resultado, str)

    def test_hash_diferente_da_senha_original(self):
        """O hash não deve ser igual à senha em texto plano."""
        senha = "senha123"
        resultado = hash_senha(senha)
        assert resultado != senha

    def test_hashes_distintos_para_mesma_senha(self):
        """Duas chamadas com a mesma senha devem gerar hashes diferentes (salt aleatório)."""
        senha = "senha_igual"
        hash1 = hash_senha(senha)
        hash2 = hash_senha(senha)
        assert hash1 != hash2

    def test_formato_bcrypt(self):
        """O hash gerado deve ter o prefixo bcrypt ($2b$)."""
        resultado = hash_senha("qualquer_senha")
        assert resultado.startswith("$2b$")


class TestVerificarSenha:
    """Testes para a função verificar_senha."""

    def test_senha_correta_retorna_true(self):
        """Deve retornar True quando a senha corresponde ao hash."""
        senha = "senha_correta"
        senha_hash = hash_senha(senha)
        assert verificar_senha(senha, senha_hash) is True

    def test_senha_errada_retorna_false(self):
        """Deve retornar False quando a senha não corresponde ao hash."""
        senha_hash = hash_senha("senha_original")
        assert verificar_senha("senha_errada", senha_hash) is False

    def test_senha_vazia_retorna_false(self):
        """Deve retornar False ao comparar senha vazia com hash de senha não-vazia."""
        senha_hash = hash_senha("alguma_senha")
        assert verificar_senha("", senha_hash) is False

    def test_parametro_hash_nao_sombreia_builtin(self):
        """Parâmetro renomeado para senha_hash — não deve conflitar com built-in hash()."""
        assert callable(hash), "built-in hash() deve permanecer acessível"
        resultado = verificar_senha("abc", hash_senha("abc"))
        assert resultado is True


class TestCriarTokenJwt:
    """Testes para a função criar_token_jwt."""

    def test_retorna_string(self):
        """Deve retornar um token JWT como string."""
        token = criar_token_jwt(1, "aluno")
        assert isinstance(token, str)

    def test_token_nao_vazio(self):
        """O token gerado não deve ser vazio."""
        token = criar_token_jwt(42, "professor")
        assert token != ""

    def test_token_tem_tres_partes(self):
        """Um JWT válido deve ter exatamente 3 partes separadas por ponto."""
        token = criar_token_jwt(1, "coordenador")
        partes = token.split(".")
        assert len(partes) == 3

    def test_payloads_distintos_geram_tokens_distintos(self):
        """Tokens para usuários diferentes devem ser distintos."""
        token1 = criar_token_jwt(1, "aluno")
        token2 = criar_token_jwt(2, "aluno")
        assert token1 != token2


class TestDecodificarTokenJwt:
    """Testes para a função decodificar_token_jwt."""

    def test_token_valido_retorna_payload(self):
        """Deve retornar o payload para um token válido."""
        token = criar_token_jwt(10, "professor")
        payload = decodificar_token_jwt(token)
        assert payload is not None

    def test_payload_contem_usuario_id(self):
        """O payload decodificado deve conter o usuario_id correto."""
        token = criar_token_jwt(99, "aluno")
        payload = decodificar_token_jwt(token)
        assert payload["usuario_id"] == 99

    def test_payload_contem_perfil(self):
        """O payload decodificado deve conter o perfil correto."""
        token = criar_token_jwt(5, "coordenador")
        payload = decodificar_token_jwt(token)
        assert payload["perfil"] == "coordenador"

    def test_token_invalido_retorna_none(self):
        """Deve retornar None para um token inválido/corrompido."""
        resultado = decodificar_token_jwt("token.invalido.aqui")
        assert resultado is None

    def test_token_vazio_retorna_none(self):
        """Deve retornar None para uma string vazia."""
        resultado = decodificar_token_jwt("")
        assert resultado is None

    def test_token_adulterado_retorna_none(self):
        """Deve retornar None para um token com assinatura adulterada."""
        token = criar_token_jwt(1, "aluno")
        partes = token.split(".")
        token_adulterado = partes[0] + "." + partes[1] + ".assinatura_falsa"
        resultado = decodificar_token_jwt(token_adulterado)
        assert resultado is None
