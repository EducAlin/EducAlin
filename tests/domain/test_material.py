import pytest
from datetime import datetime, timedelta
from src.educalin.domain.material import MaterialPDF, MaterialVideo, MaterialLink

@pytest.fixture
def agora():
    return datetime.now()

@pytest.fixture
def pdf_valido(agora):
    return MaterialPDF(
        titulo="Introdução ao Python",
        descricao="Material de estudo sobre Python.",
        autor="",
        data_upload=agora,
        num_paginas=10
    )  # 10 páginas

@pytest.fixture
def video_valido(agora):
    return MaterialVideo(
        titulo="Curso de JavaScript",
        descricao="Vídeo aula sobre JavaScript.",
        autor="",
        data_upload=agora,
        duracao_segundos=120,
        codec="H.264"
    )

@pytest.fixture
def link_valido(agora):
    return MaterialLink(
        titulo="Documentação do Django",
        descricao="Link para a documentação oficial do Django.",
        autor="",
        data_upload=agora,
        url="https://example.com",
        tipo_conteudo="Documentação"
    )

# -----------------------
# Testes: regra comum (data_upload)
# -----------------------
def test_nao_permite_data_upload_no_futuro():
    futuro = datetime.now() + timedelta(days=1)
    with pytest.raises(ValueError, match="não pode ser no futuro"):
        MaterialPDF("T", "D", "A", futuro, 1)


# -----------------------
# Testes: setters da classe base
# -----------------------
@pytest.mark.parametrize("valor_invalido", ["", "   ", None, 123])
def test_setter_titulo_invalido(pdf_valido, valor_invalido):
    with pytest.raises(ValueError):
        pdf_valido.titulo = valor_invalido


@pytest.mark.parametrize("valor_invalido", ["", "   ", None, 123])
def test_setter_autor_invalido(pdf_valido, valor_invalido):
    with pytest.raises(ValueError):
        pdf_valido.autor = valor_invalido


@pytest.mark.parametrize("valor_invalido", ["", "   ", None, 123])
def test_setter_descricao_invalido(pdf_valido, valor_invalido):
    with pytest.raises(ValueError):
        pdf_valido.descricao = valor_invalido


def test_setters_removem_espacos(pdf_valido):
    pdf_valido.titulo = "  Titulo  "
    pdf_valido.autor = "  Autor  "
    pdf_valido.descricao = "  Desc  "

    assert pdf_valido.titulo == "Titulo"
    assert pdf_valido.autor == "Autor"
    assert pdf_valido.descricao == "Desc"


# -----------------------
# Testes: MaterialPDF
# -----------------------
def test_pdf_validar_formato_ok(pdf_valido):
    assert pdf_valido.validar_formato() is True


@pytest.mark.parametrize("num_paginas", [0, -1, "10", None])
def test_pdf_validar_formato_invalido(agora, num_paginas):
    pdf = MaterialPDF("T", "D", "A", agora, num_paginas)
    with pytest.raises(ValueError):
        pdf.validar_formato()


def test_pdf_obter_tamanho(pdf_valido):
    assert pdf_valido.obter_tamanho() == 10


def test_pdf_setter_num_paginas_invalido(pdf_valido):
    with pytest.raises(ValueError):
        pdf_valido.num_paginas = 0


def test_pdf_extrair_texto(pdf_valido):
    assert pdf_valido.extrair_texto() == "Texto extraído do PDF."


# -----------------------
# Testes: MaterialVideo
# -----------------------
def test_video_validar_formato_ok(video_valido):
    assert video_valido.validar_formato() is True


@pytest.mark.parametrize("codec", ["", "   ", None, 123])
def test_video_validar_formato_invalido(agora, codec):
    video = MaterialVideo("T", "D", "A", agora, 10, codec)
    with pytest.raises(ValueError):
        video.validar_formato()


def test_video_obter_tamanho(video_valido):
    assert video_valido.obter_tamanho() == 120


def test_video_setter_duracao_invalida(video_valido):
    with pytest.raises(ValueError):
        video_valido.duracao_segundos = 0


def test_video_setter_codec_invalido(video_valido):
    with pytest.raises(ValueError):
        video_valido.codec = ""


def test_video_gerar_thumbnail(video_valido):
    assert video_valido.gerar_thumbnail() == "Caminho/para/thumbnail.jpg"


# -----------------------
# Testes: MaterialLink
# -----------------------
def test_link_validar_formato_ok(link_valido):
    assert link_valido.validar_formato() is True


@pytest.mark.parametrize("url", ["", "   ", None, 123])
def test_link_validar_formato_invalido(agora, url):
    link = MaterialLink("T", "D", "A", agora, url, "artigo")
    with pytest.raises(ValueError):
        link.validar_formato()


def test_link_obter_tamanho(link_valido):
    assert link_valido.obter_tamanho() == len("https://example.com")


def test_link_setter_url_invalida(link_valido):
    with pytest.raises(ValueError):
        link_valido.url = "   "


def test_link_setter_tipo_conteudo_invalido(link_valido):
    with pytest.raises(ValueError):
        link_valido.tipo_conteudo = ""


def test_link_verificar_disponibilidade(link_valido):
    assert link_valido.verificar_disponibilidade() is True


# -----------------------
# Teste extra: __str__
# -----------------------
def test_str_contem_campos_principais(pdf_valido):
    texto = str(pdf_valido)
    assert "MaterialPDF" in texto
    assert "Título:" in texto
    assert "Descrição:" in texto
    assert "Autor:" in texto
    assert "Data de Upload:" in texto