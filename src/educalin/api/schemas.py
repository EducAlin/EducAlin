"""
Schemas Pydantic para validação de dados da API.

Define modelos de dados para requisições e respostas da API REST.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
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


# ========================= SCHEMAS DE MATERIAIS =========================


class MaterialResponseSchema(BaseModel):
    """
    Schema para resposta de um material individual.

    Retorna os dados de um material específico, incluindo
    informações polimórficas baseadas no tipo.

    Attributes:
        id: ID único do material
        tipo_material: Tipo do material (pdf, video, link)
        titulo: Título do material
        descricao: Descrição do material
        autor_id: ID do professor (autor)
        topico: Tópico/área de estudo
        data_upload: Data de upload do material
        num_paginas: Número de páginas (apenas para PDF)
        duracao_segundos: Duração em segundos (apenas para vídeo)
        codec: Codec do vídeo (apenas para vídeo)
        url: URL do material (apenas para link)
        tipo_conteudo: Tipo de conteúdo (apenas para link)
    """
    id: int = Field(
        ...,
        description="ID único do material",
        json_schema_extra={"example": 1}
    )
    tipo_material: Literal["pdf", "video", "link"] = Field(
        ...,
        description="Tipo de material",
        json_schema_extra={"example": "pdf"}
    )
    titulo: str = Field(
        ...,
        description="Título do material",
        json_schema_extra={"example": "Introdução à POO"}
    )
    descricao: str = Field(
        ...,
        description="Descrição do material",
        json_schema_extra={"example": "Conceitos fundamentais de Programação Orientada a Objetos"}
    )
    autor_id: int = Field(
        ...,
        description="ID do professor autor",
        json_schema_extra={"example": 1}
    )
    topico: Optional[str] = Field(
        None,
        description="Tópico ou área de estudo",
        json_schema_extra={"example": "Programação"}
    )
    data_upload: datetime = Field(
        ...,
        description="Data de upload do material",
        json_schema_extra={"example": "2024-01-01T10:00:00"}
    )

    # Campos específicos por tipo (podem ser None)
    num_paginas: Optional[int] = Field(
        None,
        description="Número de páginas (apenas PDF)",
        json_schema_extra={"example": 50}
    )
    duracao_segundos: Optional[int] = Field(
        None,
        description="Duração em segundos (apenas vídeo)",
        json_schema_extra={"example": 3600}
    )
    codec: Optional[str] = Field(
        None,
        description="Codec do vídeo (apenas vídeo)",
        json_schema_extra={"example": "h264"}
    )
    url: Optional[str] = Field(
        None,
        description="URL do material (apenas link)",
        json_schema_extra={"example": "https://example.com/material"}
    )
    tipo_conteudo: Optional[str] = Field(
        None,
        description="Tipo de conteúdo (apenas link)",
        json_schema_extra={"example": "artigo"}
    )


class MaterialListSchema(BaseModel):
    """
    Schema para listagem de materiais.

    Retorna um conjunto de materiais com paginação.

    Attributes:
        total: Quantidade total de materiais
        materiais: Lista de materiais
    """
    total: int = Field(
        ...,
        description="Quantidade total de materiais",
        json_schema_extra={"example": 5}
    )
    materiais: list[MaterialResponseSchema] = Field(
        ...,
        description="Lista de materiais",
        json_schema_extra={"example": []}
    )


class MaterialUploadSchema(BaseModel):
    """
    Schema para requisição de upload de material.

    Attributes:
        titulo: Título do material
        descricao: Descrição do material
        topico: Tópico ou área de estudo
        num_paginas: Número de páginas (obrigatório apenas para PDF)
        duracao_segundos: Duração em segundos (obrigatório para vídeo)
        codec: Codec do vídeo (obrigatório para vídeo)
    """
    titulo: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Título do material",
        json_schema_extra={"example": "Introdução à POO"}
    )
    descricao: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Descrição do material",
        json_schema_extra={"example": "Conceitos fundamentais de Programação Orientada a Objetos"}
    )
    topico: Optional[str] = Field(
        None,
        max_length=100,
        description="Tópico ou área de estudo",
        json_schema_extra={"example": "Programação"}
    )

    # Campos específicos por tipo (opcionais no schema, validados posteriormente)
    num_paginas: Optional[int] = Field(
        None,
        ge=1,
        description="Número de páginas (obrigatório para PDF)",
        json_schema_extra={"example": 50}
    )
    duracao_segundos: Optional[int] = Field(
        None,
        ge=1,
        description="Duração em segundos (obrigatório para vídeo)",
        json_schema_extra={"example": 3600}
    )
    codec: Optional[str] = Field(
        None,
        max_length=50,
        description="Codec do vídeo (obrigatório para vídeo)",
        json_schema_extra={"example": "h264"}
    )

    @field_validator('titulo', 'descricao')
    @classmethod
    def validate_titulo_descricao(cls, v: str) -> str:
        """Valida que título/descrição não sejam vazios após strip."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Campo não pode ser vazio")
        return v

    @field_validator('topico')
    @classmethod
    def validate_topico(cls, v: Optional[str]) -> Optional[str]:
        """Valida tópico se fornecido."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Tópico não pode ser vazio")
        return v

    @field_validator('codec')
    @classmethod
    def validate_codec(cls, v: Optional[str]) -> Optional[str]:
        """Valida codec se fornecido."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Codec não pode ser vazio")
        return v


# ========================= SCHEMAS DE PLANOS DE AÇÃO =========================


class PlanoAcaoCreateSchema(BaseModel):
    """
    Schema para criação de um novo Plano de Ação.

    Attributes:
        objetivo: Objetivo/descrição do plano
        prazo_dias: Número de dias até a data limite
        observacoes: Observações adicionais (opcional)
    """
    objetivo: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Objetivo ou descrição do plano",
        json_schema_extra={"example": "Melhorar desempenho em Matemática"}
    )
    prazo_dias: int = Field(
        ...,
        ge=1,
        le=365,
        description="Prazo em dias (1-365)",
        json_schema_extra={"example": 30}
    )
    observacoes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observações adicionais",
        json_schema_extra={"example": "Foco em álgebra básica"}
    )

    @field_validator('objetivo')
    @classmethod
    def validate_objetivo(cls, v: str) -> str:
        """Valida que o objetivo não seja vazio após strip."""
        v = v.strip()
        if not v:
            raise ValueError("Objetivo não pode ser vazio")
        return v

    @field_validator('observacoes')
    @classmethod
    def validate_observacoes(cls, v: Optional[str]) -> Optional[str]:
        """Valida observações se fornecidas."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Observações não podem ser vazias")
        return v


class PlanoAcaoMaterialSchema(BaseModel):
    """
    Schema para adicionar/remover material de um Plano de Ação.

    Attributes:
        material_id: ID do material a adicionar
    """
    material_id: int = Field(
        ...,
        ge=1,
        description="ID do material",
        json_schema_extra={"example": 1}
    )


class PlanoAcaoStatusSchema(BaseModel):
    """
    Schema para atualizar o status de um Plano de Ação.

    Attributes:
        status: Novo status (rascunho, enviado, em_andamento, concluido, cancelado)
    """
    status: Literal["rascunho", "enviado", "em_andamento", "concluido", "cancelado"] = Field(
        ...,
        description="Novo status do plano",
        json_schema_extra={"example": "enviado"}
    )


class PlanoAcaoResponseSchema(BaseModel):
    """
    Schema para resposta de um Plano de Ação.

    Attributes:
        id: ID único do plano
        aluno_id: ID do aluno
        objetivo: Objetivo do plano
        status: Status atual
        data_criacao: Data de criação
        data_limite: Data limite/prazo
        observacoes: Observações adicionais
        materiais: IDs dos materiais adicionados
    """
    id: int = Field(
        ...,
        description="ID único do plano",
        json_schema_extra={"example": 1}
    )
    aluno_id: int = Field(
        ...,
        description="ID do aluno destinatário",
        json_schema_extra={"example": 1}
    )
    objetivo: str = Field(
        ...,
        description="Objetivo do plano",
        json_schema_extra={"example": "Melhorar desempenho em Matemática"}
    )
    status: Literal["rascunho", "enviado", "em_andamento", "concluido", "cancelado"] = Field(
        ...,
        description="Status atual do plano",
        json_schema_extra={"example": "enviado"}
    )
    data_criacao: datetime = Field(
        ...,
        description="Data de criação do plano",
        json_schema_extra={"example": "2024-01-01T10:00:00"}
    )
    data_limite: datetime = Field(
        ...,
        description="Data limite para conclusão",
        json_schema_extra={"example": "2024-02-01T10:00:00"}
    )
    observacoes: Optional[str] = Field(
        None,
        description="Observações adicionais",
        json_schema_extra={"example": "Foco em álgebra básica"}
    )
    materiais: list[int] = Field(
        default_factory=list,
        description="IDs dos materiais adicionados ao plano",
        json_schema_extra={"example": [1, 2, 3]}
    )


class PlanoAcaoListSchema(BaseModel):
    """
    Schema para listagem de Planos de Ação.

    Attributes:
        total: Quantidade total de planos
        planos: Lista de planos
    """
    total: int = Field(
        ...,
        description="Quantidade total de planos",
        json_schema_extra={"example": 5}
    )
    planos: list[PlanoAcaoResponseSchema] = Field(
        ...,
        description="Lista de planos",
        json_schema_extra={"example": []}
    )
