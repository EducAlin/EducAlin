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
    def __init__(self, nome: str, email: str, senha: str, codigo_coordenacao: str):
        """
        Cria uma nova instância de Coordenador.

        Args:
            nome (str): O nome completo do coordenador.
            email (str): O e-mail de login.
            senha (str): A senha, que será armazenada com hash.
            codigo_coordenacao (str): O código único do coordenador.
        """
        self.nome = nome
        self.email = email
        self.senha = self._hash_senha(senha)
        self.__codigo_coordenacao = codigo_coordenacao

    @property
    def nome(self):
        """Pega o nome do coordenador."""
        return self._nome
    
    @nome.setter
    def nome(self, novo_nome):
        """
        Atualiza o nome do coordenador.

        Args:
            novo_nome (str): O novo nome.

        Raises:
            ValueError: Se o nome for vazio ou só tiver espaços.
        """
        if not isinstance(novo_nome, str) or not novo_nome.strip():
            raise ValueError("O nome não pode ser vazio.")
        self._nome = novo_nome
        
    @property
    def email(self):
        """Pega o e-mail do coordenador."""
        return self._email
    
    @email.setter
    def email(self, novo_email):
        """
        Atualiza o e-mail do Coordenador.

        Args:
            novo_email (str): O novo e-mail.

        Raises:
            ValueError: Se o e-mail não tiver formato válido.
        """
        if not EMAIL_PATTERN.match(novo_email.strip()):
            raise ValueError("Formato de e-mail inválido.")
        self._email = novo_email.strip()

    @property    
    def senha(self):
        """Pega o hash da senha do coordenador."""
        return self.__senha

    @senha.setter
    def senha(self, nova_senha):
        """
        Atualiza a senha do coordenador, criando um novo hash.

        Args:
            nova_senha (str): A nova senha em texto plano.
        """
        self.__senha = self._hash_senha(nova_senha)
    
    @property
    def codigo_coordenacao(self):
        """Pega o código de coordenação."""
        return self.__codigo_coordenacao

    @codigo_coordenacao.setter
    def codigo_coordenacao(self, novo_codigo_coordenacao):
        """
        Atualiza o código de coordenação.

        Args:
            novo_codigo_coordenacao (str): O novo código.
        """
        self.__codigo_coordenacao = novo_codigo_coordenacao

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
