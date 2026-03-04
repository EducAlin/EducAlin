"""
Modelos de banco de dados usando SQLite puro (sem ORM).

Este módulo agrega e exporta os modelos de usuário.
Os modelos estão organizados em módulos separados para melhor manutenibilidade:

- schemas.py: Definições de tabelas (DDL)
- base_model.py: Classe base com validações
- usuario_models.py: Modelos de usuário (STI)

Para facilitar o uso, este arquivo importa e re-exporta tudo.
"""

# Importa schemas
from .schemas import create_usuarios_table

# Importa classe base
from .base_model import BaseModel

# Importa modelos de usuário (STI)
from .usuario_models import (
    UsuarioModel,
    ProfessorModel,
    CoordenadorModel,
    AlunoModel,
)


# Exporta tudo para facilitar imports
__all__ = [
    # Schemas
    'create_usuarios_table',
    
    # Base
    'BaseModel',
    
    # Usuários (STI)
    'UsuarioModel',
    'ProfessorModel',
    'CoordenadorModel',
    'AlunoModel',
]
