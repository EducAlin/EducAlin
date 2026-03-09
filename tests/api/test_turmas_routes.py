"""
Testes para os endpoints de turmas.

Usa TestClient do FastAPI com banco SQLite na memória,
injetado via override de dependência.
"""
# pylint: disable=redefined-outer-name, unused-argument, too-many-positional-arguments
import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-turmas")

from educalin.api.main import app  # noqa: E402
from educalin.api.dependencies import get_current_user  # noqa: E402
from educalin.api.routes.turmas import get_db  # noqa: E402
from educalin.api.schemas import UsuarioSchema  # noqa: E402
from educalin.repositories.schemas import create_all_tables  # noqa: E402
from educalin.repositories.usuario_models import ProfessorModel, AlunoModel  # noqa: E402
from educalin.repositories.turma_models import TurmaModel  # noqa: E402


@pytest.fixture
def conn():
    """Conexão em memória com schema completo"""
    conn = sqlite3.Connection(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_all_tables(conn)
    yield conn
    conn.close()

@pytest.fixture
def client(conn, professor_id):
    """TestClient com banco em memória injetado e autenticação mockada como professor"""
    def override_get_db():
        yield conn

    def override_get_current_user():
        row = conn.execute(
            "SELECT id, nome, email, tipo_usuario, registro_funcional FROM usuarios WHERE id = ?",
            (professor_id,),
        ).fetchone()
        return UsuarioSchema(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            tipo_usuario=row["tipo_usuario"],
            registro_funcional=row["registro_funcional"],
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()

@pytest.fixture
def professor_id(conn):
    """Cria e retorna ID de um professor de suporte"""
    return ProfessorModel.criar(
        conn,
        "Dr. Exemplo",
        "prof@edu.br",
        "senha123",
        "PROF001"
    )

@pytest.fixture
def aluno_id(conn):
    """Aluno para testes de matrícula e operações em turmas"""
    return AlunoModel.criar(
        conn,
        "Aluno Um",
        "aluno@edu.br",
        "senha",
        "MAT001"
    )

@pytest.fixture
def turma_id(conn, professor_id):
    """Turma para testes de operações de turmas e alunos"""
    return TurmaModel.criar(
        conn,
        "ES006",
        "POO",
        "2025.2",
        professor_id
    )


# GET /turmas
class TestListarTurmas:
    """Testa GET /turmas"""

    def test_retorna_200(self, client, professor_id):
        """Verifica que GET /turmas retorna status 200"""
        response = client.get("/turmas")

        assert response.status_code == 200

    def test_retorna_lista(self, client, professor_id):
        """Verifica que GET /turmas retorna uma lista"""
        response = client.get("/turmas")

        assert isinstance(response.json(), list)

    def test_lista_vazia_sem_turmas(self, client, professor_id):
        """Verifica que lista vazia é retornada quando professor não tem turmas"""
        response = client.get("/turmas")

        assert response.json() == []

    def test_retorna_turmas_do_professor(self, client, professor_id, turma_id):
        """Verifica que GET /turmas retorna turmas do professor autenticado"""
        response = client.get("/turmas")

        assert len(response.json()) == 1

    def test_cada_turma_tem_campos_esperados(self, client, professor_id, turma_id):
        """Verifica que cada turma contém os campos obrigatórios"""
        response = client.get("/turmas")
        turma = response.json()[0]

        assert 'id' in turma
        assert 'codigo' in turma
        assert 'disciplina' in turma
        assert 'semestre' in turma


# POST /turmas
class TestCriarTurma:
    """Testa POST /turmas"""

    def test_retorna_201(self, client, professor_id):
        """Verifica que POST /turmas retorna status 201"""
        response = client.post("/turmas", json={
            "codigo": "ES003",
            "disciplina": "Matemática",
            "semestre": "2025.1",
            "professor_id": professor_id,
        })

        assert response.status_code == 201

    def test_retorna_id_da_turma(self, client, professor_id):
        """Verifica que resposta contém ID da turma criada"""
        response = client.post("/turmas", json={
            "codigo": "ES003",
            "disciplina": "Matemática",
            "semestre": "2025.1",
            "professor_id": professor_id,
        })

        assert 'id' in response.json()
        assert isinstance(response.json()['id'], int)

    def test_turma_aparece_na_listagem(self, client, professor_id):
        """Verifica que turma criada aparece na listagem do professor autenticado"""
        client.post("/turmas", json={
            "codigo": "ES003",
            "disciplina": "Matemática",
            "semestre": "2025.1",
            "professor_id": professor_id,
        })

        response = client.get("/turmas")
        assert len(response.json()) == 1

    def test_codigo_duplicado_retorna_409(self, client, professor_id):
        """Verifica que código duplicado retorna status 409"""
        payload = {
            "codigo": "DUP001",
            "disciplina": "X",
            "semestre": "2025.2",
            "professor_id": professor_id,
        }

        client.post("/turmas", json=payload)
        response = client.post("/turmas", json=payload)

        assert response.status_code == 409

    def test_campos_obrigatorios_ausentes_retorna_422(self, client, professor_id):
        """Verifica que campos obrigatórios ausentes retornam status 422"""
        response = client.post("/turmas", json={"codigo": "X"})
        assert response.status_code == 422

    def test_professor_inexistente_retorna_404(self, client):
        """Verifica que professor_id explícito inexistente retorna status 404"""
        response = client.post("/turmas", json={
            "codigo": "X001",
            "disciplina": "X",
            "semestre": "2025.2",
            "professor_id": 99999,
        })

        assert response.status_code == 404

    def test_sem_professor_id_usa_usuario_autenticado(self, client, professor_id):
        """Verifica que omitir professor_id usa o ID do usuário autenticado"""
        response = client.post("/turmas", json={
            "codigo": "SEM-PROF",
            "disciplina": "X",
            "semestre": "2025.2",
        })

        assert response.status_code == 201
        assert response.json()["professor_id"] == professor_id


# GET /turmas/{id}
class TestDetalhesTurma:
    """Testa GET /turmas/{id}"""

    def test_retorna_200(self, client, turma_id):
        """Verifica que GET /turmas/{id} retorna status 200"""
        response = client.get(f"/turmas/{turma_id}")

        assert response.status_code == 200

    def test_retorna_dados_corretos(self, client, turma_id):
        """Verifica que GET /turmas/{id} retorna dados corretos da turma"""
        response = client.get(f"/turmas/{turma_id}")

        data = response.json()

        assert data['id'] == turma_id
        assert data['codigo'] == "ES006"
        assert data['disciplina'] == "POO"
        assert data['semestre'] == "2025.2"

    def test_id_inexistente_retorna_404(self, client):
        """Verifica que ID inexistente retorna status 404"""
        response = client.get("/turmas/99999")

        assert response.status_code == 404

    def test_resposta_contem_lista_de_alunos(self, client, turma_id):
        """Verifica que resposta contém lista de alunos da turma"""
        response = client.get(f"/turmas/{turma_id}")

        assert 'alunos' in response.json()


# POST /turmas/{id}/alunos
class TestAdicionarAluno:
    """Testa POST /turmas/{id}/alunos"""

    def test_retorna_201(self, client, turma_id, aluno_id):
        """Verifica que POST /turmas/{id}/alunos retorna status 201"""
        response = client.post(
            f"/turmas/{turma_id}/alunos",
            json={"aluno_id": aluno_id}
        )

        assert response.status_code == 201

    def test_aluno_aparece_na_turma(self, client, turma_id, aluno_id):
        """Verifica que aluno adicionado aparece na turma"""
        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_id})

        response = client.get(f"/turmas/{turma_id}")
        ids = [a['id'] for a in response.json()['alunos']]

        assert aluno_id in ids

    def test_aluno_ja_matriculado_retorna_409(self, client, turma_id, aluno_id):
        """Verifica que aluno já matriculado retorna status 409"""
        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_id})

        response = client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_id})

        assert response.status_code == 409

    def test_turma_inexistente_retorna_404(self, client, aluno_id):
        """Verifica que turma inexistente retorna status 404"""
        response = client.post("/turmas/9999/alunos", json={"aluno_id": aluno_id})

        assert response.status_code == 404

    def test_aluno_inexistente_retorna_404(self, client, turma_id):
        """Verifica que aluno inexistente retorna status 404"""
        response = client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": 9999})

        assert response.status_code == 404


# DELETE /turmas/{id}/alunos/{aluno_id}
class TestRemoverAluno:
    """Testa DELETE /turmas/{id}/alunos/{aluno_id}"""

    def test_retorna_200(self, client, turma_id, aluno_id):
        """Verifica que DELETE /turmas/{id}/alunos/{aluno_id} retorna status 200"""
        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_id})

        response = client.delete(f"/turmas/{turma_id}/alunos/{aluno_id}")

        assert response.status_code == 200

    def test_aluno_nao_aparece_mais_na_turma(self, client, turma_id, aluno_id):
        """Verifica que aluno removido não aparece mais na turma"""
        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_id})
        client.delete(f"/turmas/{turma_id}/alunos/{aluno_id}")

        response = client.get(f"/turmas/{turma_id}")
        ids = [a['id'] for a in response.json()['alunos']]

        assert aluno_id not in ids

    def test_aluno_nao_matriculado_retorna_404(self, client, turma_id, aluno_id):
        """Verifica que aluno não matriculado retorna status 404"""
        response = client.delete(f"/turmas/{turma_id}/alunos/{aluno_id}")

        assert response.status_code == 404

    def test_turma_inexistente_retorna_404(self, client, aluno_id):
        """Verifica que turma inexistente retorna status 404"""
        response = client.delete(f"/turmas/9999/alunos/{aluno_id}")

        assert response.status_code == 404


# GET /turmas/{id}/desempenho
class TestDesempenhoTurma:
    """Testa GET /turmas/{id}/desempenho"""

    def test_retorna_200(self, client, turma_id):
        """Verifica que GET /turmas/{id}/desempenho retorna status 200"""
        response = client.get(f"/turmas/{turma_id}/desempenho")

        assert response.status_code == 200

    def test_retorna_campos_obrigatorios(self, client, turma_id):
        """Verifica que resposta contém campos obrigatórios de desempenho"""
        response = client.get(f"/turmas/{turma_id}/desempenho")

        data = response.json()

        assert 'total_alunos' in data
        assert 'media_geral' in data
        assert 'taxa_aprovacao' in data

    def test_turma_vazia_retorna_zeros(self, client, turma_id):
        """Verifica que turma vazia retorna zeros nos indicadores"""
        response = client.get(f"/turmas/{turma_id}/desempenho")

        data = response.json()

        assert data['total_alunos'] == 0
        assert data['media_geral'] == 0.0
        assert data['taxa_aprovacao'] == 0.0

    def test_id_inexistente_retorna_404(self, client):
        """Verifica que ID inexistente retorna status 404"""
        response = client.get("/turmas/9999/desempenho")

        assert response.status_code == 404

    def test_media_calculada_corretamente(self, client, conn, turma_id, aluno_id):
        """Verifica que media_geral é calculada apenas com notas da própria turma"""
        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_id})

        av_id = conn.execute(
            "INSERT INTO avaliacoes (titulo, data, valor_maximo, peso, turma_id) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Prova 1", "2025-06-01", 10.0, 1.0, turma_id),
        ).lastrowid
        conn.execute(
            "INSERT INTO notas (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)",
            (aluno_id, av_id, 8.0),
        )
        conn.commit()

        response = client.get(f"/turmas/{turma_id}/desempenho")
        data = response.json()

        assert data['total_alunos'] == 1
        assert data['media_geral'] == 8.0
        assert data['taxa_aprovacao'] == 100.0

    def test_taxa_aprovacao_parcial(self, client, conn, turma_id):
        """Verifica cálculo de taxa_aprovacao com alunos aprovados e reprovados"""
        aluno_aprovado = AlunoModel.criar(conn, "Aprovado", "aprovado@edu.br", "s", "MAT002")
        aluno_reprovado = AlunoModel.criar(conn, "Reprovado", "reprovado@edu.br", "s", "MAT003")

        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_aprovado})
        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_reprovado})

        av_id = conn.execute(
            "INSERT INTO avaliacoes (titulo, data, valor_maximo, peso, turma_id) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Prova Final", "2025-12-01", 10.0, 1.0, turma_id),
        ).lastrowid
        conn.execute(
            "INSERT INTO notas (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)",
            (aluno_aprovado, av_id, 7.0),
        )
        conn.execute(
            "INSERT INTO notas (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)",
            (aluno_reprovado, av_id, 4.0),
        )
        conn.commit()

        response = client.get(f"/turmas/{turma_id}/desempenho")
        data = response.json()

        assert data['total_alunos'] == 2
        assert data['media_geral'] == 5.5
        assert data['taxa_aprovacao'] == 50.0

    def test_notas_de_outra_turma_nao_afetam_media(
        self, client, conn, turma_id, professor_id, aluno_id
    ):
        """Verifica que notas de outras turmas não contaminam media_geral"""
        outra_turma_id = TurmaModel.criar(conn, "OUT001", "Outra Disc", "2025.2", professor_id)

        client.post(f"/turmas/{turma_id}/alunos", json={"aluno_id": aluno_id})
        client.post(f"/turmas/{outra_turma_id}/alunos", json={"aluno_id": aluno_id})

        av_turma = conn.execute(
            "INSERT INTO avaliacoes (titulo, data, valor_maximo, peso, turma_id) "
            "VALUES (?, ?, ?, ?, ?)",
            ("P1 Turma", "2025-06-01", 10.0, 1.0, turma_id),
        ).lastrowid
        av_outra = conn.execute(
            "INSERT INTO avaliacoes (titulo, data, valor_maximo, peso, turma_id) "
            "VALUES (?, ?, ?, ?, ?)",
            ("P1 Outra", "2025-06-01", 10.0, 1.0, outra_turma_id),
        ).lastrowid

        conn.execute(
            "INSERT INTO notas (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)",
            (aluno_id, av_turma, 6.0),
        )
        conn.execute(
            "INSERT INTO notas (aluno_id, avaliacao_id, valor) VALUES (?, ?, ?)",
            (aluno_id, av_outra, 2.0),
        )
        conn.commit()

        response = client.get(f"/turmas/{turma_id}/desempenho")
        data = response.json()

        assert data['media_geral'] == 6.0
