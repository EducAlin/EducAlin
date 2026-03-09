"""
Módulo de rotas da API.

Este pacote contém todos os routers FastAPI organizados por domínio.
"""

from . import auth, turmas, notas, materiais, planos, views

__all__ = ["auth", "turmas", "notas", "materiais", "planos", "views"]
