"""
Dependências FastAPI compartilhadas entre todos os routers.

Fornece:
- ``get_db``: dependência de conexão com o banco de dados (SQLite).
- ``get_current_user``: dependência de autenticação via JWT.
- ``require_role``: factory de autorização por tipo de usuário.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from educalin.utils.security import decodificar_token_jwt
from educalin.repositories.usuario_repository import UsuarioRepository
from educalin.repositories.base import get_connection
from .schemas import UsuarioSchema


def get_db():
    """
    Dependência de conexão com o banco de dados.

    Abre uma conexão SQLite para a requisição e a fecha ao final,
    garantindo que cada request use sua própria conexão isolada.

    Yields:
        sqlite3.Connection: Conexão ativa com o banco de dados.
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


# Security scheme para Bearer Token
security = HTTPBearer()

# Conjunto de tokens invalidados (em produção, usar Redis ou banco persistente)
_blacklisted_tokens: set[str] = set()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UsuarioSchema:
    """
    Dependência para obter o usuário autenticado a partir do token JWT.

    Esta função é usada como dependência em rotas protegidas para:
    - Validar o token JWT fornecido no header Authorization
    - Decodificar o token e extrair informações do usuário
    - Buscar o usuário no banco de dados
    - Retornar os dados do usuário autenticado

    Args:
        credentials: Credenciais HTTP Bearer obtidas do header Authorization

    Returns:
        UsuarioSchema: Dados do usuário autenticado

    Raises:
        HTTPException: 401 se o token for inválido ou o usuário não existir

    Example:
        ```python
        @router.get("/perfil")
        def obter_perfil(current_user: UsuarioSchema = Depends(get_current_user)):
            return current_user
        ```
    """
    # Extrair o token das credenciais
    token = credentials.credentials

    # Verificar se o token foi invalidado (logout)
    if token in _blacklisted_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decodificar o token JWT
    payload = decodificar_token_jwt(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extrair o ID do usuário do payload
    usuario_id = payload.get("usuario_id")

    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: usuario_id não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar o usuário no banco de dados
    conn = get_connection()
    try:
        repo = UsuarioRepository(conn)
        usuario = repo.buscar_por_id(usuario_id)

        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Converter para UsuarioSchema
        return UsuarioSchema(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            tipo_usuario=usuario.tipo_usuario,
            registro_funcional=getattr(usuario, 'registro_funcional', None),
            codigo_coordenacao=getattr(usuario, 'codigo_coordenacao', None),
            matricula=getattr(usuario, 'matricula', None),
            criado_em=usuario.criado_em,
            atualizado_em=usuario.atualizado_em
        )

    finally:
        conn.close()


def require_role(*allowed_roles: str):
    """
    Dependência factory para restringir acesso por tipo de usuário.

    Cria uma dependência que verifica se o usuário autenticado possui
    um dos roles permitidos.

    Args:
        *allowed_roles: Tipos de usuário permitidos ('professor', 'coordenador', 'aluno')

    Returns:
        Função de dependência que valida o role do usuário

    Raises:
        HTTPException: 403 se o usuário não tiver permissão

    Example:
        ```python
        @router.post("/turmas")
        def criar_turma(
            turma: TurmaCreate,
            current_user: UsuarioSchema = Depends(require_role("professor", "coordenador"))
        ):
            # Apenas professores e coordenadores podem criar turmas
            ...
        ```
    """
    def role_checker(current_user: UsuarioSchema = Depends(get_current_user)) -> UsuarioSchema:
        if current_user.tipo_usuario not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Apenas {', '.join(allowed_roles)} podem acessar este recurso."
            )
        return current_user

    return role_checker
