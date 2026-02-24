import pytest
from datetime import datetime

from educalin.domain.material import MaterialLink, MaterialPDF, MaterialVideo
from educalin.factories.material_factory import (
    MaterialEstudoFactory,
    MaterialLinkFactory,
    MaterialPDFFactory,
    MaterialVideoFactory,
    MaterialEstudoFactoryManager,
)


@pytest.fixture
def agora():
    return datetime.now()


@pytest.fixture
def dados_pdf(agora):
    return {
        'titulo': 'Introdução ao Python',
        'descricao': 'Material de estudo sobre Python.',
        'data_upload': agora,
        'autor': 'Autor',
        'num_paginas': 10,
    }


@pytest.fixture
def dados_video(agora):
    return {
        'titulo': 'Curso de JavaScript',
        'descricao': 'Vídeo aula sobre JavaScript.',
        'data_upload': agora,
        'autor': 'Autor',
        'duracao_segundos': 120,
        'codec': 'H.264',
    }


@pytest.fixture
def dados_link(agora):
    return {
        'titulo': 'Documentação do Django',
        'descricao': 'Link para a documentação oficial do Django.',
        'data_upload': agora,
        'autor': 'Autor',
        'url': 'https://docs.djangoproject.com',
        'tipo_conteudo': 'Documentação',
    }


# -----------------------
# Testes: MaterialPDFFactory
# -----------------------

def test_pdf_factory_cria_material_valido(dados_pdf):
    factory = MaterialPDFFactory()
    material = factory.criar_material(dados_pdf)
    assert isinstance(material, MaterialPDF)
    assert material.titulo == dados_pdf['titulo']
    assert material.num_paginas == dados_pdf['num_paginas']


@pytest.mark.parametrize("chave_faltante", ['titulo', 'descricao', 'data_upload', 'autor', 'num_paginas'])
def test_pdf_factory_chave_obrigatoria_faltando(dados_pdf, chave_faltante):
    del dados_pdf[chave_faltante]
    with pytest.raises(KeyError, match="Chaves obrigatórias faltando"):
        MaterialPDFFactory().criar_material(dados_pdf)


@pytest.mark.parametrize("num_paginas", ["10", 10.0, None])
def test_pdf_factory_tipo_invalido_num_paginas(dados_pdf, num_paginas):
    dados_pdf['num_paginas'] = num_paginas
    with pytest.raises(TypeError, match="num_paginas deve ser int"):
        MaterialPDFFactory().criar_material(dados_pdf)


@pytest.mark.parametrize("num_paginas", [0, -1, -100])
def test_pdf_factory_valor_invalido_num_paginas(dados_pdf, num_paginas):
    dados_pdf['num_paginas'] = num_paginas
    with pytest.raises(ValueError, match="num_paginas deve ser positivo"):
        MaterialPDFFactory().criar_material(dados_pdf)


# -----------------------
# Testes: MaterialVideoFactory
# -----------------------

def test_video_factory_cria_material_valido(dados_video):
    factory = MaterialVideoFactory()
    material = factory.criar_material(dados_video)
    assert isinstance(material, MaterialVideo)
    assert material.titulo == dados_video['titulo']
    assert material.duracao_segundos == dados_video['duracao_segundos']
    assert material.codec == dados_video['codec']


@pytest.mark.parametrize("chave_faltante", ['titulo', 'descricao', 'data_upload', 'autor', 'duracao_segundos', 'codec'])
def test_video_factory_chave_obrigatoria_faltando(dados_video, chave_faltante):
    del dados_video[chave_faltante]
    with pytest.raises(KeyError, match="Chaves obrigatórias faltando"):
        MaterialVideoFactory().criar_material(dados_video)


@pytest.mark.parametrize("duracao", ["120", 120.0, None])
def test_video_factory_tipo_invalido_duracao(dados_video, duracao):
    dados_video['duracao_segundos'] = duracao
    with pytest.raises(TypeError, match="duracao_segundos deve ser int"):
        MaterialVideoFactory().criar_material(dados_video)


@pytest.mark.parametrize("codec", [123, None, True])
def test_video_factory_tipo_invalido_codec(dados_video, codec):
    dados_video['codec'] = codec
    with pytest.raises(TypeError, match="codec deve ser str"):
        MaterialVideoFactory().criar_material(dados_video)


@pytest.mark.parametrize("duracao", [0, -1, -60])
def test_video_factory_valor_invalido_duracao(dados_video, duracao):
    dados_video['duracao_segundos'] = duracao
    with pytest.raises(ValueError, match="duracao_segundos deve ser positiva"):
        MaterialVideoFactory().criar_material(dados_video)


@pytest.mark.parametrize("codec", ["", "   "])
def test_video_factory_valor_invalido_codec(dados_video, codec):
    dados_video['codec'] = codec
    with pytest.raises(ValueError, match="codec não pode ser vazio"):
        MaterialVideoFactory().criar_material(dados_video)


# -----------------------
# Testes: MaterialLinkFactory
# -----------------------

def test_link_factory_cria_material_valido(dados_link):
    factory = MaterialLinkFactory()
    material = factory.criar_material(dados_link)
    assert isinstance(material, MaterialLink)
    assert material.titulo == dados_link['titulo']
    assert material.url == dados_link['url']
    assert material.tipo_conteudo == dados_link['tipo_conteudo']


@pytest.mark.parametrize("chave_faltante", ['titulo', 'descricao', 'data_upload', 'autor', 'url', 'tipo_conteudo'])
def test_link_factory_chave_obrigatoria_faltando(dados_link, chave_faltante):
    del dados_link[chave_faltante]
    with pytest.raises(KeyError, match="Chaves obrigatórias faltando"):
        MaterialLinkFactory().criar_material(dados_link)


@pytest.mark.parametrize("url", [123, None, True])
def test_link_factory_tipo_invalido_url(dados_link, url):
    dados_link['url'] = url
    with pytest.raises(TypeError, match="url deve ser str"):
        MaterialLinkFactory().criar_material(dados_link)


@pytest.mark.parametrize("tipo_conteudo", [123, None, True])
def test_link_factory_tipo_invalido_tipo_conteudo(dados_link, tipo_conteudo):
    dados_link['tipo_conteudo'] = tipo_conteudo
    with pytest.raises(TypeError, match="tipo_conteudo deve ser str"):
        MaterialLinkFactory().criar_material(dados_link)


@pytest.mark.parametrize("url", ["", "   "])
def test_link_factory_valor_vazio_url(dados_link, url):
    dados_link['url'] = url
    with pytest.raises(ValueError, match="url não pode ser vazia"):
        MaterialLinkFactory().criar_material(dados_link)


@pytest.mark.parametrize("url", ["not-a-url", "://no-scheme", "example.com"])
def test_link_factory_url_formato_invalido(dados_link, url):
    dados_link['url'] = url
    with pytest.raises(ValueError, match="não é uma URL válida"):
        MaterialLinkFactory().criar_material(dados_link)


@pytest.mark.parametrize("tipo_conteudo", ["", "   "])
def test_link_factory_valor_vazio_tipo_conteudo(dados_link, tipo_conteudo):
    dados_link['tipo_conteudo'] = tipo_conteudo
    with pytest.raises(ValueError, match="tipo_conteudo não pode ser vazio"):
        MaterialLinkFactory().criar_material(dados_link)


# -----------------------
# Testes: MaterialEstudoFactoryManager
# -----------------------

def test_manager_cria_pdf_por_extensao(dados_pdf):
    material = MaterialEstudoFactoryManager.criar_por_extensao('pdf', dados_pdf)
    assert isinstance(material, MaterialPDF)


def test_manager_cria_video_por_extensao(dados_video):
    for ext in ['mp4', 'avi', 'mkv', 'mov', 'webm']:
        material = MaterialEstudoFactoryManager.criar_por_extensao(ext, dados_video)
        assert isinstance(material, MaterialVideo)


def test_manager_cria_video_mp3_por_extensao(dados_video):
    material = MaterialEstudoFactoryManager.criar_por_extensao('mp3', dados_video)
    assert isinstance(material, MaterialVideo)


def test_manager_extensao_com_ponto(dados_pdf):
    material = MaterialEstudoFactoryManager.criar_por_extensao('.pdf', dados_pdf)
    assert isinstance(material, MaterialPDF)


def test_manager_extensao_maiuscula(dados_pdf):
    material = MaterialEstudoFactoryManager.criar_por_extensao('PDF', dados_pdf)
    assert isinstance(material, MaterialPDF)


def test_manager_extensao_maiuscula_com_ponto(dados_pdf):
    material = MaterialEstudoFactoryManager.criar_por_extensao('.PDF', dados_pdf)
    assert isinstance(material, MaterialPDF)


def test_manager_extensao_nao_suportada(dados_pdf):
    with pytest.raises(ValueError, match="não suportada"):
        MaterialEstudoFactoryManager.criar_por_extensao('docx', dados_pdf)


def test_manager_mensagem_erro_extensoes_ordenadas(dados_pdf):
    with pytest.raises(ValueError) as exc_info:
        MaterialEstudoFactoryManager.criar_por_extensao('xyz', dados_pdf)
    extensoes_na_mensagem = exc_info.value.args[0].split("Tipos válidos: ")[1]
    lista = extensoes_na_mensagem.split(", ")
    assert lista == sorted(lista)


def test_manager_registrar_extensao(dados_pdf):
    MaterialEstudoFactoryManager.registrar_extensao('mypdf', MaterialPDFFactory())
    material = MaterialEstudoFactoryManager.criar_por_extensao('mypdf', dados_pdf)
    assert isinstance(material, MaterialPDF)
    # cleanup
    del MaterialEstudoFactoryManager.EXTENSOES_SUPORTADAS['mypdf']


def test_manager_extensoes_suportadas_retorna_lista():
    extensoes = MaterialEstudoFactoryManager.extensoes_suportadas()
    assert isinstance(extensoes, list)
    assert 'pdf' in extensoes
    assert 'mp4' in extensoes
