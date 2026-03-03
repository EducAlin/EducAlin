import pytest
from unittest.mock import Mock, PropertyMock
from datetime import datetime

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

    def test_init_aluno_sem_nome_lanca_type_error(self):
        """Deve lançar TypeError se aluno não tiver atributo 'nome'"""
        aluno_invalido = Mock(spec=[])  # sem nenhum atributo
        turma_mock = Mock()

        with pytest.raises(TypeError, match="nome"):
            RelatorioIndividual(aluno_invalido, turma_mock)

    def test_init_aluno_sem_matricula_lanca_type_error(self):
        """Deve lançar TypeError se aluno não tiver atributo 'matricula'"""
        aluno_invalido = Mock(spec=['nome'])  # tem nome, falta matricula
        turma_mock = Mock()

        with pytest.raises(TypeError, match="matricula"):
            RelatorioIndividual(aluno_invalido, turma_mock)

    def test_init_turma_sem_codigo_lanca_type_error(self):
        """Deve lançar TypeError se turma não tiver atributo 'codigo'"""
        aluno_mock = Mock()
        turma_invalida = Mock(spec=[])  # sem nenhum atributo

        with pytest.raises(TypeError, match="codigo"):
            RelatorioIndividual(aluno_mock, turma_invalida)

    def test_limiar_aprovacao_e_constante_de_classe(self):
        """LIMIAR_APROVACAO deve ser constante de classe com valor 7.0"""
        assert hasattr(RelatorioIndividual, 'LIMIAR_APROVACAO')
        assert RelatorioIndividual.LIMIAR_APROVACAO == 7.0


class TestRelatorioIndividualColetarDados:
    """Testes do método coletar_dados()"""

    @pytest.fixture
    def aluno_com_historico(self):
        """Fixture com aluno mock contendo histórico de notas via propriedade desempenho"""
        aluno = Mock()
        aluno.nome = "Fulano de Tal"
        aluno.matricula = "12345"
        aluno.calcular_media = Mock(return_value=7.5)

        nota1 = Mock()
        nota1.valor = 8.0
        nota1.avaliacao = Mock()
        nota1.avaliacao.titulo = "Prova 1"
        nota1.avaliacao.topico = "Álgebra"
        nota1.data_registro = datetime(2026, 1, 30)

        nota2 = Mock()
        nota2.valor = 7.0
        nota2.avaliacao = Mock()
        nota2.avaliacao.titulo = "Prova 2"
        nota2.avaliacao.topico = "Geometria"
        nota2.data_registro = datetime(2026, 2, 18)

        nota3 = Mock()
        nota3.valor = 7.5
        nota3.avaliacao = Mock()
        nota3.avaliacao.titulo = "Prova 3"
        nota3.avaliacao.topico = "Álgebra"
        nota3.data_registro = datetime(2026, 2, 20)

        # Usa a propriedade `desempenho` da classe Aluno (API correta do domínio)
        type(aluno).desempenho = PropertyMock(return_value=[nota1, nota2, nota3])

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
        """Deve incluir informações da turma"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        assert 'codigo_turma' in dados        
        assert 'disciplina' in dados        
        assert 'semestre' in dados        
        assert dados['codigo_turma'] == "ES002"
        assert dados['disciplina'] == "Matemática"

    def test_coletar_dados_inclui_historico_notas(self, aluno_com_historico, turma_mock):
        """Deve incluir histórico completo de notas com campos valor, avaliacao, topico e data"""
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

    def test_coletar_dados_usa_data_registro_da_nota(self, aluno_com_historico, turma_mock):
        """O campo 'data' do histórico deve vir de nota.data_registro"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        historico = dados['historico_notas']
        # Primeira nota (mais antiga) deve ter data_registro de 2026-01-30
        assert historico[0]['data'] == datetime(2026, 1, 30)

    def test_coletar_dados_ordena_notas_cronologicamente(self, aluno_com_historico, turma_mock):
        """Notas devem estar ordenadas por data_registro (mais antigas primeiro)"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados = relatorio.coletar_dados()

        historico = dados['historico_notas']

        for i in range(len(historico) - 1):
            data_atual = historico[i]['data']
            data_proxima = historico[i + 1]['data']
            assert data_atual <= data_proxima

    def test_coletar_dados_identifica_pontos_fortes(self, aluno_com_historico, turma_mock):
        """Deve identificar tópicos com bom desempenho (>= 7.0) após processar_dados()"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados_brutos = relatorio.coletar_dados()
        dados = relatorio.processar_dados(dados_brutos)

        assert 'pontos_fortes' in dados
        assert isinstance(dados['pontos_fortes'], list)
        assert len(dados['pontos_fortes']) > 0

    def test_coletar_dados_identifica_pontos_atencao(self, turma_mock):
        """Deve identificar tópicos que precisam de atenção (< 7.0) após processar_dados()"""
        aluno = Mock()
        aluno.nome = "Fulano"
        aluno.matricula = "9999"
        aluno.calcular_media = Mock(return_value=5.5)

        nota_baixa = Mock()
        nota_baixa.valor = 4.0
        nota_baixa.avaliacao = Mock()
        nota_baixa.avaliacao.titulo = "Prova 1"
        nota_baixa.avaliacao.topico = "Cálculo"
        nota_baixa.data_registro = datetime(2026, 1, 10)

        type(aluno).desempenho = PropertyMock(return_value=[nota_baixa])

        relatorio = RelatorioIndividual(aluno, turma_mock)

        dados_brutos = relatorio.coletar_dados()
        dados = relatorio.processar_dados(dados_brutos)

        assert 'pontos_atencao' in dados
        assert len(dados['pontos_atencao']) > 0

    def test_coletar_dados_aluno_sem_notas(self, turma_mock):
        """Deve lidar com aluno sem histórico de notas"""
        aluno = Mock()
        aluno.nome = "Fulano"
        aluno.matricula = "1111"
        aluno.calcular_media = Mock(return_value=0.0)

        type(aluno).desempenho = PropertyMock(return_value=[])

        relatorio = RelatorioIndividual(aluno, turma_mock)

        dados = relatorio.coletar_dados()

        assert dados['historico_notas'] == []
        assert dados['media_geral'] == 0.0

    def test_processar_dados_nao_muta_dados_originais(self, aluno_com_historico, turma_mock):
        """processar_dados() não deve modificar o dicionário de entrada"""
        relatorio = RelatorioIndividual(aluno_com_historico, turma_mock)

        dados_brutos = relatorio.coletar_dados()
        chaves_originais = set(dados_brutos.keys())

        relatorio.processar_dados(dados_brutos)

        # Chaves originais devem permanecer intactas
        assert set(dados_brutos.keys()) == chaves_originais
        # Chaves adicionadas pelo processamento não devem estar no original
        assert 'tendencia' not in dados_brutos
        assert 'pontos_fortes' not in dados_brutos
        assert 'pontos_atencao' not in dados_brutos
        assert 'grafico_ascii' not in dados_brutos

    
class TestRelatorioIndividualFormatarSaida:
    """Testes do método formatar_saida()"""

    @pytest.fixture
    def relatorio(self):
        """Fixture com instância de RelatorioIndividual usando mocks genéricos"""
        return RelatorioIndividual(Mock(), Mock())

    @pytest.fixture
    def dados_processados(self):
        """Fixture com dados processados contendo gráfico ASCII real"""
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
            'tendencia': 'crescente',
            'grafico_ascii': (
                "10 |██ ██ ██ ██ ██ \n"
                "   |            ██ \n"
                " 5 |██ ██ ██ ██ ██ \n"
                "   |            \n"
                " 1 |██ ██ ██ ██ ██ \n"
                "   +───────────────\n"
                "    A1 A2 A3 A4 A5 "
            ),
        }
    
    def test_formatar_saida_retorna_string(self, relatorio, dados_processados):
        """formatar_saida() deve retornar string"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_formatar_saida_inclui_cabecalho(self, relatorio, dados_processados):
        """Deve incluir cabeçalho com informações do aluno"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "Fulano de Tal" in resultado
        assert "12345" in resultado
        assert "ES002" in resultado
        assert "Matemática" in resultado

    def test_formatar_saida_inclui_estatistica(self, relatorio, dados_processados):
        """Deve incluir estatísticas do aluno"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "7.40" in resultado
        assert "5" in resultado or "cinco" in resultado.lower()

    def test_formatar_saida_inclui_historico(self, relatorio, dados_processados):
        """Deve incluir lista do histórico de notas"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "Prova 1" in resultado
        assert "Álgebra" in resultado
        assert "6.0" in resultado

    def test_formatar_saida_inclui_grafico(self, relatorio, dados_processados):
        """Deve incluir seção de evolução de notas com gráfico ASCII"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "EVOLUÇÃO DAS NOTAS" in resultado
        assert any(char in resultado for char in ['│', '─', '█', '*', '#', '|', '-'])

    def test_formatar_saida_inclui_analise_tendencia(self, relatorio, dados_processados):
        """Deve incluir análise de tendência"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert any(palavra in resultado.lower()
                   for palavra in ['crescente', 'melhor', 'progress', 'evolu', 'ascend'])
        
    def test_formatar_saida_inclui_pontos_fortes(self, relatorio, dados_processados):
        """Deve listar pontos fortes do aluno"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "pontos fortes" in resultado.lower() or "destaque" in resultado.lower()
        assert "Álgebra" in resultado

    def test_formatar_saida_inclui_pontos_fracos(self, relatorio, dados_processados):
        """Deve listar pontos que precisam de atenção"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "atenção" in resultado.lower() or "melhorar" in resultado.lower()

    def test_formatar_saida_status_ok_para_nota_aprovada(self, relatorio):
        """Notas >= 7.0 devem ter status [OK] no histórico"""
        dados = {
            'historico_notas': [
                {'valor': 8.5, 'avaliacao': 'Prova 1', 'topico': 'Álgebra', 'data': datetime(2026, 1, 10)},
            ],
        }
        resultado = relatorio.formatar_saida(dados)

        assert "[OK]" in resultado

    def test_formatar_saida_status_atencao_para_nota_reprovada(self, relatorio):
        """Notas < 7.0 devem ter status [!] no histórico"""
        dados = {
            'historico_notas': [
                {'valor': 4.0, 'avaliacao': 'Prova 1', 'topico': 'Cálculo', 'data': datetime(2026, 1, 10)},
            ],
        }
        resultado = relatorio.formatar_saida(dados)

        assert "[!]" in resultado

    def test_formatar_saida_valor_none_nao_lanca_excecao(self, relatorio):
        """Guard contra None em nota['valor'] não deve lançar TypeError"""
        dados = {
            'historico_notas': [
                {'valor': None, 'avaliacao': 'Prova 1', 'topico': 'Álgebra', 'data': datetime(2026, 1, 10)},
            ],
        }
        # Não deve lançar TypeError ao comparar None >= 7.0
        resultado = relatorio.formatar_saida(dados)
        assert isinstance(resultado, str)

    
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

    def test_processar_dados_tendencia_historico_unico_e_estavel(self, aluno_mock, turma_mock):
        """Histórico com apenas 1 nota deve resultar em tendência estável"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {
            'historico_notas': [
                {'valor': 9.0, 'data': datetime(2026, 1, 10)},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert dados_processados['tendencia'] == 'estavel'

    def test_processar_dados_tendencia_historico_vazio_e_estavel(self, aluno_mock, turma_mock):
        """Histórico vazio deve resultar em tendência estável"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {'historico_notas': []}

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert dados_processados['tendencia'] == 'estavel'

    def test_processar_dados_tendencia_divisao_simetrica_impar(self, aluno_mock, turma_mock):
        """Com 3 notas, a comparação deve ser simétrica (1ª nota vs 3ª nota) ignorando o centro"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        # 6.0 (inicio) vs 8.0 (fim) — diferença = +2.0 -> crescente
        dados_brutos = {
            'historico_notas': [
                {'valor': 6.0, 'data': datetime(2026, 1, 1)},
                {'valor': 1.0, 'data': datetime(2026, 1, 15)},  # centro ignorado
                {'valor': 8.0, 'data': datetime(2026, 2, 1)},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert dados_processados['tendencia'] == 'crescente'

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
        assert any(char in grafico for char in ['─', '█', '|'])

    def test_processar_dados_grafico_contem_rotulos_sequenciais(self, aluno_mock, turma_mock):
        """Gráfico ASCII deve usar rótulos sequenciais A1, A2, A3"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {
            'historico_notas': [
                {'valor': 7.0, 'avaliacao': 'Prova 1', 'data': datetime(2026, 1, 1)},
                {'valor': 8.0, 'avaliacao': 'Prova 2', 'data': datetime(2026, 2, 1)},
            ]
        }

        dados_processados = relatorio.processar_dados(dados_brutos)
        grafico = dados_processados['grafico_ascii']

        assert 'A1' in grafico
        assert 'A2' in grafico

    def test_processar_dados_grafico_vazio_sem_historico(self, aluno_mock, turma_mock):
        """Gráfico com histórico vazio deve retornar mensagem de fallback"""
        relatorio = RelatorioIndividual(aluno_mock, turma_mock)

        dados_brutos = {'historico_notas': []}

        dados_processados = relatorio.processar_dados(dados_brutos)

        assert "(sem avaliações registradas)" in dados_processados['grafico_ascii']


class TestRelatorioIndividualIntegracao:
    """Testes de integração end-to-end"""

    @pytest.fixture
    def aluno_completo(self):
        """Aluno com histórico completo para teste end-to-end via propriedade desempenho"""
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
            nota.data_registro = datetime(2025, 1 + i, 15)
            notas.append(nota)

        type(aluno).desempenho = PropertyMock(return_value=notas)

        return aluno
    
    @pytest.fixture
    def turma_completa(self):
        """Turma mock para testes de integração"""
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
        assert "8.20" in resultado

    def test_gerar_relatorio_inclui_historico_e_tendencia(self, aluno_completo, turma_completa):
        """Relatório gerado deve conter histórico de notas e tendência"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        resultado = relatorio.gerar()

        assert "HISTÓRICO COMPLETO DE AVALIAÇÕES" in resultado
        assert "Tendência:" in resultado
        assert any(t in resultado for t in ['CRESCENTE', 'ESTÁVEL', 'DECRESCENTE'])

    def test_gerar_relatorio_inclui_pontos_fortes_ou_atencao(self, aluno_completo, turma_completa):
        """Relatório gerado deve incluir seção de pontos fortes ou de atenção"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        resultado = relatorio.gerar()

        tem_pontos_fortes = "PONTOS FORTES" in resultado
        tem_pontos_atencao = "PONTOS QUE NECESSITAM DE ATENÇÃO" in resultado

        assert tem_pontos_fortes or tem_pontos_atencao

    def test_gerar_relatorio_inclui_grafico_ascii(self, aluno_completo, turma_completa):
        """Relatório gerado deve incluir seção de evolução com gráfico ASCII"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        resultado = relatorio.gerar()

        assert "EVOLUÇÃO DAS NOTAS" in resultado
        assert "█" in resultado

    def test_gerar_relatorio_turma_presente(self, aluno_completo, turma_completa):
        """Informações da turma devem aparecer no relatório gerado"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        resultado = relatorio.gerar()

        assert "ES002" in resultado
        assert "Matemática" in resultado
        assert "2025.1" in resultado

    def test_gerar_e_exportar_texto(self, aluno_completo, turma_completa):
        """Deve poder gerar e exportar como texto"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        conteudo = relatorio.gerar()
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.TEXTO)

        assert isinstance(resultado, bytes)
        assert "Glip Glarp".encode() in resultado

    def test_gerar_e_exportar_texto_conteudo_utf8(self, aluno_completo, turma_completa):
        """Exportação como texto deve conter conteúdo UTF-8 válido incluindo caracteres especiais"""
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        conteudo = relatorio.gerar()
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.TEXTO)

        # Deve ser decodificável como UTF-8 sem erros
        texto_decodificado = resultado.decode('utf-8')
        assert "Glip Glarp" in texto_decodificado
        assert "RELATÓRIO INDIVIDUAL" in texto_decodificado
        # Caractere especial do gráfico ASCII deve sobreviver ao encode/decode
        assert "█" in texto_decodificado

    def test_gerar_e_exportar_json(self, aluno_completo, turma_completa):
        """Deve poder gerar e exportar como JSON com metadados, serializando datetime corretamente"""
        import json
        relatorio = RelatorioIndividual(aluno_completo, turma_completa)

        conteudo = relatorio.gerar()
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.JSON)

        assert isinstance(resultado, bytes)
        dados_json = json.loads(resultado.decode('utf-8'))
        assert 'relatorio' in dados_json
        assert 'data_geracao' in dados_json
        # data_geracao deve ser string ISO 8601, não objeto datetime
        assert isinstance(dados_json['data_geracao'], str)
