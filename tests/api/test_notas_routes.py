"""
Testes para os endpoints de avaliações e notas.

Usa TestClient do FastAPI com banco SQLite em memória,
injetado via override de dependência.
"""
# pylint: disable=redefined-outer-name, unused-argument, too-many-positional-arguments
import sqlite3
from datetime import date
import pytest
from fastapi.testclient import TestClient

from educalin.api.main import app
from educalin.api.routes.notas import get_db
from educalin.repositories.schemas import create_all_tables
from educalin.repositories.usuario_models import ProfessorModel, AlunoModel
from educalin.repositories.turma_models import TurmaModel
from educalin.repositories.avaliacao_models import AvaliacaoModel


@pytest.fixture
def conn():
    """Conexão SQLite em memória isolada por teste."""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_all_tables(conn)
    yield conn
    conn.close()


@pytest.fixture
def client(conn):
    """TestClient com banco em memória injetado."""
    def override_get_db():
        yield conn

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def professor_id(conn):
    """Cria um professor para os testes."""
    return ProfessorModel.criar(conn, "Dr. Exemplo", "prof@edu.com", "senha123", "PROF001")

@pytest.fixture
def aluno_id(conn):
    """Cria um aluno para os testes."""
    return AlunoModel.criar(conn, "Aluno Um", "aluno1@edu.com", "senha", "MAT001")

@pytest.fixture
def outro_aluno_id(conn):
    """Cria um segundo aluno para testes de isolamento."""
    return AlunoModel.criar(conn, "Aluno Dois", "aluno2@edu.com", "senha", "MAT002")

@pytest.fixture
def turma_id(conn, professor_id):
    """Cria uma turma vinculada a um professor."""
    return TurmaModel.criar(conn, "POO-2026.1", "POO", "2026.1", professor_id)

@pytest.fixture
def avaliacao_id(conn, turma_id):
    """Cria uma avaliação vinculada a uma turma."""
    return AvaliacaoModel.criar(
        conn,
        titulo="Prova 1",
        data=date(2026, 4, 10),
        valor_maximo=10.0,
        peso=0.4,
        turma_id=turma_id,
    )

@pytest.fixture
def avaliacao_com_topico_id(conn, turma_id):
    """Cria uma avaliação com o campo 'topico' preenchido."""
    return AvaliacaoModel.criar(
        conn,
        titulo="Prova Herança",
        data=date(2026, 5, 10),
        valor_maximo=10.0,
        peso=0.3,
        turma_id=turma_id,
        topico="heranca",
    )


# POST /turmas/{id}/avaliacoes
class TestCriarAvaliacao:
    """Testa POST /turmas/{id}/avaliacoes."""

    def test_retorna_201(self, client, turma_id):
        """Deve retornar status 201 ao criar avaliação válida."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova 1",
            "data": "2026-04-10",
            "valor_maximo": 10.0,
            "peso": 0.4,
        })
        assert response.status_code == 201

    def test_retorna_id_da_avaliacao(self, client, turma_id):
        """A resposta deve conter o ID da avaliação criada."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova 1",
            "data": "2026-04-10",
            "valor_maximo": 10.0,
            "peso": 0.4,
        })
        assert 'id' in response.json()
        assert isinstance(response.json()['id'], int)

    def test_retorna_campos_da_avaliacao(self, client, turma_id):
        """A resposta deve ecoar os dados da avaliação criada."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova 1",
            "data": "2026-04-10",
            "valor_maximo": 10.0,
            "peso": 0.4,
        })
        data = response.json()
        assert data['titulo'] == "Prova 1"
        assert data['turma_id'] == turma_id
        assert data['valor_maximo'] == 10.0

    def test_turma_inexistente_retorna_404(self, client):
        """Deve retornar 404 ao tentar criar avaliação para turma inexistente."""
        response = client.post("/turmas/99999/avaliacoes", json={
            "titulo": "Prova 1",
            "data": "2026-04-10",
            "valor_maximo": 10.0,
            "peso": 0.4,
        })
        assert response.status_code == 404

    def test_titulo_vazio_retorna_422(self, client, turma_id):
        """Título vazio deve ser rejeitado com 422."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "",
            "data": "2026-04-10",
            "valor_maximo": 10.0,
            "peso": 0.4,
        })
        assert response.status_code == 422

    def test_valor_maximo_negativo_retorna_422(self, client, turma_id):
        """Valor máximo negativo deve ser rejeitado com 422."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova 1",
            "data": "2026-04-10",
            "valor_maximo": -1.0,
            "peso": 0.4,
        })
        assert response.status_code == 422

    def test_peso_fora_do_intervalo_retorna_422(self, client, turma_id):
        """Peso acima de 1.0 deve ser rejeitado com 422."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova 1",
            "data": "2026-04-10",
            "valor_maximo": 10.0,
            "peso": 1.5,
        })
        assert response.status_code == 422

    def test_campos_ausentes_retorna_422(self, client, turma_id):
        """A falta de campos obrigatórios deve resultar em 422."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova 1",
        })
        assert response.status_code == 422

    def test_peso_zero_valido(self, client, turma_id):
        """Peso igual a 0.0 é válido (ge=0) e deve retornar 201."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Atividade Opcional",
            "data": "2026-06-01",
            "valor_maximo": 5.0,
            "peso": 0.0,
        })
        assert response.status_code == 201

    def test_valor_maximo_zero_retorna_422(self, client, turma_id):
        """valor_maximo=0 deve ser rejeitado com 422 (gt=0)."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova Invalida",
            "data": "2026-06-01",
            "valor_maximo": 0.0,
            "peso": 0.4,
        })
        assert response.status_code == 422

    def test_com_topico_opcional(self, client, turma_id):
        """Campo topico é opcional e deve ser aceito."""
        response = client.post(f"/turmas/{turma_id}/avaliacoes", json={
            "titulo": "Prova Herança",
            "data": "2026-05-10",
            "valor_maximo": 10.0,
            "peso": 0.3,
            "topico": "heranca",
        })
        assert response.status_code == 201
        assert response.json().get('topico') == "heranca"


# POST /avaliacoes/{id}/notas
class TestRegistrarNota:
    """Testa POST /avaliacoes/{id}/notas."""

    def test_retorna_201(self, client, avaliacao_id, aluno_id):
        """Deve retornar 201 ao registrar nota válida."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id,
            "valor": 7.5,
        })
        assert response.status_code == 201

    def test_retorna_id_da_nota(self, client, avaliacao_id, aluno_id):
        """A resposta deve conter o ID da nota registrada."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id,
            "valor": 7.5,
        })
        assert 'id' in response.json()

    def test_retorna_campos_da_nota(self, client, avaliacao_id, aluno_id):
        """A resposta deve ecoar os dados da nota registrada."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id,
            "valor": 7.5,
        })
        data = response.json()
        assert data['aluno_id'] == aluno_id
        assert data['avaliacao_id'] == avaliacao_id
        assert data['valor'] == 7.5

    def test_valor_acima_do_maximo_retorna_422(self, client, avaliacao_id, aluno_id):
        """valor_maximo da avaliação é 10.0 — nota 11 deve ser rejeitada."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id,
            "valor": 11.0,
        })
        assert response.status_code == 422

    def test_valor_negativo_retorna_422(self, client, avaliacao_id, aluno_id):
        """Nota com valor negativo deve ser rejeitada com 422."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id,
            "valor": -1.0,
        })
        assert response.status_code == 422

    def test_nota_duplicada_retorna_409(self, client, avaliacao_id, aluno_id):
        """Não deve permitir registrar duas notas para o mesmo aluno na mesma avaliação."""
        client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id, "valor": 7.5,
        })
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id, "valor": 8.0,
        })
        assert response.status_code == 409

    def test_avaliacao_inexistente_retorna_404(self, client, aluno_id):
        """Deve retornar 404 ao registrar nota para avaliação inexistente."""
        response = client.post("/avaliacoes/99999/notas", json={
            "aluno_id": aluno_id,
            "valor": 7.5,
        })
        assert response.status_code == 404

    def test_aluno_inexistente_retorna_404(self, client, avaliacao_id):
        """Deve retornar 404 ao registrar nota para aluno inexistente."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": 99999,
            "valor": 7.5,
        })
        assert response.status_code == 404

    def test_professor_como_aluno_retorna_404(self, client, avaliacao_id, professor_id):
        """Usuário do tipo 'professor' não deve ser aceito como aluno."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": professor_id,
            "valor": 7.5,
        })
        assert response.status_code == 404

    def test_valor_zero_valido(self, client, avaliacao_id, aluno_id):
        """Nota zero deve ser permitida."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id,
            "valor": 0.0,
        })
        assert response.status_code == 201

    def test_valor_igual_ao_maximo_valido(self, client, avaliacao_id, aluno_id):
        """Nota igual ao valor máximo da avaliação deve ser permitida."""
        response = client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id,
            "valor": 10.0,
        })
        assert response.status_code == 201


# GET /alunos/{id}/notas
class TestHistoricoAluno:
    """Testa GET /alunos/{id}/notas."""

    def test_retorna_200(self, client, aluno_id):
        """Deve retornar status 200 ao buscar histórico do aluno."""
        response = client.get(f"/alunos/{aluno_id}/notas")
        assert response.status_code == 200

    def test_retorna_lista(self, client, aluno_id):
        """Deve retornar uma lista (mesmo que vazia)."""
        assert isinstance(client.get(f"/alunos/{aluno_id}/notas").json(), list)

    def test_lista_vazia_sem_notas(self, client, aluno_id):
        """Deve retornar lista vazia se o aluno não tiver notas."""
        assert client.get(f"/alunos/{aluno_id}/notas").json() == []

    def test_retorna_notas_registradas(self, client, aluno_id, avaliacao_id):
        """Deve listar as notas que foram registradas para o aluno."""
        client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id, "valor": 8.0,
        })
        notas = client.get(f"/alunos/{aluno_id}/notas").json()
        assert len(notas) == 1

    def test_cada_nota_tem_campos_obrigatorios(self, client, aluno_id, avaliacao_id):
        """As notas no histórico devem conter valor e IDs de referência."""
        client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id, "valor": 8.0,
        })
        nota = client.get(f"/alunos/{aluno_id}/notas").json()[0]
        assert 'valor' in nota
        assert 'avaliacao_id' in nota
        assert 'aluno_id' in nota

    def test_filtra_por_turma(self, client, aluno_id, turma_id, avaliacao_id, professor_id, conn):
        """Query param turma_id deve filtrar notas pela turma."""
        outra_turma_id = TurmaModel.criar(conn, "MAT-2026.1", "Mat", "2026.1", professor_id)
        outra_av_id = AvaliacaoModel.criar(
            conn, "P1 Mat", date(2026, 4, 20), 10.0, 0.3, outra_turma_id
        )
        client.post(f"/avaliacoes/{avaliacao_id}/notas", json={"aluno_id": aluno_id, "valor": 7.0})
        client.post(f"/avaliacoes/{outra_av_id}/notas", json={"aluno_id": aluno_id, "valor": 9.0})
        notas = client.get(f"/alunos/{aluno_id}/notas?turma_id={turma_id}").json()
        assert len(notas) == 1
        assert notas[0]['valor'] == 7.0

    def test_isola_notas_entre_alunos(self, client, aluno_id, outro_aluno_id, avaliacao_id):
        """O histórico de um aluno não deve conter notas de outro aluno."""
        client.post(f"/avaliacoes/{avaliacao_id}/notas", json={"aluno_id": aluno_id, "valor": 8.0})
        notas = client.get(f"/alunos/{outro_aluno_id}/notas").json()
        assert notas == []

    def test_aluno_inexistente_retorna_404(self, client):
        """Deve retornar 404 ao buscar histórico de aluno inexistente."""
        response = client.get("/alunos/99999/notas")
        assert response.status_code == 404

    def test_turma_inexistente_como_filtro_retorna_lista_vazia(
        self, client, aluno_id, avaliacao_id
    ):
        """turma_id inexistente como query param deve retornar lista vazia."""
        client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id, "valor": 8.0,
        })
        notas = client.get(f"/alunos/{aluno_id}/notas?turma_id=99999").json()
        assert notas == []


# GET /turmas/{id}/relatorio
class TestRelatorioTurma:
    """Testa GET /turmas/{id}/relatorio."""

    def test_retorna_200(self, client, turma_id):
        """Deve retornar status 200 ao solicitar relatório da turma."""
        response = client.get(f"/turmas/{turma_id}/relatorio")
        assert response.status_code == 200

    def test_retorna_conteudo_string(self, client, turma_id):
        """Relatório é gerado via Template Method e retornado como texto."""
        data = client.get(f"/turmas/{turma_id}/relatorio").json()
        assert 'conteudo' in data
        assert isinstance(data['conteudo'], str)

    def test_conteudo_contem_cabecalho(self, client, turma_id):
        """O conteúdo do relatório deve possuir um cabeçalho identificador."""
        data = client.get(f"/turmas/{turma_id}/relatorio").json()
        assert "RELATÓRIO" in data['conteudo'].upper()

    def test_conteudo_contem_codigo_da_turma(self, client, turma_id, conn):
        """Código da turma deve aparecer no corpo do relatório."""
        data = client.get(f"/turmas/{turma_id}/relatorio").json()
        assert "POO-2026.1" in data['conteudo']

    def test_turma_inexistente_retorna_404(self, client):
        """Deve retornar 404 ao solicitar relatório de turma inexistente."""
        response = client.get("/turmas/99999/relatorio")
        assert response.status_code == 404

    def test_formato_txt_aceito(self, client, turma_id):
        """Deve aceitar explicitamente o formato 'txt'."""
        response = client.get(f"/turmas/{turma_id}/relatorio?formato=txt")
        assert response.status_code == 200

    def test_formato_invalido_retorna_422(self, client, turma_id):
        """Formatos não suportados (ex: xls) devem retornar 422."""
        response = client.get(f"/turmas/{turma_id}/relatorio?formato=xls")
        assert response.status_code == 422

    def test_relatorio_turma_sem_alunos_retorna_200(self, client, turma_id):
        """Turma sem alunos matriculados deve gerar relatório válido com conteúdo."""
        response = client.get(f"/turmas/{turma_id}/relatorio")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data['conteudo'], str)
        assert len(data['conteudo']) > 0

    def test_relatorio_com_aluno_e_nota_exibe_dados_reais(
        self, client, turma_id, aluno_id, avaliacao_id, conn
    ):
        """Relatório de turma com aluno matriculado e nota deve exibir dados reais."""
        from educalin.repositories.turma_models import TurmaModel as TM
        turma = TM.buscar_por_id(conn, turma_id)
        turma.adicionar_aluno(conn, aluno_id)

        client.post(f"/avaliacoes/{avaliacao_id}/notas", json={
            "aluno_id": aluno_id, "valor": 8.5,
        })

        response = client.get(f"/turmas/{turma_id}/relatorio")
        assert response.status_code == 200
        conteudo = response.json()['conteudo']

        # O relatório deve conter o código da turma e o aluno matriculado
        assert "POO-2026.1" in conteudo
        assert "Total de Alunos" in conteudo
        # Média gerada deve aparecer formatada
        assert "8.50" in conteudo
