import re
from abc import ABC

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class Usuario(ABC):
    """
    Uma classe base abstrata que define o que todo usuário do sistema deve ter.

    Funciona como um contrato: qualquer classe que herdar de `Usuario`
    (como Aluno, Professor, etc.) herda as propriedades `nome`, `email` e `senha`
    com validações centralizadas.
    """
    @abstractmethod
    def __init__(self, nome: str, email: str, senha: str):
        """
        Construtor abstrato que deve ser implementado pelas subclasses.
        
        Args:
            nome (str): O nome do usuário.
            email (str): O e-mail do usuário.
            senha (str): A senha do usuário.
        """
        pass
    
    @property
    def nome(self):
        """Pega o nome do usuário."""
        return self._nome
    
    @nome.setter
    def nome(self, novo_nome):
        """
        Atualiza o nome do usuário.

        Args:
            novo_nome (str): O novo nome.

        Raises:
            ValueError: Se o nome for vazio ou só tiver espaços.
        """
        if not isinstance(novo_nome, str) or not novo_nome.strip():
            raise ValueError("O nome não pode ser vazio.")
        self._nome = novo_nome.strip()
    
    @property
    def email(self):
        """Pega o e-mail do usuário."""
        return self._email
    
    @email.setter
    def email(self, novo_email):
        """
        Atualiza o e-mail do Usuário.

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
        """Pega o hash da senha do usuário."""
        return self._Usuario__senha

    @senha.setter
    def senha(self, nova_senha):
        """
        Atualiza a senha do usuário, criando um novo hash.

        Args:
            nova_senha (str): A nova senha em texto plano.
        """
        from ..utils.mixins import AutenticavelMixin
        # Usa o método de hash do mixin se disponível
        if hasattr(self, '_hash_senha'):
            self._Usuario__senha = self._hash_senha(nova_senha)
        else:
            self._Usuario__senha = nova_senha
