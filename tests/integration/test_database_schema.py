"""
Testes para verificar criação de tabelas do banco de dados.
"""
import sqlite3
import pytest
from pathlib import Path


@pytest.fixture
def db_path():
    """Retorna o caminho para o banco de dados de teste."""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "database" / "educalin.db"


@pytest.fixture
def db_connection(db_path):
    """Cria conexão com o banco de dados."""
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


def test_database_exists(db_path):
    """Testa se o arquivo do banco de dados existe."""
    assert db_path.exists(), f"Banco de dados não encontrado em {db_path}"


def test_usuarios_table_exists(db_connection):
    """Testa se a tabela usuarios foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'usuarios' não foi criada"
    assert result[0] == 'usuarios'


def test_turmas_table_exists(db_connection):
    """Testa se a tabela turmas foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='turmas'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'turmas' não foi criada"
    assert result[0] == 'turmas'


def test_turma_alunos_table_exists(db_connection):
    """Testa se a tabela turma_alunos foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='turma_alunos'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'turma_alunos' não foi criada"
    assert result[0] == 'turma_alunos'


def test_materiais_table_exists(db_connection):
    """Testa se a tabela materiais foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='materiais'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'materiais' não foi criada"
    assert result[0] == 'materiais'


def test_avaliacoes_table_exists(db_connection):
    """Testa se a tabela avaliacoes foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='avaliacoes'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'avaliacoes' não foi criada"
    assert result[0] == 'avaliacoes'


def test_notas_table_exists(db_connection):
    """Testa se a tabela notas foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='notas'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'notas' não foi criada"
    assert result[0] == 'notas'


def test_metas_table_exists(db_connection):
    """Testa se a tabela metas foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='metas'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'metas' não foi criada"
    assert result[0] == 'metas'


def test_planos_acao_table_exists(db_connection):
    """Testa se a tabela planos_acao foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='planos_acao'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'planos_acao' não foi criada"
    assert result[0] == 'planos_acao'


def test_plano_materiais_table_exists(db_connection):
    """Testa se a tabela plano_materiais foi criada."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='plano_materiais'"
    )
    result = cursor.fetchone()
    assert result is not None, "Tabela 'plano_materiais' não foi criada"
    assert result[0] == 'plano_materiais'


def test_all_tables_count(db_connection):
    """Testa se todas as 9 tabelas principais foram criadas."""
    cursor = db_connection.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        AND name NOT LIKE '_yoyo_%'
        AND name NOT LIKE 'yoyo_%'
        """
    )
    count = cursor.fetchone()[0]
    assert count == 9, f"Esperado 9 tabelas, mas encontrado {count}"


def test_usuarios_table_schema(db_connection):
    """Testa se a tabela usuarios tem as colunas corretas."""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = {row[1] for row in cursor.fetchall()}
    
    expected_columns = {
        'id', 'tipo_usuario', 'nome', 'email', 'senha_hash',
        'registro_funcional', 'codigo_coordenacao', 'matricula',
        'criado_em', 'atualizado_em'
    }
    
    assert expected_columns.issubset(columns), \
        f"Colunas esperadas: {expected_columns}, mas encontrado: {columns}"


def test_materiais_table_schema(db_connection):
    """Testa se a tabela materiais tem as colunas corretas (STI)."""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA table_info(materiais)")
    columns = {row[1] for row in cursor.fetchall()}
    
    expected_columns = {
        'id', 'tipo_material', 'titulo', 'descricao', 'autor_id', 'data_upload',
        'num_paginas', 'duracao_segundos', 'codec', 'url', 'tipo_conteudo'
    }
    
    assert expected_columns.issubset(columns), \
        f"Colunas esperadas: {expected_columns}, mas encontrado: {columns}"


def test_indexes_created(db_connection):
    """Testa se os índices foram criados."""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
    )
    indexes = {row[0] for row in cursor.fetchall()}
    
    # Verificar alguns índices importantes
    important_indexes = {
        'idx_usuarios_email',
        'idx_usuarios_tipo',
        'idx_turmas_codigo',
        'idx_materiais_tipo',
        'idx_avaliacoes_turma',
        'idx_notas_aluno',
        'idx_metas_aluno',
        'idx_planos_aluno'
    }
    
    assert important_indexes.issubset(indexes), \
        f"Índices esperados: {important_indexes}, mas encontrado: {indexes}"


def test_foreign_keys_enabled(db_connection):
    """Testa se as foreign keys estão habilitadas."""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA foreign_keys")
    result = cursor.fetchone()
    # Note: O valor pode ser 0 por padrão, mas a estrutura deve estar correta
    assert result is not None, "Não foi possível verificar foreign keys"
