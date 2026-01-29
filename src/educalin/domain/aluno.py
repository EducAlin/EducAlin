from .usuario import Usuario
from ..utils.mixins import AutenticavelMixin

class Aluno(Usuario, AutenticavelMixin):
    """
    Representa um aluno no sistema.

    Essa classe herda de Usuario e usa o AutenticavelMixin pra poder logar.
    Ela guarda informações como nome, e-mail, matrícula e o desempenho.
    """
    def __init__(self, nome: str, email: str, senha: str, matricula: str):
        """
        Cria uma nova instância de Aluno.

        Args:
            nome (str): O nome completo do aluno.
            email (str): O e-mail que o aluno vai usar pra logar.
            senha (str): A senha, que vai ser guardada com segurança (hash).
            matricula (str): O número de matrícula único do aluno.
        """
        self._nome = nome
        self._email = email
        self.__senha = self._hash_senha(senha)
        self._matricula = matricula
        self.__desempenho = {}

    @property
    def nome(self):
        """Pega o nome do aluno."""
        return self._nome
    
    @nome.setter
    def nome(self, novo_nome):
        """
        Atualiza o nome do aluno.

        Args:
            novo_nome (str): O novo nome do aluno.

        Raises:
            ValueError: Se o nome for vazio ou só tiver espaços.
        """
        if not isinstance(novo_nome, str) or not novo_nome.strip():
            raise ValueError("O nome não pode ser vazio.")
        self._nome = novo_nome
        
    @property
    def email(self):
        """Pega o e-mail do aluno."""
        return self._email
    
    @email.setter
    def email(self, novo_email):
        """
        Atualiza o e-mail do aluno.

        Args:
            novo_email (str): O novo e-mail.

        Raises:
            ValueError: Se o e-mail não tiver um "@".
        """
        if "@" not in novo_email:
            raise ValueError("Formato de e-mail inválido.")
        self._email = novo_email

    @property    
    def senha(self):
        """Pega o hash da senha do aluno."""
        return self.__senha

    @senha.setter
    def senha(self, nova_senha):
        """
        Atualiza a senha do aluno, criando um novo hash.

        Args:
            nova_senha (str): A nova senha em texto plano.
        """
        self.__senha = self._hash_senha(nova_senha)

    @property
    def matricula(self):
        """Pega a matrícula do aluno."""
        return self._matricula

    @property
    def desempenho(self):
        """Pega o dicionário de desempenho do aluno."""
        return self.__desempenho

    @desempenho.setter
    def desempenho(self, novo_desempenho):
        """
        Atualiza o dicionário de desempenho do aluno.

        Args:
            novo_desempenho (dict): O novo dicionário com as notas e etc.

        Raises:
            ValueError: Se o valor passado não for um dicionário.
        """
        if not isinstance(novo_desempenho, dict):
            raise ValueError("Desempenho deve ser um dicionário.")
        self.__desempenho = novo_desempenho 
        
    def visualizar_desempenho(self):
        """
        Mostra o desempenho do aluno na tela.

        Returns:
            None: A função só imprime o resultado, não retorna nada.
        """
        return print(self.desempenho)
    
    def acessar_material(self, material_id):
        """
        Permite que o aluno acesse um material de estudo.

        Args:
            material_id: O identificador do material que ele quer ver.
        """
        pass