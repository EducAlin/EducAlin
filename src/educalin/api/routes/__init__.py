"""
Módulo de rotas da API.

Este pacote contém todos os routers FastAPI organizados por domínio.
"""

from . import auth, turmas, materiais, planos

__all__ = ["auth", "turmas", "materiais", "planos"]
