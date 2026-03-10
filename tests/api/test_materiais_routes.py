"""
Testes de integração para rotas de materiais.

Testa os endpoints de upload, listagem, detalhe e exclusão de materiais.
"""

import io
import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures auxiliares
# ---------------------------------------------------------------------------

@pytest.fixture
def professor_autenticado(client):
    """Registra e autentica um professor, retornando headers com o token."""
    dados = {
        "nome": "Prof Materiais",
        "email": "prof.materiais@test.com",
        "senha": "senha12345",
        "tipo": "professor",
        "registro_funcional": "PROF_MAT01",
    }
    resp = client.post("/auth/register", json=dados)
    assert resp.status_code == 201
    usuario = resp.json()

    login = client.post("/auth/login", json={"email": dados["email"], "senha": dados["senha"]})
    assert login.status_code == 200
    token = login.json()["access_token"]

    return {
        "usuario": usuario,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def coordenador_autenticado(client):
    """Registra e autentica um coordenador, retornando headers com o token."""
    dados = {
        "nome": "Coord Materiais",
        "email": "coord.materiais@test.com",
        "senha": "senha12345",
        "tipo": "coordenador",
        "codigo_coordenacao": "COORD_MAT01",
    }
    resp = client.post("/auth/register", json=dados)
    assert resp.status_code == 201
    usuario = resp.json()

    login = client.post("/auth/login", json={"email": dados["email"], "senha": dados["senha"]})
    assert login.status_code == 200
    token = login.json()["access_token"]

    return {
        "usuario": usuario,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def aluno_autenticado(client):
    """Registra e autentica um aluno, retornando headers com o token."""
    dados = {
        "nome": "Aluno Materiais",
        "email": "aluno.materiais@test.com",
        "senha": "senha12345",
        "tipo": "aluno",
        "matricula": "MAT_ALU001",
    }
    resp = client.post("/auth/register", json=dados)
    assert resp.status_code == 201
    usuario = resp.json()

    login = client.post("/auth/login", json={"email": dados["email"], "senha": dados["senha"]})
    assert login.status_code == 200
    token = login.json()["access_token"]

    return {
        "usuario": usuario,
        "headers": {"Authorization": f"Bearer {token}"},
    }


def _pdf_upload_data(titulo="Apostila POO", descricao="Introdução a POO", topico="POO", num_paginas=50):
    """Retorna dados de formulário multipart para upload de PDF."""
    return {
        "titulo": titulo,
        "descricao": descricao,
        "topico": topico,
        "num_paginas": str(num_paginas),
    }


def _pdf_file():
    """Retorna um arquivo PDF simulado (bytes mínimos válidos)."""
    return ("apostila.pdf", io.BytesIO(b"%PDF-1.4 fake content"), "application/pdf")


def _video_upload_data(titulo="Aula POO", descricao="Vídeo POO", topico="POO", duracao=3600, codec="h264"):
    """Retorna dados de formulário multipart para upload de vídeo."""
    return {
        "titulo": titulo,
        "descricao": descricao,
        "topico": topico,
        "duracao_segundos": str(duracao),
        "codec": codec,
    }


def _video_file():
    """Retorna um arquivo MP4 simulado."""
    return ("aula.mp4", io.BytesIO(b"fake mp4 content"), "video/mp4")


# ---------------------------------------------------------------------------
# POST /materiais/upload
# ---------------------------------------------------------------------------

class TestUploadMaterial:
    """Testes para o endpoint POST /materiais/upload"""

    def test_upload_pdf_sucesso(self, client, professor_autenticado):
        """Deve criar material PDF com campos multipart corretos."""
        resp = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["tipo_material"] == "pdf"
        assert data["titulo"] == "Apostila POO"
        assert data["topico"] == "POO"
        assert data["num_paginas"] == 50
        assert "id" in data

    def test_upload_video_sucesso(self, client, professor_autenticado):
        """Deve criar material de vídeo com campos multipart corretos."""
        resp = client.post(
            "/materiais/upload",
            data=_video_upload_data(),
            files={"arquivo": _video_file()},
            headers=professor_autenticado["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["tipo_material"] == "video"
        assert data["duracao_segundos"] == 3600
        assert data["codec"] == "h264"

    def test_upload_sem_autenticacao(self, client):
        """Deve retornar 401 sem token."""
        resp = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(),
            files={"arquivo": _pdf_file()},
        )
        assert resp.status_code == 401

    def test_upload_por_aluno_proibido(self, client, aluno_autenticado):
        """Apenas professores podem fazer upload; alunos devem receber 403."""
        resp = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(),
            files={"arquivo": _pdf_file()},
            headers=aluno_autenticado["headers"],
        )
        assert resp.status_code == 403

    def test_upload_extensao_invalida(self, client, professor_autenticado):
        """Extensão não suportada deve retornar 400."""
        resp = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(),
            files={"arquivo": ("arquivo.exe", io.BytesIO(b"bad content"), "application/octet-stream")},
            headers=professor_autenticado["headers"],
        )
        assert resp.status_code == 400

    def test_upload_pdf_sem_num_paginas(self, client, professor_autenticado):
        """Upload de PDF sem num_paginas deve retornar 400."""
        resp = client.post(
            "/materiais/upload",
            data={"titulo": "Sem páginas", "descricao": "Desc"},
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        assert resp.status_code == 400

    def test_upload_video_sem_duracao(self, client, professor_autenticado):
        """Upload de vídeo sem duracao_segundos deve retornar 400."""
        resp = client.post(
            "/materiais/upload",
            data={"titulo": "Sem duração", "descricao": "Desc", "codec": "h264"},
            files={"arquivo": _video_file()},
            headers=professor_autenticado["headers"],
        )
        assert resp.status_code == 400

    def test_upload_arquivo_maior_50mb(self, client, professor_autenticado):
        """Arquivo maior que 50 MB deve retornar 400."""
        chunk = b"x" * (1024 * 1024)  # 1 MB
        big_file = io.BytesIO(chunk * 51)  # 51 MB
        resp = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(),
            files={"arquivo": ("grande.pdf", big_file, "application/pdf")},
            headers=professor_autenticado["headers"],
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /materiais
# ---------------------------------------------------------------------------

class TestListarMateriais:
    """Testes para o endpoint GET /materiais"""

    def test_listar_materiais_vazio(self, client, professor_autenticado):
        """Lista vazia para professor sem materiais."""
        resp = client.get("/materiais", headers=professor_autenticado["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["materiais"] == []

    def test_listar_materiais_apos_upload(self, client, professor_autenticado):
        """Lista deve conter material após upload."""
        client.post(
            "/materiais/upload",
            data=_pdf_upload_data(titulo="Material A"),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        resp = client.get("/materiais", headers=professor_autenticado["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["materiais"][0]["titulo"] == "Material A"

    def test_filtrar_por_tipo_pdf(self, client, professor_autenticado):
        """Filtro por tipo 'pdf' deve retornar apenas PDFs."""
        client.post(
            "/materiais/upload",
            data=_pdf_upload_data(titulo="PDF 1"),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        client.post(
            "/materiais/upload",
            data=_video_upload_data(titulo="Vídeo 1"),
            files={"arquivo": _video_file()},
            headers=professor_autenticado["headers"],
        )
        resp = client.get("/materiais?tipo=pdf", headers=professor_autenticado["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert all(m["tipo_material"] == "pdf" for m in data["materiais"])

    def test_filtrar_por_tipo_video(self, client, professor_autenticado):
        """Filtro por tipo 'video' deve retornar apenas vídeos."""
        client.post(
            "/materiais/upload",
            data=_pdf_upload_data(),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        client.post(
            "/materiais/upload",
            data=_video_upload_data(),
            files={"arquivo": _video_file()},
            headers=professor_autenticado["headers"],
        )
        resp = client.get("/materiais?tipo=video", headers=professor_autenticado["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert all(m["tipo_material"] == "video" for m in data["materiais"])

    def test_filtrar_tipo_invalido(self, client, professor_autenticado):
        """Tipo de filtro inválido deve retornar 400."""
        resp = client.get("/materiais?tipo=invalido", headers=professor_autenticado["headers"])
        assert resp.status_code == 400

    def test_listar_sem_autenticacao(self, client):
        """Deve retornar 401 sem token."""
        resp = client.get("/materiais")
        assert resp.status_code == 401

    def test_listar_por_aluno_proibido(self, client, aluno_autenticado):
        """Aluno não pode listar materiais de professor; deve receber 403."""
        resp = client.get("/materiais", headers=aluno_autenticado["headers"])
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /materiais/{id}
# ---------------------------------------------------------------------------

class TestObterMaterial:
    """Testes para o endpoint GET /materiais/{id}"""

    def test_obter_material_existente(self, client, professor_autenticado):
        """Deve retornar dados completos de um material existente."""
        upload = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(titulo="Detalhes PDF"),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        material_id = upload.json()["id"]

        resp = client.get(f"/materiais/{material_id}", headers=professor_autenticado["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == material_id
        assert data["titulo"] == "Detalhes PDF"

    def test_obter_material_inexistente(self, client, professor_autenticado):
        """Deve retornar 404 para ID inexistente."""
        resp = client.get("/materiais/99999", headers=professor_autenticado["headers"])
        assert resp.status_code == 404

    def test_obter_material_id_invalido(self, client, professor_autenticado):
        """Deve rejeitar ID negativo."""
        resp = client.get("/materiais/-1", headers=professor_autenticado["headers"])
        assert resp.status_code == 400

    def test_obter_material_sem_autenticacao(self, client):
        """Deve retornar 401 sem token."""
        resp = client.get("/materiais/1")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /materiais/{id}
# ---------------------------------------------------------------------------

class TestDeletarMaterial:
    """Testes para o endpoint DELETE /materiais/{id}"""

    def test_deletar_por_autor(self, client, professor_autenticado):
        """Professor autor pode deletar seu próprio material."""
        upload = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(titulo="Para deletar"),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        material_id = upload.json()["id"]

        resp = client.delete(f"/materiais/{material_id}", headers=professor_autenticado["headers"])
        assert resp.status_code == 204

        # Confirma que foi removido
        get_resp = client.get(f"/materiais/{material_id}", headers=professor_autenticado["headers"])
        assert get_resp.status_code == 404

    def test_deletar_por_coordenador(self, client, professor_autenticado, coordenador_autenticado):
        """Coordenador pode deletar qualquer material."""
        upload = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(titulo="Coord delete"),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        material_id = upload.json()["id"]

        resp = client.delete(f"/materiais/{material_id}", headers=coordenador_autenticado["headers"])
        assert resp.status_code == 204

    def test_deletar_por_outro_professor_proibido(self, client, professor_autenticado, client_outro_professor):
        """Professor não autor deve receber 403 ao tentar deletar."""
        upload = client.post(
            "/materiais/upload",
            data=_pdf_upload_data(titulo="Não seu material"),
            files={"arquivo": _pdf_file()},
            headers=professor_autenticado["headers"],
        )
        material_id = upload.json()["id"]

        resp = client.delete(f"/materiais/{material_id}", headers=client_outro_professor["headers"])
        assert resp.status_code == 403

    def test_deletar_material_inexistente(self, client, professor_autenticado):
        """Deve retornar 404 ao deletar material inexistente."""
        resp = client.delete("/materiais/99999", headers=professor_autenticado["headers"])
        assert resp.status_code == 404

    def test_deletar_sem_autenticacao(self, client):
        """Deve retornar 401 sem token."""
        resp = client.delete("/materiais/1")
        assert resp.status_code == 401


@pytest.fixture
def client_outro_professor(client):
    """Registra e autentica um segundo professor."""
    dados = {
        "nome": "Outro Professor",
        "email": "outro.prof@test.com",
        "senha": "senha12345",
        "tipo": "professor",
        "registro_funcional": "PROF_OUT02",
    }
    resp = client.post("/auth/register", json=dados)
    assert resp.status_code == 201

    login = client.post("/auth/login", json={"email": dados["email"], "senha": dados["senha"]})
    assert login.status_code == 200
    token = login.json()["access_token"]

    return {"headers": {"Authorization": f"Bearer {token}"}}
