from typing import Optional, List, Dict
from datetime import datetime, timedelta
import uuid

class PlanoJaConcluidoException(Exception):
    """Lançada quando tenta modificar plano já concluído"""
    pass

class TransicaoStatusInvalidaException(Exception):
    """Lançada quando tenta fazer transição de status inválida"""
    pass

class MaterialObrigatorioException(Exception):
    """Lançada quando tenta enviar plano sem materiais"""
    pass

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
            raise PlanoJaConcluidoException("Plano não pode ser editado")
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
    
    # =================================
    # Métodos de gestão de materiais
    # =================================
    
    def adicionar_material(self, material: 'MaterialEstudo') -> bool:
        """
        Adiciona material à composição do plano.

        Args:
            material: Instância de MaterialEstudo

        Returns:
            True se adicionado, False se já existia

        Raises:
            TypeError: Se não for MaterialEstudo
            PlanoJaConcluidoException: Se plano já está concluído
        """
        from educalin.domain.material import MaterialEstudo

        if not isinstance(material, MaterialEstudo):
            raise TypeError(
                f"Esperado instância de MaterialEstudo, recebido {type(material).__name__}"
            )
        
        # Valida status do plano
        if not self.pode_ser_editado():
            raise PlanoJaConcluidoException(
                f"Não é possível adicionar material em plano {self._status.value}"
            )
        
        # Verifica duplicação
        if material in self.materiais:
            return False
        
        self._materiais.append(material)

        # TODO implementar notificacao observer

        return True
    
    def remover_material(self, material: 'MaterialEstudo') -> bool:
        """
        Remove material da composição.

        Args:
            material: Material a ser retirado
        
        Returns:
            True se removido, False se não existia

        Raises:
            PlanoJaConcluidoException: Se plano já está concluído
        """
        if not self.pode_ser_editado():
            raise PlanoJaConcluidoException("Plano não pode ser editado")
        
        if material not in self._materiais:
            return False
        
        self._materiais.remove(material)

        # TODO impelmentar notificação observer

        return True
    
    # =================================
    # Métodos de gerenciamento de status
    # =================================

    def enviar(self) -> None:
        """
        Envia o plano para o aluno (transição: RASCUNHO -> ENVIADO)

        Raises:
            MaterialObrigatorioException: Se não houver materiais
            TransicaoStatusInvalidaException: Se status atual inválido
        """
        if self._status != StatusPlano.RASCUNHO:
            raise TransicaoStatusInvalidaException(
                f"Não é possível enviar plano com status {self._status.value}"
            )
        
        if self.total_materiais == 0:
            raise MaterialObrigatorioException(
                "PlanoAcao deve ter pelo menos 1 material para ser enviado"
            )
        
        self._status = StatusPlano.ENVIADO
        self._data_envio = datetime.now()
        self._registrar_historico(StatusPlano.ENVIADO)

        # TODO implementar notificacao observer

    def iniciar(self) -> None:
        """
        Inicia o plano (transição: ENVIADO -> EM_ANDAMENTO)

        Raises:
            TransicaoStatusInvalidaException: Se status atual inválido
        """
        if self._status != StatusPlano.RASCUNHO:
            raise TransicaoStatusInvalidaException(
                f"Não é possível enviar plano com status {self._status.value}"
            )
        
        self._status = StatusPlano.EM_ANDAMENTO
        self._data_inicio = datetime.now()
        self._registrar_historico(StatusPlano.EM_ANDAMENTO)

        # TODO implementar notificacao observer

    def concluir(self) -> None:
        """
        Conclui o plano (transições aceitas: ENVIADO/EM_ANDAMENTO -> CONCLUIDO)

        Raises:
            TransicaoStatusInvalidaException: Se status atual inválido
        """
        status_validos = [StatusPlano.ENVIADO, StatusPlano.EM_ANDAMENTO]

        if self._status not in status_validos:
            raise TransicaoStatusInvalidaException(
                f"Não é possível enviar plano com status {self._status.value}"
            )
        
        self._status = StatusPlano.CONCLUIDO
        self._data_conclusao - datetime.now()
        self._registrar_historico(StatusPlano.CONCLUIDO)

        # TODO implementar notificacao observer

    def cancelar(self, motivo) -> None:
        """
        Cancela o plano

        Args:
            motivo: Motivo do cancelamento

        Raises:
            TransicaoStatusInvalidaException: Se já está concluído/cancelado
        """
        if self._status in [StatusPlano.CONCLUIDO, StatusPlano.CANCELADO]:
            raise TransicaoStatusInvalidaException(
                f"Não é possível cancelar plano com status {self._status.value}"
            )
        
        self._status = StatusPlano.CANCELADO
        self._motivo_cancelamento = motivo
        self._registrar_historico(StatusPlano.CANCELADO)

        # TODO implementar notificacao observer

    def _registrar_historico(self, novoStatus: StatusPlano) -> None:
        """Registra transição no histórico"""
        self._historico_status.append({
            'status': novoStatus,
            'data': datetime.now(),
            'usuario': None #Pode preencher depois
        })