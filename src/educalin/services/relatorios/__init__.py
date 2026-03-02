"""
Módulo de geração de relatórios.

Fornece classe base abstrata e implementações concretas para
diferentes tipos de relatórios usando Template Method Pattern.
"""

from .base import (
    GeradorRelatorio,
    FormatoRelatorio,
    RelatorioVazioException
)

from .turma import RelatorioTurma
from .individual import RelatorioIndividual

__all__ = [
    'GeradorRelatorio',
    'FormatoRelatorio',
    'RelatorioVazioException',
    'RelatorioTurma',
    'RelatorioIndividual',
]