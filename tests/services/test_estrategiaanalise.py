"""
Testes para as estratégias de análise de desempenho.
"""
import pytest
from educalin.services.estrategiaanalise import EstrategiaAnalise


class TestEstrategiaAnalise:
    """Testes para a classe abstrata EstrategiaAnalise."""
    
    def test_nao_pode_instanciar_classe_abstrata(self):
        """Testa que não é possível instanciar a classe abstrata."""
        with pytest.raises(TypeError):
            EstrategiaAnalise()