"""
Cria as tabelas de turmas e relacionamentos com alunos.

depends: 001_create_usuarios_table
"""

from yoyo import step

__depends__ = ['001_create_usuarios_table']

steps = [
    step(
        """
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
        """,
        "DROP TABLE IF EXISTS turmas"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_turmas_codigo ON turmas(codigo)",
        "DROP INDEX IF EXISTS idx_turmas_codigo"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_turmas_professor ON turmas(professor_id)",
        "DROP INDEX IF EXISTS idx_turmas_professor"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS turma_alunos (
            turma_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (turma_id, aluno_id),
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
        """,
        "DROP TABLE IF EXISTS turma_alunos"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_turma_alunos_turma ON turma_alunos(turma_id)",
        "DROP INDEX IF EXISTS idx_turma_alunos_turma"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_turma_alunos_aluno ON turma_alunos(aluno_id)",
        "DROP INDEX IF EXISTS idx_turma_alunos_aluno"
    )
]
