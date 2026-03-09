"""
Fixtures compartilhadas para testes de integração da API.
"""

import pytest
import sqlite3
import tempfile
import os
from fastapi.testclient import TestClient

# Definir variável de ambiente JWT_SECRET_KEY ANTES de importar a app
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-jwt-operations-only"

from educalin.api.main import app


@pytest.fixture(scope="session")
def test_db():
    """
    Cria um banco de dados temporário para testes.
    
    Scope 'session' garante que o banco seja criado uma vez por sessão de testes.
    """
    # Criar arquivo temporário para o banco
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Criar conexão e estrutura do banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_usuario TEXT NOT NULL,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            registro_funcional TEXT,
            codigo_coordenacao TEXT,
            matricula TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Criar tabelas adicionais que possam ser necessárias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            ano INTEGER NOT NULL,
            semestre INTEGER NOT NULL,
            professor_id INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (professor_id) REFERENCES usuarios (id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup: remover arquivo temporário
    try:
        os.unlink(db_path)
    except Exception:
        pass


@pytest.fixture(scope="function")
def db_connection(test_db, monkeypatch):
    """
    Fornece uma conexão com o banco de dados de teste.
    
    Usa monkeypatch para substituir get_connection() durante os testes.
    """
    def mock_get_connection():
        conn = sqlite3.connect(test_db)
        # Configurar row_factory para permitir acesso por nome de coluna
        conn.row_factory = sqlite3.Row
        # Habilitar foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # Substituir a função get_connection para usar o banco de teste
    monkeypatch.setattr("educalin.repositories.base.get_connection", mock_get_connection)
    monkeypatch.setattr("educalin.api.routes.auth.get_connection", mock_get_connection)
    monkeypatch.setattr("educalin.api.dependencies.get_connection", mock_get_connection)
    
    conn = mock_get_connection()
    yield conn
    
    # Limpar dados após cada teste
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios")
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


@pytest.fixture
def client(db_connection):
    """
    Fornece um cliente de teste do FastAPI.
    
    O cliente usa o banco de dados de teste configurado.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def usuario_registrado(client):
    """
    Cria e retorna um usuário já registrado no sistema.
    
    Útil para testes que precisam de um usuário existente.
    """
    usuario_data = {
        "nome": "João Silva",
        "email": "joao@test.com",
        "senha": "senha12345",
        "tipo": "professor",
        "registro_funcional": "PROF123"
    }
    
    response = client.post("/auth/register", json=usuario_data)
    if response.status_code != 201:
        print(f"ERROR registering user: {response.json()}")
    assert response.status_code == 201
    
    return {
        "data": usuario_data,
        "response": response.json()
    }


@pytest.fixture
def usuario_autenticado(client, usuario_registrado):
    """
    Retorna um usuário autenticado com token JWT.
    
    Útil para testes que precisam de autenticação.
    """
    login_data = {
        "email": usuario_registrado["data"]["email"],
        "senha": usuario_registrado["data"]["senha"]
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    
    return {
        "usuario": usuario_registrado["response"],
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }
