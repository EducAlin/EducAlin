import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from educalin.services.relatorio import (
    RelatorioTurma,
    GeradorRelatorio,
    FormatoRelatorio,
    RelatorioVazioException
)

class TestRelatorioTurmaHeranca:
    """Testes de herança e estrutura"""

    def test_herda_de_gerador_relatorio(self):
        """RelatorioTurma deve herdar de GeradorRelatorio"""
        assert issubclass(RelatorioTurma, GeradorRelatorio)

    def test_pode_ser_instanciado(self):
        """RelatorioTurma deve poder ser instanciado (implementa abstratos)"""
        turma_mock = Mock()

        relatorio = RelatorioTurma(turma_mock)

        assert isinstance(relatorio, RelatorioTurma)
        assert isinstance(relatorio, GeradorRelatorio)

    def test_tem_atributo_turma(self):
        """Deve ter atributo _turma"""
        turma_mock = Mock()

        relatorio = RelatorioTurma(turma_mock)

        assert hasattr(relatorio, '_turma')
        assert relatorio._turma == turma_mock


class TestRelatorioTurmaColetarDados:
    """Testes do método coletar_dados()"""

    @pytest.fixture
    def turma_com_alunos(self):
        """Fixture com turma mock contendo alunos"""
        turma = Mock()
        turma.codigo = "ES006"
        turma.disciplina = "POO"
        turma.semestre = "2025.2"
        turma.total_alunos = 3

        aluno1 = Mock()
        aluno1.nome = "Fulano 1"
        aluno1.matricula = "001"
        aluno1.calcular_media = Mock(return_value=8.5)

        aluno2 = Mock()
        aluno2.nome = "Fulano 2"
        aluno2.matricula = "002"
        aluno2.calcular_media = Mock(return_value=5.0)

        aluno3 = Mock()
        aluno3.nome = "Fulano 3"
        aluno3.matricula = "003"
        aluno3.calcular_media = Mock(return_value=7.0)

        turma.alunos = [aluno1, aluno2, aluno3]

        turma.obter_desempenho_geral = Mock(return_value={
            'media_geral': 6.83,
            'total_alunos': 3,
            'alunos_com_dificuldade': 1,
            'taxa_aprovacao': 66.67
        })

        return turma
    
    def test_coletar_dados_retorna_dict(self, turma_com_alunos):
        """coletar_dados() deve retornar dicionário com dados da turma"""
        relatorio = RelatorioTurma(turma_com_alunos)

        dados = relatorio.coletar_dados()

        assert isinstance(dados, dict)
        assert len(dados) > 0

    def test_coletar_dados_inclui_info_turma(self, turma_com_alunos):
        """Deve incluir informações básicas da turma"""
        relatorio = RelatorioTurma(turma_com_alunos)

        dados = relatorio.coletar_dados()

        assert 'codigo_turma' in dados
        assert 'disciplina' in dados
        assert 'semestre' in dados
        assert dados['codigo_turma'] == "ES006"
        assert dados['disciplina'] == "POO"

    def test_coletar_dados_inclui_estatisticas(self, turma_com_alunos):
        """Deve incluir estatísticas gerais da turma"""
        relatorio = RelatorioTurma(turma_com_alunos)

        dados = relatorio.coletar_dados()

        assert 'media_geral' in dados
        assert 'total_alunos' in dados
        assert 'taxa_aprovacao' in dados
        assert dados['media_geral'] == 6.83
        assert dados['total_alunos'] == 3
        assert dados['taxa_aprovacao'] == 66.67

    def test_coletar_dados_inclui_lista_alunos(self, turma_com_alunos):
        """Deve incluir lista com dados de todos os alunos"""
        relatorio = RelatorioTurma(turma_com_alunos)

        dados = relatorio.coletar_dados()

        assert 'alunos' in dados
        assert isinstance(dados['alunos'], list)
        assert len(dados['alunos']) == 3

        aluno_data = dados['alunos'][0]
        assert 'nome' in aluno_data
        assert 'matricula' in aluno_data
        assert 'media' in aluno_data

    def test_coletar_dados_inclui_alunos_dificuldade(self, turma_com_alunos):
        """Deve identificar alunos com dificuldade (média < 6.0)"""
        relatorio = RelatorioTurma(turma_com_alunos)

        dados = relatorio.coletar_dados()

        assert 'alunos_dificuldade' in dados
        assert isinstance(dados['alunos_dificuldade'], list)
        assert len(dados['alunos_dificuldade']) == 1
        assert dados['alunos_dificuldade'][0]['nome'] == "Fulano 2"

    def test_coletar_dados_turma_vazia(self):
        """Deve retornar dados mesmo se turma não tem alunos"""
        turma = Mock()
        turma.codigo = "ES001"
        turma.disciplina = "Introdução à Programação"
        turma.semestre = "2025.1"
        turma.alunos = []
        turma.total_alunos = 0
        turma.obter_desempenho_geral = Mock(return_value={
            'media_geral': 0.0,
            'total_alunos': 0,
            'alunos_com_dificuldade': 0,
            'taxa_aprovacao': 0
        })

        relatorio = RelatorioTurma(turma)

        dados = relatorio.coletar_dados()

        assert dados['total_alunos'] == 0
        assert dados['alunos'] == []


class TestRelatorioTurmaFormatarSaida:
    """Testes do método formatar_saida()"""

    @pytest.fixture
    def dados_processados(self):
        """Fixture com dados processados para formatação"""
        return {
            'codigo_turma': 'ES006',
            'disciplina': 'Programação Orientada à Objetos',
            'semestre': '2025.2',
            'total_alunos': 40,
            'media_geral': 7.5,
            'taxa_aprovacao': 80.0,
            'alunos': [
                {'nome': 'Fulano 1', 'matricula': '001', 'media': 9.5},
                {'nome': 'Fulano 2', 'matricula': '002', 'media': 5.5},
                {'nome': 'Fulano 3', 'matricula': '003', 'media': 7.5}
            ],
            'alunos_dificuldade': [
                {'nome': 'Fulano 2', 'matricula': '002', 'media': 5.5}
            ],
            'ranking_top5': [
                {'nome': 'Fulano 1', 'matricula': '001', 'media': 9.5},
                {'nome': 'Fulano 3', 'matricula': '003', 'media': 7.5}
            ]
        }
    
    def test_formatar_saida_retorna_string(self, dados_processados):
        """formatar_saida() deve retornar string formatada"""
        turma_mock = Mock()
        relatorio = RelatorioTurma(turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_formatar_saida_inclui_cabecalho(self, dados_processados):
        """Deve incluir cabeçalho com informações da turma"""
        turma_mock = Mock()
        relatorio = RelatorioTurma(turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "ES006" in resultado
        assert "Programação Orientada à Objetos" in resultado
        assert "2025.2" in resultado

    def test_formatar_saida_inclui_estatisticas(self, dados_processados):
        """Deve incluir estatísticas gerais"""
        turma_mock = Mock()
        relatorio = RelatorioTurma(turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "40" in resultado # total_alunos
        assert "7.5" in resultado # media_geral
        assert "80.0" in resultado or "80%" in resultado # taxa_aprovacao

    def test_formatar_saida_inclui_secao_dificuldade(self, dados_processados):
        """Deve ter seção de alunos com dificuldade"""
        turma_mock = Mock()
        relatorio = RelatorioTurma(turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "dificuldade" in resultado.lower() or "atenção" in resultado.lower()
        assert "Fulano 2" in resultado

    def test_formatar_saida_inclui_ranking(self, dados_processados):
        """Deve incluir ranking dos melhores alunos"""
        turma_mock = Mock()
        relatorio = RelatorioTurma(turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "ranking" in resultado.lower() or "melhores" in resultado.lower()
        assert "Fulano 1" in resultado

    def test_formatar_saida_formatacao_legivel(self, dados_processados):
        turma_mock = Mock()
        relatorio = RelatorioTurma(turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "=" in resultado or "-" in resultado
        assert "\n" in resultado

        linhas = resultado.split('\n')
        assert len(linhas) > 10


class TestRelatorioTurmaProcessarDados:
    """Testes do método processar_dados()"""

    @pytest.fixture
    def turma_mock(self):
        turma = Mock()
        turma.codigo = "ES006"
        turma.alunos = []
        return turma
    
    def test_processar_dados_adiciona_ranking(self, turma_mock):
        """Se sobrescrito, deve adicionar ranking dos alunos"""
        relatorio = RelatorioTurma(turma_mock)

        dados_brutos = {
            'alunos': [
                {'nome': 'Fulano 1', 'media': 8.5},
                {'nome': 'Fulano 2', 'media': 9.0},
                {'nome': 'Fulano 3', 'media': 7.0},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)

        if 'ranking_top5' in dados_processados:
            ranking = dados_processados['ranking_top5']
            assert ranking[0]['nome'] == "Fulano 2"
            assert ranking[0]['media'] == 9.0


class TestRelatorioTurmaIntegracao:
    """Testes de integração com Template Method"""

    @pytest.fixture
    def turma_completa(self):
        """Fixture com turma completa para teste end-to-end"""
        turma = Mock()
        turma.codigo = "ES006"
        turma.disciplina = "POO"
        turma.semestre = "2025.2"
        turma.total_alunos = 3

        aluno1 = Mock()
        aluno1.nome = "Fulano 1"
        aluno1.matricula = "001"
        aluno1.calcular_media = Mock(return_value=8.5)

        aluno2 = Mock()
        aluno2.nome = "Fulano 2"
        aluno2.matricula = "002"
        aluno2.calcular_media = Mock(return_value=5.0)

        aluno3 = Mock()
        aluno3.nome = "Fulano 3"
        aluno3.matricula = "003"
        aluno3.calcular_media = Mock(return_value=7.0)

        turma.alunos = [aluno1, aluno2, aluno3]

        turma.obter_desempenho_geral = Mock(return_value={
            'media_geral': 6.83,
            'total_alunos': 3,
            'alunos_com_dificuldade': 1,
            'taxa_aprovacao': 66.67
        })

        return turma
    
    def test_gerador_relatorio_completo(self, turma_completa):
        """Teste end-to-end: ferar() usa template method completo"""
        relatorio = RelatorioTurma(turma_completa)

        resultado = relatorio.gerar()

        assert isinstance(resultado, str)
        assert len(resultado) > 0

        assert "ES006" in resultado
        assert "POO" in resultado
        assert "2025.2" in resultado
        assert "Fulano 1" in resultado
        assert "Fulano 3" in resultado

    def test_gerar_e_exportar_pdf(self, turma_completa):
        """Deve poder gerar e exportar para PDF"""
        relatorio = RelatorioTurma(turma_completa)

        conteudo = relatorio.gerar()

        resultado = relatorio.exportar(conteudo, FormatoRelatorio.TEXTO)

        assert isinstance(resultado, bytes)

    def test_tem_metadados_apos_gerar(self, turma_completa):
        """Deve ter metadados após gerar (herdado do template)"""
        relatorio = RelatorioTurma(turma_completa)
        relatorio.gerar()

        metadados = relatorio.obter_metadados()

        assert 'data_geracao' in metadados
        assert 'total_dados' in metadados