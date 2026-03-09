"""
Schema da tabela de usuários com Single Table Inheritance (STI).

Define apenas a tabela 'usuarios' que armazena Professor, Coordenador e Aluno
em uma única tabela usando o padrão Single Table Inheritance.
"""

import sqlite3


def create_usuarios_table(conn: sqlite3.Connection):
    """
    Cria a tabela de usuários com Single Table Inheritance.

    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()

    # Tabela de Usuários com Single Table Inheritance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('professor', 'coordenador', 'aluno')),

            -- Campos comuns a todos os usuários
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,

            -- Campos específicos (podem ser NULL dependendo do tipo)
            registro_funcional TEXT UNIQUE,  -- Professor
            codigo_coordenacao TEXT UNIQUE,  -- Coordenador
            matricula TEXT UNIQUE,           -- Aluno

            -- Timestamps
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo_usuario)")

    conn.commit()
    print("[OK] Tabela 'usuarios' criada com sucesso!")


def create_turmas_tables(conn: sqlite3.Connection):
    """
    Cria as tabelas relacionadas a turmas e seus relacionamentos.

    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()

    # Tabela de Turmas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            disciplina TEXT NOT NULL,
            semestre TEXT NOT NULL,
            professor_id INTEGER,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (professor_id) REFERENCES usuarios(id) ON DELETE SET NULL,
            CHECK(codigo != ''),
            CHECK(disciplina != ''),
            CHECK(semestre != '')
        )
    """)

    # Tabela intermediária Turma-Aluno (Many-to-Many)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turma_alunos (
            turma_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (turma_id, aluno_id),
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turmas_codigo ON turmas(codigo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turmas_professor ON turmas(professor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turma_alunos_turma ON turma_alunos(turma_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turma_alunos_aluno ON turma_alunos(aluno_id)")

    conn.commit()
    print("[OK] Tabelas 'turmas' e 'turma_alunos' criadas com sucesso!")


def create_materiais_table(conn: sqlite3.Connection):
    """
    Cria a tabela de materiais de estudo com Single Table Inheritance.

    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()

    # Tabela de Materiais com Single Table Inheritance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_material TEXT NOT NULL CHECK(tipo_material IN ('pdf', 'video', 'link')),

            -- Campos comuns a todos os materiais
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            autor_id INTEGER NOT NULL,
            topico TEXT DEFAULT NULL,
            data_upload TIMESTAMP NOT NULL,

            -- Campos específicos (podem ser NULL dependendo do tipo)
            num_paginas INTEGER,          -- PDF
            duracao_segundos INTEGER,     -- Video
            codec TEXT,                   -- Video
            url TEXT,                     -- Link
            tipo_conteudo TEXT,           -- Link

            FOREIGN KEY (autor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(titulo != ''),
            CHECK(descricao != '')
        )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_materiais_tipo ON materiais(tipo_material)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_materiais_autor ON materiais(autor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_materiais_topico ON materiais(topico)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_materiais_data ON materiais(data_upload)")

    conn.commit()
    print("[OK] Tabela 'materiais' criada com sucesso!")


def create_avaliacoes_table(conn: sqlite3.Connection):
    """
    Cria a tabela de avaliações.

    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()

    # Tabela de Avaliações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data DATE NOT NULL,
            valor_maximo REAL NOT NULL CHECK(valor_maximo > 0),
            peso REAL NOT NULL CHECK(peso >= 0 AND peso <= 1),
            turma_id INTEGER NOT NULL,
            topico TEXT,
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
            CHECK(titulo != '')
        )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_avaliacoes_turma ON avaliacoes(turma_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_avaliacoes_data ON avaliacoes(data)")

    conn.commit()
    print("[OK] Tabela 'avaliacoes' criada com sucesso!")


def create_notas_table(conn: sqlite3.Connection):
    """
    Cria a tabela de notas (classe de associação entre aluno e avaliação).

    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()

    # Tabela de Notas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            avaliacao_id INTEGER NOT NULL,
            valor REAL NOT NULL CHECK(valor >= 0),
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes(id) ON DELETE CASCADE,
            UNIQUE(aluno_id, avaliacao_id)
        )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_aluno ON notas(aluno_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_avaliacao ON notas(avaliacao_id)")

    conn.commit()
    print("[OK] Tabela 'notas' criada com sucesso!")


def create_metas_table(conn: sqlite3.Connection):
    """
    Cria a tabela de metas de aprendizado.

    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()

    # Tabela de Metas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor_alvo REAL NOT NULL CHECK(valor_alvo > 0),
            prazo TIMESTAMP NOT NULL,
            progresso_atual REAL NOT NULL DEFAULT 0.0 CHECK(progresso_atual >= 0),
            meta_atingida_em TIMESTAMP,
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(descricao != ''),
            CHECK(progresso_atual <= valor_alvo)
        )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metas_aluno ON metas(aluno_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metas_prazo ON metas(prazo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metas_atingida ON metas(meta_atingida_em)")

    conn.commit()
    print("[OK] Tabela 'metas' criada com sucesso!")


def create_planos_acao_tables(conn: sqlite3.Connection):
    """
    Cria as tabelas de planos de ação e relacionamentos com materiais.

    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()

    # Tabela de Planos de Ação
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planos_acao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            objetivo TEXT NOT NULL,
            data_criacao TIMESTAMP NOT NULL,
            data_limite TIMESTAMP NOT NULL,
            status TEXT NOT NULL DEFAULT 'rascunho'
                CHECK(status IN ('rascunho', 'enviado', 'em_andamento', 'concluido', 'cancelado')),
            observacoes TEXT,

            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(objetivo != ''),
            CHECK(data_limite > data_criacao)
        )
    """)

    # Tabela intermediária Plano-Material (Composição Many-to-Many)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plano_materiais (
            plano_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (plano_id, material_id),
            FOREIGN KEY (plano_id) REFERENCES planos_acao(id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materiais(id) ON DELETE CASCADE
        )
    """)

    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_planos_aluno ON planos_acao(aluno_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_planos_status ON planos_acao(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_planos_limite ON planos_acao(data_limite)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plano_materiais_plano ON plano_materiais(plano_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_plano_materiais_material ON plano_materiais(material_id)")

    conn.commit()
    print("[OK] Tabelas 'planos_acao' e 'plano_materiais' criadas com sucesso!")


def create_all_tables(conn: sqlite3.Connection):
    """
    Cria todas as tabelas do sistema na ordem correta.

    Args:
        conn: Conexão ativa com o banco de dados
    """
    print("[INFO] Iniciando criação das tabelas...")

    # Ordem é importante devido às dependências de Foreign Keys
    create_usuarios_table(conn)
    create_turmas_tables(conn)
    create_materiais_table(conn)
    create_avaliacoes_table(conn)
    create_notas_table(conn)
    create_metas_table(conn)
    create_planos_acao_tables(conn)

    print("[OK] Todas as tabelas foram criadas com sucesso!")
