import os
import warnings
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from educalin.utils.security import (
    ALGORITHM,
    TOKEN_EXPIRATION_HOURS,
    _FALLBACK_SECRET_KEY,
    _obter_secret_key,
    criar_token_jwt,
    decodificar_token_jwt,
    hash_senha,
    verificar_senha,
)


# ---------------------------------------------------------------------------
# hash_senha
# ---------------------------------------------------------------------------

class TestHashSenha:
    """Testes para hash_senha()."""

    def test_retorna_string(self):
        """hash_senha deve retornar uma string."""
        resultado = hash_senha("minha_senha_123")
        assert isinstance(resultado, str)

    def test_hash_valido_bcrypt(self):
        """O hash produzido deve ser verificável como bcrypt."""
        import bcrypt
        senha = "senha_teste"
        resultado = hash_senha(senha)
        assert bcrypt.checkpw(senha.encode("utf-8"), resultado.encode("utf-8"))

    def test_hashes_diferentes_para_mesma_senha(self):
        """Dois hashes da mesma senha devem ser diferentes (salt aleatório)."""
        senha = "mesma_senha"
        hash1 = hash_senha(senha)
        hash2 = hash_senha(senha)
        assert hash1 != hash2

    def test_senha_vazia(self):
        """hash_senha deve aceitar senha vazia."""
        resultado = hash_senha("")
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_senha_unicode(self):
        """hash_senha deve lidar com caracteres unicode."""
        resultado = hash_senha("sênha_açúcar_ção")
        assert isinstance(resultado, str)


# ---------------------------------------------------------------------------
# verificar_senha
# ---------------------------------------------------------------------------

class TestVerificarSenha:
    """Testes para verificar_senha()."""

    @pytest.fixture
    def senha_e_hash(self):
        """Fixture com senha em texto plano e seu hash."""
        senha = "senha123"
        return senha, hash_senha(senha)

    def test_senha_correta_retorna_true(self, senha_e_hash):
        """Deve retornar True para senha que corresponde ao hash."""
        senha, h = senha_e_hash
        assert verificar_senha(senha, h) is True

    def test_senha_errada_retorna_false(self, senha_e_hash):
        """Deve retornar False para senha incorreta."""
        _, h = senha_e_hash
        assert verificar_senha("senha_errada", h) is False

    def test_senha_vazia_contra_hash_correto(self):
        """Deve retornar True quando a senha vazia foi hasheada."""
        h = hash_senha("")
        assert verificar_senha("", h) is True

    def test_senha_vazia_contra_hash_incorreto(self, senha_e_hash):
        """Deve retornar False para senha vazia contra hash de outra senha."""
        _, h = senha_e_hash
        assert verificar_senha("", h) is False

    @pytest.mark.parametrize("senha_errada", [
        "SENHA123",
        "senha124",
        " senha123",
        "senha123 ",
    ])
    def test_variantes_erradas_retornam_false(self, senha_e_hash, senha_errada):
        """Variantes próximas da senha correta devem retornar False."""
        _, h = senha_e_hash
        assert verificar_senha(senha_errada, h) is False


# ---------------------------------------------------------------------------
# criar_token_jwt
# ---------------------------------------------------------------------------

class TestCriarTokenJwt:
    """Testes para criar_token_jwt()."""

    def test_retorna_string(self):
        """criar_token_jwt deve retornar uma string."""
        token = criar_token_jwt(1, "aluno")
        assert isinstance(token, str)

    def test_token_decodificavel(self):
        """O token deve ser decodificável com a chave secreta."""
        os.environ["JWT_SECRET_KEY"] = "chave-de-teste-segura"
        try:
            token = criar_token_jwt(42, "professor")
            payload = jwt.decode(token, "chave-de-teste-segura", algorithms=[ALGORITHM])
            assert payload["usuario_id"] == 42
            assert payload["perfil"] == "professor"
        finally:
            del os.environ["JWT_SECRET_KEY"]

    def test_payload_contem_exp_e_iat(self):
        """O payload deve conter os campos 'exp' e 'iat'."""
        os.environ["JWT_SECRET_KEY"] = "chave-de-teste-segura"
        try:
            token = criar_token_jwt(1, "aluno")
            payload = jwt.decode(token, "chave-de-teste-segura", algorithms=[ALGORITHM])
            assert "exp" in payload
            assert "iat" in payload
        finally:
            del os.environ["JWT_SECRET_KEY"]

    def test_expiracao_em_24_horas(self):
        """O token deve expirar em TOKEN_EXPIRATION_HOURS horas."""
        os.environ["JWT_SECRET_KEY"] = "chave-de-teste-segura"
        try:
            antes = datetime.now(timezone.utc).replace(microsecond=0)
            token = criar_token_jwt(1, "aluno")
            depois = datetime.now(timezone.utc).replace(microsecond=0)
            payload = jwt.decode(token, "chave-de-teste-segura", algorithms=[ALGORITHM])
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            assert exp >= antes + timedelta(hours=TOKEN_EXPIRATION_HOURS)
            # buffer de 5 segundos para cobrir o tempo de execução do teste
            assert exp <= depois + timedelta(hours=TOKEN_EXPIRATION_HOURS, seconds=5)
        finally:
            del os.environ["JWT_SECRET_KEY"]

    @pytest.mark.parametrize("perfil", ["aluno", "professor", "coordenador"])
    def test_perfis_validos(self, perfil):
        """Deve criar tokens para todos os perfis suportados."""
        os.environ["JWT_SECRET_KEY"] = "chave-de-teste-segura"
        try:
            token = criar_token_jwt(1, perfil)
            assert isinstance(token, str)
        finally:
            del os.environ["JWT_SECRET_KEY"]


# ---------------------------------------------------------------------------
# decodificar_token_jwt
# ---------------------------------------------------------------------------

class TestDecodificarTokenJwt:
    """Testes para decodificar_token_jwt()."""

    @pytest.fixture(autouse=True)
    def definir_secret_key(self):
        """Define JWT_SECRET_KEY para todos os testes desta classe."""
        os.environ["JWT_SECRET_KEY"] = "chave-de-teste-segura"
        yield
        os.environ.pop("JWT_SECRET_KEY", None)

    def test_token_valido_retorna_payload(self):
        """Token válido deve retornar o payload como dicionário."""
        token = criar_token_jwt(1, "professor")
        payload = decodificar_token_jwt(token)
        assert payload is not None
        assert payload["usuario_id"] == 1
        assert payload["perfil"] == "professor"

    def test_token_invalido_retorna_none(self):
        """Token com assinatura inválida deve retornar None."""
        resultado = decodificar_token_jwt("token.invalido.aqui")
        assert resultado is None

    def test_token_expirado_retorna_none(self):
        """Token já expirado deve retornar None."""
        payload = {
            "usuario_id": 1,
            "perfil": "aluno",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        token_expirado = jwt.encode(payload, "chave-de-teste-segura", algorithm=ALGORITHM)
        resultado = decodificar_token_jwt(token_expirado)
        assert resultado is None

    def test_token_assinado_com_chave_errada_retorna_none(self):
        """Token assinado com outra chave deve retornar None."""
        payload = {
            "usuario_id": 1,
            "perfil": "aluno",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }
        token_outra_chave = jwt.encode(payload, "chave-errada", algorithm=ALGORITHM)
        resultado = decodificar_token_jwt(token_outra_chave)
        assert resultado is None

    def test_string_vazia_retorna_none(self):
        """String vazia como token deve retornar None."""
        resultado = decodificar_token_jwt("")
        assert resultado is None


# ---------------------------------------------------------------------------
# _obter_secret_key
# ---------------------------------------------------------------------------

class TestObterSecretKey:
    """Testes para o comportamento da obtenção da chave secreta."""

    def test_usa_variavel_de_ambiente_quando_configurada(self):
        """Deve retornar o valor da variável de ambiente."""
        os.environ["JWT_SECRET_KEY"] = "minha-chave-secreta"
        try:
            chave = _obter_secret_key()
            assert chave == "minha-chave-secreta"
        finally:
            del os.environ["JWT_SECRET_KEY"]

    def test_emite_aviso_quando_variavel_nao_configurada(self):
        """Deve emitir UserWarning quando JWT_SECRET_KEY não está definida."""
        os.environ.pop("JWT_SECRET_KEY", None)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            chave = _obter_secret_key()
            assert any(issubclass(warning.category, UserWarning) for warning in w)
            assert any("JWT_SECRET_KEY" in str(warning.message) for warning in w)

    def test_retorna_fallback_quando_variavel_nao_configurada(self):
        """Deve retornar a chave fallback quando JWT_SECRET_KEY não está definida."""
        os.environ.pop("JWT_SECRET_KEY", None)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            chave = _obter_secret_key()
        assert chave == _FALLBACK_SECRET_KEY
