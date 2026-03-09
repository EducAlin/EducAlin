"""
Testes para PlanoAcaoRepository.

Testa todas as operações CRUD de planos de ação usando SQL puro.
"""

import pytest
import sqlite3
from datetime import datetime, timedelta

from educalin.repositories.plano_acao_repository import PlanoAcaoRepository
from educalin.repositories.plano_acao_models import PlanoAcaoModel
from educalin.repositories.usuario_repository import UsuarioRepository
from educalin.repositories.material_repository import MaterialRepository


@pytest.fixture
def conn():
    """Cria uma conexão em memória para testes."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Tabela de usuários
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
    
    # Tabela de materiais
    conn.execute("""
        CREATE TABLE materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_material TEXT NOT NULL CHECK(tipo_material IN ('pdf', 'video', 'link')),
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            autor_id INTEGER NOT NULL,
            topico TEXT DEFAULT NULL,
            data_upload TIMESTAMP NOT NULL,
            num_paginas INTEGER,
            duracao_segundos INTEGER,
            codec TEXT,
            url TEXT,
            tipo_conteudo TEXT,
            
            FOREIGN KEY (autor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(titulo != ''),
            CHECK(descricao != '')
        )
    """)
    
    # Tabela de planos de ação
    conn.execute("""
        CREATE TABLE planos_acao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            objetivo TEXT NOT NULL,
            data_criacao TIMESTAMP NOT NULL,
            data_limite TIMESTAMP NOT NULL,
            status TEXT NOT NULL DEFAULT 'rascunho' 
                CHECK(status IN ('rascunho', 'enviado', 'em_andamento', 'concluido', 'cancelado')),
            observacoes TEXT DEFAULT NULL,
            
            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(objetivo != '')
        )
    """)
    
    # Tabela de plano_materiais (composição)
    conn.execute("""
        CREATE TABLE plano_materiais (
            plano_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (plano_id, material_id),
            FOREIGN KEY (plano_id) REFERENCES planos_acao(id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materiais(id) ON DELETE CASCADE
        )
    """)
    
    yield conn
    conn.close()


@pytest.fixture
def repo(conn):
    """Cria um PlanoAcaoRepository para testes."""
    return PlanoAcaoRepository(conn)


@pytest.fixture
def usuario_repo(conn):
    """Cria um UsuarioRepository para testes."""
    return UsuarioRepository(conn)


@pytest.fixture
def material_repo(conn):
    """Cria um MaterialRepository para testes."""
    return MaterialRepository(conn)


@pytest.fixture
def aluno_id(usuario_repo):
    """Cria um aluno para testes."""
    return usuario_repo.criar({
        'tipo_usuario': 'aluno',
        'nome': 'Maria Silva',
        'email': 'maria@email.com',
        'senha': 'senha123',
        'matricula': 'ALU001'
    })


@pytest.fixture
def professor_id(usuario_repo):
    """Cria um professor para testes."""
    return usuario_repo.criar({
        'tipo_usuario': 'professor',
        'nome': 'João Santos',
        'email': 'joao@email.com',
        'senha': 'senha123',
        'registro_funcional': 'PROF001'
    })


@pytest.fixture
def material_id(material_repo, professor_id):
    """Cria um material para testes."""
    return material_repo.criar({
        'tipo_material': 'pdf',
        'titulo': 'Introdução à POO',
        'descricao': 'Conceitos básicos',
        'autor_id': professor_id,
        'topico': 'Programação',
        'num_paginas': 50
    })


class TestCriar:
    """Testes para o método criar()."""
    
    def test_criar_plano_sucesso(self, repo, aluno_id):
        """Deve criar um plano de ação com sucesso."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Melhorar notas em POO',
            'prazo_dias': 30
        })
        
        assert plano_id > 0
        plano = repo.buscar_por_id(plano_id)
        assert plano.objetivo == 'Melhorar notas em POO'
        assert plano.status == 'rascunho'
    
    def test_criar_plano_com_observacoes(self, repo, aluno_id):
        """Deve criar um plano com observações."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Estudar design patterns',
            'prazo_dias': 45,
            'observacoes': 'Foco em estratégias e factories'
        })
        
        plano = repo.buscar_por_id(plano_id)
        assert plano.observacoes == 'Foco em estratégias e factories'
    
    def test_criar_plano_sem_objetivo(self, repo, aluno_id):
        """Deve lançar erro se objetivo não for fornecido."""
        with pytest.raises(ValueError, match="Campos obrigatórios"):
            repo.criar({
                'aluno_id': aluno_id,
                'prazo_dias': 30
            })
    
    def test_criar_plano_prazo_invalido(self, repo, aluno_id):
        """Deve lançar erro se prazo for inválido."""
        with pytest.raises(ValueError, match="inteiro positivo"):
            repo.criar({
                'aluno_id': aluno_id,
                'objetivo': 'Estudar',
                'prazo_dias': -5
            })
    
    def test_criar_plano_aluno_inexistente(self, repo):
        """Deve lançar erro se aluno não existe."""
        with pytest.raises(ValueError, match="Aluno com ID 999 não existe"):
            repo.criar({
                'aluno_id': 999,
                'objetivo': 'Estudar',
                'prazo_dias': 30
            })


class TestBuscar:
    """Testes para busca de planos."""
    
    def test_buscar_por_id_existente(self, repo, aluno_id):
        """Deve buscar um plano existente."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Teste',
            'prazo_dias': 20
        })
        
        plano = repo.buscar_por_id(plano_id)
        assert plano is not None
        assert plano.id == plano_id
        assert plano.objetivo == 'Teste'
    
    def test_buscar_por_id_inexistente(self, repo):
        """Deve retornar None para ID inexistente."""
        plano = repo.buscar_por_id(999)
        assert plano is None
    
    def test_buscar_por_id_invalido(self, repo):
        """Deve lançar erro para ID inválido."""
        with pytest.raises(ValueError, match="inteiro positivo"):
            repo.buscar_por_id(-1)


class TestListarPorAluno:
    """Testes para listar planos por aluno."""
    
    def test_listar_por_aluno(self, repo, aluno_id):
        """Deve listar todos os planos de um aluno."""
        repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano 1',
            'prazo_dias': 10
        })
        repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano 2',
            'prazo_dias': 20
        })
        
        planos = repo.listar_por_aluno(aluno_id)
        assert len(planos) == 2
        assert all(p.aluno_id == aluno_id for p in planos)
    
    def test_listar_por_aluno_com_filtro_status(self, repo, aluno_id, material_id):
        """Deve filtrar planos por status."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 10
        })
        
        # Apenas rascunho no início
        planos_rascunho = repo.listar_por_aluno(aluno_id, status='rascunho')
        assert len(planos_rascunho) == 1
        
        # Adicionar material e enviar plano
        repo.adicionar_material(plano_id, material_id)
        repo.atualizar_status(plano_id, 'enviado')
        
        # Agora deve ter um plano enviado
        planos_enviados = repo.listar_por_aluno(aluno_id, status='enviado')
        assert len(planos_enviados) == 1
    
    def test_listar_por_aluno_vazio(self, repo):
        """Deve retornar lista vazia para aluno sem planos."""
        planos = repo.listar_por_aluno(999)
        assert planos == []


class TestMateriais:
    """Testes para operações com materiais."""
    
    def test_adicionar_material(self, repo, aluno_id, material_id):
        """Deve adicionar um material ao plano."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Teste',
            'prazo_dias': 20
        })
        
        repo.adicionar_material(plano_id, material_id)
        materiais = repo.listar_materiais(plano_id)
        assert len(materiais) == 1
        assert materiais[0] == material_id
    
    def test_adicionar_material_duplicado(self, repo, aluno_id, material_id):
        """Deve lançar erro ao adicionar material duplicado."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Teste',
            'prazo_dias': 20
        })
        
        repo.adicionar_material(plano_id, material_id)
        
        with pytest.raises(ValueError, match="já está adicionado"):
            repo.adicionar_material(plano_id, material_id)
    
    def test_adicionar_material_inexistente(self, repo, aluno_id):
        """Deve lançar erro para material inexistente."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Teste',
            'prazo_dias': 20
        })
        
        with pytest.raises(ValueError, match="Material com ID 999 não existe"):
            repo.adicionar_material(plano_id, 999)
    
    def test_remover_material(self, repo, aluno_id, material_id):
        """Deve remover um material do plano."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Teste',
            'prazo_dias': 20
        })
        
        repo.adicionar_material(plano_id, material_id)
        assert len(repo.listar_materiais(plano_id)) == 1
        
        sucesso = repo.remover_material(plano_id, material_id)
        assert sucesso is True
        assert len(repo.listar_materiais(plano_id)) == 0
    
    def test_remover_material_inexistente(self, repo, aluno_id):
        """Deve retornar False ao remover material inexistente."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Teste',
            'prazo_dias': 20
        })
        
        sucesso = repo.remover_material(plano_id, 999)
        assert sucesso is False


class TestStatus:
    """Testes para operações com status."""
    
    def test_atualizar_status_rascunho_para_enviado(self, repo, aluno_id, material_id):
        """Deve enviar plano (requer pelo menos um material)."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        # Deve falhar sem material
        with pytest.raises(ValueError, match="sem materiais"):
            repo.atualizar_status(plano_id, 'enviado')
        
        # Adicionar material e tentar novamente
        repo.adicionar_material(plano_id, material_id)
        repo.atualizar_status(plano_id, 'enviado')
        
        plano = repo.buscar_por_id(plano_id)
        assert plano.status == 'enviado'
    
    def test_atualizar_status_enviado_para_em_andamento(self, repo, aluno_id, material_id):
        """Deve passar de enviado para em_andamento."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        repo.adicionar_material(plano_id, material_id)
        repo.atualizar_status(plano_id, 'enviado')
        repo.atualizar_status(plano_id, 'em_andamento')
        
        plano = repo.buscar_por_id(plano_id)
        assert plano.status == 'em_andamento'
    
    def test_atualizar_status_invalido(self, repo, aluno_id):
        """Deve lançar erro para status inválido."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        with pytest.raises(ValueError, match="Status inválido"):
            repo.atualizar_status(plano_id, 'invalido')
    
    def test_transicao_invalida(self, repo, aluno_id):
        """Deve rejeitar transições inválidas."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        # Não pode ir direto de rascunho para concluido
        with pytest.raises(ValueError, match="Transição inválida"):
            repo.atualizar_status(plano_id, 'concluido')


class TestAtualizar:
    """Testes para atualização de planos."""
    
    def test_atualizar_objetivo(self, repo, aluno_id):
        """Deve atualizar o objetivo."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Objetivo antigo',
            'prazo_dias': 20
        })
        
        repo.atualizar(plano_id, objetivo='Novo objetivo')
        plano = repo.buscar_por_id(plano_id)
        assert plano.objetivo == 'Novo objetivo'
    
    def test_atualizar_data_limite(self, repo, aluno_id):
        """Deve atualizar a data limite."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        nova_data = datetime.now() + timedelta(days=60)
        repo.atualizar(plano_id, data_limite=nova_data)
        plano = repo.buscar_por_id(plano_id)
        
        # Comparar apenas a data (ignorar microssegundos)
        assert plano.data_limite.date() == nova_data.date()
    
    def test_atualizar_observacoes(self, repo, aluno_id):
        """Deve atualizar observações."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        repo.atualizar(plano_id, observacoes='Novas observações')
        plano = repo.buscar_por_id(plano_id)
        assert plano.observacoes == 'Novas observações'


class TestExcluir:
    """Testes para exclusão de planos."""
    
    def test_excluir_plano(self, repo, aluno_id):
        """Deve excluir um plano."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano a deletar',
            'prazo_dias': 20
        })
        
        sucesso = repo.excluir(plano_id)
        assert sucesso is True
        assert repo.buscar_por_id(plano_id) is None
    
    def test_excluir_plano_inexistente(self, repo):
        """Deve retornar False para plano inexistente."""
        sucesso = repo.excluir(999)
        assert sucesso is False
    
    def test_excluir_remove_materiais(self, repo, aluno_id, material_id):
        """Deve remover materiais ao deletar plano."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        repo.adicionar_material(plano_id, material_id)
        assert len(repo.listar_materiais(plano_id)) == 1
        
        repo.excluir(plano_id)
        assert repo.buscar_por_id(plano_id) is None


class TestContar:
    """Testes para contar planos."""
    
    def test_contar_total(self, repo, aluno_id):
        """Deve contar total de planos."""
        repo.criar({'aluno_id': aluno_id, 'objetivo': 'P1', 'prazo_dias': 10})
        repo.criar({'aluno_id': aluno_id, 'objetivo': 'P2', 'prazo_dias': 20})
        
        total = repo.contar()
        assert total == 2
    
    def test_contar_por_aluno(self, repo, aluno_id):
        """Deve contar planos de um aluno específico."""
        repo.criar({'aluno_id': aluno_id, 'objetivo': 'P1', 'prazo_dias': 10})
        repo.criar({'aluno_id': aluno_id, 'objetivo': 'P2', 'prazo_dias': 20})
        
        total = repo.contar(aluno_id=aluno_id)
        assert total == 2
    
    def test_contar_por_status(self, repo, aluno_id, material_id):
        """Deve contar planos por status."""
        plano_id = repo.criar({
            'aluno_id': aluno_id,
            'objetivo': 'Plano',
            'prazo_dias': 20
        })
        
        rascunho = repo.contar(status='rascunho')
        assert rascunho == 1
        
        repo.adicionar_material(plano_id, material_id)
        repo.atualizar_status(plano_id, 'enviado')
        
        enviados = repo.contar(status='enviado')
        assert enviados == 1
        rascunho = repo.contar(status='rascunho')
        assert rascunho == 0


class TestContextManager:
    """Testes para uso com context manager."""
    
    def test_context_manager(self, conn):
        """Deve funcionar como context manager."""
        with PlanoAcaoRepository(conn) as repo:
            assert repo is not None
            assert repo.conn is not None
    
    def test_context_manager_sem_conexao(self, monkeypatch):
        """Deve criar e fechar conexão automaticamente usando in-memory DB."""
        def mock_get_connection():
            conn = sqlite3.connect(':memory:')
            conn.row_factory = sqlite3.Row
            return conn
        
        monkeypatch.setattr(
            'educalin.repositories.plano_acao_repository.get_connection',
            mock_get_connection
        )
        
        with PlanoAcaoRepository() as repo:
            assert repo is not None
            assert repo.conn is not None
