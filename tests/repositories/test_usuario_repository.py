"""
Testes para UsuarioRepository.

Testa todas as operações CRUD e autenticação de usuários usando SQL puro.
"""

import pytest
import sqlite3
from educalin.repositories.usuario_repository import UsuarioRepository
from educalin.repositories.usuario_models import ProfessorModel, CoordenadorModel, AlunoModel


@pytest.fixture
def conn():
    """Cria uma conexão em memória para testes."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Criar tabela de usuários
    conn.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('professor', 'coordenador', 'aluno')),
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            registro_funcional TEXT UNIQUE,
            codigo_coordenacao TEXT UNIQUE,
            matricula TEXT UNIQUE,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    yield conn
    conn.close()


@pytest.fixture
def repo(conn):
    """Cria um UsuarioRepository para testes."""
    return UsuarioRepository(conn)


class TestCriar:
    """Testes para o método criar()."""
    
    def test_criar_professor_sucesso(self, repo):
        """Deve criar um professor com sucesso."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF001'
        })
        
        assert usuario_id > 0
        
        # Verificar se foi criado corretamente
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario is not None
        assert isinstance(usuario, ProfessorModel)
        assert usuario.nome == 'João Silva'
        assert usuario.email == 'joao@email.com'
        assert usuario.registro_funcional == 'PROF001'
    
    def test_criar_coordenador_sucesso(self, repo):
        """Deve criar um coordenador com sucesso."""
        usuario_id = repo.criar({
            'tipo_usuario': 'coordenador',
            'nome': 'Ana Paula',
            'email': 'ana@email.com',
            'senha': 'senha456',
            'codigo_coordenacao': 'COORD001'
        })
        
        assert usuario_id > 0
        
        usuario = repo.buscar_por_id(usuario_id)
        assert isinstance(usuario, CoordenadorModel)
        assert usuario.codigo_coordenacao == 'COORD001'
    
    def test_criar_aluno_sucesso(self, repo):
        """Deve criar um aluno com sucesso."""
        usuario_id = repo.criar({
            'tipo_usuario': 'aluno',
            'nome': 'Maria Santos',
            'email': 'maria@email.com',
            'senha': 'senha789',
            'matricula': '2024001'
        })
        
        assert usuario_id > 0
        
        usuario = repo.buscar_por_id(usuario_id)
        assert isinstance(usuario, AlunoModel)
        assert usuario.matricula == '2024001'
    
    def test_criar_email_normalizado(self, repo):
        """Deve normalizar o email (lowercase e trim)."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': '  JOAO@EMAIL.COM  ',
            'senha': 'senha123',
            'registro_funcional': 'PROF002'
        })
        
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario.email == 'joao@email.com'
    
    def test_criar_senha_hasheada(self, repo):
        """Deve armazenar senha hasheada, não texto plano."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF003'
        })
        
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario.senha_hash != 'senha123'
        assert usuario.senha_hash.startswith('$2b$')  # bcrypt hash
    
    def test_criar_campos_obrigatorios_faltando(self, repo):
        """Deve falhar se campos obrigatórios estiverem faltando."""
        with pytest.raises(ValueError, match="Campos obrigatórios"):
            repo.criar({
                'tipo_usuario': 'professor',
                'nome': 'João Silva',
                # falta email e senha
            })
    
    def test_criar_tipo_usuario_invalido(self, repo):
        """Deve falhar com tipo de usuário inválido."""
        with pytest.raises(ValueError, match="tipo_usuario deve ser"):
            repo.criar({
                'tipo_usuario': 'administrador',  # tipo inválido
                'nome': 'João Silva',
                'email': 'joao@email.com',
                'senha': 'senha123'
            })
    
    def test_criar_professor_sem_registro(self, repo):
        """Deve falhar ao criar professor sem registro funcional."""
        with pytest.raises(ValueError, match="registro_funcional é obrigatório"):
            repo.criar({
                'tipo_usuario': 'professor',
                'nome': 'João Silva',
                'email': 'joao@email.com',
                'senha': 'senha123'
                # falta registro_funcional
            })
    
    def test_criar_coordenador_sem_codigo(self, repo):
        """Deve falhar ao criar coordenador sem código."""
        with pytest.raises(ValueError, match="codigo_coordenacao é obrigatório"):
            repo.criar({
                'tipo_usuario': 'coordenador',
                'nome': 'Ana Paula',
                'email': 'ana@email.com',
                'senha': 'senha456'
                # falta codigo_coordenacao
            })
    
    def test_criar_aluno_sem_matricula(self, repo):
        """Deve falhar ao criar aluno sem matrícula."""
        with pytest.raises(ValueError, match="matricula é obrigatória"):
            repo.criar({
                'tipo_usuario': 'aluno',
                'nome': 'Maria Santos',
                'email': 'maria@email.com',
                'senha': 'senha789'
                # falta matricula
            })
    
    def test_criar_email_duplicado(self, repo):
        """Deve falhar ao criar usuário com email duplicado."""
        # Criar primeiro usuário
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF004'
        })
        
        # Tentar criar outro com mesmo email
        with pytest.raises(ValueError, match="já está cadastrado"):
            repo.criar({
                'tipo_usuario': 'aluno',
                'nome': 'Outro Usuário',
                'email': 'joao@email.com',  # email duplicado
                'senha': 'senha456',
                'matricula': '2024002'
            })
    
    def test_criar_email_invalido(self, repo):
        """Deve falhar com formato de email inválido."""
        with pytest.raises(ValueError, match="Formato de e-mail inválido"):
            repo.criar({
                'tipo_usuario': 'professor',
                'nome': 'João Silva',
                'email': 'email_invalido',
                'senha': 'senha123',
                'registro_funcional': 'PROF005'
            })
    
    def test_criar_nome_vazio(self, repo):
        """Deve falhar com nome vazio."""
        with pytest.raises(ValueError, match="Nome não pode ser vazio"):
            repo.criar({
                'tipo_usuario': 'professor',
                'nome': '   ',  # apenas espaços
                'email': 'joao@email.com',
                'senha': 'senha123',
                'registro_funcional': 'PROF006'
            })


class TestBuscarPorId:
    """Testes para o método buscar_por_id()."""
    
    def test_buscar_por_id_existente(self, repo):
        """Deve encontrar usuário por ID existente."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF007'
        })
        
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario is not None
        assert usuario.id == usuario_id
        assert usuario.nome == 'João Silva'
    
    def test_buscar_por_id_inexistente(self, repo):
        """Deve retornar None para ID inexistente."""
        usuario = repo.buscar_por_id(9999)
        assert usuario is None
    
    def test_buscar_por_id_retorna_tipo_correto(self, repo):
        """Deve retornar a subclasse correta (polimorfismo)."""
        prof_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF008'
        })
        
        coord_id = repo.criar({
            'tipo_usuario': 'coordenador',
            'nome': 'Ana',
            'email': 'ana@email.com',
            'senha': 'senha456',
            'codigo_coordenacao': 'COORD002'
        })
        
        aluno_id = repo.criar({
            'tipo_usuario': 'aluno',
            'nome': 'Maria',
            'email': 'maria@email.com',
            'senha': 'senha789',
            'matricula': '2024003'
        })
        
        professor = repo.buscar_por_id(prof_id)
        coordenador = repo.buscar_por_id(coord_id)
        aluno = repo.buscar_por_id(aluno_id)
        
        assert isinstance(professor, ProfessorModel)
        assert isinstance(coordenador, CoordenadorModel)
        assert isinstance(aluno, AlunoModel)


class TestBuscarPorEmail:
    """Testes para o método buscar_por_email()."""
    
    def test_buscar_por_email_existente(self, repo):
        """Deve encontrar usuário por email existente."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF009'
        })
        
        usuario = repo.buscar_por_email('joao@email.com')
        assert usuario is not None
        assert usuario.email == 'joao@email.com'
        assert usuario.nome == 'João Silva'
    
    def test_buscar_por_email_inexistente(self, repo):
        """Deve retornar None para email inexistente."""
        usuario = repo.buscar_por_email('inexistente@email.com')
        assert usuario is None
    
    def test_buscar_por_email_case_insensitive(self, repo):
        """Busca por email deve ser case-insensitive."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF010'
        })
        
        usuario = repo.buscar_por_email('JOAO@EMAIL.COM')
        assert usuario is not None
        assert usuario.email == 'joao@email.com'
    
    def test_buscar_por_email_com_espacos(self, repo):
        """Deve normalizar email com espaços."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF011'
        })
        
        usuario = repo.buscar_por_email('  joao@email.com  ')
        assert usuario is not None
        assert usuario.email == 'joao@email.com'


class TestAtualizar:
    """Testes para o método atualizar()."""
    
    def test_atualizar_nome(self, repo):
        """Deve atualizar o nome do usuário."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF012'
        })
        
        sucesso = repo.atualizar(usuario_id, {'nome': 'João Silva Santos'})
        assert sucesso is True
        
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario.nome == 'João Silva Santos'
    
    def test_atualizar_email(self, repo):
        """Deve atualizar o email do usuário."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF013'
        })
        
        sucesso = repo.atualizar(usuario_id, {'email': 'joao.novo@email.com'})
        assert sucesso is True
        
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario.email == 'joao.novo@email.com'
    
    def test_atualizar_senha(self, repo):
        """Deve atualizar a senha (hasheada) do usuário."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF014'
        })
        
        usuario_antes = repo.buscar_por_id(usuario_id)
        senha_hash_antiga = usuario_antes.senha_hash
        
        sucesso = repo.atualizar(usuario_id, {'senha': 'nova_senha456'})
        assert sucesso is True
        
        usuario_depois = repo.buscar_por_id(usuario_id)
        assert usuario_depois.senha_hash != senha_hash_antiga
        assert usuario_depois.senha_hash.startswith('$2b$')
    
    def test_atualizar_multiplos_campos(self, repo):
        """Deve atualizar múltiplos campos ao mesmo tempo."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF015'
        })
        
        sucesso = repo.atualizar(usuario_id, {
            'nome': 'João Silva Santos',
            'email': 'joao.novo@email.com',
            'senha': 'nova_senha'
        })
        assert sucesso is True
        
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario.nome == 'João Silva Santos'
        assert usuario.email == 'joao.novo@email.com'
    
    def test_atualizar_usuario_inexistente(self, repo):
        """Deve retornar False ao atualizar usuário inexistente."""
        sucesso = repo.atualizar(9999, {'nome': 'Novo Nome'})
        assert sucesso is False
    
    def test_atualizar_sem_dados(self, repo):
        """Deve falhar ao atualizar sem fornecer dados."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF016'
        })
        
        with pytest.raises(ValueError, match="Nenhum dado fornecido"):
            repo.atualizar(usuario_id, {})
    
    def test_atualizar_email_duplicado(self, repo):
        """Deve falhar ao atualizar para email já existente."""
        # Criar dois usuários
        usuario1_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF017'
        })
        
        repo.criar({
            'tipo_usuario': 'aluno',
            'nome': 'Maria Santos',
            'email': 'maria@email.com',
            'senha': 'senha456',
            'matricula': '2024004'
        })
        
        # Tentar atualizar usuario1 para email do usuario2
        with pytest.raises(ValueError, match="já está cadastrado"):
            repo.atualizar(usuario1_id, {'email': 'maria@email.com'})
    
    def test_atualizar_email_invalido(self, repo):
        """Deve falhar ao atualizar para email inválido."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF018'
        })
        
        with pytest.raises(ValueError, match="Formato de e-mail inválido"):
            repo.atualizar(usuario_id, {'email': 'email_invalido'})


class TestAutenticar:
    """Testes para o método autenticar()."""
    
    def test_autenticar_credenciais_validas(self, repo):
        """Deve autenticar com credenciais válidas."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF019'
        })
        
        usuario = repo.autenticar('joao@email.com', 'senha123')
        assert usuario is not None
        assert usuario.email == 'joao@email.com'
        assert usuario.nome == 'João Silva'
    
    def test_autenticar_senha_incorreta(self, repo):
        """Deve retornar None com senha incorreta."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF020'
        })
        
        usuario = repo.autenticar('joao@email.com', 'senha_errada')
        assert usuario is None
    
    def test_autenticar_email_inexistente(self, repo):
        """Deve retornar None com email inexistente."""
        usuario = repo.autenticar('inexistente@email.com', 'senha123')
        assert usuario is None
    
    def test_autenticar_email_case_insensitive(self, repo):
        """Autenticação deve ser case-insensitive para email."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF021'
        })
        
        usuario = repo.autenticar('JOAO@EMAIL.COM', 'senha123')
        assert usuario is not None
        assert usuario.email == 'joao@email.com'
    
    def test_autenticar_retorna_tipo_correto(self, repo):
        """Deve retornar a subclasse correta ao autenticar."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF022'
        })
        
        usuario = repo.autenticar('joao@email.com', 'senha123')
        assert isinstance(usuario, ProfessorModel)
        assert usuario.registro_funcional == 'PROF022'


class TestListarTodos:
    """Testes para o método listar_todos()."""
    
    def test_listar_todos_usuarios(self, repo):
        """Deve listar todos os usuários."""
        # Criar 3 usuários
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF023'
        })
        
        repo.criar({
            'tipo_usuario': 'coordenador',
            'nome': 'Ana Paula',
            'email': 'ana@email.com',
            'senha': 'senha456',
            'codigo_coordenacao': 'COORD003'
        })
        
        repo.criar({
            'tipo_usuario': 'aluno',
            'nome': 'Maria Santos',
            'email': 'maria@email.com',
            'senha': 'senha789',
            'matricula': '2024005'
        })
        
        usuarios = repo.listar_todos()
        assert len(usuarios) == 3
    
    def test_listar_por_tipo_professor(self, repo):
        """Deve filtrar apenas professores."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF024'
        })
        
        repo.criar({
            'tipo_usuario': 'aluno',
            'nome': 'Maria Santos',
            'email': 'maria@email.com',
            'senha': 'senha789',
            'matricula': '2024006'
        })
        
        professores = repo.listar_todos(tipo_usuario='professor')
        assert len(professores) == 1
        assert all(isinstance(u, ProfessorModel) for u in professores)
    
    def test_listar_por_tipo_invalido(self, repo):
        """Deve falhar com tipo de usuário inválido."""
        with pytest.raises(ValueError, match="tipo_usuario deve ser"):
            repo.listar_todos(tipo_usuario='administrador')
    
    def test_listar_todos_vazio(self, repo):
        """Deve retornar lista vazia quando não há usuários."""
        usuarios = repo.listar_todos()
        assert usuarios == []


class TestDeletar:
    """Testes para o método deletar()."""
    
    def test_deletar_usuario_existente(self, repo):
        """Deve deletar usuário existente."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF025'
        })
        
        sucesso = repo.deletar(usuario_id)
        assert sucesso is True
        
        # Verificar que foi deletado
        usuario = repo.buscar_por_id(usuario_id)
        assert usuario is None
    
    def test_deletar_usuario_inexistente(self, repo):
        """Deve retornar False ao deletar usuário inexistente."""
        sucesso = repo.deletar(9999)
        assert sucesso is False


class TestExisteEmail:
    """Testes para o método existe_email()."""
    
    def test_existe_email_cadastrado(self, repo):
        """Deve retornar True para email cadastrado."""
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF026'
        })
        
        assert repo.existe_email('joao@email.com') is True
    
    def test_existe_email_nao_cadastrado(self, repo):
        """Deve retornar False para email não cadastrado."""
        assert repo.existe_email('inexistente@email.com') is False
    
    def test_existe_email_excluindo_proprio(self, repo):
        """Deve excluir o próprio ID ao verificar (útil para updates)."""
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF027'
        })
        
        # Verificar email excluindo o próprio usuário (não deve existir)
        assert repo.existe_email('joao@email.com', excluir_id=usuario_id) is False


class TestContextManager:
    """Testes para uso como context manager."""
    
    def test_usar_como_context_manager(self, conn):
        """Deve funcionar como context manager."""
        with UsuarioRepository(conn) as repo:
            usuario_id = repo.criar({
                'tipo_usuario': 'professor',
                'nome': 'João Silva',
                'email': 'joao@email.com',
                'senha': 'senha123',
                'registro_funcional': 'PROF028'
            })
            
            assert usuario_id > 0
        
        # Conexão não deve ser fechada (pois foi passada externamente)
        cursor = conn.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        assert count == 1
