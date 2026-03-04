"""
Modelos de banco de dados usando SQLite puro (sem ORM).

Este módulo agrega e exporta os modelos do sistema.
Os modelos estão organizados em módulos separados para melhor manutenibilidade:

- schemas.py: Definições de tabelas (DDL)
- base_model.py: Classe base com validações
- usuario_models.py: Modelos de usuário (STI)
- turma_models.py: Modelos de turma com relacionamentos

Para facilitar o uso, este arquivo importa e re-exporta tudo.
"""

# Importa schemas
from .schemas import create_usuarios_table, create_turmas_tables

# Importa classe base
from .base_model import BaseModel

# Importa modelos de usuário (STI)
from .usuario_models import (
    UsuarioModel,
    ProfessorModel,
    CoordenadorModel,
    AlunoModel,
)

# Importa modelos de turma
from .turma_models import TurmaModel


# Exporta tudo para facilitar imports
__all__ = [
    # Schemas
    'create_usuarios_table',
    'create_turmas_tables',
    
    # Base
    'BaseModel',
    
    # Usuários (STI)
    'UsuarioModel',
    'ProfessorModel',
    'CoordenadorModel',
    'AlunoModel',
    
    # Turmas
    'TurmaModel',
]
