from usuario import Usuario
from turma import Turma

class Coordenador(Usuario):
    def __init__(self, nome: str, email: str, senha: str, codigo_coordenacao: str):
        self.nome = nome
        self._email = email
        self.__senha = senha
        self.__codigo_coordenacao = codigo_coordenacao

    @property
    def nome(self):
        return self.nome
    
    @nome.setter
    def nome(self, novo_nome):
        self.nome = self.novo_nome
        
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, novo_email):
        self._email = self.novo_email

    @property    
    def senha(self):
        return self.__senha

    @senha.setter
    def senha(self, nova_senha):
        self.__senha = self.nova_senha
    
    @property
    def codigo_coordenacao(self):
        return self.__codigo_coordenacao

    @codigo_coordenacao.setter
    def codigo_coordenacao(self, novo_codigo_coordenacao):
        if not isinstance(novo_codigo_coordenacao, str):
            raise ValueError("O código tem que ser uma str.")
        if novo_codigo_coordenacao == self.codigo_coordenacao:
            raise ValueError("O novo código não pode ser igual ao anterior.")
        self._codigo_coordenacao = novo_codigo_coordenacao

    def comparar_turmas(self, turma1, turma2):
        return turma1.codigo == turma2.codigo