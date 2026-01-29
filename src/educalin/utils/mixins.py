import bcrypt

class AutenticavelMixin:
    """
    Um Mixin que dá pra qualquer classe a capacidade de se autenticar.

    Ele cuida da parte chata de criar um hash seguro pra senha e de
    verificar se o login e a senha batem. A classe que usar ele só
    precisa ter as propriedades `email` e `senha`.
    """
    def _hash_senha(self, senha_texto_plano: str) -> bytes:
        """
        Transforma uma senha comum em um hash seguro usando bcrypt.

        Args:
            senha_texto_plano (str): A senha como ela foi digitada, sem segredo.

        Returns:
            bytes: O hash da senha, pronto pra ser guardado no banco.
        """
        return bcrypt.hashpw(senha_texto_plano.encode('utf-8'), bcrypt.gensalt())

    def validar_credenciais(self, email: str, senha_fornecida: str) -> bool:
        """
        Confere se o e-mail e a senha que o usuário passou estão corretos.

        Args:
            email (str): O e-mail que o usuário tentou usar pra logar.
            senha_fornecida (str): A senha que o usuário digitou.

        Returns:
            bool: Retorna True se tudo estiver certo, se não, False.
        """
        if self.email != email:
            return False
        return bcrypt.checkpw(senha_fornecida.encode('utf-8'), self.senha)

    def resetar_senha(self, nova_senha: str):
        """
        Atualiza a senha do usuário pra uma nova.

        Essa função basicamente chama o setter da propriedade `senha`,
        que deve usar o `_hash_senha` pra guardar a nova senha segura.

        Args:
            nova_senha (str): A nova senha que o usuário escolheu.
        """
        self.senha = nova_senha