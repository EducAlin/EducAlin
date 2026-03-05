"""
Modelos de usuário usando Single Table Inheritance (STI).

Hierarquia: UsuarioModel -> ProfessorModel, CoordenadorModel, AlunoModel
Todos armazenados na mesma tabela 'usuarios' com discriminador 'tipo_usuario'.
"""

import sqlite3
from typing import Optional
from .base_model import BaseModel


class UsuarioModel(BaseModel):
    """
    Classe base para usuários usando Single Table Inheritance.
    
    O discriminador 'tipo_usuario' determina o tipo concreto:
    - 'professor' -> ProfessorModel
    - 'coordenador' -> CoordenadorModel
    - 'aluno' -> AlunoModel
    """
    
    def __init__(
        self,
        id: int,
        nome: str,
        email: str,
        senha_hash: str,
        tipo_usuario: str,
        registro_funcional: Optional[str] = None,
        codigo_coordenacao: Optional[str] = None,
        matricula: Optional[str] = None,
    ):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.tipo_usuario = tipo_usuario
        self.registro_funcional = registro_funcional
        self.codigo_coordenacao = codigo_coordenacao
        self.matricula = matricula
    
    @staticmethod
    def _criar_instancia_polimórfica(row: sqlite3.Row) -> 'UsuarioModel':
        """
        Factory method que retorna a subclasse correta baseada em tipo_usuario.
        Implementa polimorfismo em consultas.
        """
        tipo = row['tipo_usuario']
        
        if tipo == 'professor':
            return ProfessorModel(
                id=row['id'],
                nome=row['nome'],
                email=row['email'],
                senha_hash=row['senha_hash'],
                tipo_usuario=row['tipo_usuario'],
                registro_funcional=row['registro_funcional'],
            )
        elif tipo == 'coordenador':
            return CoordenadorModel(
                id=row['id'],
                nome=row['nome'],
                email=row['email'],
                senha_hash=row['senha_hash'],
                tipo_usuario=row['tipo_usuario'],
                codigo_coordenacao=row['codigo_coordenacao'],
            )
        elif tipo == 'aluno':
            return AlunoModel(
                id=row['id'],
                nome=row['nome'],
                email=row['email'],
                senha_hash=row['senha_hash'],
                tipo_usuario=row['tipo_usuario'],
                matricula=row['matricula'],
            )
        else:
            # Fallback para UsuarioModel genérico
            return UsuarioModel(
                id=row['id'],
                nome=row['nome'],
                email=row['email'],
                senha_hash=row['senha_hash'],
                tipo_usuario=row['tipo_usuario'],
            )
    
    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, usuario_id: int) -> Optional['UsuarioModel']:
        """Busca usuário por ID, retornando a subclasse correta."""
        cursor = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (usuario_id,)
        )
        row = cursor.fetchone()
        return cls._criar_instancia_polimórfica(row) if row else None
    
    @classmethod
    def buscar_por_email(cls, conn: sqlite3.Connection, email: str) -> Optional['UsuarioModel']:
        """Busca usuário por email, retornando a subclasse correta."""
        cursor = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        return cls._criar_instancia_polimórfica(row) if row else None
    
    @classmethod
    def listar_todos(cls, conn: sqlite3.Connection, tipo_usuario: Optional[str] = None) -> list['UsuarioModel']:
        """
        Lista todos os usuários, opcionalmente filtrados por tipo.
        Retorna instâncias polimórficas corretas.
        """
        if tipo_usuario:
            cursor = conn.execute(
                "SELECT * FROM usuarios WHERE tipo_usuario = ? ORDER BY nome",
                (tipo_usuario,)
            )
        else:
            cursor = conn.execute("SELECT * FROM usuarios ORDER BY nome")
        
        return [cls._criar_instancia_polimórfica(row) for row in cursor.fetchall()]
    
    def atualizar(self, conn: sqlite3.Connection, **campos) -> None:
        """
        Atualiza campos do usuário.
        
        Args:
            conn: Conexão SQLite
            **campos: Campos a atualizar (nome, email, senha)
        """
        # Validações
        if 'email' in campos:
            self._validate_email(campos['email'])
        
        # Hash da senha se for fornecida
        if 'senha' in campos:
            campos['senha_hash'] = self._hash_password(campos.pop('senha'))
        
        # Monta query dinamicamente
        sets = ', '.join(f"{campo} = ?" for campo in campos.keys())
        valores = list(campos.values()) + [self.id]
        
        conn.execute(
            f"UPDATE usuarios SET {sets} WHERE id = ?",
            valores
        )
        conn.commit()
        
        # Atualiza instância local
        for campo, valor in campos.items():
            setattr(self, campo, valor)
    
    def deletar(self, conn: sqlite3.Connection) -> None:
        """Remove usuário do banco."""
        conn.execute("DELETE FROM usuarios WHERE id = ?", (self.id,))
        conn.commit()
    
    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return self._verify_password(senha, self.senha_hash)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, nome='{self.nome}', email='{self.email}')>"


class ProfessorModel(UsuarioModel):
    """Modelo de Professor (herda de UsuarioModel via STI)."""
    
    def __init__(
        self,
        id: int,
        nome: str,
        email: str,
        senha_hash: str,
        tipo_usuario: str,
        registro_funcional: str,
    ):
        super().__init__(
            id=id,
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            tipo_usuario=tipo_usuario,
            registro_funcional=registro_funcional,
        )
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        nome: str,
        email: str,
        senha: str,
        registro_funcional: str,
    ) -> int:
        """
        Cria um novo professor.
        
        Returns:
            ID do professor criado
        """
        # Validações
        cls._validate_required(nome=nome, email=email, senha=senha, registro_funcional=registro_funcional)
        cls._validate_email(email)
        
        senha_hash = cls._hash_password(senha)
        
        cursor = conn.execute(
            """
            INSERT INTO usuarios (tipo_usuario, nome, email, senha_hash, registro_funcional)
            VALUES (?, ?, ?, ?, ?)
            """,
            ('professor', nome, email, senha_hash, registro_funcional)
        )
        conn.commit()
        return cursor.lastrowid
    
    @classmethod
    def buscar_por_registro(cls, conn: sqlite3.Connection, registro_funcional: str) -> Optional['ProfessorModel']:
        """Busca professor por registro funcional."""
        cursor = conn.execute(
            "SELECT * FROM usuarios WHERE tipo_usuario = 'professor' AND registro_funcional = ?",
            (registro_funcional,)
        )
        row = cursor.fetchone()
        return cls._criar_instancia_polimórfica(row) if row else None
    
    def __repr__(self) -> str:
        return f"<ProfessorModel(id={self.id}, nome='{self.nome}', registro='{self.registro_funcional}')>"


class CoordenadorModel(UsuarioModel):
    """Modelo de Coordenador (herda de UsuarioModel via STI)."""
    
    def __init__(
        self,
        id: int,
        nome: str,
        email: str,
        senha_hash: str,
        tipo_usuario: str,
        codigo_coordenacao: str,
    ):
        super().__init__(
            id=id,
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            tipo_usuario=tipo_usuario,
            codigo_coordenacao=codigo_coordenacao,
        )
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        nome: str,
        email: str,
        senha: str,
        codigo_coordenacao: str,
    ) -> int:
        """
        Cria um novo coordenador.
        
        Returns:
            ID do coordenador criado
        """
        # Validações
        cls._validate_required(nome=nome, email=email, senha=senha, codigo_coordenacao=codigo_coordenacao)
        cls._validate_email(email)
        
        senha_hash = cls._hash_password(senha)
        
        cursor = conn.execute(
            """
            INSERT INTO usuarios (tipo_usuario, nome, email, senha_hash, codigo_coordenacao)
            VALUES (?, ?, ?, ?, ?)
            """,
            ('coordenador', nome, email, senha_hash, codigo_coordenacao)
        )
        conn.commit()
        return cursor.lastrowid
    
    @classmethod
    def buscar_por_codigo(cls, conn: sqlite3.Connection, codigo_coordenacao: str) -> Optional['CoordenadorModel']:
        """Busca coordenador por código de coordenação."""
        cursor = conn.execute(
            "SELECT * FROM usuarios WHERE tipo_usuario = 'coordenador' AND codigo_coordenacao = ?",
            (codigo_coordenacao,)
        )
        row = cursor.fetchone()
        return cls._criar_instancia_polimórfica(row) if row else None
    
    def __repr__(self) -> str:
        return f"<CoordenadorModel(id={self.id}, nome='{self.nome}', codigo='{self.codigo_coordenacao}')>"


class AlunoModel(UsuarioModel):
    """Modelo de Aluno (herda de UsuarioModel via STI)."""
    
    def __init__(
        self,
        id: int,
        nome: str,
        email: str,
        senha_hash: str,
        tipo_usuario: str,
        matricula: str,
    ):
        super().__init__(
            id=id,
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            tipo_usuario=tipo_usuario,
            matricula=matricula,
        )
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        nome: str,
        email: str,
        senha: str,
        matricula: str,
    ) -> int:
        """
        Cria um novo aluno.
        
        Returns:
            ID do aluno criado
        """
        # Validações
        cls._validate_required(nome=nome, email=email, senha=senha, matricula=matricula)
        cls._validate_email(email)
        
        senha_hash = cls._hash_password(senha)
        
        cursor = conn.execute(
            """
            INSERT INTO usuarios (tipo_usuario, nome, email, senha_hash, matricula)
            VALUES (?, ?, ?, ?, ?)
            """,
            ('aluno', nome, email, senha_hash, matricula)
        )
        conn.commit()
        return cursor.lastrowid
    
    @classmethod
    def buscar_por_matricula(cls, conn: sqlite3.Connection, matricula: str) -> Optional['AlunoModel']:
        """Busca aluno por matrícula."""
        cursor = conn.execute(
            "SELECT * FROM usuarios WHERE tipo_usuario = 'aluno' AND matricula = ?",
            (matricula,)
        )
        row = cursor.fetchone()
        return cls._criar_instancia_polimórfica(row) if row else None
    
    def __repr__(self) -> str:
        return f"<AlunoModel(id={self.id}, nome='{self.nome}', matricula='{self.matricula}')>"
