"""
Módulo de rotas da API.

Este pacote contém todos os routers FastAPI organizados por domínio.
"""

from . import auth
from . import materiais

__all__ = ["auth", "materiais"]
