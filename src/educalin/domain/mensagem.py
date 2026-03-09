"""
Módulo contendo a entidade de domínio Mensagem.

US10: Sistema de mensagens privadas professor-aluno.
"""

from datetime import datetime
from typing import Optional


class MensagemVaziaException(Exception):
    """Lançada quando tenta criar mensagem sem conteúdo"""
    pass


class Mensagem:
    """
    Representa uma mensagem privada entre professor e aluno.
    
    Implementa US10: "Como professor/aluno, quero enviar mensagens privadas
    para estabelecer comunicação direta."
    
    Attributes:
        _id (Optional[int]): Identificador único da mensagem
        _remetente_id (int): ID do usuário remetente
        _destinatario_id (int): ID do usuário destinatário
        _conteudo (str): Conteúdo da mensagem
        _lida (bool): Indica se a mensagem foi lida
        _data_envio (datetime): Data e hora do envio
        _data_leitura (Optional[datetime]): Data e hora da leitura
    
    Examples:
        >>> mensagem = Mensagem(
        ...     remetente_id=1,
        ...     destinatario_id=2,
        ...     conteudo="Boa tarde, preciso de ajuda com álgebra"
        ... )
        >>> mensagem.marcar_como_lida()
        >>> mensagem.lida
        True
    """
    
    def __init__(
        self,
        remetente_id: int,
        destinatario_id: int,
        conteudo: str,
        id: Optional[int] = None,
        lida: bool = False,
        data_envio: Optional[datetime] = None,
        data_leitura: Optional[datetime] = None
    ):
        """
        Inicializa uma nova Mensagem.
        
        Args:
            remetente_id: ID do usuário que envia a mensagem
            destinatario_id: ID do usuário que receberá a mensagem
            conteudo: Texto da mensagem
            id: ID da mensagem (se já persistida)
            lida: Se a mensagem já foi lida
            data_envio: Data de envio (default: agora)
            data_leitura: Data de leitura (default: None)
            
        Raises:
            ValueError: Se IDs forem inválidos ou iguais
            MensagemVaziaException: Se conteúdo estiver vazio
        """
        if remetente_id <= 0:
            raise ValueError("ID do remetente deve ser positivo")
        if destinatario_id <= 0:
            raise ValueError("ID do destinatário deve ser positivo")
        if remetente_id == destinatario_id:
            raise ValueError("Remetente e destinatário não podem ser o mesmo usuário")
        
        conteudo_limpo = conteudo.strip() if conteudo else ""
        if not conteudo_limpo:
            raise MensagemVaziaException("Conteúdo da mensagem não pode ser vazio")
        
        if len(conteudo_limpo) > 5000:
            raise ValueError("Mensagem não pode ter mais de 5000 caracteres")
        
        self._id = id
        self._remetente_id = remetente_id
        self._destinatario_id = destinatario_id
        self._conteudo = conteudo_limpo
        self._lida = lida
        self._data_envio = data_envio or datetime.now()
        self._data_leitura = data_leitura
    
    @property
    def id(self) -> Optional[int]:
        """Retorna o ID da mensagem"""
        return self._id
    
    @property
    def remetente_id(self) -> int:
        """Retorna o ID do remetente"""
        return self._remetente_id
    
    @property
    def destinatario_id(self) -> int:
        """Retorna o ID do destinatário"""
        return self._destinatario_id
    
    @property
    def conteudo(self) -> str:
        """Retorna o conteúdo da mensagem"""
        return self._conteudo
    
    @property
    def lida(self) -> bool:
        """Retorna se a mensagem foi lida"""
        return self._lida
    
    @property
    def data_envio(self) -> datetime:
        """Retorna a data de envio"""
        return self._data_envio
    
    @property
    def data_leitura(self) -> Optional[datetime]:
        """Retorna a data de leitura (se lida)"""
        return self._data_leitura
    
    def marcar_como_lida(self) -> None:
        """
        Marca a mensagem como lida e registra a data/hora.
        
        Raises:
            ValueError: Se a mensagem já estiver marcada como lida
        """
        if self._lida:
            raise ValueError("Mensagem já foi lida anteriormente")
        
        self._lida = True
        self._data_leitura = datetime.now()
    
    def __repr__(self) -> str:
        return (
            f"Mensagem(id={self._id}, remetente={self._remetente_id}, "
            f"destinatario={self._destinatario_id}, lida={self._lida})"
        )
    
    def __str__(self) -> str:
        status = "LIDA" if self._lida else "NÃO LIDA"
        preview = self._conteudo[:50] + "..." if len(self._conteudo) > 50 else self._conteudo
        return f"[{status}] {preview}"
