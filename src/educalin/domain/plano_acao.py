from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid

class PlanoAcao():
    """
    Representa um Plano de Ação personalizado para um aluno.

    Um PlanoAcao é composto por materiais de estudo (composição) e
    implementa o padrão Observer para notificar sobre mudanças.

    Attributes:
        __id (str): Identificador Único
        _aluno_alvo (Aluno): Aluno destinatário do plano
        _objetivo (str): Objetivo/descrição do plano
        _data_criacao (datetime): Data de criação
        _data_limite (datetime): Prazo para conclusão
        _materiais (List[MateriaisEstudo]): Materiais do plano (composição)
        _status (StatusPlano): Status atual do plano
        _observacoes (str): Observações adicionais
        _observers (List[Observer]): Lista de observadores
    
    Examples:
        >>> plano = PlanoAcao(aluno, "Melhorar em álgebra", prazo_dias=30)
        >>> plano.adicionar_material(material_pdf)
        >>> plano.enviar()
        >>> plano.status
        StatusPlano.ENVIADO
    """

    def __init__(
        self,
        aluno_alvo: 'Aluno',
        objetivo: str,
        prazo_dias: int,
        observacoes: Optional[str] = None
    ):
        """
        Inicializa um novo PlanoAcao

        Args:
            aluno_alvo: Aluno destinatário do plano
            objetivo: Descrição do objetivo do plano
            prazo_dias: Número de dias para a conclusão (a partir de hoje)
            observacoes: Observações adicionais (opcional)
        """
        # Validações

        if not aluno_alvo:
            raise ValueError("Aluno alvo é obrigatório")
        if not objetivo:
            raise ValueError("Objetivo não pode ser vazio")
        if not prazo_dias:
            raise ValueError("Prazo deve ser maior que zero")
        
        # Atributos principais
        self.__id = str(uuid.uuid4()) # TODO trocar implementação de id para melhor performance
        self._aluno_alvo = aluno_alvo
        self._objetivo = objetivo.strip()
        self._observacoes = observacoes.strip if observacoes else None

        # Datas
        self._data_cricacao = datetime.now()
        self._data_limite = self._data_cricacao + timedelta(days=prazo_dias)
        self._data_envio: Optional[datetime] = None
        self._data_inicio: Optional[datetime] = None
        self._data_conclusao: Optional[datetime] = None

        # Status
        self._status = StatusPlano.RASCUNHO
        self._motivo_cancelamento: Optional[str] = None

        # Composição
        self._materiais: List['MateriaisEstudo'] = []

        # Observer
        self._observers = List[Observer] = []

        # Histórico
        self._historico_status: List[Dict] = [
            {
                'status': StatusPlano.RASCUNHO,
                'data': self._data_cricacao,
                'usuario': None
            }
        ]

    # Encapsulamento

    @property
    def id(self) -> str:
        """Retorna o ID único do plano"""
        return self.__id
    
    @property
    def aluno_alvo(self) -> 'Aluno':
        """Retorna o aluno destinatário"""
        return self._aluno_alvo
    
    @property
    def objetivo(self) -> str:
        """Retorna o objetivo do plano"""
        return self._objetivo
    
    @objetivo.setter
    def objetivo(self, valor: str) -> None:
        """
        Atualiza o objetivo (apenas se ainda pode ser editado)

        Raises:
            PlanoJaConcluidoException: Se plano já foi concluído
        """
        if not self.pode_ser_editado():
            raise PlanoJaConcluidoException(
                "Não é possível editar plano com status " + self._status.value
            )
        self._objetivo = valor.strip()

    @property
    def observacoes(self) -> Optional[str]:
        """Retorna as observações"""
        return self._observacoes
    
    @observacoes.setter
    def observacoes(self, valor: str) -> None:
        """Atualiza observações"""
        if not self.pode_ser_editado():
            raise PlanoJaConcluidoExceptio("Plano não pode ser editado")
        self._observacoes = valor.strip() if valor else None

    @property
    def status(self) -> StatusPlano:
        """Retorna o status atual"""
        return self._status
    
    @property
    def materiais(self) -> List['MaterialEstudo']:
        """Retorna cópia da lista de materiais"""
        return self._materiais.copy()
    
    @property
    def total_materiais(self) -> int:
        """Retorna número total de materiais"""
        return len(self._materiais)
    
    @property
    def data_criacao(self) -> datetime:
        """Retorna data de criação"""
        return self._data_cricacao
    
    @property
    def data_limite(self) -> datetime:
        """Retorna data limite"""
        return self._data_limite
    
    @property
    def data_envio(self) -> Optional[datetime]:
        """Retorna data de envio (se já foi enviado)"""
        return self._data_envio
    
    @property
    def data_inicio(self) -> Optional[datetime]:
        """Retorna data de início (se já foi iniciado)"""
        return self._data_inicio
    
    @property
    def data_conclusao(self) -> Optional[datetime]:
        """Retorna data de conclusão (se já foi concluído)"""
        return self._data_conclusao
    
    @property
    def motivo_conclusao(self) -> Optional[str]:
        """Retorna motivo de cancelamento (se foi cancelado)"""
        return self._motivo_cancelamento

    @property
    def historico_status(self) -> List[Dict]:
        """Retorna histórico de transições de status"""
        return self._historico_status.copy()