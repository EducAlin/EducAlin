"""
Testes para MaterialRepository.

Testa todas as operações CRUD de materiais usando SQL puro.
"""

import pytest
import sqlite3
from datetime import datetime

from educalin.repositories.material_repository import MaterialRepository
from educalin.repositories.material_models import (
    MaterialModel, MaterialPDFModel, MaterialVideoModel, MaterialLinkModel
)
from educalin.repositories.usuario_repository import UsuarioRepository


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
    
    # Criar tabela de materiais
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
    
    yield conn
    conn.close()


@pytest.fixture
def repo(conn):
    """Cria um MaterialRepository para testes."""
    return MaterialRepository(conn)


@pytest.fixture
def usuario_repo(conn):
    """Cria um UsuarioRepository para testes."""
    return UsuarioRepository(conn)


@pytest.fixture
def professor_id(usuario_repo):
    """Cria um professor para testes."""
    return usuario_repo.criar({
        'tipo_usuario': 'professor',
        'nome': 'João Silva',
        'email': 'joao@email.com',
        'senha': 'senha123',
        'registro_funcional': 'PROF001'
    })


class TestCriar:
    """Testes para o método criar()."""
    
    def test_criar_material_pdf_sucesso(self, repo, professor_id):
        """Deve criar um material PDF com sucesso."""
        material_id = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Introdução à POO',
            'descricao': 'Conceitos básicos de POO',
            'autor_id': professor_id,
            'topico': 'Programação',
            'num_paginas': 50
        })
        
        assert material_id > 0
        
        # Verificar se foi criado corretamente
        material = repo.buscar_por_id(material_id)
        assert material is not None
        assert isinstance(material, MaterialPDFModel)
        assert material.titulo == 'Introdução à POO'
        assert material.descricao == 'Conceitos básicos de POO'
        assert material.tipo_material == 'pdf'
        assert material.num_paginas == 50
        assert material.topico == 'Programação'
    
    def test_criar_material_video_sucesso(self, repo, professor_id):
        """Deve criar um material Vídeo com sucesso."""
        material_id = repo.criar({
            'tipo_material': 'video',
            'titulo': 'Tutorial Python',
            'descricao': 'Introdução a Python',
            'autor_id': professor_id,
            'topico': 'Linguagens',
            'duracao_segundos': 3600,
            'codec': 'h264'
        })
        
        assert material_id > 0
        
        material = repo.buscar_por_id(material_id)
        assert isinstance(material, MaterialVideoModel)
        assert material.tipo_material == 'video'
        assert material.duracao_segundos == 3600
        assert material.codec == 'h264'
    
    def test_criar_material_link_sucesso(self, repo, professor_id):
        """Deve criar um material Link com sucesso."""
        material_id = repo.criar({
            'tipo_material': 'link',
            'titulo': 'Artigo sobre POO',
            'descricao': 'Referência completa',
            'autor_id': professor_id,
            'topico': 'Referências',
            'url': 'https://example.com/poo',
            'tipo_conteudo': 'artigo'
        })
        
        assert material_id > 0
        
        material = repo.buscar_por_id(material_id)
        assert isinstance(material, MaterialLinkModel)
        assert material.tipo_material == 'link'
        assert material.url == 'https://example.com/poo'
        assert material.tipo_conteudo == 'artigo'
    
    def test_criar_campos_obrigatorios_faltando(self, repo, professor_id):
        """Deve falhar se campos obrigatórios estiverem faltando."""
        with pytest.raises(ValueError, match="Campos obrigatórios"):
            repo.criar({
                'tipo_material': 'pdf',
                'titulo': 'Título',
                # falta descricao e autor_id
            })
    
    def test_criar_tipo_material_invalido(self, repo, professor_id):
        """Deve falhar com tipo de material inválido."""
        with pytest.raises(ValueError, match="tipo_material deve ser"):
            repo.criar({
                'tipo_material': 'imagem',  # tipo inválido
                'titulo': 'Título',
                'descricao': 'Descrição',
                'autor_id': professor_id,
                'num_paginas': 10
            })
    
    def test_criar_pdf_sem_num_paginas(self, repo, professor_id):
        """Deve falhar ao criar PDF sem num_paginas."""
        with pytest.raises(ValueError, match="num_paginas é obrigatório"):
            repo.criar({
                'tipo_material': 'pdf',
                'titulo': 'Título',
                'descricao': 'Descrição',
                'autor_id': professor_id
                # falta num_paginas
            })
    
    def test_criar_pdf_num_paginas_invalido(self, repo, professor_id):
        """Deve falhar ao criar PDF com num_paginas inválido."""
        with pytest.raises(ValueError, match="num_paginas deve ser"):
            repo.criar({
                'tipo_material': 'pdf',
                'titulo': 'Título',
                'descricao': 'Descrição',
                'autor_id': professor_id,
                'num_paginas': 0  # deve ser positivo
            })
    
    def test_criar_video_sem_duracao(self, repo, professor_id):
        """Deve falhar ao criar Vídeo sem duracao_segundos."""
        with pytest.raises(ValueError, match="duracao_segundos é obrigatório"):
            repo.criar({
                'tipo_material': 'video',
                'titulo': 'Título',
                'descricao': 'Descrição',
                'autor_id': professor_id,
                'codec': 'h264'
                # falta duracao_segundos
            })
    
    def test_criar_link_sem_url(self, repo, professor_id):
        """Deve falhar ao criar Link sem URL."""
        with pytest.raises(ValueError, match="url é obrigatória"):
            repo.criar({
                'tipo_material': 'link',
                'titulo': 'Título',
                'descricao': 'Descrição',
                'autor_id': professor_id,
                'tipo_conteudo': 'artigo'
                # falta url
            })
    
    def test_criar_link_url_invalida(self, repo, professor_id):
        """Deve falhar ao criar Link com URL inválida."""
        with pytest.raises(ValueError, match="url deve conter"):
            repo.criar({
                'tipo_material': 'link',
                'titulo': 'Título',
                'descricao': 'Descrição',
                'autor_id': professor_id,
                'url': 'exemplo.com',  # sem protocolo
                'tipo_conteudo': 'artigo'
            })
    
    def test_criar_autor_inexistente(self, repo):
        """Deve falhar ao criar material com autor que não existe."""
        with pytest.raises(ValueError, match="Autor com ID 999 não existe"):
            repo.criar({
                'tipo_material': 'pdf',
                'titulo': 'Título',
                'descricao': 'Descrição',
                'autor_id': 999,  # autor não existe
                'num_paginas': 50
            })


class TestBuscarPorId:
    """Testes para o método buscar_por_id()."""
    
    def test_buscar_material_por_id_sucesso(self, repo, professor_id):
        """Deve buscar um material por ID."""
        material_id = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Título',
            'descricao': 'Descrição',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        
        material = repo.buscar_por_id(material_id)
        assert material is not None
        assert material.id == material_id
        assert material.titulo == 'Título'
    
    def test_buscar_material_inexistente(self, repo):
        """Deve retornar None ao buscar material inexistente."""
        material = repo.buscar_por_id(999)
        assert material is None
    
    def test_buscar_retorna_subclasse_correta(self, repo, professor_id):
        """Deve retornar a subclasse polimórfica correta."""
        pdf_id = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'PDF',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        
        video_id = repo.criar({
            'tipo_material': 'video',
            'titulo': 'Vídeo',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'duracao_segundos': 3600,
            'codec': 'h264'
        })
        
        pdf = repo.buscar_por_id(pdf_id)
        video = repo.buscar_por_id(video_id)
        
        assert isinstance(pdf, MaterialPDFModel)
        assert isinstance(video, MaterialVideoModel)


class TestListarPorProfessor:
    """Testes para o método listar_por_professor()."""
    
    def test_listar_materiais_professor(self, repo, professor_id):
        """Deve listar todos os materiais de um professor."""
        # Criar 3 materiais
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material 1',
            'descricao': 'Desc 1',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        repo.criar({
            'tipo_material': 'video',
            'titulo': 'Material 2',
            'descricao': 'Desc 2',
            'autor_id': professor_id,
            'duracao_segundos': 3600,
            'codec': 'h264'
        })
        repo.criar({
            'tipo_material': 'link',
            'titulo': 'Material 3',
            'descricao': 'Desc 3',
            'autor_id': professor_id,
            'url': 'https://example.com',
            'tipo_conteudo': 'curso'
        })
        
        materiais = repo.listar_por_professor(professor_id)
        assert len(materiais) == 3
    
    def test_listar_professor_sem_materiais(self, repo, usuario_repo):
        """Deve retornar lista vazia para professor sem materiais."""
        prof2_id = usuario_repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'Maria Silva',
            'email': 'maria@email.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF002'
        })
        
        materiais = repo.listar_por_professor(prof2_id)
        assert materiais == []
    
    def test_listar_em_ordem_recente(self, repo, professor_id):
        """Deve listar materiais em ordem decrescente de data."""
        import time
        
        id1 = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material 1',
            'descricao': 'Desc 1',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        
        time.sleep(0.01)  # Pequeno atraso para diferenciar timestamps
        
        id2 = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material 2',
            'descricao': 'Desc 2',
            'autor_id': professor_id,
            'num_paginas': 60
        })
        
        materiais = repo.listar_por_professor(professor_id)
        assert len(materiais) == 2
        # Material mais recente deve estar primeiro
        assert materiais[0].id == id2
        assert materiais[1].id == id1


class TestBuscarPorTopico:
    """Testes para o método buscar_por_topico()."""
    
    def test_buscar_por_topico_sucesso(self, repo, professor_id):
        """Deve buscar materiais por tópico."""
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material 1',
            'descricao': 'Desc 1',
            'autor_id': professor_id,
            'topico': 'Programação',
            'num_paginas': 50
        })
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material 2',
            'descricao': 'Desc 2',
            'autor_id': professor_id,
            'topico': 'Programação',
            'num_paginas': 60
        })
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material 3',
            'descricao': 'Desc 3',
            'autor_id': professor_id,
            'topico': 'Matemática',
            'num_paginas': 70
        })
        
        materiais = repo.buscar_por_topico('Programação')
        assert len(materiais) == 2
        assert all(m.topico == 'Programação' for m in materiais)
    
    def test_buscar_por_topico_inexistente(self, repo, professor_id):
        """Deve retornar lista vazia para tópico inexistente."""
        materiais = repo.buscar_por_topico('Tópico Inexistente')
        assert materiais == []
    
    def test_buscar_por_topico_case_insensitive(self, repo, professor_id):
        """Deve buscar tópicos case-insensitively."""
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'topico': 'PYTHON',
            'num_paginas': 50
        })
        
        materiais1 = repo.buscar_por_topico('python')
        materiais2 = repo.buscar_por_topico('Python')
        materiais3 = repo.buscar_por_topico('PYTHON')
        
        assert len(materiais1) == 1
        assert len(materiais2) == 1
        assert len(materiais3) == 1


class TestExcluir:
    """Testes para o método excluir()."""
    
    def test_excluir_material_sucesso(self, repo, professor_id):
        """Deve excluir um material com sucesso."""
        material_id = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        
        sucesso = repo.excluir(material_id)
        assert sucesso is True
        
        # Verificar que foi deletado
        material = repo.buscar_por_id(material_id)
        assert material is None
    
    def test_excluir_material_inexistente(self, repo):
        """Deve retornar False ao tentar excluir material inexistente."""
        sucesso = repo.excluir(999)
        assert sucesso is False
    
    def test_excluir_material_id_invalido(self, repo):
        """Deve falhar com material_id inválido."""
        with pytest.raises(ValueError, match="material_id deve ser"):
            repo.excluir(0)
        
        with pytest.raises(ValueError, match="material_id deve ser"):
            repo.excluir(-1)


class TestListarTodos:
    """Testes para o método listar_todos()."""
    
    def test_listar_todos_materiais(self, repo, professor_id):
        """Deve listar todos os materiais."""
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'PDF',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        repo.criar({
            'tipo_material': 'video',
            'titulo': 'Vídeo',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'duracao_segundos': 3600,
            'codec': 'h264'
        })
        
        materiais = repo.listar_todos()
        assert len(materiais) == 2
    
    def test_listar_filtrado_por_tipo(self, repo, professor_id):
        """Deve listar apenas materiais de um tipo específico."""
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'PDF',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'PDF 2',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 60
        })
        repo.criar({
            'tipo_material': 'video',
            'titulo': 'Vídeo',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'duracao_segundos': 3600,
            'codec': 'h264'
        })
        
        pdfs = repo.listar_todos('pdf')
        assert len(pdfs) == 2
        assert all(m.tipo_material == 'pdf' for m in pdfs)


class TestContar:
    """Testes para o método contar()."""
    
    def test_contar_todos_materiais(self, repo, professor_id):
        """Deve contar todos os materiais."""
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'PDF',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        repo.criar({
            'tipo_material': 'video',
            'titulo': 'Vídeo',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'duracao_segundos': 3600,
            'codec': 'h264'
        })
        
        total = repo.contar()
        assert total == 2
    
    def test_contar_por_tipo(self, repo, professor_id):
        """Deve contar materiais por tipo."""
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'PDF',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 50
        })
        repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'PDF 2',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'num_paginas': 60
        })
        repo.criar({
            'tipo_material': 'video',
            'titulo': 'Vídeo',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'duracao_segundos': 3600,
            'codec': 'h264'
        })
        
        pdfs = repo.contar(tipo_material='pdf')
        videos = repo.contar(tipo_material='video')
        
        assert pdfs == 2
        assert videos == 1


class TestAtualizarTopico:
    """Testes para o método atualizar_topico()."""
    
    def test_atualizar_topico_sucesso(self, repo, professor_id):
        """Deve atualizar o tópico de um material."""
        material_id = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'topico': 'Tópico Antigo',
            'num_paginas': 50
        })
        
        sucesso = repo.atualizar_topico(material_id, 'Novo Tópico')
        assert sucesso is True
        
        material = repo.buscar_por_id(material_id)
        assert material.topico == 'Novo Tópico'
    
    def test_atualizar_topico_para_none(self, repo, professor_id):
        """Deve limpar o tópico ao passar None."""
        material_id = repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Material',
            'descricao': 'Desc',
            'autor_id': professor_id,
            'topico': 'Tópico',
            'num_paginas': 50
        })
        
        sucesso = repo.atualizar_topico(material_id, None)
        assert sucesso is True
        
        material = repo.buscar_por_id(material_id)
        assert material.topico is None
    
    def test_atualizar_topico_inexistente(self, repo):
        """Deve retornar False ao atualizar material inexistente."""
        sucesso = repo.atualizar_topico(999, 'Novo Tópico')
        assert sucesso is False
