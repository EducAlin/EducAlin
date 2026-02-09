import bcrypt
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class AutenticavelMixin:
    """
    Um Mixin que dá pra qualquer classe a capacidade de se autenticar.

    Ele cuida da parte chata de criar um hash seguro pra senha e de
    verificar se o login e a senha batem. A classe que usar ele só
    precisa ter as propriedades `email` e `senha`.
    """
    def __init__(self, *args, **kwargs):
        """Coopera com herança múltipla."""
        super().__init__(*args, **kwargs)

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

class NotificavelMixin:
    """
    Mixin que adiciona capacidades de notificação.

    Permite que a classe receba, armazene e gerencie notificações,
    além de configurar preferência de canal (email, push, SMS).

    Examples:
        >>> class Aluno(Usuario, NotificavelMixin):
        ...     pass
        >>> aluno = Aluno("Maria", "maria@email.com", "senha")
        >>> aluno.receber_notificacao("Nova nota registrada", tipo="info")
        >>> len(aluno.obter_notificacoes())
        1
    """

    def __init__(self, *args, **kwargs):
        """
        Inicializa atributos do mixin.

        Usa super().__init__ para cooperar com MRO
        (Method Resolution Order) em herança múltipla.
        """
        super().__init__(*args, **kwargs)

        # Lista de notificações
        self._notificacoes: List[Dict] = []

        # Preferências de canal
        self._preferencias_notificacao: Dict[str, bool] = {
            'email': True,
            'push': True,
            'sms': False
        }

    def receber_notificacao(
        self,
        mensagem: str,
        tipo: str = 'info',
        dados_adicionais: Optional[Dict] = None
    ) -> str:
        """
        Recebe e armazena uma notificação.

        Args:
            mensagem: Conteúdo da notificação
            tipo: Tipo ('info', 'aviso', 'urgente', 'sucesso')
            dados_adicionais: Dados extras (opcional)
        
        Examples:
            >>> usuario.receber_notificacao(
            ...     "Novo material disponível",
            ...     tipo="info",
            ...     dados_adicionais={'material_id': '123'}
            ... )
        """
        tipos_validos = {'info', 'aviso', 'urgente', 'sucesso'}

        if tipo not in tipos_validos:
            raise ValueError(f"Tipo inválido. Use: {tipos_validos}")
        
        notificacao = {
            'id': str(uuid.uuid4()),
            'mensagem': mensagem,
            'tipo': tipo,
            'data': datetime.now(),
            'lida': False,
            'dados': dados_adicionais or {}
        }

        self._notificacoes.append(notificacao)
        return notificacao['id']

    def obter_notificacoes(
            self,
            apenas_nao_lidas: bool = False,
            limite: Optional[int] = None
    ) -> List[Dict]:
        """
        Retorna lista de notificações.

        Args:
            apenas_nao_lidas: Se True, filtra apenas não lidas
            limite: Número máximo de notificações (mais recentes)
        
        Returns:
            Lista de dicionários com notificações ordenadas por data (desc)

        Examples:
            >>> notifs = usuario.obter_notificacoes(apenas_nao_lidas=True)
            >>> len(notifs)
            3
        """
        # Filtro
        if apenas_nao_lidas:
            notificacoes = [n for n in self._notificacoes if not n['lida']]
        else:
            notificacoes = self._notificacoes.copy()

        # Ordenar por data
        notificacoes.sort(key=lambda n: n['data'], reverse=True)

        # Limite
        if limite:
            notificacoes = notificacoes[:limite]

        return notificacoes
    
    def marcar_como_lida(self, notificacao_id: str) -> bool:
        """
        Marca notificação como lida.

        Args:
            notificacao_id: ID da notificação (UUID)

        Returns:
            True se encontrada e marcada, False se não encontrado

        Examples:
            >>> notifs = usuario.obter_notificacoes()
            >>> usuario.marcar_como_lida(notifs[0]['id'])
            True
        """
        for notificacao in self._notificacoes:
            if notificacao['id'] == notificacao_id:
                notificacao['lida'] = True
                return True
            
        return False
    
    def marcar_todas_como_lidas(self) -> int:
        """
        Marcar todas as notificações como lidas.

        Returns:
            Número de notificações marcadas

        Examples:
            >>> usuario.marcar_todas_como_lidas()
            5
        """
        contador = 0
        for notificacao in self._notificacoes:
            if not notificacao['lida']:
                notificacao['lida'] = True
                contador += 1
        
        return contador
    
    def configurar_preferencias(self, **preferencias) -> None:
        """
        Configura preferências de canal de notificação.

        Args:
            **preferencias: Canais e valores booleanos

        Examples:
            >>> usuario.configurar_preferencias(
            ...     email=True,
            ...     push=False,
            ...     sms=True
            ... )
        """
        canais_validos = ['email', 'push', 'sms']

        for canal, ativo in preferencias.items():
            if canal not in canais_validos:
                raise ValueError(f"Canal '{canal}' inválido. Use: {canais_validos}")
            
            if not isinstance(ativo, bool):
                raise TypeError(f"Valor de '{canal}' deve ser booleano")
            
            self._preferencias_notificacao[canal] = ativo

    def obter_preferencias(self) -> Dict[str, bool]:
        """
        Retorna cópia das preferências atuais.

        Returns:
            Dicionário com preferências de canal
        """
        return self._preferencias_notificacao.copy()
    
    def limpar_notificacoes(self, apenas_lidas: bool = True) -> int:
        """
        Remove notificações.

        Args:
            apenas_lidas: Se True, remove apenas lidas. Se False, remove todas.

        Returns:
            Número de notificações removidas

        Examples:
            >>> usuario.limpar_notificacoes(apenas_lidas=True)
            10
        """
        if apenas_lidas:
            notificacoes_mantidas = [n for n in self._notificacoes if not n['lida']]
            removidas = len(self._notificacoes) - len(notificacoes_mantidas)
            self._notificacoes = notificacoes_mantidas
        else:
            removidas = len(self._notificacoes)
            self._notificacoes = []

        return removidas
    
    @property
    def total_notificacoes_nao_lidas(self) -> int:
        """
        Retorna número de notificações não lidas.

        Returns:
            Contador de notificações não lidas
        """
        return sum(1 for n in self._notificacoes if not n['lida'])