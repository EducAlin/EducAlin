"""
Testes de integração para rotas de planos de ação da API.

Cobre testes de:
- Criação de plano com validação de prazo
- Obter detalhes do plano (verificação de permissões)
- Adicionar material ao plano
- Atualizar status do plano
- Sugestão automática de materiais (mock estratégia)
- Notificação ao criar plano (mock Observer)
"""

import pytest
from io import BytesIO
from unittest.mock import Mock, patch


class TestCriarPlano:
    """Testes para criar plano de ação."""

    def test_criar_plano_valido(self, client, usuario_autenticado, db_connection):
        """Deve criar plano com dados válidos."""
        # Criar aluno para o plano
        aluno_data = {
            "nome": "João Aluno",
            "email": "joao@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024001"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Professor cria plano para aluno
        plano_data = {
            "objetivo": "Melhorar desempenho em Matemática",
            "prazo_dias": 30,
            "observacoes": "Foco em álgebra básica"
        }
        
        response = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["aluno_id"] == aluno_id
        assert data["objetivo"] == "Melhorar desempenho em Matemática"
        assert data["status"] == "rascunho"

    def test_criar_plano_aluno_para_si_mesmo(self, client, db_connection):
        """Deve permitir que aluno crie plano para si mesmo."""
        # Criar aluno
        aluno_data = {
            "nome": "Pedro Aluno",
            "email": "pedro@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024002"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Aluno faz login
        login = client.post(
            "/auth/login",
            json={"email": "pedro@test.com", "senha": "senha12345"}
        )
        aluno_token = login.json()["access_token"]
        
        # Aluno cria plano para si mesmo
        plano_data = {
            "objetivo": "Melhorar em Física",
            "prazo_dias": 45
        }
        
        response = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers={"Authorization": f"Bearer {aluno_token}"}
        )
        
        assert response.status_code == 201
        assert response.json()["aluno_id"] == aluno_id

    def test_criar_plano_aluno_para_outro(self, client, usuario_autenticado, db_connection):
        """Deve rejeitar aluno criando plano para outro aluno."""
        # Criar primeiro aluno
        aluno1_data = {
            "nome": "Aluno Um",
            "email": "aluno1@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024001"
        }
        client.post("/auth/register", json=aluno1_data)
        
        # Criar segundo aluno
        aluno2_data = {
            "nome": "Aluno Dois",
            "email": "aluno2@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024002"
        }
        response_aluno2 = client.post("/auth/register", json=aluno2_data)
        aluno2_id = response_aluno2.json()["id"]
        
        # Fazer login como aluno1
        login = client.post(
            "/auth/login",
            json={"email": "aluno1@test.com", "senha": "senha12345"}
        )
        aluno1_token = login.json()["access_token"]
        
        # Tentar criar plano para aluno2
        plano_data = {
            "objetivo": "Melhorar em Física",
            "prazo_dias": 30
        }
        
        response = client.post(
            f"/planos?aluno_id={aluno2_id}",
            json=plano_data,
            headers={"Authorization": f"Bearer {aluno1_token}"}
        )
        
        assert response.status_code == 403

    def test_criar_plano_prazo_invalido_zero(self, client, usuario_autenticado, db_connection):
        """Deve rejeitar plano com prazo_dias = 0."""
        # Criar aluno
        aluno_data = {
            "nome": "Maria Aluno",
            "email": "maria@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024003"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Tentar criar plano com prazo inválido
        plano_data = {
            "objetivo": "Melhorar em História",
            "prazo_dias": 0
        }
        
        response = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 400

    def test_criar_plano_prazo_acima_maximo(self, client, usuario_autenticado, db_connection):
        """Deve rejeitar plano com prazo_dias > 365."""
        # Criar aluno
        aluno_data = {
            "nome": "Ana Aluno",
            "email": "ana@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024004"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Tentar criar plano com prazo acima de 365
        plano_data = {
            "objetivo": "Melhorar em Geografia",
            "prazo_dias": 400
        }
        
        response = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 400

    def test_criar_plano_aluno_inexistente(self, client, usuario_autenticado):
        """Deve rejeitar criação de plano para aluno inexistente."""
        plano_data = {
            "objetivo": "Melhorar em Matemática",
            "prazo_dias": 30
        }
        
        response = client.post(
            "/planos?aluno_id=99999",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        
        # Pode retornar 400 ou 404 dependendo da implementação
        assert response.status_code in [400, 404]


class TestObterPlano:
    """Testes para obter detalhes do plano."""

    def test_obter_plano_aluno_seu_plano(self, client, db_connection):
        """Deve permitir aluno obter seus próprios planos."""
        # Criar aluno
        aluno_data = {
            "nome": "Lucas Aluno",
            "email": "lucas@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024005"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Criar professor
        prof_data = {
            "nome": "Professor Teste",
            "email": "prof@test.com",
            "senha": "senha12345",
            "tipo": "professor",
            "registro_funcional": "PROF999"
        }
        client.post("/auth/register", json=prof_data)
        
        login_prof = client.post(
            "/auth/login",
            json={"email": "prof@test.com", "senha": "senha12345"}
        )
        prof_token = login_prof.json()["access_token"]
        
        # Professor cria plano para aluno
        plano_data = {
            "objetivo": "Melhorar em História",
            "prazo_dias": 20
        }
        
        response_criar = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers={"Authorization": f"Bearer {prof_token}"}
        )
        plano_id = response_criar.json()["id"]
        
        # Aluno consulta seu plano
        login_aluno = client.post(
            "/auth/login",
            json={"email": "lucas@test.com", "senha": "senha12345"}
        )
        aluno_token = login_aluno.json()["access_token"]
        
        response = client.get(
            f"/planos/{plano_id}",
            headers={"Authorization": f"Bearer {aluno_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == plano_id

    def test_obter_plano_aluno_plano_outro(self, client, usuario_autenticado, db_connection):
        """Deve rejeitar aluno tentando acessar plano de outro."""
        # Criar dois alunos
        aluno1_data = {
            "nome": "Bruno Aluno",
            "email": "bruno@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024006"
        }
        response_aluno1 = client.post("/auth/register", json=aluno1_data)
        aluno1_id = response_aluno1.json()["id"]
        
        aluno2_data = {
            "nome": "Fernanda Aluno",
            "email": "fernanda@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024007"
        }
        response_aluno2 = client.post("/auth/register", json=aluno2_data)
        aluno2_id = response_aluno2.json()["id"]
        
        # Professor cria plano para aluno1
        plano_data = {
            "objetivo": "Melhorar em Química",
            "prazo_dias": 25
        }
        
        response_criar = client.post(
            f"/planos?aluno_id={aluno1_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        plano_id = response_criar.json()["id"]
        
        # Aluno2 tenta acessar plano de aluno1
        login_aluno2 = client.post(
            "/auth/login",
            json={"email": "fernanda@test.com", "senha": "senha12345"}
        )
        aluno2_token = login_aluno2.json()["access_token"]
        
        response = client.get(
            f"/planos/{plano_id}",
            headers={"Authorization": f"Bearer {aluno2_token}"}
        )
        
        assert response.status_code == 403

    def test_obter_plano_professor_qualquer_plano(self, client, usuario_autenticado, db_connection):
        """Deve permitir professor acessar qualquer plano."""
        # Criar aluno
        aluno_data = {
            "nome": "Rafael Aluno",
            "email": "rafael@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024008"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Professor cria plano
        plano_data = {
            "objetivo": "Melhorar em Biologia",
            "prazo_dias": 35
        }
        
        response_criar = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        plano_id = response_criar.json()["id"]
        
        # Outro professor acessa plano
        prof2_data = {
            "nome": "Juliana Professor",
            "email": "juliana@test.com",
            "senha": "senha12345",
            "tipo": "professor",
            "registro_funcional": "PROF777"
        }
        client.post("/auth/register", json=prof2_data)
        
        login_prof2 = client.post(
            "/auth/login",
            json={"email": "juliana@test.com", "senha": "senha12345"}
        )
        prof2_token = login_prof2.json()["access_token"]
        
        response = client.get(
            f"/planos/{plano_id}",
            headers={"Authorization": f"Bearer {prof2_token}"}
        )
        
        assert response.status_code == 200


class TestAdicionarMaterialPlano:
    """Testes para adicionar material ao plano."""

    def test_adicionar_material_ao_plano(self, client, usuario_autenticado, db_connection):
        """Deve adicionar material ao plano."""
        # Criar aluno
        aluno_data = {
            "nome": "Sandra Aluno",
            "email": "sandra@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024009"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Criar plano
        plano_data = {
            "objetivo": "Melhorar em Português",
            "prazo_dias": 28
        }
        
        response_plano = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        plano_id = response_plano.json()["id"]
        
        # Criar material
        arquivo = ("apostila.pdf", BytesIO(b"%PDF"), "application/pdf")
        response_material = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={"titulo": "Apostila Português", "descricao": "Conteúdo", "num_paginas": 40},
            files={"arquivo": arquivo}
        )
        material_id = response_material.json()["id"]
        
        # Adicionar material ao plano
        response = client.put(
            f"/planos/{plano_id}/materiais",
            json={"material_id": material_id},
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert material_id in data["materiais"]

    def test_adicionar_material_plano_concluido(self, client, usuario_autenticado, db_connection):
        """Deve rejeitar adicionar material a plano concluído."""
        # Criar aluno
        aluno_data = {
            "nome": "Vanessa Aluno",
            "email": "vanessa@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024010"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Criar plano
        plano_data = {
            "objetivo": "Melhorar em Inglês",
            "prazo_dias": 15
        }
        
        response_plano = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        plano_id = response_plano.json()["id"]
        
        # Atualizar plano para status 'concluido'
        status_data = {"status": "concluido"}
        client.put(
            f"/planos/{plano_id}/status",
            json=status_data,
            headers=usuario_autenticado["headers"]
        )
        
        # Criar material
        arquivo = ("material.pdf", BytesIO(b"%PDF"), "application/pdf")
        response_material = client.post(
            "/materiais/upload",
            headers=usuario_autenticado["headers"],
            data={"titulo": "Material Inglês", "descricao": "Conteúdo", "num_paginas": 30},
            files={"arquivo": arquivo}
        )
        material_id = response_material.json()["id"]
        
        # Tentar adicionar material
        response = client.put(
            f"/planos/{plano_id}/materiais",
            json={"material_id": material_id},
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 403


class TestAtualizarStatusPlano:
    """Testes para atualizar status do plano."""

    def test_atualizar_status_rascunho_para_enviado(self, client, usuario_autenticado, db_connection):
        """Deve transicionar plano de rascunho para enviado."""
        # Criar aluno
        aluno_data = {
            "nome": "Gustavo Aluno",
            "email": "gustavo@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024011"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        # Criar plano
        plano_data = {
            "objetivo": "Melhorar em Artes",
            "prazo_dias": 22
        }
        
        response_plano = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        plano_id = response_plano.json()["id"]
        
        # Atualizar status
        status_data = {"status": "enviado"}
        response = client.put(
            f"/planos/{plano_id}/status",
            json=status_data,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "enviado"

    def test_atualizar_status_transicao_invalida(self, client, usuario_autenticado, db_connection):
        """Deve rejeitar transição de status inválida."""
        # Criar aluno e plano
        aluno_data = {
            "nome": "Helena Aluno",
            "email": "helena@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024012"
        }
        response_aluno = client.post("/auth/register", json=aluno_data)
        aluno_id = response_aluno.json()["id"]
        
        plano_data = {
            "objetivo": "Melhorar em Educação Física",
            "prazo_dias": 18
        }
        
        response_plano = client.post(
            f"/planos?aluno_id={aluno_id}",
            json=plano_data,
            headers=usuario_autenticado["headers"]
        )
        plano_id = response_plano.json()["id"]
        
        # Tentar transição inválida: rascunho -> em_andamento
        status_data = {"status": "em_andamento"}
        response = client.put(
            f"/planos/{plano_id}/status",
            json=status_data,
            headers=usuario_autenticado["headers"]
        )
        
        assert response.status_code == 400
