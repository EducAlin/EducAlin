"""
Modelos de banco de dados usando SQLite puro (sem ORM).

Este módulo agrega e exporta os modelos do sistema.
Os modelos estão organizados em módulos separados para melhor manutenibilidade:

- schemas.py: Definições de tabelas (DDL)
- base_model.py: Classe base com validações
- usuario_models.py: Modelos de usuário (STI)
- turma_models.py: Modelos de turma com relacionamentos
- material_models.py: Modelos de material de estudo (STI com polimorfismo)
- avaliacao_models.py: Modelos de avaliação
- nota_models.py: Modelos de nota (classe de associação)
- meta_models.py: Modelos de meta de aprendizado
- plano_acao_models.py: Modelos de plano de ação com composição

Para facilitar o uso, este arquivo importa e re-exporta tudo.
"""

# Importa schemas
from .schemas import (
    create_usuarios_table,
    create_turmas_tables,
    create_materiais_table,
    create_avaliacoes_table,
    create_notas_table,
    create_metas_table,
    create_planos_acao_tables,
    create_all_tables,
)

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

# Importa modelos de material (STI com polimorfismo)
from .material_models import (
    MaterialModel,
    MaterialPDFModel,
    MaterialVideoModel,
    MaterialLinkModel,
)

# Importa modelos de avaliação, nota e meta
from .avaliacao_models import AvaliacaoModel
from .nota_models import NotaModel
from .meta_models import MetaModel

# Importa modelos de plano de ação
from .plano_acao_models import PlanoAcaoModel

# Importa repositórios
from .usuario_repository import UsuarioRepository
from .material_repository import MaterialRepository


# Exporta tudo para facilitar imports
__all__ = [
    # Schemas
    'create_usuarios_table',
    'create_turmas_tables',
    'create_materiais_table',
    'create_avaliacoes_table',
    'create_notas_table',
    'create_metas_table',
    'create_planos_acao_tables',
    'create_all_tables',
    
    # Base
    'BaseModel',
    
    # Usuários (STI)
    'UsuarioModel',
    'ProfessorModel',
    'CoordenadorModel',
    'AlunoModel',
    
    # Turmas
    'TurmaModel',
    
    # Materiais (STI com polimorfismo)
    'MaterialModel',
    'MaterialPDFModel',
    'MaterialVideoModel',
    'MaterialLinkModel',
    
    # Avaliações e Notas
    'AvaliacaoModel',
    'NotaModel',
    
    # Metas
    'MetaModel',
    
    # Planos de Ação
    'PlanoAcaoModel',
    
    # Repositórios
    'UsuarioRepository',
    'MaterialRepository',
]

