"""
Módulo de repositórios e modelos de banco de dados SQLite.

Este módulo fornece acesso aos modelos de usuário e funções de inicialização
do banco de dados usando sqlite3 puro (sem ORM).
"""

from .base import get_connection, get_db, init_db, DATABASE_PATH
from .models import (
    create_usuarios_table,
    BaseModel,
    UsuarioModel,
    ProfessorModel,
    CoordenadorModel,
    AlunoModel,
)

__all__ = [
    # Base e configuração
    'get_connection',
    'get_db',
    'init_db',
    'DATABASE_PATH',
    'create_usuarios_table',
    
    # Modelos
    'BaseModel',
    'UsuarioModel',
    'ProfessorModel',
    'CoordenadorModel',
    'AlunoModel',
]
