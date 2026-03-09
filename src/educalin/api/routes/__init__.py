"""
Módulo de rotas da API.

Este pacote contém todos os routers FastAPI organizados por domínio.
"""

from . import auth, notas, turmas

__all__ = ["auth", "notas", "turmas"]
