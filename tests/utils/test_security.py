"""
Testes para o módulo utils/security.py.

Cobre hash/verificação de senha e encode/decode de JWT.
"""

import time
import pytest

from educalin.utils.security import (
    hash_senha,
    verificar_senha,
    criar_token_jwt,
    decodificar_token_jwt,
    TOKEN_EXPIRATION_HOURS,
)


class TestHashSenha:
    """Testes para a função hash_senha."""

    def test_retorna_string(self):
        """Deve retornar uma string."""
        resultado = hash_senha("minha_senha_123")
        assert isinstance(resultado, str)

    def test_hash_diferente_da_senha_original(self):
        """O hash não deve ser igual à senha original."""
        senha = "senha_original"
        assert hash_senha(senha) != senha

    def test_hashes_diferentes_para_mesma_senha(self):
        """Duas chamadas com a mesma senha devem gerar hashes diferentes (salt)."""
        senha = "senha_igual"
        assert hash_senha(senha) != hash_senha(senha)

    def test_hash_nao_vazio(self):
        """O hash não deve ser uma string vazia."""
        assert hash_senha("qualquer_senha") != ""


class TestVerificarSenha:
    """Testes para a função verificar_senha."""

    def test_senha_correta_retorna_true(self):
        """Deve retornar True para senha correta."""
        senha = "senha_correta_123"
        hash_gerado = hash_senha(senha)
        assert verificar_senha(senha, hash_gerado) is True

    def test_senha_errada_retorna_false(self):
        """Deve retornar False para senha incorreta."""
        hash_gerado = hash_senha("senha_correta")
        assert verificar_senha("senha_errada", hash_gerado) is False

    def test_senha_vazia_retorna_false(self):
        """Deve retornar False para senha vazia contra hash de senha não-vazia."""
        hash_gerado = hash_senha("senha_nao_vazia")
        assert verificar_senha("", hash_gerado) is False

    def test_hash_de_senha_diferente_retorna_false(self):
        """Deve retornar False quando o hash não corresponde à senha."""
        hash_outra_senha = hash_senha("outra_senha")
        assert verificar_senha("minha_senha", hash_outra_senha) is False


class TestCriarTokenJwt:
    """Testes para a função criar_token_jwt."""

    def test_retorna_string(self):
        """Deve retornar uma string."""
        token = criar_token_jwt(1, "aluno")
        assert isinstance(token, str)

    def test_token_nao_vazio(self):
        """O token não deve ser uma string vazia."""
        assert criar_token_jwt(42, "professor") != ""

    def test_token_decodificavel(self):
        """O token criado deve ser decodificável."""
        token = criar_token_jwt(10, "coordenador")
        payload = decodificar_token_jwt(token)
        assert payload is not None

    def test_payload_contem_usuario_id(self):
        """O payload deve conter o usuario_id correto."""
        token = criar_token_jwt(99, "aluno")
        payload = decodificar_token_jwt(token)
        assert payload["usuario_id"] == 99

    def test_payload_contem_perfil(self):
        """O payload deve conter o perfil correto."""
        token = criar_token_jwt(1, "professor")
        payload = decodificar_token_jwt(token)
        assert payload["perfil"] == "professor"

    def test_payload_contem_exp(self):
        """O payload deve conter o campo de expiração."""
        token = criar_token_jwt(1, "aluno")
        payload = decodificar_token_jwt(token)
        assert "exp" in payload

    def test_payload_contem_iat(self):
        """O payload deve conter o campo de emissão."""
        token = criar_token_jwt(1, "aluno")
        payload = decodificar_token_jwt(token)
        assert "iat" in payload

    @pytest.mark.parametrize("perfil", ["aluno", "professor", "coordenador"])
    def test_diferentes_perfis(self, perfil):
        """Deve criar tokens para todos os perfis válidos."""
        token = criar_token_jwt(1, perfil)
        payload = decodificar_token_jwt(token)
        assert payload["perfil"] == perfil


class TestDecodificarTokenJwt:
    """Testes para a função decodificar_token_jwt."""

    def test_token_valido_retorna_payload(self):
        """Deve retornar o payload para token válido."""
        token = criar_token_jwt(5, "aluno")
        payload = decodificar_token_jwt(token)
        assert payload is not None
        assert payload["usuario_id"] == 5

    def test_token_invalido_retorna_none(self):
        """Deve retornar None para token completamente inválido."""
        resultado = decodificar_token_jwt("token.invalido.aqui")
        assert resultado is None

    def test_token_vazio_retorna_none(self):
        """Deve retornar None para string vazia."""
        resultado = decodificar_token_jwt("")
        assert resultado is None

    def test_token_adulterado_retorna_none(self):
        """Deve retornar None para token com assinatura adulterada."""
        token = criar_token_jwt(1, "aluno")
        partes = token.split(".")
        token_adulterado = partes[0] + "." + partes[1] + ".assinatura_falsa"
        resultado = decodificar_token_jwt(token_adulterado)
        assert resultado is None

    def test_token_expirado_retorna_none(self):
        """Deve retornar None para token expirado."""
        import jwt
        from datetime import datetime, timedelta, timezone
        from educalin.utils.security import SECRET_KEY, ALGORITHM

        payload_expirado = {
            "usuario_id": 1,
            "perfil": "aluno",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=25),
        }
        token_expirado = jwt.encode(payload_expirado, SECRET_KEY, algorithm=ALGORITHM)
        resultado = decodificar_token_jwt(token_expirado)
        assert resultado is None
