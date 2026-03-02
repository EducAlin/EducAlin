import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from educalin.services.relatorios import (
    RelatorioIndividual,
    GeradorRelatorio,
    FormatoRelatorio,
    RelatorioVazioException
)


class TestRelatorioIndividualHeranca:
    """Testes de herança e estrutura"""

    def test_herda_de_gerador_relatorio(self):
        """RelatorioIndividual deve herdar de GeradorRelatorio"""
        assert issubclass(RelatorioIndividual, GeradorRelatorio)

    def test_pode_ser_instanciado(self):
        """RelatorioIndividual deve poder ser instanciado (implementa abstratos)"""
        aluno_mock = Mock()
        turma_mock = Mock()

        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        assert isinstance(relatorio, RelatorioIndividual)
        assert isinstance(relatorio, GeradorRelatorio)

    def test_tem_atributos_aluno_e_turma(self):
        """Deve ter atributos _aluno e _turma"""
        aluno_mock = Mock()
        turma_mock = Mock()

        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        assert hasattr(relatorio, '_aluno')
        assert hasattr(relatorio, '_turma')
        assert relatorio._aluno == aluno_mock
        assert relatorio._turma == turma_mock


class TestRelatorioIndividualColetarDados:
    """Testes do método coletar_dados()"""

    @pytest.fixture
    def aluno_com_historico(self):
        """Fixture com aluno mock contendo histórico de notas"""
        aluno = Mock()
        aluno.nome = "Fulano de Tal"
        aluno.matricula = "12345"
        aluno.calcular_media = Mock(return_value=7.5)

        nota1 = Mock()
        nota1.valor = 8.0
        nota1.avaliacao = Mock()
        nota1.avaliacao.titulo = "Prova 1"
        nota1.avaliacao.topico = "Álgebra"
        nota1.avaliacao.data = datetime(2026, 1, 30)
        nota1.data_registro = datetime(2026, 1, 30)

        nota2 = Mock()
        nota2.valor = 7.0
        nota2.avaliacao = Mock()
        nota2.avaliacao.titulo = "Prova 2"
        nota2.avaliacao.topico = "Geometria"
        nota2.avaliacao.data = datetime(2026, 2, 18)
        nota2.data_registro = datetime(2026, 2, 18)

        nota3 = Mock()
        nota3.valor = 7.5
        nota3.avaliacao = Mock()
        nota3.avaliacao.titulo = "Prova 3"
        nota3.avaliacao.topico = "Álgebra"
        nota3.avaliacao.data = datetime(2026, 2, 20)
        nota3.data_registro = datetime(2026, 2, 20)

        aluno.obter_historico_notas = Mock(return_value=[nota1, nota2, nota3])

        return aluno
    
    @pytest.fixture
    def turma_mock(self):
        """Fixture com turma mock"""
        turma = Mock()
        turma.codigo = "ES002"
        turma.disciplina = "Matemática"
        turma.semestre = "2025.1"

        return turma
    
    def test_coletar_dados_retorna_dict(self, aluno_com_historico, turma_mock):
        """coletar_dados() deve retornar dicionário"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        assert isinstance(dados, dict)
        assert len(dados) > 0

    def test_coletar_dados_inclui_info_aluno(self, aluno_com_historico, turma_mock):
        """Deve incluir informações do aluno"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        assert 'nome_aluno' in dados
        assert 'matricula' in dados
        assert 'media_geral' in dados
        assert dados['nome_aluno'] == "Fulano de Tal"
        assert dados['matricula'] == "12345"
        assert dados['media_geral'] == 7.5

    def test_coletar_dados_inclui_info_turma(self, aluno_com_historico, turma_mock):
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        assert 'codigo_turma' in dados        
        assert 'disciplina' in dados        
        assert 'semestre' in dados        
        assert dados['codigo_turma'] == "ES002"
        assert dados['disciplina'] == "Matemática"

    def test_coletar_dados_inclui_historico_notas(self, aluno_com_historico, turma_mock):
        """Deve incluir histórico completo de notas"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        assert 'historico_notas' in dados
        assert isinstance(dados['historico_notas'], list)
        assert len(dados['historico_notas']) == 3

        nota = dados['historico_notas'][0]
        assert 'valor' in nota
        assert 'avaliacao' in nota
        assert 'topico' in nota
        assert 'data' in nota

    def test_coletar_dados_ordena_notas_cronologicamente(self, aluno_com_historico, turma_mock):
        """Notas devem estar ordenadas por data (mais antigas primeiro)"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        historico = dados['historico_notas']

        for i in range(len(historico) - 1):
            data_atual = historico[i]['data']
            data_proxima = historico[i + 1]['data']
            assert data_atual <= data_proxima

    def test_coletar_dados_identifica_pontos_fortes(self, aluno_com_historico, turma_mock):
        """Deve identificar tópicos com bom desempenho (>= 7.0)"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        assert 'pontos_fortes' in dados
        assert isinstance(dados['pontos_fortes'], list)
        assert len(dados['pontos_fortes']) > 0

    def test_coletar_dados_identifica_pontos_atencao(self, turma_mock):
        """Deve identificar tópicos que precisa de atenção (< 7.0)"""
        aluno = Mock()
        aluno.nome = "Fulano"
        aluno.matricula = "9999"
        aluno.calcular_media = Mock(return_value=5.5)

        nota_baixa = Mock()
        nota_baixa.valor = 4.0
        nota_baixa.avaliacao = Mock()
        nota_baixa.avaliacao.titulo = "Prova 1"
        nota_baixa.avaliacao.descricao = "Cáluclo"
        nota_baixa.avaliacao.data = datetime(2026, 1, 10)

        aluno.obter_historico_notas = Mock(return_value=[nota_baixa])

        relatorio = RelatorioIndividual(aluno, turma_mock)

        dados = relatorio.coletar_dados()

        assert 'pontos_atencao' in dados
        assert len(dados['pontos_atencao']) > 0

    def test_coletar_dados_aluno_sem_notas(self, turma_mock):
        """Deve lidar com aluno sem histórico de notas"""
        aluno = Mock()
        aluno.nome = "Fulano"
        aluno.matricula = "1111"
        aluno.calcular_media = Mock(return_value=0.0)
        aluno.obter_historico_notas = Mock(return_value=[])

        relatorio = RelatorioIndividual(aluno, turma_mock)

        dados = relatorio.coletar_dados()

        assert dados['historico_notas'] == []
        assert dados['media_geral'] == 0.0

    
class TestRelatorioIndividualFormatarSaida:
    """Testes do método formatar_saida()"""

    @pytest.fixture
    def dados_processados(self):
        """Fixture com dados processados"""
        return {
            'nome_aluno': 'Fulano de Tal',
            'matricula': '12345',
            'codigo_turma': 'ES002',
            'disciplina': 'Matemática',
            'semestre': '2025.1',
            'media_geral': 7.4,
            'total_avaliacoes': 5,
            'historico_notas': [
                {'valor': 6.0, 'avaliacao': 'Prova 1', 'topico': 'Álgebra', 'data': datetime(2025, 11, 20)},
                {'valor': 6.5, 'avaliacao': 'Prova 2', 'topico': 'Geometria', 'data': datetime(2025, 12, 10)},
                {'valor': 8.0, 'avaliacao': 'Prova 3', 'topico': 'Álgebra', 'data': datetime(2026, 1, 12)},
                {'valor': 7.5, 'avaliacao': 'Prova 4', 'topico': 'Cálculo', 'data': datetime(2026, 1, 19)},
                {'valor': 9.0, 'avaliacao': 'Prova 5', 'topico': 'Álgebra', 'data': datetime(2026, 2, 10)},
            ],
            'pontos_fortes': [
                {'topico': 'Álgebra', 'media': 8.0, 'avaliacoes': 3}
            ],
            'pontos_atencao': [
                {'topico': 'Geometria', 'media': 6.5, 'avaliacoes': 1}
            ],
            'tendencia': 'crescente',                 # tipos são 'crescente', 'estavel', 'descrescente'
            'grafico_ascii': 'Gráfico de evolução...' # TODO implementação para retorno de algo para gráfico real em interface?
        }
    
    def test_formatar_saida_retorna_string(self, dados_processados):
        """formatar_saida() deve retornar string"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_formatar_saida_inclui_cabecalho(self, dados_processados):
        """Deve incluir cabeçalho com informações do aluno"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "Fulano de Tal" in resultado
        assert "12345" in resultado
        assert "ES002" in resultado
        assert "Matemática" in resultado

    def test_formatar_saida_inclui_estatistica(self, dados_processados):
        """Deve incluir estatísticas do aluno"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "7.5" in resultado
        assert "5" in resultado or "cinco" in resultado.lower()

    def test_formatar_saida_inclui_historico(self, dados_processados):
        """Deve incluir lista do histórico de notas"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "Prova 1" in resultado
        assert "Álgebra" in resultado
        assert "6.0" in resultado

    def test_formatar_saida_inclui_grafico(self, dados_processados):
        """Deve incluir gráfico de evolução"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "evolução" in resultado.lower() or "gráfico" in resultado.lower()
        assert any(char in resultado for char in ['│', '─', '█', '*', '#', '|', '-'])

    def test_formatar_saida_inclui_analise_tendencia(self, dados_processados):
        """Deve incluir análise de tendência"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert any(palavra in resultado.lower()
                   for palavra in ['crescente', 'melhor', 'progress', 'evolu', 'ascend'])
        
    def test_formatar_saida_inclui_pontos_fortes(self, dados_processados):
        """Deve listar pontos fortes do aluno"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "pontos fortes" in resultado.lower() or "destaque" in resultado.lower()
        assert "Álgebra" in resultado

    def test_formatar_saida_inclui_pontos_fracos(self, dados_processados):
        """Deve listar pontos que precisam de atenção"""
        aluno_mock = Mock()
        turma_mock = Mock()
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        resultado = relatorio.formatar_saida(dados_processados)

        assert "atenção" in resultado.lower() or "melhorar" in resultado.lower()

    
class TestRelatorioIndividualProcessarDados:
    """Testes do método processar_dados()"""

    @pytest.fixture
    def aluno_mock(self):
        return Mock()
    
    @pytest.fixture
    def turma_mock(self):
        return Mock()
    
    def test_processar_dados_calcula_tendencia_crescente(self, aluno_mock, turma_mock):
        """Deve identificar tendência crescente"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {
            'historico_notas': [
                {'valor': 6.0, 'data': datetime(2025, 12, 10)},
                {'valor': 7.0, 'data': datetime(2026, 1, 10)},
                {'valor': 8.0, 'data': datetime(2026, 2, 10)},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert 'tendencia' in dados_processados
        assert dados_processados['tendencia'] == 'crescente'

    def test_processar_dados_calcula_tendencia_decrescente(self, aluno_mock, turma_mock):
        """Deve identificar tendência decrescente"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {
            'historico_notas': [
                {'valor': 9.0, 'data': datetime(2025, 12, 10)},
                {'valor': 7.0, 'data': datetime(2026, 1, 10)},
                {'valor': 5.0, 'data': datetime(2026, 2, 10)},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert dados_processados['tendencia'] == 'decrescente'

    def test_processar_dados_calcula_tendencia_estavel(self, aluno_mock, turma_mock):
        """Deve identificar tendência estável"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {
            'historico_notas': [
                {'valor': 7.0, 'data': datetime(2025, 12, 10)},
                {'valor': 7.2, 'data': datetime(2026, 1, 10)},
                {'valor': 6.8, 'data': datetime(2026, 2, 10)},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert dados_processados['tendencia'] == 'estavel'

    def test_processar_dados_gera_grafico_ascii(self, aluno_mock, turma_mock):
        """Deve gerar gráfico ASCII de evolução"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {
            'historico_notas': [
                {'valor': 5.0, 'avaliacao': 'P1', 'data': datetime(2025, 12, 10)},
                {'valor': 7.0, 'avaliacao': 'P2', 'data': datetime(2026, 1, 10)},
                {'valor': 9.0, 'avaliacao': 'P3', 'data': datetime(2026, 2, 10)},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert 'grafico_ascii' in dados_processados
        grafico = dados_processados['grafico_ascii']
        assert isinstance(grafico, str)
        assert len(grafico) > 0
        assert any(char in grafico for char in ['│', '─', '█', '*', '#'])


class TestRelatorioIndividualIntegracao:
    """Testes de integração end-to-end"""

    @pytest.fixture
    def aluno_completo(self):
        """Aluno com histórico completo para teste end-to-end"""
        aluno = Mock()
        aluno.nome = "Glip Glarp"
        aluno.matricula = "54321"
        aluno.calcular_media = Mock(return_value=8.2)

        notas = []
        for i in range(4):
            nota = Mock()
            nota.valor = 7.0 + i * 0.5
            nota.avaliacao = Mock()
            nota.avaliacao.titulo = f"Prova {i+1}"
            nota.avaliacao.topico = "Álgebra" if i % 2 == 0 else "Geometria"
            nota.avaliacao.data = datetime(2025, 1 + i, 15)
            nota.data_registro = datetime(2025, 1 + i, 15)
            notas.append(nota)

        aluno.obter_historico_notas = Mock(return_value=notas)

        return aluno
    
    @pytest.fixture
    def turma_completa(self):
        turma = Mock()
        turma.codigo = "ES002"
        turma.disciplina = "Matemática"
        turma.semestre = "2025.1"
        return turma
    
    def test_gerar_relatorio_completo(self, aluno_completo, turma_completa):
        """Teste end-to-end: gerar relatório individual completo"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        resultado = relatorio.gerar()

        assert isinstance(resultado, str)
        assert len(resultado) > 0
        assert "Glip Glarp" in resultado
        assert "54321" in resultado
        assert "8.2" in resultado

    def test_gerar_e_exportar_pdf(self, aluno_completo, turma_completa):
        """Deve poder gerar e exportar para PDF"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        conteudo = relatorio.gerar()
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.TEXTO)

        assert isinstance(resultado, bytes)