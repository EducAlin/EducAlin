"""
Schemas Pydantic para validação de dados da API.

Define modelos de dados para requisições e respostas da API REST.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Literal, Optional
from datetime import datetime


class LoginSchema(BaseModel):
    """
    Schema para autenticação de usuário.
    
    Attributes:
        email: Email do usuário
        senha: Senha em texto plano
    """
    email: EmailStr = Field(
        ...,
        description="Email do usuário",
        json_schema_extra={"example": "usuario@email.com"}
    )
    senha: str = Field(
        ...,
        min_length=8,
        description="Senha do usuário (mínimo 8 caracteres)",
        json_schema_extra={"example": "senha123"}
    )


class RegisterSchema(BaseModel):
    """
    Schema para registro de novo usuário.
    
    Attributes:
        nome: Nome completo do usuário
        email: Email único do usuário
        senha: Senha (mínimo 8 caracteres)
        tipo: Tipo de usuário (professor, coordenador, aluno)
        registro_funcional: Registro funcional (apenas para professor)
        codigo_coordenacao: Código de coordenação (apenas para coordenador)
        matricula: Matrícula do aluno (apenas para aluno)
    """
    nome: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Nome completo do usuário",
        json_schema_extra={"example": "João Silva"}
    )
    email: EmailStr = Field(
        ...,
        description="Email único do usuário",
        json_schema_extra={"example": "joao@email.com"}
    )
    senha: str = Field(
        ...,
        min_length=8,
        description="Senha do usuário (mínimo 8 caracteres)",
        json_schema_extra={"example": "senha12345"}
    )
    tipo: Literal["professor", "coordenador", "aluno"] = Field(
        ...,
        description="Tipo de usuário",
        json_schema_extra={"example": "professor"}
    )
    
    # Campos específicos por tipo
    registro_funcional: Optional[str] = Field(
        None,
        description="Registro funcional (obrigatório para professor)",
        json_schema_extra={"example": "PROF001"}
    )
    codigo_coordenacao: Optional[str] = Field(
        None,
        description="Código de coordenação (obrigatório para coordenador)",
        json_schema_extra={"example": "COORD001"}
    )
    matricula: Optional[str] = Field(
        None,
        description="Matrícula (obrigatória para aluno)",
        json_schema_extra={"example": "2024001"}
    )
    
    @field_validator('nome')
    @classmethod
    def validate_nome(cls, v: str) -> str:
        """Valida que o nome não seja vazio após strip."""
        v = v.strip()
        if not v:
            raise ValueError("Nome não pode ser vazio")
        return v
    
    @field_validator('senha')
    @classmethod
    def validate_senha(cls, v: str) -> str:
        """Valida requisitos mínimos de senha."""
        if len(v) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")
        if v.isspace():
            raise ValueError("Senha não pode conter apenas espaços")
        return v
    
    @model_validator(mode='after')
    def validate_campos_por_tipo(self) -> 'RegisterSchema':
        """Valida campos específicos por tipo após inicialização."""
        if self.tipo == 'professor' and not self.registro_funcional:
            raise ValueError("registro_funcional é obrigatório para professores")
        if self.tipo == 'coordenador' and not self.codigo_coordenacao:
            raise ValueError("codigo_coordenacao é obrigatório para coordenadores")
        if self.tipo == 'aluno' and not self.matricula:
            raise ValueError("matricula é obrigatória para alunos")
        return self


class TokenSchema(BaseModel):
    """
    Schema para resposta de autenticação com token JWT.
    
    Attributes:
        access_token: Token JWT de acesso
        token_type: Tipo do token (sempre "bearer")
    """
    access_token: str = Field(
        ...,
        description="Token JWT de acesso",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    token_type: Literal["bearer"] = Field(
        default="bearer",
        description="Tipo do token",
        json_schema_extra={"example": "bearer"}
    )


class UsuarioSchema(BaseModel):
    """
    Schema para representação de usuário na API.
    
    Attributes:
        id: ID do usuário
        nome: Nome completo
        email: Email do usuário
        tipo_usuario: Tipo de usuário
        registro_funcional: Registro funcional (se professor)
        codigo_coordenacao: Código de coordenação (se coordenador)
        matricula: Matrícula (se aluno)
        criado_em: Data de criação
        atualizado_em: Data de última atualização
    """
    id: int = Field(
        ...,
        description="ID único do usuário",
        json_schema_extra={"example": 1}
    )
    nome: str = Field(
        ...,
        description="Nome completo do usuário",
        json_schema_extra={"example": "João Silva"}
    )
    email: EmailStr = Field(
        ...,
        description="Email do usuário",
        json_schema_extra={"example": "joao@email.com"}
    )
    tipo_usuario: Literal["professor", "coordenador", "aluno"] = Field(
        ...,
        description="Tipo de usuário",
        json_schema_extra={"example": "professor"}
    )
    
    # Campos específicos opcionais
    registro_funcional: Optional[str] = Field(
        None,
        description="Registro funcional (apenas professores)",
        json_schema_extra={"example": "PROF001"}
    )
    codigo_coordenacao: Optional[str] = Field(
        None,
        description="Código de coordenação (apenas coordenadores)",
        json_schema_extra={"example": "COORD001"}
    )
    matricula: Optional[str] = Field(
        None,
        description="Matrícula (apenas alunos)",
        json_schema_extra={"example": "2024001"}
    )
    
    criado_em: Optional[datetime] = Field(
        None,
        description="Data de criação do usuário",
        json_schema_extra={"example": "2024-01-01T10:00:00"}
    )
    atualizado_em: Optional[datetime] = Field(
        None,
        description="Data de última atualização",
        json_schema_extra={"example": "2024-01-01T10:00:00"}
    )
    
    model_config = ConfigDict(from_attributes=True)


class UsuarioUpdateSchema(BaseModel):
    """
    Schema para atualização de dados de usuário.
    
    Todos os campos são opcionais.
    """
    nome: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Novo nome do usuário",
        json_schema_extra={"example": "João Silva Santos"}
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Novo email do usuário",
        json_schema_extra={"example": "joao.novo@email.com"}
    )
    senha: Optional[str] = Field(
        None,
        min_length=8,
        description="Nova senha (mínimo 8 caracteres)",
        json_schema_extra={"example": "novasenha123"}
    )
    
    @field_validator('nome')
    @classmethod
    def validate_nome(cls, v: Optional[str]) -> Optional[str]:
        """Valida que o nome não seja vazio após strip."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Nome não pode ser vazio")
        return v
    
    @field_validator('senha')
    @classmethod
    def validate_senha(cls, v: Optional[str]) -> Optional[str]:
        """Valida requisitos mínimos de senha."""
        if v is not None:
            if len(v) < 8:
                raise ValueError("Senha deve ter no mínimo 8 caracteres")
            if v.isspace():
                raise ValueError("Senha não pode conter apenas espaços")
        return v


class RecuperarSenhaSchema(BaseModel):
    """
    Schema para solicitação de recuperação de senha.
    
    Attributes:
        email: Email do usuário que deseja recuperar a senha
    """
    email: EmailStr = Field(
        ...,
        description="Email do usuário",
        json_schema_extra={"example": "usuario@email.com"}
    )


class ErrorSchema(BaseModel):
    """
    Schema para respostas de erro.
    
    Attributes:
        detail: Mensagem de erro detalhada
    """
    detail: str = Field(
        ...,
        description="Mensagem de erro",
        json_schema_extra={"example": "Erro ao processar requisição"}
    )
