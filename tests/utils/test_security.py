"""
Testes unitários para o módulo de segurança (src/educalin/utils/security.py).

Cobre: hash_senha, verificar_senha, criar_token_jwt e decodificar_token_jwt.
"""

import time
from datetime import datetime, timedelta, timezone

import pytest

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
        senha = "minha_senha_123"
        assert hash_senha(senha) != senha

    def test_hashes_diferentes_para_mesma_senha(self):
        """Chamadas distintas devem gerar hashes distintos (salt aleatório)."""
        senha = "minha_senha_123"
        assert hash_senha(senha) != hash_senha(senha)

    def test_hash_nao_vazio(self):
        """O hash não deve ser vazio."""
        assert hash_senha("senha") != ""


class TestVerificarSenha:
    """Testes para a função verificar_senha."""

    def test_senha_correta_retorna_true(self):
        """Deve retornar True quando a senha corresponde ao hash."""
        senha = "senha_correta_123"
        h = hash_senha(senha)
        assert verificar_senha(senha, h) is True

    def test_senha_incorreta_retorna_false(self):
        """Deve retornar False quando a senha não corresponde ao hash."""
        h = hash_senha("senha_correta_123")
        assert verificar_senha("senha_errada", h) is False

    def test_senha_vazia_incorreta(self):
        """Deve retornar False para senha vazia comparada a hash não-vazio."""
        h = hash_senha("senha123")
        assert verificar_senha("", h) is False

    def test_case_sensitive(self):
        """A verificação deve ser sensível a maiúsculas/minúsculas."""
        h = hash_senha("SenhaMaiuscula")
        assert verificar_senha("senhamaiuscula", h) is False


class TestCriarTokenJwt:
    """Testes para a função criar_token_jwt."""

    def test_retorna_string(self):
        """Deve retornar uma string."""
        token = criar_token_jwt(1, "professor")
        assert isinstance(token, str)

    def test_token_nao_vazio(self):
        """O token não deve ser vazio."""
        assert criar_token_jwt(1, "aluno") != ""

    def test_tokens_diferentes_para_ids_diferentes(self):
        """Tokens gerados para IDs distintos devem ser diferentes."""
        token1 = criar_token_jwt(1, "professor")
        token2 = criar_token_jwt(2, "professor")
        assert token1 != token2

    def test_payload_contem_usuario_id(self):
        """O payload decodificado deve conter o usuario_id correto."""
        token = criar_token_jwt(42, "aluno")
        payload = decodificar_token_jwt(token)
        assert payload is not None
        assert payload["usuario_id"] == 42

    def test_payload_contem_perfil(self):
        """O payload decodificado deve conter o perfil correto."""
        token = criar_token_jwt(1, "coordenador")
        payload = decodificar_token_jwt(token)
        assert payload is not None
        assert payload["perfil"] == "coordenador"

    def test_payload_contem_exp(self):
        """O payload deve conter o campo de expiração."""
        token = criar_token_jwt(1, "professor")
        payload = decodificar_token_jwt(token)
        assert payload is not None
        assert "exp" in payload

    def test_payload_contem_iat(self):
        """O payload deve conter o campo issued-at."""
        token = criar_token_jwt(1, "professor")
        payload = decodificar_token_jwt(token)
        assert payload is not None
        assert "iat" in payload


class TestDecodificarTokenJwt:
    """Testes para a função decodificar_token_jwt."""

    def test_token_valido_retorna_dict(self):
        """Deve retornar um dicionário para token válido."""
        token = criar_token_jwt(1, "professor")
        resultado = decodificar_token_jwt(token)
        assert isinstance(resultado, dict)

    def test_token_invalido_retorna_none(self):
        """Deve retornar None para token inválido."""
        assert decodificar_token_jwt("token.invalido.aqui") is None

    def test_token_vazio_retorna_none(self):
        """Deve retornar None para string vazia."""
        assert decodificar_token_jwt("") is None

    def test_token_adulterado_retorna_none(self):
        """Deve retornar None para token com assinatura adulterada."""
        token = criar_token_jwt(1, "professor")
        partes = token.split(".")
        partes[2] = "assinaturafalsa"
        token_adulterado = ".".join(partes)
        assert decodificar_token_jwt(token_adulterado) is None

    def test_token_expirado_retorna_none(self):
        """Deve retornar None para token expirado."""
        import jwt as pyjwt
        from educalin.utils.security import ALGORITHM, _get_secret_key

        payload = {
            "usuario_id": 1,
            "perfil": "professor",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=25),
        }
        token_expirado = pyjwt.encode(payload, _get_secret_key(), algorithm=ALGORITHM)
        assert decodificar_token_jwt(token_expirado) is None
