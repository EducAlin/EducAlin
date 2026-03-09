"""
Testes de integração para rotas de materiais da API.

Cobre testes de:
- Upload de PDF, Vídeo com validação de formato/tamanho
- Listar materiais do professor
- Obter detalhes de material
- Deletar material com validação de permissões
"""

import pytest
from io import BytesIO


class TestUploadMaterial:
    """Testes para upload de materiais."""

    def test_upload_pdf_valido(self, client, usuario_autenticado):
        """Deve fazer upload de PDF com num_paginas válido."""
        # Simular arquivo PDF
        arquivo = ("documento.pdf", BytesIO(b"%PDF-1.4\n..."), "application/pdf")
        
        response = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={
                "titulo": "Introdução à POO",
                "descricao": "Conceitos fundamentais",
                "topico": "Programação",
                "num_paginas": 50
            },
            files={"arquivo": arquivo}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["tipo_material"] == "pdf"
        assert data["titulo"] == "Introdução à POO"
        assert data["num_paginas"] == 50

    def test_upload_pdf_sem_num_paginas(self, client, usuario_autenticado):
        """Deve rejeitar PDF sem num_paginas."""
        arquivo = ("documento.pdf", BytesIO(b"%PDF-1.4\n..."), "application/pdf")
        
        response = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={
                "titulo": "Introdução à POO",
                "descricao": "Conceitos fundamentais",
            },
            files={"arquivo": arquivo}
        )
        
        assert response.status_code == 400
        assert "num_paginas" in response.json()["detail"].lower()

    def test_upload_video_valido(self, client, usuario_autenticado):
        """Deve fazer upload de vídeo com duracao_segundos e codec válidos."""
        arquivo = ("video.mp4", BytesIO(b"..."), "video/mp4")
        
        response = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={
                "titulo": "Aula de Herança",
                "descricao": "Explicação de herança em POO",
                "duracao_segundos": 1800,
                "codec": "h264"
            },
            files={"arquivo": arquivo}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["tipo_material"] == "video"
        assert data["duracao_segundos"] == 1800
        assert data["codec"] == "h264"

    def test_upload_video_sem_codec(self, client, usuario_autenticado):
        """Deve rejeitar vídeo sem codec."""
        arquivo = ("video.mp4", BytesIO(b"..."), "video/mp4")
        
        response = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={
                "titulo": "Aula de Herança",
                "descricao": "Explicação de herança",
                "duracao_segundos": 1800
            },
            files={"arquivo": arquivo}
        )
        
        assert response.status_code == 400
        assert "codec" in response.json()["detail"].lower()

    def test_upload_extensao_nao_suportada(self, client, usuario_autenticado):
        """Deve rejeitar arquivo com extensão não suportada."""
        arquivo = ("arquivo.docx", BytesIO(b"..."), "application/vnd.openxmlformats")
        
        response = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={
                "titulo": "Documento",
                "descricao": "Algum documento"
            },
            files={"arquivo": arquivo}
        )
        
        assert response.status_code == 400
        assert "suportado" in response.json()["detail"].lower()

    def test_upload_sem_autenticacao(self, client):
        """Deve rejeitar upload sem token JWT."""
        arquivo = ("documento.pdf", BytesIO(b"%PDF"), "application/pdf")
        
        response = client.post(
            "/materiais/upload",
            data={"titulo": "Documento", "descricao": "Desc", "num_paginas": 10},
            files={"arquivo": arquivo}
        )
        
        assert response.status_code == 403

    def test_upload_usuario_nao_professor(self, client, db_connection):
        """Deve rejeitar upload de usuário que não é professor."""
        # Criar aluno
        aluno_data = {
            "nome": "Pedro Aluno",
            "email": "pedro@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024001"
        }
        
        response = client.post("/auth/register", json=aluno_data)
        assert response.status_code == 201
        
        # Fazer login como aluno
        login = client.post(
            "/auth/login",
            json={"email": "pedro@test.com", "senha": "senha12345"}
        )
        aluno_token = login.json()["access_token"]
        
        # Tentar fazer upload
        arquivo = ("documento.pdf", BytesIO(b"%PDF"), "application/pdf")
        response = client.post(
            "/materiais/upload",
            headers={"Authorization": f"Bearer {aluno_token}"},
            data={"titulo": "Doc", "descricao": "Desc", "num_paginas": 10},
            files={"arquivo": arquivo}
        )
        
        assert response.status_code == 403
        assert "professor" in response.json()["detail"].lower()


class TestListarMateriais:
    """Testes para listar materiais do professor."""

    def test_listar_materiais_vazio(self, client, usuario_autenticado):
        """Deve retornar lista vazia se professor não tem materiais."""
        response = client.get(
            "/materiais",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["materiais"] == []

    def test_listar_materiais_com_filtro_tipo(self, client, usuario_autenticado):
        """Deve filtrar materiais por tipo."""
        # Upload de PDF
        arquivo_pdf = ("doc.pdf", BytesIO(b"%PDF"), "application/pdf")
        client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={"titulo": "PDF", "descricao": "Desc", "num_paginas": 10},
            files={"arquivo": arquivo_pdf}
        )
        
        # Upload de vídeo
        arquivo_video = ("video.mp4", BytesIO(b"..."), "video/mp4")
        client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={"titulo": "Vídeo", "descricao": "Desc", "duracao_segundos": 1800, "codec": "h264"},
            files={"arquivo": arquivo_video}
        )
        
        # Listar apenas PDFs
        response = client.get(
            "/materiais?tipo=pdf",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["materiais"][0]["tipo_material"] == "pdf"

    def test_listar_materiais_tipo_invalido(self, client, usuario_autenticado):
        """Deve rejeitar tipo de filtro inválido."""
        response = client.get(
            "/materiais?tipo=invalido",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 400


class TestObterMaterial:
    """Testes para obter detalhes de um material."""

    def test_obter_material_existente(self, client, usuario_autenticado):
        """Deve retornar detalhes de um material existente."""
        # Upload material
        arquivo = ("doc.pdf", BytesIO(b"%PDF"), "application/pdf")
        response_upload = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={"titulo": "Documento", "descricao": "Descrição", "num_paginas": 25},
            files={"arquivo": arquivo}
        )
        material_id = response_upload.json()["id"]
        
        # Obter detalhes
        response = client.get(
            f"/materiais/{material_id}",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == material_id
        assert data["titulo"] == "Documento"
        assert data["num_paginas"] == 25

    def test_obter_material_nao_existente(self, client, usuario_autenticado):
        """Deve retornar 404 para material inexistente."""
        response = client.get(
            "/materiais/99999",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()

    def test_obter_material_id_invalido(self, client, usuario_autenticado):
        """Deve rejeitar ID de material inválido."""
        response = client.get(
            "/materiais/-1",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 400


class TestDeletarMaterial:
    """Testes para deletar material."""

    def test_deletar_material_do_autor(self, client, usuario_autenticado):
        """Deve permitir que autor delete seu material."""
        # Upload material
        arquivo = ("doc.pdf", BytesIO(b"%PDF"), "application/pdf")
        response_upload = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={"titulo": "Documento", "descricao": "Descrição", "num_paginas": 10},
            files={"arquivo": arquivo}
        )
        material_id = response_upload.json()["id"]
        
        # Deletar
        response = client.delete(
            f"/materiais/{material_id}",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 204

    def test_deletar_material_outro_professor(self, client, usuario_autenticado):
        """Deve rejeitar delete de material de outro professor."""
        # Upload material com primeiro professor
        arquivo = ("doc.pdf", BytesIO(b"%PDF"), "application/pdf")
        response_upload = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={"titulo": "Documento", "descricao": "Descrição", "num_paginas": 10},
            files={"arquivo": arquivo}
        )
        material_id = response_upload.json()["id"]
        
        # Criar segundo professor
        professor2_data = {
            "nome": "Carlos Professor",
            "email": "carlos@test.com",
            "senha": "senha12345",
            "tipo": "professor",
            "registro_funcional": "PROF456"
        }
        client.post("/auth/register", json=professor2_data)
        
        login_prof2 = client.post(
            "/auth/login",
            json={"email": "carlos@test.com", "senha": "senha12345"}
        )
        prof2_token = login_prof2.json()["access_token"]
        
        # Tentar deletar com segundo professor
        response = client.delete(
            f"/materiais/{material_id}",
            headers={"Authorization": f"Bearer {prof2_token}"}
        )
        
        assert response.status_code == 403

    def test_deletar_material_nao_existente(self, client, usuario_autenticado):
        """Deve retornar 404 ao tentar deletar material inexistente."""
        response = client.delete(
            "/materiais/99999",
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 404
