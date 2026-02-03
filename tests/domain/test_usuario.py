import pytest
from educalin.domain.usuario import Usuario

def test_nao_deve_instanciar_usuario_diretamente():
    """
    Testa se a classe abstrata Usuario não pode ser instanciada diretamente.
    Deve levantar um TypeError, pois é uma classe base abstrata (ABC).
    """
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        Usuario()