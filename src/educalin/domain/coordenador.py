import uuid
import re
from .usuario import Usuario
from ..utils.mixins import AutenticavelMixin

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class Coordenador(Usuario, AutenticavelMixin):
    """
    Representa um coordenador no sistema.

    O coordenador pode fazer tudo que um usuário faz e também tem
    permissões especiais, como comparar turmas e gerar relatórios gerais.
    """
    def __init__(self, nome: str, email: str, senha: str, codigo_coordenacao: str = None):
        """
        Cria uma nova instância de Coordenador.

        Args:
            nome (str): O nome completo do coordenador.
            email (str): O e-mail de login.
            senha (str): A senha, que será armazenada com hash.
            codigo_coordenacao (str, optional): O código único do coordenador. Se não fornecido, será gerado automaticamente.
        """
        self.nome = nome
        self.email = email
        self.senha = senha
        self.__codigo_coordenacao = codigo_coordenacao or str(uuid.uuid4())

    @property
    def codigo_coordenacao(self):
        """Pega o código de coordenação (imutável)."""
        return self.__codigo_coordenacao

    @staticmethod
    def comparar_turmas(turma1, turma2):
        """
        Compara duas turmas pra ver se são a mesma, olhando pelo código.

        Esse método é estático porque ele não precisa de nenhuma informação
        específica de um coordenador pra funcionar, só das turmas.

        Args:
            turma1 (Turma): A primeira turma pra comparar.
            turma2 (Turma): A segunda turma pra comparar.

        Returns:
            bool: Retorna True se os códigos forem iguais, se não, False.
        """
        return turma1.codigo == turma2.codigo
