"""
Repository para operações de banco de dados com Planos de Ação.

Implementa o padrão Repository para abstrair operações de persistência
de planos de ação usando SQL puro (SQLite3).
Suporta composição com materiais de estudo através de relacionamento many-to-many.
"""

import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from .base_model import BaseModel
from .plano_acao_models import PlanoAcaoModel
from .base import get_connection


class PlanoAcaoRepository:
    """
    Repository para operações CRUD de planos de ação.
    
    Utiliza SQL puro para interagir com as tabelas 'planos_acao' e 'plano_materiais'.
    Suporta composição com materiais de estudo através de relacionamento many-to-many.
    
    Status possíveis: rascunho, enviado, em_andamento, concluido, cancelado
    
    Example:
        >>> repo = PlanoAcaoRepository()
        >>> plano_id = repo.criar({
        ...     'aluno_id': 1,
        ...     'objetivo': 'Melhorar notas em POO',
        ...     'prazo_dias': 30,
        ...     'observacoes': 'Foco em design patterns'
        ... })
        >>> plano = repo.buscar_por_id(plano_id)
        >>> repo.adicionar_material(plano_id, 5)
        >>> repo.atualizar_status(plano_id, 'enviado')
    """
    
    # Status válidos do plano
    STATUS_VALIDOS = ['rascunho', 'enviado', 'em_andamento', 'concluido', 'cancelado']
    
    # Transições permitidas entre status
    TRANSICOES_VALIDAS = {
        'rascunho': ['enviado', 'cancelado'],
        'enviado': ['em_andamento', 'cancelado'],
        'em_andamento': ['concluido', 'cancelado'],
        'concluido': [],      # Status final
        'cancelado': [],      # Status final
    }
    
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        """
        Inicializa o repository.
        
        Args:
            conn: Conexão SQLite opcional. Se não fornecida, cria uma nova.
        """
        self.conn = conn or get_connection()
        self._own_connection = conn is None
    
    def __enter__(self):
        """Suporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão ao sair do context manager (se for própria)."""
        if self._own_connection:
            self.conn.close()
    
    def criar(self, plano_data: Dict[str, Any]) -> int:
        """
        Cria um novo plano de ação no banco de dados.
        
        Inicia o plano com status 'rascunho'. Para enviar, use atualizar_status().
        
        Args:
            plano_data: Dicionário com os dados do plano:
                - aluno_id: ID do aluno destinatário (obrigatório, FK)
                - objetivo: Objetivo/descrição do plano (obrigatório)
                - prazo_dias: Número de dias até a data limite (obrigatório, int > 0)
                - observacoes: Observações adicionais (opcional)
        
        Returns:
            int: ID do plano criado
        
        Raises:
            ValueError: Se dados obrigatórios faltarem ou forem inválidos
            sqlite3.IntegrityError: Se houver violação de constraints
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> plano_id = repo.criar({
            ...     'aluno_id': 1,
            ...     'objetivo': 'Estudar POO',
            ...     'prazo_dias': 30
            ... })
            >>> print(f"Plano criado: {plano_id}")
        
        Example com observações:
            >>> plano_id = repo.criar({
            ...     'aluno_id': 1,
            ...     'objetivo': 'Reforço em Programação',
            ...     'prazo_dias': 45,
            ...     'observacoes': 'Priorizar design patterns'
            ... })
        """
        # Validações de campos obrigatórios
        aluno_id = plano_data.get('aluno_id')
        objetivo = plano_data.get('objetivo')
        prazo_dias = plano_data.get('prazo_dias')
        
        if not all([aluno_id is not None, objetivo, prazo_dias is not None]):
            raise ValueError(
                "Campos obrigatórios: aluno_id, objetivo, prazo_dias"
            )
        
        # Validar aluno_id
        if not isinstance(aluno_id, int) or aluno_id <= 0:
            raise ValueError("aluno_id deve ser um inteiro positivo")
        
        # Validar objetivo
        objetivo = BaseModel._validate_not_empty(objetivo, "Objetivo")
        
        # Validar prazo_dias
        if not isinstance(prazo_dias, int) or prazo_dias <= 0:
            raise ValueError("prazo_dias deve ser um inteiro positivo")
        
        # Validar observações se fornecidas
        observacoes = plano_data.get('observacoes')
        if observacoes is not None and observacoes:
            observacoes = BaseModel._validate_not_empty(observacoes, "Observações")
        else:
            observacoes = None
        
        # Verificar se aluno existe
        cursor = self.conn.execute(
            "SELECT id FROM usuarios WHERE id = ? AND tipo_usuario = 'aluno'",
            (aluno_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Aluno com ID {aluno_id} não existe")
        
        # Calcular datas
        data_criacao = datetime.now()
        data_limite = data_criacao + timedelta(days=prazo_dias)
        
        # Inserir no banco
        try:
            cursor = self.conn.execute(
                """
                INSERT INTO planos_acao 
                (aluno_id, objetivo, data_criacao, data_limite, status, observacoes)
                VALUES (?, ?, ?, ?, 'rascunho', ?)
                """,
                (
                    aluno_id, objetivo, data_criacao.isoformat(), 
                    data_limite.isoformat(), observacoes
                )
            )
            self.conn.commit()
            return cursor.lastrowid
        
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if 'aluno_id' in str(e):
                raise ValueError(f"Erro ao criar plano: {e}")
            else:
                raise ValueError(f"Erro de integridade: {e}")
    
    def buscar_por_id(self, plano_id: int) -> Optional[PlanoAcaoModel]:
        """
        Busca um plano de ação por ID.
        
        Args:
            plano_id: ID do plano
        
        Returns:
            PlanoAcaoModel se encontrado, None caso contrário
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> plano = repo.buscar_por_id(1)
            >>> if plano:
            ...     print(f"Objetivo: {plano.objetivo}")
            ...     print(f"Status: {plano.status}")
        """
        if not isinstance(plano_id, int) or plano_id <= 0:
            raise ValueError("plano_id deve ser um inteiro positivo")
        
        cursor = self.conn.execute(
            "SELECT * FROM planos_acao WHERE id = ?",
            (plano_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return self._criar_modelo(row)
        return None
    
    def listar_por_aluno(
        self,
        aluno_id: int,
        status: Optional[str] = None
    ) -> List[PlanoAcaoModel]:
        """
        Lista todos os planos de ação de um aluno.
        
        Retorna os planos em ordem decrescente de data de criação (mais recentes primeiro).
        
        Args:
            aluno_id: ID do aluno
            status: Filtrar por status (opcional). De: rascunho, enviado, em_andamento, 
                    concluido, cancelado
        
        Returns:
            Lista de PlanoAcaoModel
        
        Raises:
            ValueError: Se aluno_id inválido ou status inválido
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> planos = repo.listar_por_aluno(1)
            >>> for plano in planos:
            ...     print(f"{plano.objetivo} - {plano.status}")
        
        Example com filtro de status:
            >>> planos_ativos = repo.listar_por_aluno(1, status='em_andamento')
            >>> planos_rascunho = repo.listar_por_aluno(1, status='rascunho')
        """
        if not isinstance(aluno_id, int) or aluno_id <= 0:
            raise ValueError("aluno_id deve ser um inteiro positivo")
        
        if status is not None:
            if status not in self.STATUS_VALIDOS:
                raise ValueError(f"Status inválido. Use um de: {self.STATUS_VALIDOS}")
            
            cursor = self.conn.execute(
                """
                SELECT * FROM planos_acao 
                WHERE aluno_id = ? AND status = ? 
                ORDER BY data_criacao DESC
                """,
                (aluno_id, status)
            )
        else:
            cursor = self.conn.execute(
                """
                SELECT * FROM planos_acao 
                WHERE aluno_id = ? 
                ORDER BY data_criacao DESC
                """,
                (aluno_id,)
            )
        
        return [self._criar_modelo(row) for row in cursor.fetchall()]
    
    def listar_todos(self, status: Optional[str] = None) -> List[PlanoAcaoModel]:
        """
        Lista todos os planos de ação do sistema.
        
        Retorna os planos em ordem decrescente de data de criação.
        
        Args:
            status: Filtrar por status (opcional)
        
        Returns:
            Lista de PlanoAcaoModel
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> todos = repo.listar_todos()
            >>> enviados = repo.listar_todos(status='enviado')
        """
        if status is not None:
            if status not in self.STATUS_VALIDOS:
                raise ValueError(f"Status inválido. Use um de: {self.STATUS_VALIDOS}")
            
            cursor = self.conn.execute(
                """
                SELECT * FROM planos_acao 
                WHERE status = ? 
                ORDER BY data_criacao DESC
                """,
                (status,)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM planos_acao ORDER BY data_criacao DESC"
            )
        
        return [self._criar_modelo(row) for row in cursor.fetchall()]
    
    def listar_vencidos(self, status: Optional[str] = None) -> List[PlanoAcaoModel]:
        """
        Lista planos de ação com prazo vencido.
        
        Retorna apenas planos não concluídos e não cancelados cuja data_limite
        é anterior ao momento atual.
        
        Args:
            status: Filtrar por status adicional (opcional)
        
        Returns:
            Lista de PlanoAcaoModel
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> vencidos = repo.listar_vencidos()
            >>> vencidos_ativos = repo.listar_vencidos(status='em_andamento')
        """
        query = """
            SELECT * FROM planos_acao 
            WHERE data_limite < ? AND status NOT IN ('concluido', 'cancelado')
        """
        params = [datetime.now().isoformat()]
        
        if status:
            if status not in self.STATUS_VALIDOS:
                raise ValueError(f"Status inválido. Use um de: {self.STATUS_VALIDOS}")
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY data_limite ASC"
        
        cursor = self.conn.execute(query, params)
        return [self._criar_modelo(row) for row in cursor.fetchall()]
    
    def adicionar_material(self, plano_id: int, material_id: int) -> None:
        """
        Adiciona um material ao plano de ação.
        
        Um plano pode conter múltiplos materiais. O mesmo material não pode
        ser adicionado duas vezes ao mesmo plano.
        
        Args:
            plano_id: ID do plano
            material_id: ID do material a adicionar
        
        Raises:
            ValueError: Se o plano está concluído/cancelado, material inexiste, 
                       ou material já está no plano
            sqlite3.IntegrityError: Se houver outras violações de constraint
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> repo.adicionar_material(1, 5)
            >>> repo.adicionar_material(1, 10)
        """
        if not isinstance(plano_id, int) or plano_id <= 0:
            raise ValueError("plano_id deve ser um inteiro positivo")
        if not isinstance(material_id, int) or material_id <= 0:
            raise ValueError("material_id deve ser um inteiro positivo")
        
        # Buscar plano para validar status
        plano = self.buscar_por_id(plano_id)
        if not plano:
            raise ValueError(f"Plano com ID {plano_id} não existe")
        
        if plano.status in ['concluido', 'cancelado']:
            raise ValueError(
                f"Não é possível adicionar materiais a um plano {plano.status}"
            )
        
        # Verificar se material existe
        cursor = self.conn.execute(
            "SELECT id FROM materiais WHERE id = ?",
            (material_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Material com ID {material_id} não existe")
        
        # Verificar se material já está no plano
        cursor = self.conn.execute(
            "SELECT 1 FROM plano_materiais WHERE plano_id = ? AND material_id = ?",
            (plano_id, material_id)
        )
        if cursor.fetchone():
            raise ValueError("Material já está adicionado a este plano")
        
        # Adicionar material
        try:
            self.conn.execute(
                """
                INSERT INTO plano_materiais (plano_id, material_id, data_adicao)
                VALUES (?, ?, ?)
                """,
                (plano_id, material_id, datetime.now().isoformat())
            )
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao adicionar material: {e}")
    
    def remover_material(self, plano_id: int, material_id: int) -> bool:
        """
        Remove um material do plano de ação.
        
        Args:
            plano_id: ID do plano
            material_id: ID do material a remover
        
        Returns:
            bool: True se removeu com sucesso, False se associação não existe
        
        Raises:
            ValueError: Se plano está concluído/cancelado ou plano_id inválido
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> sucesso = repo.remover_material(1, 5)
            >>> if sucesso:
            ...     print("Material removido")
        """
        if not isinstance(plano_id, int) or plano_id <= 0:
            raise ValueError("plano_id deve ser um inteiro positivo")
        if not isinstance(material_id, int) or material_id <= 0:
            raise ValueError("material_id deve ser um inteiro positivo")
        
        # Validar status do plano
        plano = self.buscar_por_id(plano_id)
        if not plano:
            raise ValueError(f"Plano com ID {plano_id} não existe")
        
        if plano.status in ['concluido', 'cancelado']:
            raise ValueError(
                f"Não é possível remover materiais de um plano {plano.status}"
            )
        
        # Remover material
        try:
            cursor = self.conn.execute(
                """
                DELETE FROM plano_materiais 
                WHERE plano_id = ? AND material_id = ?
                """,
                (plano_id, material_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao remover material: {e}")
    
    def listar_materiais(self, plano_id: int) -> List[int]:
        """
        Lista os IDs de todos os materiais de um plano.
        
        Retorna os materiais em ordem de adição ao plano.
        
        Args:
            plano_id: ID do plano
        
        Returns:
            Lista de IDs de materiais
        
        Raises:
            ValueError: Se plano_id inválido
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> materiais = repo.listar_materiais(1)
            >>> print(f"Plano tem {len(materiais)} materiais")
        """
        if not isinstance(plano_id, int) or plano_id <= 0:
            raise ValueError("plano_id deve ser um inteiro positivo")
        
        cursor = self.conn.execute(
            """
            SELECT material_id FROM plano_materiais 
            WHERE plano_id = ? 
            ORDER BY data_adicao ASC
            """,
            (plano_id,)
        )
        
        return [row['material_id'] for row in cursor.fetchall()]
    
    def atualizar_status(self, plano_id: int, novo_status: str) -> None:
        """
        Atualiza o status do plano de ação.
        
        Valida transições permitidas entre status:
        - rascunho → enviado, cancelado
        - enviado → em_andamento, cancelado
        - em_andamento → concluido, cancelado
        - concluido → (final, sem transições)
        - cancelado → (final, sem transições)
        
        Para enviar um plano (rascunho → enviado), o plano deve ter
        pelo menos um material adicionado.
        
        Args:
            plano_id: ID do plano
            novo_status: Novo status do plano
        
        Raises:
            ValueError: Se status inválido, transição não permitida, ou 
                       plano não tem materiais para envio
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> repo.atualizar_status(1, 'enviado')
            >>> repo.atualizar_status(1, 'em_andamento')
            >>> repo.atualizar_status(1, 'concluido')
        """
        if not isinstance(plano_id, int) or plano_id <= 0:
            raise ValueError("plano_id deve ser um inteiro positivo")
        
        if novo_status not in self.STATUS_VALIDOS:
            raise ValueError(f"Status inválido. Use um de: {self.STATUS_VALIDOS}")
        
        # Buscar plano atual
        plano = self.buscar_por_id(plano_id)
        if not plano:
            raise ValueError(f"Plano com ID {plano_id} não existe")
        
        # Validar transição
        transicoes_permitidas = self.TRANSICOES_VALIDAS.get(plano.status, [])
        if novo_status not in transicoes_permitidas:
            raise ValueError(
                f"Transição inválida de '{plano.status}' para '{novo_status}'. "
                f"Transições permitidas: {transicoes_permitidas}"
            )
        
        # Validar que há materiais antes de enviar
        if novo_status == 'enviado':
            cursor = self.conn.execute(
                "SELECT COUNT(*) as total FROM plano_materiais WHERE plano_id = ?",
                (plano_id,)
            )
            if cursor.fetchone()['total'] == 0:
                raise ValueError("Não é possível enviar um plano sem materiais")
        
        # Atualizar status
        try:
            self.conn.execute(
                "UPDATE planos_acao SET status = ? WHERE id = ?",
                (novo_status, plano_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar status: {e}")
    
    def atualizar(
        self,
        plano_id: int,
        objetivo: Optional[str] = None,
        data_limite: Optional[datetime] = None,
        observacoes: Optional[str] = None
    ) -> None:
        """
        Atualiza campos de um plano de ação.
        
        Não permite atualizar campos em planos concluídos ou cancelados.
        Mínimo um campo deve ser fornecido.
        
        Args:
            plano_id: ID do plano
            objetivo: Novo objetivo (opcional)
            data_limite: Nova data limite (opcional, deve ser datetime)
            observacoes: Novas observações (opcional)
        
        Raises:
            ValueError: Se plano não existe, está finalizado, ou dados inválidos
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> repo.atualizar(1, objetivo='Novo objetivo')
            >>> repo.atualizar(1, observacoes='Analisar progresso')
            >>> from datetime import datetime, timedelta
            >>> repo.atualizar(1, data_limite=datetime.now() + timedelta(days=15))
        """
        if not isinstance(plano_id, int) or plano_id <= 0:
            raise ValueError("plano_id deve ser um inteiro positivo")
        
        # Buscar plano
        plano = self.buscar_por_id(plano_id)
        if not plano:
            raise ValueError(f"Plano com ID {plano_id} não existe")
        
        if plano.status in ['concluido', 'cancelado']:
            raise ValueError(f"Não é possível atualizar um plano {plano.status}")
        
        # Preparar updates
        campos_a_atualizar = {}
        
        if objetivo is not None:
            objetivo = BaseModel._validate_not_empty(objetivo, "Objetivo")
            campos_a_atualizar['objetivo'] = objetivo
        
        if data_limite is not None:
            if not isinstance(data_limite, datetime):
                raise ValueError("data_limite deve ser um objeto datetime")
            if data_limite < plano.data_criacao:
                raise ValueError("Data limite não pode ser anterior à data de criação")
            campos_a_atualizar['data_limite'] = data_limite.isoformat()
        
        if observacoes is not None:
            if observacoes:  # Se não é vazio, valida
                observacoes = BaseModel._validate_not_empty(observacoes, "Observações")
            campos_a_atualizar['observacoes'] = observacoes
        
        if not campos_a_atualizar:
            raise ValueError("Nenhum campo foi fornecido para atualizar")
        
        # Montar query dinamicamente
        sets = ", ".join(f"{campo} = ?" for campo in campos_a_atualizar.keys())
        valores = list(campos_a_atualizar.values()) + [plano_id]
        
        try:
            self.conn.execute(
                f"UPDATE planos_acao SET {sets} WHERE id = ?",
                valores
            )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar plano: {e}")
    
    def excluir(self, plano_id: int) -> bool:
        """
        Exclui um plano de ação e todos os seus materiais associados.
        
        Cascata automática remove registros de plano_materiais.
        
        Args:
            plano_id: ID do plano a deletar
        
        Returns:
            bool: True se deleteou com sucesso, False se plano não existe
        
        Raises:
            ValueError: Se plano_id inválido
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> sucesso = repo.excluir(1)
            >>> if sucesso:
            ...     print("Plano deletado")
        """
        if not isinstance(plano_id, int) or plano_id <= 0:
            raise ValueError("plano_id deve ser um inteiro positivo")
        
        # Verificar existência
        plano = self.buscar_por_id(plano_id)
        if not plano:
            return False
        
        try:
            self.conn.execute(
                "DELETE FROM planos_acao WHERE id = ?",
                (plano_id,)
            )
            self.conn.commit()
            return True
        
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao deletar plano: {e}")
    
    def contar(
        self,
        aluno_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Conta quantidade de planos, opcionalmente filtrados.
        
        Args:
            aluno_id: Filtrar por aluno (opcional)
            status: Filtrar por status (opcional)
        
        Returns:
            int: Quantidade de planos encontrados
        
        Raises:
            ValueError: Se parâmetros inválidos
        
        Example:
            >>> repo = PlanoAcaoRepository()
            >>> total = repo.contar()
            >>> do_aluno_1 = repo.contar(aluno_id=1)
            >>> enviados = repo.contar(status='enviado')
            >>> enviados_aluno_1 = repo.contar(aluno_id=1, status='enviado')
        """
        query = "SELECT COUNT(*) as total FROM planos_acao WHERE 1=1"
        params = []
        
        if aluno_id:
            if not isinstance(aluno_id, int) or aluno_id <= 0:
                raise ValueError("aluno_id deve ser um inteiro positivo")
            query += " AND aluno_id = ?"
            params.append(aluno_id)
        
        if status:
            if status not in self.STATUS_VALIDOS:
                raise ValueError(f"Status inválido. Use um de: {self.STATUS_VALIDOS}")
            query += " AND status = ?"
            params.append(status)
        
        cursor = self.conn.execute(query, params)
        result = cursor.fetchone()
        return result['total'] if result else 0
    
    # ============ Métodos auxiliares ============
    
    @staticmethod
    def _criar_modelo(row: sqlite3.Row) -> PlanoAcaoModel:
        """
        Cria instância de PlanoAcaoModel a partir de uma linha do banco.
        
        Args:
            row: Linha (Row) do banco de dados
        
        Returns:
            PlanoAcaoModel
        """
        return PlanoAcaoModel(
            id=row['id'],
            aluno_id=row['aluno_id'],
            objetivo=row['objetivo'],
            data_criacao=datetime.fromisoformat(row['data_criacao']),
            data_limite=datetime.fromisoformat(row['data_limite']),
            status=row['status'],
            observacoes=row['observacoes']
        )
