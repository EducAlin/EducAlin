"""
Repository para operações de banco de dados com Usuários.

Implementa o padrão Repository para abstrair operações de persistência
de usuários usando SQL puro (SQLite3).
"""

import sqlite3
from typing import Optional, Dict, Any
from .base_model import BaseModel
from .usuario_models import UsuarioModel, ProfessorModel, CoordenadorModel, AlunoModel
from .base import get_connection


class UsuarioRepository:
    """
    Repository para operações CRUD de usuários.
    
    Utiliza SQL puro para interagir com a tabela 'usuarios'.
    Suporta Single Table Inheritance (STI) para diferentes tipos de usuários.
    """
    
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
    
    def criar(self, usuario_data: Dict[str, Any]) -> int:
        """
        Cria um novo usuário no banco de dados.
        
        Args:
            usuario_data: Dicionário com os dados do usuário:
                - tipo_usuario: 'professor', 'coordenador' ou 'aluno'
                - nome: Nome completo
                - email: E-mail (deve ser único)
                - senha: Senha em texto plano (será hasheada)
                - registro_funcional: (opcional) Para professores
                - codigo_coordenacao: (opcional) Para coordenadores
                - matricula: (opcional) Para alunos
        
        Returns:
            int: ID do usuário criado
        
        Raises:
            ValueError: Se dados obrigatórios estiverem faltando, inválidos, ou se
                ocorrer violação de integridade/unicidade (ex.: email já existir)
        
        Example:
            >>> repo = UsuarioRepository()
            >>> usuario_id = repo.criar({
            ...     'tipo_usuario': 'professor',
            ...     'nome': 'João Silva',
            ...     'email': 'joao@email.com',
            ...     'senha': 'senha123',
            ...     'registro_funcional': 'PROF001'
            ... })
        """
        # Validações básicas
        tipo_usuario = usuario_data.get('tipo_usuario')
        nome = usuario_data.get('nome')
        email = usuario_data.get('email')
        senha = usuario_data.get('senha')
        
        if not all([tipo_usuario, nome, email, senha]):
            raise ValueError("Campos obrigatórios: tipo_usuario, nome, email, senha")
        
        if tipo_usuario not in ('professor', 'coordenador', 'aluno'):
            raise ValueError("tipo_usuario deve ser: professor, coordenador ou aluno")
        
        # Validar e normalizar email
        email = BaseModel._validate_email(email)
        
        # Validar nome não vazio
        nome = BaseModel._validate_not_empty(nome, "Nome")
        
        # Hash da senha
        senha_hash = BaseModel._hash_password(senha)
        
        # Validar campos específicos por tipo
        registro_funcional = usuario_data.get('registro_funcional')
        codigo_coordenacao = usuario_data.get('codigo_coordenacao')
        matricula = usuario_data.get('matricula')
        
        if tipo_usuario == 'professor' and not registro_funcional:
            raise ValueError("registro_funcional é obrigatório para professores")
        
        if tipo_usuario == 'coordenador' and not codigo_coordenacao:
            raise ValueError("codigo_coordenacao é obrigatório para coordenadores")
        
        if tipo_usuario == 'aluno' and not matricula:
            raise ValueError("matricula é obrigatória para alunos")
        
        # Inserir no banco
        try:
            cursor = self.conn.execute(
                """
                INSERT INTO usuarios (
                    tipo_usuario, nome, email, senha_hash,
                    registro_funcional, codigo_coordenacao, matricula
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tipo_usuario, nome, email, senha_hash,
                    registro_funcional, codigo_coordenacao, matricula
                )
            )
            self.conn.commit()
            return cursor.lastrowid
        
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if 'email' in str(e):
                raise ValueError(f"E-mail '{email}' já está cadastrado")
            elif 'registro_funcional' in str(e):
                raise ValueError(f"Registro funcional '{registro_funcional}' já está cadastrado")
            elif 'codigo_coordenacao' in str(e):
                raise ValueError(f"Código de coordenação '{codigo_coordenacao}' já está cadastrado")
            elif 'matricula' in str(e):
                raise ValueError(f"Matrícula '{matricula}' já está cadastrada")
            else:
                raise ValueError(f"Erro de integridade: {e}")
    
    def buscar_por_id(self, id: int) -> Optional[UsuarioModel]:
        """
        Busca um usuário por ID.
        
        Args:
            id: ID do usuário
        
        Returns:
            UsuarioModel (ou subclasse) se encontrado, None caso contrário
        
        Example:
            >>> repo = UsuarioRepository()
            >>> usuario = repo.buscar_por_id(1)
            >>> if usuario:
            ...     print(usuario.nome)
        """
        cursor = self.conn.execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row:
            return UsuarioModel._criar_instancia_polimórfica(row)
        return None
    
    def buscar_por_email(self, email: str) -> Optional[UsuarioModel]:
        """
        Busca um usuário por e-mail.
        
        Args:
            email: E-mail do usuário (não é case-sensitive)
        
        Returns:
            UsuarioModel (ou subclasse) se encontrado, None caso contrário
        
        Example:
            >>> repo = UsuarioRepository()
            >>> usuario = repo.buscar_por_email('joao@email.com')
            >>> if usuario:
            ...     print(f"Encontrado: {usuario.nome}")
        """
        # Normalizar email
        email = email.strip().lower()
        
        cursor = self.conn.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        
        if row:
            return UsuarioModel._criar_instancia_polimórfica(row)
        return None
    
    def atualizar(self, id: int, dados: Dict[str, Any]) -> bool:
        """
        Atualiza dados de um usuário existente.
        
        Args:
            id: ID do usuário a ser atualizado
            dados: Dicionário com os campos a atualizar:
                - nome: (opcional) Novo nome
                - email: (opcional) Novo e-mail
                - senha: (opcional) Nova senha (será hasheada)
                - registro_funcional: (opcional) Novo registro (professores)
                - codigo_coordenacao: (opcional) Novo código (coordenadores)
                - matricula: (opcional) Nova matrícula (alunos)
        
        Returns:
            bool: True se atualizou com sucesso, False se usuário não existe
        
        Raises:
            ValueError: Se dados inválidos forem fornecidos ou se houver conflito de integridade
                (por exemplo, e-mail duplicado)
        
        Example:
            >>> repo = UsuarioRepository()
            >>> sucesso = repo.atualizar(1, {
            ...     'nome': 'João Silva Santos',
            ...     'email': 'joao.novo@email.com'
            ... })
        """
        if not dados:
            raise ValueError("Nenhum dado fornecido para atualização")

        # Chaves permitidas na atualização
        _CAMPOS_PERMITIDOS = {
            'nome', 'email', 'senha',
            'registro_funcional', 'codigo_coordenacao', 'matricula',
        }
        chaves_invalidas = set(dados.keys()) - _CAMPOS_PERMITIDOS
        if chaves_invalidas:
            raise ValueError(
                f"Campos não permitidos para atualização: {', '.join(sorted(chaves_invalidas))}"
            )

        campos_validos = set(dados.keys()) & _CAMPOS_PERMITIDOS
        if not campos_validos:
            raise ValueError("Nenhum campo atualizável válido fornecido")

        # Verificar se usuário existe
        usuario = self.buscar_por_id(id)
        if not usuario:
            return False

        # Validações de campos por tipo de usuário
        tipo_usuario = usuario.tipo_usuario

        if 'registro_funcional' in dados:
            if tipo_usuario != 'professor':
                raise ValueError("registro_funcional só pode ser atualizado para professores")
            if dados['registro_funcional'] is not None and not dados['registro_funcional']:
                raise ValueError("registro_funcional não pode ser vazio para professores")

        if 'codigo_coordenacao' in dados:
            if tipo_usuario != 'coordenador':
                raise ValueError("codigo_coordenacao só pode ser atualizado para coordenadores")
            if dados['codigo_coordenacao'] is not None and not dados['codigo_coordenacao']:
                raise ValueError("codigo_coordenacao não pode ser vazio para coordenadores")

        if 'matricula' in dados:
            if tipo_usuario != 'aluno':
                raise ValueError("matricula só pode ser atualizada para alunos")
            if dados['matricula'] is not None and not dados['matricula']:
                raise ValueError("matricula não pode ser vazia para alunos")

        # Validações
        campos_atualizados = {}
        
        if 'nome' in dados:
            campos_atualizados['nome'] = BaseModel._validate_not_empty(dados['nome'], "Nome")
        
        if 'email' in dados:
            campos_atualizados['email'] = BaseModel._validate_email(dados['email'])
        
        if 'senha' in dados:
            campos_atualizados['senha_hash'] = BaseModel._hash_password(dados['senha'])
        
        if 'registro_funcional' in dados:
            campos_atualizados['registro_funcional'] = dados['registro_funcional']
        
        if 'codigo_coordenacao' in dados:
            campos_atualizados['codigo_coordenacao'] = dados['codigo_coordenacao']
        
        if 'matricula' in dados:
            campos_atualizados['matricula'] = dados['matricula']
        
        # Garante que pelo menos um campo efetivo foi fornecido
        if not campos_atualizados:
            raise ValueError(
                "Nenhum campo válido para atualização foi fornecido. "
                "Campos permitidos: nome, email, senha, registro_funcional, "
                "codigo_coordenacao, matricula."
            )
        
        # Atualizar atualizado_em
        campos_atualizados['atualizado_em'] = 'CURRENT_TIMESTAMP'
        
        # Construir query dinamicamente
        set_clauses = []
        valores = []
        
        for campo, valor in campos_atualizados.items():
            if campo == 'atualizado_em':
                set_clauses.append(f"{campo} = CURRENT_TIMESTAMP")
            else:
                set_clauses.append(f"{campo} = ?")
                valores.append(valor)
        
        valores.append(id)  # para o WHERE
        
        query = f"UPDATE usuarios SET {', '.join(set_clauses)} WHERE id = ?"
        
        try:
            self.conn.execute(query, valores)
            self.conn.commit()
            return True
        
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if 'email' in str(e):
                raise ValueError(f"E-mail '{dados.get('email')}' já está cadastrado")
            elif 'registro_funcional' in str(e):
                raise ValueError(f"Registro funcional já está cadastrado")
            elif 'codigo_coordenacao' in str(e):
                raise ValueError(f"Código de coordenação já está cadastrado")
            elif 'matricula' in str(e):
                raise ValueError(f"Matrícula já está cadastrada")
            else:
                raise ValueError(f"Erro de integridade: {e}")
    
    def autenticar(self, email: str, senha: str) -> Optional[UsuarioModel]:
        """
        Autentica um usuário por e-mail e senha.
        
        Args:
            email: E-mail do usuário
            senha: Senha em texto plano
        
        Returns:
            UsuarioModel (ou subclasse) se autenticação bem-sucedida,
            None caso contrário
        
        Example:
            >>> repo = UsuarioRepository()
            >>> usuario = repo.autenticar('joao@email.com', 'senha123')
            >>> if usuario:
            ...     print(f"Login bem-sucedido: {usuario.nome}")
            ... else:
            ...     print("E-mail ou senha inválidos")
        """
        # Buscar usuário por email
        usuario = self.buscar_por_email(email)
        
        if not usuario:
            return None
        
        # Verificar senha
        if BaseModel._verify_password(senha, usuario.senha_hash):
            return usuario
        
        return None
    
    def listar_todos(self, tipo_usuario: Optional[str] = None) -> list[UsuarioModel]:
        """
        Lista todos os usuários, opcionalmente filtrados por tipo.
        
        Args:
            tipo_usuario: (opcional) Filtrar por tipo: 'professor', 'coordenador', 'aluno'
        
        Returns:
            Lista de UsuarioModel (com subclasses apropriadas)
        
        Example:
            >>> repo = UsuarioRepository()
            >>> professores = repo.listar_todos(tipo_usuario='professor')
            >>> for prof in professores:
            ...     print(f"{prof.nome} - {prof.registro_funcional}")
        """
        if tipo_usuario:
            if tipo_usuario not in ('professor', 'coordenador', 'aluno'):
                raise ValueError("tipo_usuario deve ser: professor, coordenador ou aluno")
            
            cursor = self.conn.execute(
                "SELECT * FROM usuarios WHERE tipo_usuario = ? ORDER BY nome",
                (tipo_usuario,)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM usuarios ORDER BY nome"
            )
        
        return [
            UsuarioModel._criar_instancia_polimórfica(row)
            for row in cursor.fetchall()
        ]

    def buscar(self, query: str, tipo_usuario: Optional[str] = None, limite: int = 10) -> list[UsuarioModel]:
        """
        Busca usuários por nome ou e-mail que contenham a query.

        Args:
            query: Texto para busca (nome ou e-mail).
            tipo_usuario: Opcional, filtra pelo tipo de usuário.
            limite: Máximo de resultados.

        Returns:
            Lista de objetos UsuarioModel (subclasses polimórficas).
        """
        # Normalizar query
        search_term = f"%{query.strip().lower()}%"
        
        sql = "SELECT * FROM usuarios WHERE (LOWER(nome) LIKE ? OR LOWER(email) LIKE ?)"
        params = [search_term, search_term]

        if tipo_usuario:
            if tipo_usuario not in ('professor', 'coordenador', 'aluno'):
                raise ValueError("tipo_usuario deve ser: professor, coordenador ou aluno")
            sql += " AND tipo_usuario = ?"
            params.append(tipo_usuario)

        sql += " ORDER BY nome LIMIT ?"
        params.append(limite)

        cursor = self.conn.execute(sql, params)
        rows = cursor.fetchall()

        return [UsuarioModel._criar_instancia_polimórfica(row) for row in rows]
    
    def deletar(self, id: int) -> bool:
        """
        Remove um usuário do banco de dados.
        
        Args:
            id: ID do usuário a ser removido
        
        Returns:
            bool: True se removeu com sucesso, False se usuário não existe
        
        Example:
            >>> repo = UsuarioRepository()
            >>> sucesso = repo.deletar(1)
        """
        cursor = self.conn.execute(
            "DELETE FROM usuarios WHERE id = ?",
            (id,)
        )
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def existe_email(self, email: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se um e-mail já está cadastrado.
        
        Args:
            email: E-mail a verificar
            excluir_id: (opcional) ID de usuário a excluir da verificação
                       (útil para atualizações)
        
        Returns:
            bool: True se e-mail já existe, False caso contrário
        
        Example:
            >>> repo = UsuarioRepository()
            >>> if repo.existe_email('joao@email.com'):
            ...     print("E-mail já cadastrado")
        """
        email = email.strip().lower()
        
        if excluir_id is not None:
            cursor = self.conn.execute(
                "SELECT COUNT(*) FROM usuarios WHERE email = ? AND id != ?",
                (email, excluir_id)
            )
        else:
            cursor = self.conn.execute(
                "SELECT COUNT(*) FROM usuarios WHERE email = ?",
                (email,)
            )
        
        count = cursor.fetchone()[0]
        return count > 0
