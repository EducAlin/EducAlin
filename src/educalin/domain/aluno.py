from typing import List
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
        super()._init__(nome, email, senha)
        self._matricula = matricula
        self.__desempenho: List['Nota'] = []

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
        """Retorna uma cópia da lista de notas (desempenho) do aluno."""
        return self.__desempenho.copy()

    def adicionar_nota(self, nota: 'Nota'):
        """
        Adiciona uma nota ao desempenho do aluno.

        Args:
            nota (Nota): A instância de Nota a ser adicionada.

        Raises:
            TypeError: Se o objeto não for uma instância de Nota.
            ValueError: Se a nota pertencer a outro aluno.
        """
        from .nota import Nota
        if not isinstance(nota, Nota):
            raise TypeError("O objeto adicionado deve ser uma instância de Nota.")
        if nota.aluno is not self:
            raise ValueError("Esta nota pertence a outro aluno.")
        self.__desempenho.append(nota)

    def calcular_media(self) -> float:
        """
        Calcula a média das notas do aluno.

        As notas são pegas da lista de objetos Nota no desempenho.

        Returns:
            float: A média das notas. Retorna 0.0 se não houver notas.
        """
        if not self.__desempenho:
            return 0.0
        
        soma_das_notas = sum(nota.valor for nota in self.__desempenho)
        return soma_das_notas / len(self.__desempenho)

    def visualizar_desempenho(self):
        """
        Mostra o desempenho do aluno na tela.
        """
        if not self.__desempenho:
            print(f"Nenhum desempenho registrado para {self.nome}.")
            return
        print(f"Desempenho de {self.nome} ({self.matricula}):")
        for nota in self.__desempenho:
            print(f"- {nota.avaliacao.titulo}: {nota.valor:.1f} / {nota.avaliacao.valor_maximo:.1f}")
        print(f"Média Geral: {self.calcular_media():.2f}")
    
    def acessar_material(self, material_id):
        """
        Permite que o aluno acesse um material de estudo.

        Args:
            material_id: O identificador do material que ele quer ver.
        """
        pass