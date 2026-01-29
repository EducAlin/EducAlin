from abc import ABC, abstractmethod

class Usuario(ABC):
    """
    Uma classe base abstrata que define o que todo usuário do sistema deve ter.

    Funciona como um contrato: qualquer classe que herdar de `Usuario`
    (como Aluno, Professor, etc.) é obrigada a implementar as propriedades
    `nome`, `email` e `senha`.
    """
    @property
    @abstractmethod
    def nome(self):
        """
        Propriedade abstrata para o nome do usuário.
        As classes filhas precisam implementar isso.
        """
        pass
    
    @property
    @abstractmethod
    def email(self):
        """
        Propriedade abstrata para o e-mail do usuário.
        As classes filhas precisam implementar isso.
        """
        pass

    @property
    @abstractmethod
    def senha(self):
        """
        Propriedade abstrata para a senha (ou hash da senha) do usuário.
        As classes filhas precisam implementar isso.
        """
        pass
