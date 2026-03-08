"""
Testes de integração para rotas de autenticação.

Testa os endpoints de registro, login e acesso a rotas protegidas.
"""

import pytest
from fastapi.testclient import TestClient


class TestRegistro:
    """Testes para o endpoint POST /auth/register"""
    
    def test_registro_com_dados_validos_professor(self, client):
        """
        Testa POST /auth/register com dados válidos de professor.
        
        Deve:
        - Retornar status 201 (Created)
        - Retornar dados do usuário criado
        - Não retornar a senha no response
        - Gerar ID único
        """
        usuario_data = {
            "nome": "Maria Santos",
            "email": "maria@test.com",
            "senha": "senha12345",
            "tipo": "professor",
            "registro_funcional": "PROF001"
        }
        
        response = client.post("/auth/register", json=usuario_data)
        
        # Verificar status code
        assert response.status_code == 201
        
        # Verificar estrutura do response
        data = response.json()
        assert "id" in data
        assert data["nome"] == usuario_data["nome"]
        assert data["email"] == usuario_data["email"]
        assert data["tipo"] == usuario_data["tipo"]
        assert data["registro_funcional"] == usuario_data["registro_funcional"]
        
        # Garantir que senha não é retornada
        assert "senha" not in data
        assert "senha_hash" not in data
        
        # Verificar campos de timestamp
        assert "criado_em" in data
        assert "atualizado_em" in data
    
    def test_registro_com_dados_validos_coordenador(self, client):
        """
        Testa POST /auth/register com dados válidos de coordenador.
        """
        usuario_data = {
            "nome": "Carlos Coordenador",
            "email": "carlos@test.com",
            "senha": "senha12345",
            "tipo": "coordenador",
            "codigo_coordenacao": "COORD001"
        }
        
        response = client.post("/auth/register", json=usuario_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["tipo"] == "coordenador"
        assert data["codigo_coordenacao"] == usuario_data["codigo_coordenacao"]
    
    def test_registro_com_dados_validos_aluno(self, client):
        """
        Testa POST /auth/register com dados válidos de aluno.
        """
        usuario_data = {
            "nome": "Ana Aluna",
            "email": "ana@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024001"
        }
        
        response = client.post("/auth/register", json=usuario_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["tipo"] == "aluno"
        assert data["matricula"] == usuario_data["matricula"]
    
    def test_registro_com_email_duplicado(self, client, usuario_registrado):
        """
        Testa registro com email duplicado (deve falhar).
        
        Deve:
        - Retornar status 400 (Bad Request)
        - Retornar mensagem de erro apropriada
        """
        # Tentar registrar com mesmo email
        usuario_data = {
            "nome": "Outro Usuario",
            "email": usuario_registrado["data"]["email"],  # Email já existe
            "senha": "outrasenha123",
            "tipo": "professor",
            "registro_funcional": "PROF999"
        }
        
        response = client.post("/auth/register", json=usuario_data)
        
        # Deve falhar com 400
        assert response.status_code == 400
        
        # Verificar mensagem de erro
        data = response.json()
        assert "detail" in data
        # Aceitar várias possíveis mensagens de erro que indicam email duplicado
        detail_lower = data["detail"].lower()
        assert any(palavra in detail_lower for palavra in ["email", "cadastrado", "duplicado", "já existe"])
    
    def test_registro_sem_campo_obrigatorio_tipo(self, client):
        """
        Testa registro sem campo obrigatório específico do tipo.
        
        Professor sem registro_funcional deve falhar.
        """
        usuario_data = {
            "nome": "Professor Sem Registro",
            "email": "prof@test.com",
            "senha": "senha12345",
            "tipo": "professor"
            # Falta registro_funcional
        }
        
        response = client.post("/auth/register", json=usuario_data)
        
        # Deve falhar com 400 ou 422
        assert response.status_code in [400, 422]
    
    def test_registro_com_senha_curta(self, client):
        """
        Testa registro com senha muito curta (menos de 8 caracteres).
        """
        usuario_data = {
            "nome": "Usuario Teste",
            "email": "user@test.com",
            "senha": "123",  # Senha muito curta
            "tipo": "aluno",
            "matricula": "2024999"
        }
        
        response = client.post("/auth/register", json=usuario_data)
        
        # Deve falhar com 422 (validation error)
        assert response.status_code == 422


class TestLogin:
    """Testes para o endpoint POST /auth/login"""
    
    def test_login_com_credenciais_corretas(self, client, usuario_registrado):
        """
        Testa POST /auth/login com credenciais corretas.
        
        Deve:
        - Retornar status 200 (OK)
        - Retornar access_token
        - Retornar token_type "bearer"
        """
        login_data = {
            "email": usuario_registrado["data"]["email"],
            "senha": usuario_registrado["data"]["senha"]
        }
        
        response = client.post("/auth/login", json=login_data)
        
        # Verificar status code
        assert response.status_code == 200
        
        # Verificar estrutura do response
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Token deve ser uma string não vazia
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    def test_login_com_senha_errada(self, client, usuario_registrado):
        """
        Testa login com senha incorreta (deve falhar).
        
        Deve:
        - Retornar status 401 (Unauthorized)
        - Retornar mensagem de erro apropriada
        """
        login_data = {
            "email": usuario_registrado["data"]["email"],
            "senha": "senhaerrada123"  # Senha incorreta
        }
        
        response = client.post("/auth/login", json=login_data)
        
        # Deve falhar com 401
        assert response.status_code == 401
        
        # Verificar mensagem de erro
        data = response.json()
        assert "detail" in data
        assert "inválid" in data["detail"].lower() or "incorret" in data["detail"].lower()
    
    def test_login_com_email_inexistente(self, client):
        """
        Testa login com email que não existe.
        
        Deve retornar 401 (não revelar se email existe ou não).
        """
        login_data = {
            "email": "naoexiste@test.com",
            "senha": "qualquersenha123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        # Deve falhar com 401
        assert response.status_code == 401
    
    def test_login_com_email_invalido(self, client):
        """
        Testa login com formato de email inválido.
        """
        login_data = {
            "email": "emailinvalido",  # Não é um email válido
            "senha": "senha12345"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        # Deve falhar com 422 (validation error)
        assert response.status_code == 422


class TestRotasProtegidas:
    """Testes para acesso a rotas protegidas (que requerem autenticação)"""
    
    def test_acesso_sem_token(self, client):
        """
        Testa acesso a rota protegida sem token (deve falhar 401).
        
        Deve:
        - Retornar status 401 (Unauthorized)
        - Retornar mensagem de erro apropriada
        """
        # Tentar acessar /auth/me sem token
        response = client.get("/auth/me")
        
        # Deve falhar com 401 ou 403
        assert response.status_code in [401, 403]
    
    def test_acesso_com_token_invalido(self, client):
        """
        Testa acesso a rota protegida com token inválido.
        """
        headers = {
            "Authorization": "Bearer token_invalido_123"
        }
        
        response = client.get("/auth/me", headers=headers)
        
        # Deve falhar com 401
        assert response.status_code == 401
    
    def test_acesso_com_token_malformado(self, client):
        """
        Testa acesso com token malformado (sem Bearer).
        """
        headers = {
            "Authorization": "token_sem_bearer"
        }
        
        response = client.get("/auth/me", headers=headers)
        
        # Deve falhar com 401 ou 403
        assert response.status_code in [401, 403]
    
    def test_acesso_com_token_valido(self, client, usuario_autenticado):
        """
        Testa acesso a rota protegida com token válido.
        
        Deve:
        - Retornar status 200 (OK)
        - Retornar dados do usuário autenticado
        """
        # Acessar /auth/me com token válido
        response = client.get("/auth/me", headers=usuario_autenticado["headers"])
        
        # Deve ter sucesso
        assert response.status_code == 200
        
        # Verificar dados retornados
        data = response.json()
        assert data["id"] == usuario_autenticado["usuario"]["id"]
        assert data["email"] == usuario_autenticado["usuario"]["email"]
        assert data["nome"] == usuario_autenticado["usuario"]["nome"]
        
        # Garantir que senha não é retornada
        assert "senha" not in data
        assert "senha_hash" not in data
    
    def test_token_contem_informacoes_usuario(self, client, usuario_autenticado):
        """
        Testa que ao usar o token, o sistema retorna o usuário correto.
        """
        # Fazer requisição autenticada
        response = client.get("/auth/me", headers=usuario_autenticado["headers"])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que os dados batem com o usuário original
        assert data["email"] == usuario_autenticado["usuario"]["email"]
        assert data["tipo"] == usuario_autenticado["usuario"]["tipo"]


class TestFluxoCompletoAutenticacao:
    """Testes de fluxo completo de autenticação"""
    
    def test_fluxo_completo_registro_login_acesso(self, client):
        """
        Testa fluxo completo: registro -> login -> acesso a rota protegida.
        """
        # 1. Registrar usuário
        usuario_data = {
            "nome": "Teste Completo",
            "email": "completo@test.com",
            "senha": "senha12345",
            "tipo": "professor",
            "registro_funcional": "PROF777"
        }
        
        registro_response = client.post("/auth/register", json=usuario_data)
        assert registro_response.status_code == 201
        usuario = registro_response.json()
        
        # 2. Fazer login
        login_data = {
            "email": usuario_data["email"],
            "senha": usuario_data["senha"]
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        # 3. Acessar rota protegida
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        me_data = me_response.json()
        assert me_data["id"] == usuario["id"]
        assert me_data["email"] == usuario_data["email"]
    
    def test_multiplos_usuarios_tokens_independentes(self, client):
        """
        Testa que múltiplos usuários têm tokens independentes.
        """
        # Criar dois usuários
        usuario1_data = {
            "nome": "Usuario 1",
            "email": "user1@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024001"
        }
        
        usuario2_data = {
            "nome": "Usuario 2",
            "email": "user2@test.com",
            "senha": "senha12345",
            "tipo": "aluno",
            "matricula": "2024002"
        }
        
        # Registrar ambos
        reg1 = client.post("/auth/register", json=usuario1_data)
        reg2 = client.post("/auth/register", json=usuario2_data)
        
        assert reg1.status_code == 201
        assert reg2.status_code == 201
        
        # Login de ambos
        login1 = client.post("/auth/login", json={
            "email": usuario1_data["email"],
            "senha": usuario1_data["senha"]
        })
        login2 = client.post("/auth/login", json={
            "email": usuario2_data["email"],
            "senha": usuario2_data["senha"]
        })
        
        token1 = login1.json()["access_token"]
        token2 = login2.json()["access_token"]
        
        # Tokens devem ser diferentes
        assert token1 != token2
        
        # Cada token deve retornar seu respectivo usuário
        me1 = client.get("/auth/me", headers={"Authorization": f"Bearer {token1}"})
        me2 = client.get("/auth/me", headers={"Authorization": f"Bearer {token2}"})
        
        assert me1.json()["email"] == usuario1_data["email"]
        assert me2.json()["email"] == usuario2_data["email"]
