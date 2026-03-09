"""
Rotas de upload e gestão de materiais de estudo da API FastAPI.

Este módulo implementa endpoints para:
- Upload de novos materiais (com detecção de tipo e validação)
- Listagem de materiais do professor autenticado
- Visualização de detalhes de um material
- Exclusão de materiais
"""

import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime

from ..schemas import (
    MaterialResponseSchema,
    MaterialListSchema,
    UsuarioSchema,
    ErrorSchema
)
from ..dependencies import get_current_user
from educalin.repositories.material_repository import MaterialRepository
from educalin.repositories.base import get_connection
from educalin.factories.material_factory import MaterialEstudoFactoryManager


# Criar router para rotas de materiais
router = APIRouter(
    prefix="/materiais",
    tags=["Materiais"],
    responses={
        401: {"model": ErrorSchema, "description": "Não autorizado"},
        400: {"model": ErrorSchema, "description": "Requisição inválida"},
        404: {"model": ErrorSchema, "description": "Material não encontrado"},
    }
)


# Constantes de validação
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB em bytes
SUPPORTED_EXTENSIONS = MaterialEstudoFactoryManager.extensoes_suportadas()
STORAGE_PATH = Path(__file__).parent.parent.parent.parent.parent / "uploads"


def _validar_arquivo(
    arquivo: UploadFile,
    extensoes_permitidas: list[str]
) -> tuple[str, int]:
    """
    Valida um arquivo de upload.

    Args:
        arquivo: UploadFile do FastAPI
        extensoes_permitidas: Lista de extensões permitidas

    Returns:
        Tupla (extensão, tamanho em bytes)

    Raises:
        ValueError: Se arquivo for inválido
    """
    if not arquivo.filename:
        raise ValueError("Nome do arquivo inválido")

    # Extrair extensão
    nome_arquivo = arquivo.filename.lower()
    if '.' not in nome_arquivo:
        raise ValueError("Arquivo deve ter uma extensão")

    extensao = nome_arquivo.rsplit('.', 1)[1]

    # Validar extensão
    if extensao not in extensoes_permitidas:
        raise ValueError(
            f"Tipo de arquivo '.{extensao}' não suportado. "
            f"Tipos aceitos: {', '.join(extensoes_permitidas)}"
        )

    # Validar tipo MIME (verificação básica)
    if arquivo.content_type and not _validar_mime_type(extensao, arquivo.content_type):
        raise ValueError(
            f"Tipo MIME '{arquivo.content_type}' não corresponde à extensão '.{extensao}'"
        )

    # Nota: O tamanho exato será verificado durante a leitura do arquivo
    # FastAPI automaticamente lê o arquivo, então não conseguimos o tamanho antes

    return extensao, 0


def _validar_mime_type(extensao: str, content_type: str) -> bool:
    """
    Valida se o MIME type corresponde à extensão.

    Args:
        extensao: Extensão do arquivo (ex: 'pdf')
        content_type: Header Content-Type

    Returns:
        bool: True se válido, False caso contrário
    """
    mime_validos = {
        'pdf': ['application/pdf'],
        'mp4': ['video/mp4'],
        'avi': ['video/x-msvideo', 'video/avi'],
        'mkv': ['video/x-matroska'],
        'mov': ['video/quicktime'],
        'webm': ['video/webm'],
        'mp3': ['audio/mpeg', 'audio/mp3'],
    }

    if extensao not in mime_validos:
        return True  # Se não temos validação específica, aceita

    return any(mime in content_type for mime in mime_validos.get(extensao, []))


def _salvar_arquivo_simulado(arquivo: UploadFile, extensao: str) -> tuple[str, int]:
    """
    Simula salvamento de arquivo e valida tamanho.

    Lê o conteúdo em chunks para verificar se o arquivo excede o limite de 50 MB.
    Usa UUID para gerar um nome único e seguro para o arquivo.

    Args:
        arquivo: UploadFile do FastAPI
        extensao: Extensão do arquivo

    Returns:
        Tupla (nome_arquivo_salvo, tamanho_em_bytes)

    Raises:
        ValueError: Se arquivo exceder tamanho máximo
    """
    # Usar apenas o nome base do arquivo para evitar path traversal
    nome_base = Path(arquivo.filename).name
    nome_salvo = f"{uuid.uuid4().hex}_{nome_base}"

    CHUNK_SIZE = 1024 * 1024  # 1 MB por chunk
    tamanho_lido = 0

    while True:
        chunk = arquivo.file.read(CHUNK_SIZE)
        if not chunk:
            break
        tamanho_lido += len(chunk)
        if tamanho_lido > MAX_FILE_SIZE:
            raise ValueError(
                f"Arquivo excede tamanho máximo de 50 MB ({tamanho_lido / (1024*1024):.1f} MB lidos)"
            )

    return nome_salvo, tamanho_lido


@router.post(
    "/upload",
    response_model=MaterialResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Upload de novo material",
    description="Faz upload de um novo material de estudo. Detecta o tipo automaticamente pela extensão do arquivo.",
    responses={
        201: {"description": "Material criado com sucesso"},
        400: {"description": "Arquivo inválido ou dados incompletos"},
        401: {"description": "Usuário não autenticado"},
        413: {"description": "Arquivo excede tamanho máximo (50 MB)"},
    }
)
async def upload_material(
    arquivo: UploadFile = File(..., description="Arquivo a fazer upload"),
    titulo: str = Form(..., description="Título do material"),
    descricao: str = Form(..., description="Descrição do material"),
    topico: Optional[str] = Form(None, description="Tópico/área de estudo"),
    num_paginas: Optional[int] = Form(None, description="Número de páginas (obrigatório para PDF)"),
    duracao_segundos: Optional[int] = Form(None, description="Duração em segundos (obrigatório para vídeo)"),
    codec: Optional[str] = Form(None, description="Codec do vídeo (obrigatório para vídeo)"),
    current_user: UsuarioSchema = Depends(get_current_user)
) -> MaterialResponseSchema:
    """
    Faz upload de um novo material de estudo.

    O sistema detecta automaticamente o tipo de material pela extensão:
    - **.pdf**: Arquivo PDF (obrigatório fornecer `num_paginas`)
    - **.mp4, .avi, .mkv, .mov, .webm, .mp3**: Vídeo/Áudio (obrigatório `duracao_segundos` e `codec`)

    Validações:
    - Arquivo máximo de 50 MB
    - Formato suportado (PDF, Vídeo/Áudio)
    - Usuário autenticado deve ser professor

    Args:
        arquivo: Arquivo a fazer upload
        titulo: Título do material (obrigatório)
        descricao: Descrição do material (obrigatório)
        topico: Tópico/área de estudo (opcional)
        num_paginas: Número de páginas (obrigatório para PDF)
        duracao_segundos: Duração em segundos (obrigatório para vídeo)
        codec: Codec do vídeo (obrigatório para vídeo)
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        MaterialResponseSchema: Dados do material criado

    Raises:
        HTTPException 400: Se dados forem inválidos
        HTTPException 413: Se arquivo exceder 50 MB
        HTTPException 401: Se usuário não autenticado ou não é professor
    """
    # Validar que o usuário é professor
    if current_user.tipo_usuario != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas professores podem fazer upload de materiais"
        )

    try:
        # Validar arquivo
        extensao, _ = _validar_arquivo(arquivo, SUPPORTED_EXTENSIONS)

        # Salvar arquivo (lê em chunks para validar tamanho de 50 MB)
        nome_salvo, tamanho = _salvar_arquivo_simulado(arquivo, extensao)

        # Preparar dados do material
        material_data = {
            'tipo_material': _extensao_para_tipo(extensao),
            'titulo': titulo.strip(),
            'descricao': descricao.strip(),
            'autor_id': current_user.id,
            'topico': topico.strip() if topico else None,
        }

        # Validar e adicionar campos específicos por tipo
        tipo_material = material_data['tipo_material']

        if tipo_material == 'pdf':
            if num_paginas is None:
                raise ValueError("num_paginas é obrigatório para arquivos PDF")
            if not isinstance(num_paginas, int) or num_paginas <= 0:
                raise ValueError("num_paginas deve ser um número inteiro positivo")
            material_data['num_paginas'] = num_paginas

        elif tipo_material == 'video':
            if duracao_segundos is None:
                raise ValueError("duracao_segundos é obrigatório para vídeos")
            if not isinstance(duracao_segundos, int) or duracao_segundos <= 0:
                raise ValueError("duracao_segundos deve ser um número inteiro positivo")
            if not codec or not codec.strip():
                raise ValueError("codec é obrigatório para vídeos")

            material_data['duracao_segundos'] = duracao_segundos
            material_data['codec'] = codec.strip()

        # Criar material no banco de dados
        conn = get_connection()
        try:
            repo = MaterialRepository(conn)
            material_id = repo.criar(material_data)

            # Buscar material criado para retornar
            material = repo.buscar_por_id(material_id)

            if not material:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao criar material"
                )

            # Converter para schema de resposta
            return MaterialResponseSchema(
                id=material.id,
                tipo_material=material.tipo_material,
                titulo=material.titulo,
                descricao=material.descricao,
                autor_id=material.autor_id,
                topico=material.topico,
                data_upload=material.data_upload,
                num_paginas=material.num_paginas,
                duracao_segundos=material.duracao_segundos,
                codec=material.codec,
                url=material.url,
                tipo_conteudo=material.tipo_conteudo,
            )

        finally:
            conn.close()

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar upload: {str(e)}"
        )


@router.get(
    "",
    response_model=MaterialListSchema,
    summary="Listar materiais do professor",
    description="Lista todos os materiais criados pelo professor autenticado.",
    responses={
        200: {"description": "Lista de materiais"},
        401: {"description": "Usuário não autenticado"},
    }
)
def listar_materiais(
    tipo: Optional[str] = None,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> MaterialListSchema:
    """
    Lista materiais criados pelo professor autenticado.

    Opcionalmente, pode filtrar por tipo de material.

    Args:
        tipo: (opcional) Filtrar por tipo: 'pdf', 'video' ou 'link'
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        MaterialListSchema: Lista de materiais do professor

    Raises:
        HTTPException 401: Se usuário não autenticado
        HTTPException 403: Se usuário não é professor
    """
    if current_user.tipo_usuario != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas professores podem listar seus materiais"
        )

    try:
        # Validar tipo se fornecido
        if tipo and tipo not in ('pdf', 'video', 'link'):
            raise ValueError("tipo deve ser: 'pdf', 'video' ou 'link'")

        conn = get_connection()
        try:
            repo = MaterialRepository(conn)

            # Buscar materiais do professor
            materiais = repo.listar_por_professor(current_user.id)

            # Filtrar por tipo se especificado
            if tipo:
                materiais = [m for m in materiais if m.tipo_material == tipo]

            # Converter para schemas de resposta
            materiais_response = [
                MaterialResponseSchema(
                    id=m.id,
                    tipo_material=m.tipo_material,
                    titulo=m.titulo,
                    descricao=m.descricao,
                    autor_id=m.autor_id,
                    topico=m.topico,
                    data_upload=m.data_upload,
                    num_paginas=m.num_paginas,
                    duracao_segundos=m.duracao_segundos,
                    codec=m.codec,
                    url=m.url,
                    tipo_conteudo=m.tipo_conteudo,
                )
                for m in materiais
            ]

            return MaterialListSchema(
                total=len(materiais_response),
                materiais=materiais_response
            )

        finally:
            conn.close()

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar materiais: {str(e)}"
        )


@router.get(
    "/{material_id}",
    response_model=MaterialResponseSchema,
    summary="Obter detalhes de um material",
    description="Retorna os detalhes completos de um material específico.",
    responses={
        200: {"description": "Detalhes do material"},
        401: {"description": "Usuário não autenticado"},
        404: {"description": "Material não encontrado"},
    }
)
def obter_material(
    material_id: int,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> MaterialResponseSchema:
    """
    Obtém os detalhes de um material específico.

    Args:
        material_id: ID do material
        current_user: Usuário autenticado (via Bearer Token)

    Returns:
        MaterialResponseSchema: Dados do material

    Raises:
        HTTPException 401: Se usuário não autenticado
        HTTPException 404: Se material não existe
    """
    if material_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do material deve ser um número positivo"
        )

    try:
        conn = get_connection()
        try:
            repo = MaterialRepository(conn)
            material = repo.buscar_por_id(material_id)

            if not material:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Material com ID {material_id} não encontrado"
                )

            # Converter para schema de resposta
            return MaterialResponseSchema(
                id=material.id,
                tipo_material=material.tipo_material,
                titulo=material.titulo,
                descricao=material.descricao,
                autor_id=material.autor_id,
                topico=material.topico,
                data_upload=material.data_upload,
                num_paginas=material.num_paginas,
                duracao_segundos=material.duracao_segundos,
                codec=material.codec,
                url=material.url,
                tipo_conteudo=material.tipo_conteudo,
            )

        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar material: {str(e)}"
        )


@router.delete(
    "/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar um material",
    description="Remove um material de estudo (apenas o professor autor ou coordenador pode deletar).",
    responses={
        204: {"description": "Material deletado com sucesso"},
        401: {"description": "Usuário não autenticado"},
        403: {"description": "Sem permissão para deletar este material"},
        404: {"description": "Material não encontrado"},
    }
)
def deletar_material(
    material_id: int,
    current_user: UsuarioSchema = Depends(get_current_user)
) -> None:
    """
    Deleta um material de estudo.

    Apenas o professor que criou o material ou um coordenador pode deletá-lo.

    Args:
        material_id: ID do material a deletar
        current_user: Usuário autenticado (via Bearer Token)

    Raises:
        HTTPException 401: Se usuário não autenticado
        HTTPException 403: Se não for o autor do material nem coordenador
        HTTPException 404: Se material não existe
    """
    if material_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do material deve ser um número positivo"
        )

    try:
        conn = get_connection()
        try:
            repo = MaterialRepository(conn)

            # Verificar se material existe e se o usuário é o autor
            material = repo.buscar_por_id(material_id)

            if not material:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Material com ID {material_id} não encontrado"
                )

            # Verificar permissão (apenas o autor pode deletar)
            if material.autor_id != current_user.id and current_user.tipo_usuario != "coordenador":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sem permissão para deletar este material"
                )

            # Deletar material
            sucesso = repo.excluir(material_id)

            if not sucesso:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Material com ID {material_id} não encontrado"
                )

        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar material: {str(e)}"
        )


def _extensao_para_tipo(extensao: str) -> str:
    """
    Mapeia extensão de arquivo para tipo de material.

    Args:
        extensao: Extensão do arquivo (ex: 'pdf')

    Returns:
        str: Tipo de material ('pdf', 'video' ou 'link')

    Raises:
        ValueError: Se extensão não mapeada
    """
    extensao = extensao.lower()

    if extensao == 'pdf':
        return 'pdf'
    elif extensao in ('mp4', 'avi', 'mkv', 'mov', 'webm', 'mp3'):
        return 'video'
    else:
        raise ValueError(f"Extensão '{extensao}' não mapeada para um tipo de material")
