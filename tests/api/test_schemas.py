"""
Testes unitários para os schemas Pydantic da API.

Cobre validações de LoginSchema, RegisterSchema, TokenSchema,
UsuarioSchema e UsuarioUpdateSchema.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from educalin.api.schemas import (
    LoginSchema,
    RegisterSchema,
    TokenSchema,
    UsuarioSchema,
    UsuarioUpdateSchema,
    ErrorSchema,
)


class TestLoginSchema:
    """Testes para LoginSchema."""

    def test_login_valido(self):
        """Deve criar LoginSchema com dados válidos."""
        schema = LoginSchema(email="usuario@email.com", senha="senha123")
        assert schema.email == "usuario@email.com"
        assert schema.senha == "senha123"

    def test_email_invalido(self):
        """Deve falhar com email inválido."""
        with pytest.raises(ValidationError):
            LoginSchema(email="email_invalido", senha="senha123")

    def test_senha_muito_curta(self):
        """Deve falhar com senha menor que 8 caracteres."""
        with pytest.raises(ValidationError):
            LoginSchema(email="usuario@email.com", senha="abc")

    def test_senha_exatamente_8_caracteres(self):
        """Deve aceitar senha com exatamente 8 caracteres."""
        schema = LoginSchema(email="usuario@email.com", senha="12345678")
        assert schema.senha == "12345678"

    def test_email_obrigatorio(self):
        """Deve falhar sem email."""
        with pytest.raises(ValidationError):
            LoginSchema(senha="senha123")

    def test_senha_obrigatoria(self):
        """Deve falhar sem senha."""
        with pytest.raises(ValidationError):
            LoginSchema(email="usuario@email.com")


class TestRegisterSchema:
    """Testes para RegisterSchema."""

    def test_register_professor_valido(self):
        """Deve criar RegisterSchema para professor com dados válidos."""
        schema = RegisterSchema(
            nome="João Silva",
            email="joao@email.com",
            senha="senha123",
            tipo="professor",
            registro_funcional="PROF001",
        )
        assert schema.nome == "João Silva"
        assert schema.tipo == "professor"
        assert schema.registro_funcional == "PROF001"

    def test_register_coordenador_valido(self):
        """Deve criar RegisterSchema para coordenador com dados válidos."""
        schema = RegisterSchema(
            nome="Maria Souza",
            email="maria@email.com",
            senha="senha123",
            tipo="coordenador",
            codigo_coordenacao="COORD001",
        )
        assert schema.tipo == "coordenador"
        assert schema.codigo_coordenacao == "COORD001"

    def test_register_aluno_valido(self):
        """Deve criar RegisterSchema para aluno com dados válidos."""
        schema = RegisterSchema(
            nome="Pedro Lima",
            email="pedro@email.com",
            senha="senha123",
            tipo="aluno",
            matricula="2024001",
        )
        assert schema.tipo == "aluno"
        assert schema.matricula == "2024001"

    def test_nome_muito_curto(self):
        """Deve falhar com nome menor que 3 caracteres."""
        with pytest.raises(ValidationError):
            RegisterSchema(
                nome="AB",
                email="joao@email.com",
                senha="senha123",
                tipo="professor",
                registro_funcional="PROF001",
            )

    def test_nome_apenas_espacos(self):
        """Deve falhar com nome contendo apenas espaços."""
        with pytest.raises(ValidationError):
            RegisterSchema(
                nome="   ",
                email="joao@email.com",
                senha="senha123",
                tipo="professor",
                registro_funcional="PROF001",
            )

    def test_nome_strip_preservado(self):
        """Deve remover espaços do início e fim do nome."""
        schema = RegisterSchema(
            nome="  João Silva  ",
            email="joao@email.com",
            senha="senha123",
            tipo="professor",
            registro_funcional="PROF001",
        )
        assert schema.nome == "João Silva"

    def test_senha_apenas_espacos(self):
        """Deve falhar com senha contendo apenas espaços."""
        with pytest.raises(ValidationError):
            RegisterSchema(
                nome="João Silva",
                email="joao@email.com",
                senha="        ",
                tipo="professor",
                registro_funcional="PROF001",
            )

    def test_tipo_invalido(self):
        """Deve falhar com tipo de usuário inválido."""
        with pytest.raises(ValidationError):
            RegisterSchema(
                nome="João Silva",
                email="joao@email.com",
                senha="senha123",
                tipo="admin",
            )

    def test_professor_sem_registro_funcional(self):
        """Deve falhar ao criar professor sem registro_funcional."""
        with pytest.raises(ValueError, match="registro_funcional"):
            RegisterSchema(
                nome="João Silva",
                email="joao@email.com",
                senha="senha123",
                tipo="professor",
            )

    def test_coordenador_sem_codigo_coordenacao(self):
        """Deve falhar ao criar coordenador sem codigo_coordenacao."""
        with pytest.raises(ValueError, match="codigo_coordenacao"):
            RegisterSchema(
                nome="Maria Souza",
                email="maria@email.com",
                senha="senha123",
                tipo="coordenador",
            )

    def test_aluno_sem_matricula(self):
        """Deve falhar ao criar aluno sem matricula."""
        with pytest.raises(ValueError, match="matricula"):
            RegisterSchema(
                nome="Pedro Lima",
                email="pedro@email.com",
                senha="senha123",
                tipo="aluno",
            )

    def test_email_invalido(self):
        """Deve falhar com email inválido."""
        with pytest.raises(ValidationError):
            RegisterSchema(
                nome="João Silva",
                email="email_invalido",
                senha="senha123",
                tipo="professor",
                registro_funcional="PROF001",
            )


class TestTokenSchema:
    """Testes para TokenSchema."""

    def test_token_valido(self):
        """Deve criar TokenSchema com access_token."""
        schema = TokenSchema(access_token="meu_token_jwt")
        assert schema.access_token == "meu_token_jwt"
        assert schema.token_type == "bearer"

    def test_token_type_padrao_bearer(self):
        """Deve usar 'bearer' como valor padrão de token_type."""
        schema = TokenSchema(access_token="token")
        assert schema.token_type == "bearer"

    def test_token_type_invalido(self):
        """Deve falhar com token_type diferente de 'bearer'."""
        with pytest.raises(ValidationError):
            TokenSchema(access_token="token", token_type="invalid")

    def test_access_token_obrigatorio(self):
        """Deve falhar sem access_token."""
        with pytest.raises(ValidationError):
            TokenSchema()


class TestUsuarioSchema:
    """Testes para UsuarioSchema."""

    def test_usuario_professor_valido(self):
        """Deve criar UsuarioSchema para professor com dados válidos."""
        schema = UsuarioSchema(
            id=1,
            nome="João Silva",
            email="joao@email.com",
            tipo_usuario="professor",
            registro_funcional="PROF001",
        )
        assert schema.id == 1
        assert schema.nome == "João Silva"
        assert schema.tipo_usuario == "professor"
        assert schema.criado_em is None
        assert schema.atualizado_em is None

    def test_usuario_com_timestamps(self):
        """Deve criar UsuarioSchema com timestamps opcionais."""
        now = datetime(2024, 1, 1, 10, 0, 0)
        schema = UsuarioSchema(
            id=1,
            nome="João Silva",
            email="joao@email.com",
            tipo_usuario="professor",
            criado_em=now,
            atualizado_em=now,
        )
        assert schema.criado_em == now
        assert schema.atualizado_em == now

    def test_usuario_from_attributes(self):
        """Deve criar UsuarioSchema a partir de objeto com atributos (ORM mode)."""

        class UsuarioMock:
            id = 2
            nome = "Maria Souza"
            email = "maria@email.com"
            tipo_usuario = "coordenador"
            registro_funcional = None
            codigo_coordenacao = "COORD001"
            matricula = None
            criado_em = None
            atualizado_em = None

        schema = UsuarioSchema.model_validate(UsuarioMock())
        assert schema.id == 2
        assert schema.tipo_usuario == "coordenador"
        assert schema.codigo_coordenacao == "COORD001"

    def test_usuario_tipo_invalido(self):
        """Deve falhar com tipo_usuario inválido."""
        with pytest.raises(ValidationError):
            UsuarioSchema(
                id=1,
                nome="João",
                email="joao@email.com",
                tipo_usuario="invalido",
            )

    def test_usuario_campos_obrigatorios(self):
        """Deve falhar sem campos obrigatórios."""
        with pytest.raises(ValidationError):
            UsuarioSchema(nome="João", email="joao@email.com")


class TestUsuarioUpdateSchema:
    """Testes para UsuarioUpdateSchema."""

    def test_update_todos_opcionais(self):
        """Deve criar schema vazio (todos os campos opcionais)."""
        schema = UsuarioUpdateSchema()
        assert schema.nome is None
        assert schema.email is None
        assert schema.senha is None

    def test_update_apenas_nome(self):
        """Deve criar schema com apenas nome."""
        schema = UsuarioUpdateSchema(nome="Novo Nome")
        assert schema.nome == "Novo Nome"
        assert schema.email is None

    def test_update_nome_apenas_espacos(self):
        """Deve falhar com nome contendo apenas espaços."""
        with pytest.raises(ValidationError):
            UsuarioUpdateSchema(nome="   ")

    def test_update_senha_muito_curta(self):
        """Deve falhar com senha menor que 8 caracteres."""
        with pytest.raises(ValidationError):
            UsuarioUpdateSchema(senha="abc")

    def test_update_senha_apenas_espacos(self):
        """Deve falhar com senha contendo apenas espaços."""
        with pytest.raises(ValidationError):
            UsuarioUpdateSchema(senha="        ")

    def test_update_email_invalido(self):
        """Deve falhar com email inválido."""
        with pytest.raises(ValidationError):
            UsuarioUpdateSchema(email="email_invalido")

    def test_update_nome_strip(self):
        """Deve remover espaços do início e fim do nome."""
        schema = UsuarioUpdateSchema(nome="  Novo Nome  ")
        assert schema.nome == "Novo Nome"


class TestErrorSchema:
    """Testes para ErrorSchema."""

    def test_error_valido(self):
        """Deve criar ErrorSchema com mensagem de erro."""
        schema = ErrorSchema(detail="Ocorreu um erro")
        assert schema.detail == "Ocorreu um erro"

    def test_detail_obrigatorio(self):
        """Deve falhar sem campo detail."""
        with pytest.raises(ValidationError):
            ErrorSchema()
