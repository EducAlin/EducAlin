"""
Rotas de autenticação da API FastAPI.

Este módulo implementa endpoints para:
- Registro de novos usuários
- Login e autenticação
- Logout (invalidação de tokens)
- Recuperação de senha
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthCredentials
from typing import Dict

from ..schemas import (
    RegisterSchema,
    LoginSchema,
    TokenSchema,
    UsuarioSchema,
    RecuperarSenhaSchema,
    ErrorSchema
)
from ..dependencies import get_current_user, security, _blacklisted_tokens
from ...repositories.usuario_repository import UsuarioRepository
from ...repositories.base import get_connection
from ...utils.security import criar_token_jwt


# Criar router para rotas de autenticação
router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
    responses={
        401: {"model": ErrorSchema, "description": "Não autorizado"},
        400: {"model": ErrorSchema, "description": "Requisição inválida"},
    }
)


@router.post(
    "/register",
    response_model=UsuarioSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
    description="Cria um novo usuário no sistema com os dados fornecidos.",
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"description": "Dados inválidos ou email já cadastrado"},
    }
)
def register(dados: RegisterSchema) -> UsuarioSchema:
    """
    Cadastra um novo usuário no sistema.
    
    O tipo de usuário determina quais campos adicionais são obrigatórios:
    - **professor**: requer `registro_funcional`
    - **coordenador**: requer `codigo_coordenacao`
    - **aluno**: requer `matricula`
    
    Returns:
        Dados do usuário criado (sem a senha)
    """
    conn = get_connection()
    
    try:
        repo = UsuarioRepository(conn)
        
        # Preparar dados do usuário
        usuario_data = {
            'tipo_usuario': dados.tipo,
            'nome': dados.nome,
            'email': dados.email,
            'senha': dados.senha,
            'registro_funcional': dados.registro_funcional,
            'codigo_coordenacao': dados.codigo_coordenacao,
            'matricula': dados.matricula
        }
        
        # Criar usuário
        usuario_id = repo.criar(usuario_data)
        
        # Buscar usuário criado
        usuario = repo.buscar_por_id(usuario_id)
        
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar usuário"
            )
        
        # Retornar dados do usuário
        return UsuarioSchema(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            tipo=usuario.tipo_usuario,
            registro_funcional=getattr(usuario, 'registro_funcional', None),
            codigo_coordenacao=getattr(usuario, 'codigo_coordenacao', None),
            matricula=getattr(usuario, 'matricula', None),
            criado_em=usuario.criado_em,
            atualizado_em=usuario.atualizado_em
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    finally:
        conn.close()


@router.post(
    "/login",
    response_model=TokenSchema,
    summary="Fazer login",
    description="Autentica um usuário com email e senha, retornando um token JWT.",
    responses={
        200: {"description": "Login realizado com sucesso"},
        401: {"description": "Email ou senha inválidos"},
    }
)
def login(dados: LoginSchema) -> TokenSchema:
    """
    Autentica um usuário e retorna um token JWT.
    
    O token deve ser incluído nas requisições subsequentes no header:
    ```
    Authorization: Bearer <token>
    ```
    
    Returns:
        Token JWT válido por 24 horas
    """
    conn = get_connection()
    
    try:
        repo = UsuarioRepository(conn)
        
        # Tentar autenticar
        usuario = repo.autenticar(dados.email, dados.senha)
        
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha inválidos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar token JWT
        token = criar_token_jwt(
            usuario_id=usuario.id,
            perfil=usuario.tipo_usuario
        )
        
        return TokenSchema(
            access_token=token,
            token_type="bearer"
        )
    
    finally:
        conn.close()


@router.post(
    "/logout",
    response_model=Dict[str, str],
    summary="Fazer logout",
    description="Invalida o token JWT do usuário autenticado.",
    responses={
        200: {"description": "Logout realizado com sucesso"},
        401: {"description": "Token inválido ou expirado"},
    }
)
def logout(
    credentials: HTTPAuthCredentials = Depends(security),
    current_user: UsuarioSchema = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Realiza logout invalidando o token do usuário.
    
    O token é adicionado à blacklist em memória e rejeitado em chamadas futuras.
    
    **Nota**: A blacklist é mantida em memória (processo único). Em produção,
    utilize Redis ou banco de dados para persistir tokens invalidados.
    
    Returns:
        Mensagem de confirmação
    """
    _blacklisted_tokens.add(credentials.credentials)

    return {
        "message": "Logout realizado com sucesso",
        "detail": f"Usuário {current_user.nome} desconectado"
    }


@router.post(
    "/recuperar-senha",
    response_model=Dict[str, str],
    summary="Solicitar recuperação de senha",
    description="Solicita o envio de email para recuperação de senha.",
    responses={
        200: {"description": "Email de recuperação enviado (se o email existir)"},
        400: {"description": "Email inválido"},
    }
)
def recuperar_senha(dados: RecuperarSenhaSchema) -> Dict[str, str]:
    """
    Solicita recuperação de senha.
    
    **Nota**: Esta implementação é simplificada para demonstração.
    Em produção, seria necessário:
    - Gerar token único de recuperação com validade curta
    - Armazenar token no banco de dados
    - Enviar email com link contendo o token
    - Implementar endpoint para resetar senha com o token
    
    Por segurança, sempre retorna sucesso mesmo se o email não existir,
    para evitar enumeração de usuários.
    
    Returns:
        Mensagem de confirmação
    """
    conn = get_connection()
    
    try:
        repo = UsuarioRepository(conn)
        
        # Verificar se usuário existe
        usuario = repo.buscar_por_email(dados.email)
        
        # Por segurança, não revelamos se o email existe ou não
        # Em produção real, aqui seria:
        # 1. Gerar token de recuperação único
        # 2. Salvar token no banco com validade de 1 hora
        # 3. Enviar email com link de recuperação
        
        if usuario:
            # TODO: Implementar envio de email
            # send_password_recovery_email(usuario.email, recovery_token)
            pass
        
        # Sempre retorna sucesso para não revelar se email existe
        return {
            "message": "Se o email estiver cadastrado, você receberá instruções para recuperar sua senha",
            "detail": "Verifique sua caixa de entrada e spam"
        }
    
    finally:
        conn.close()


@router.get(
    "/me",
    response_model=UsuarioSchema,
    summary="Obter perfil do usuário autenticado",
    description="Retorna os dados do usuário atualmente autenticado.",
    responses={
        200: {"description": "Dados do usuário"},
        401: {"description": "Token inválido ou expirado"},
    }
)
def get_me(current_user: UsuarioSchema = Depends(get_current_user)) -> UsuarioSchema:
    """
    Retorna os dados do usuário autenticado.
    
    Útil para verificar se o token ainda é válido e obter
    informações atualizadas do usuário.
    
    Returns:
        Dados completos do usuário autenticado
    """
    return current_user
