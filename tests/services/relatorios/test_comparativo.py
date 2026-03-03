"""
Testes para RelatorioComparativo
"""

import copy
from unittest.mock import Mock
import pytest

from educalin.services.relatorios import (
    RelatorioComparativo,
    GeradorRelatorio,
)

# Fixtures

@pytest.fixture
def turma_mock_factory():
    """Factory de mocks de Turma com dados configuráveis."""
    def _criar(codigo: str, disciplina: str, semestre: str, medias: list[float]):
        turma = Mock()
        turma.codigo = codigo
        turma.disciplina = disciplina
        turma.semestre = semestre

        alunos = []
        for media in medias:
            aluno = Mock()
            aluno.calcular_media = Mock(return_value=media)
            alunos.append(aluno)

        turma.alunos = alunos
        turma.total_alunos = len(alunos)
        turma.obter_desempenho_geral = Mock(return_value={
            'media_geral': round(sum(medias) / len(medias), 2) if medias else 0.0,
            'total_alunos': len(medias),
            'alunos_com_dificuldade': sum(1 for m in medias if m < 7.0),
            'taxa_aprovacao': round(
                sum(1 for m in medias if m >= 7.0) / len(medias) * 100, 2
            ) if medias else 0.0,
        })
        return turma
    return _criar

@pytest.fixture
def duas_turmas(turma_mock_factory):
    """Fixture com duas turmas prontas para uso."""
    t1 = turma_mock_factory('ES006', 'POO', '2025.2', [8.0, 7.5, 6.0, 9.0])
    t2 = turma_mock_factory('ES007', 'POO', '2025.2', [5.0, 4.5, 6.5, 7.0])
    return [t1, t2]

@pytest.fixture
def relatorio(duas_turmas):
    """Fixture com RelatorioComparativo instanciado."""
    return RelatorioComparativo(duas_turmas)


class TestRelatorioComparativoEstrutura:
    """Testes de herança e estrutura da classe"""

    def test_herda_de_gerador_relatorio(self, relatorio):
        """Deve herdar de GeradorRelatorio"""
        assert isinstance(relatorio, GeradorRelatorio)

    def test_nao_sobrescreve_gerar(self):
        """Não deve ser possível sobrescrever gerar()"""
        assert 'gerar' not in RelatorioComparativo.__dict__

    def test_possui_atributo_turmas(self, relatorio):
        """Deve expor a lista de turma via atributo _turmas"""
        assert hasattr(relatorio, '_turmas')

    def test_implementa_coletar_dados(self, relatorio):
        """Deve implementar o método abstrato coletar_dados()"""
        assert callable(getattr(relatorio, 'coletar_dados', None))

    def test_implementa_formatar_saida(self, relatorio):
        """Deve implementar o método abstrato formatar_saida()"""
        assert callable(getattr(relatorio, 'formatar_saida', None))

    def test_implementa_processar_dados(self):
        """Deve sobrescrever o hook processar_dados()"""
        assert 'processar_dados' in RelatorioComparativo.__dict__


class TestRelatorioComparativoInicializacao:
    """Testes de inicialização e validação de entrada"""

    def test_inicializacao_com_lista_valida(self, duas_turmas):
        """Deve inicializar corretamente com lista de turmas válidas"""
        relatorio_local = RelatorioComparativo(duas_turmas)
        assert relatorio_local._turmas == duas_turmas

    def test_inicializacao_com_turma_unica(self, turma_mock_factory):
        """Deve aceitar lista com apenas uma turma"""
        turma = turma_mock_factory('ES001', 'Matemática', '2025.1', [7.0, 8.0])
        relatorio_local = RelatorioComparativo([turma])
        assert len(relatorio_local._turmas) == 1 

    def test_lista_vazia_lanca_erro(self):
        """Deve lançar ValueError se a lista de turmas estiver vazia"""
        with pytest.raises(ValueError, match="pelo menos uma turma"):
            RelatorioComparativo([])

    def test_lista_none_lanca_erro(self):
        """Deve lançar TypeError se turmas for None"""
        with pytest.raises(TypeError, match="turmas deve ser uma lista"):
            RelatorioComparativo(None)

    def test_item_sem_atributo_codigo_lanca_erro(self):
        """Deve lançar TypeError se algum item da lista não tiver atributo 'codigo'"""
        with pytest.raises(TypeError, match="todos os itens devem ser Turma"):
            RelatorioComparativo(["nao é turma"])

    def test_item_sem_obter_desempenho_geral_lanca_erro(self):
        """Deve lançar TypeError se algum item da lista não tiver obter_desempenho_geral"""
        turma_invalida = Mock()
        turma_invalida.codigo = 'ES001'
        turma_invalida.disciplina = 'Mat'
        turma_invalida.semestre = '2025.1'
        # obter_desempenho_geral deliberadamente ausente
        del turma_invalida.obter_desempenho_geral
        with pytest.raises(TypeError, match="todos os itens devem ser Turma"):
            RelatorioComparativo([turma_invalida])

    def test_turmas_armazenadas_como_copia(self, duas_turmas):
        """Deve armazenar cópia da lista para evitar mutação externa"""
        relatorio_local = RelatorioComparativo(duas_turmas)
        duas_turmas.append(Mock())
        assert len(relatorio_local._turmas) == 2


class TestRelatorioComparativoColetarDados:
    """Testes do método coletar_dados()"""

    def test_retorna_dicionario(self, relatorio):
        """Deve retornar um dicionário"""
        dados = relatorio.coletar_dados()
        assert isinstance(dados, dict)

    def test_contem_total_turmas(self, relatorio):
        """Deve incluir o total de turmas analisadas"""
        dados = relatorio.coletar_dados()

        assert 'total_turmas' in dados
        assert dados['total_turmas'] == 2

    def test_contem_dados_por_turma(self, relatorio):
        """Deve incluir lista com dados individuais de cada turma"""
        dados = relatorio.coletar_dados()

        assert 'turmas' in dados
        assert len(dados['turmas']) == 2

    def test_dados_por_turma_contem_campos_obrigatorios(self, relatorio):
        """Cada entrada de turma deve ter os campos esperados"""
        dados = relatorio.coletar_dados()
        campos = {'codigo', 'disciplina', 'semestre', 'media_geral',
                  'total_alunos', 'alunos_com_dificuldade', 'taxa_aprovacao'}

        for turma_dados in dados['turmas']:
            assert campos.issubset(turma_dados.keys())

    def test_media_geral_global_calculada(self, relatorio):
        """Deve calcular a média geral entre todas as turmas"""
        dados = relatorio.coletar_dados()

        assert 'media_geral_global' in dados
        assert isinstance(dados['media_geral_global'], float)

    def test_media_geral_global_valor_correto(self, turma_mock_factory):
        """Média global deve ser a média das médias das turmas"""
        t1 = turma_mock_factory('ES001', 'Matemática', '2025.2', [8.0, 8.0])
        t2 = turma_mock_factory('ES002', 'Matemática', '2025.2', [6.0, 6.0])
        relatorio_local = RelatorioComparativo([t1, t2])

        dados = relatorio_local.coletar_dados()

        assert dados['media_geral_global'] == pytest.approx(7.0, abs=0.01)

    def test_contem_semestre(self, relatorio):
        """Deve incluir o semestre de referência"""
        dados = relatorio.coletar_dados()

        assert 'semestre' in dados

    def test_semestre_unico_sem_separador(self, turma_mock_factory):
        """Com turmas do mesmo semestre, exibe apenas um semestre sem vírgula"""
        t1 = turma_mock_factory('ES001', 'Mat', '2025.1', [7.0])
        t2 = turma_mock_factory('ES002', 'Mat', '2025.1', [8.0])
        relatorio_local = RelatorioComparativo([t1, t2])

        dados = relatorio_local.coletar_dados()

        assert dados['semestre'] == '2025.1'

    def test_semestre_multiplos_concatenados(self, turma_mock_factory):
        """Com turmas de semestres distintos, exibe todos separados por vírgula"""
        t1 = turma_mock_factory('ES001', 'Mat', '2025.1', [7.0])
        t2 = turma_mock_factory('ES002', 'Mat', '2025.2', [8.0])
        relatorio_local = RelatorioComparativo([t1, t2])

        dados = relatorio_local.coletar_dados()

        assert '2025.1' in dados['semestre']
        assert '2025.2' in dados['semestre']
        assert ',' in dados['semestre']

    def test_turmas_ordenadas_por_media_decrescente(self, turma_mock_factory):
        """As turmas na lista devem estar ordenadas por média decrescente"""
        t1 = turma_mock_factory('ES001', 'Mat', '2025.1', [5.0, 5.0])
        t2 = turma_mock_factory('ES002', 'Mat', '2025.1', [9.0, 9.0])

        relatorio_local = RelatorioComparativo([t1, t2])
        dados = relatorio_local.coletar_dados()

        medias = [t['media_geral'] for t in dados['turmas']]
        assert medias == sorted(medias, reverse=True)


class TestRelatorioComparativoProcessarDados:
    """Testes do hook processar_dados()"""

    @pytest.fixture
    def dados_brutos(self, relatorio):
        """Fixture que retorna os dados brutos coletados para teste"""
        return relatorio.coletar_dados()

    def test_retorna_dicionario(self, relatorio, dados_brutos):
        """Deve retornar um dicionário"""
        resultado = relatorio.processar_dados(dados_brutos)

        assert isinstance(resultado, dict)

    def test_nao_muta_dados_originais(self, relatorio, dados_brutos):
        """Não deve modificar o dicionário de entrada"""
        copia = copy.deepcopy(dados_brutos)
        relatorio.processar_dados(dados_brutos)

        assert dados_brutos == copia

    def test_adiciona_ranking(self, relatorio, dados_brutos):
        """Deve adicionar lista 'ranking' ao resultado"""
        resultado = relatorio.processar_dados(dados_brutos)

        assert 'ranking' in resultado

    def test_ranking_ordenado_por_media(self, relatorio, dados_brutos):
        """O ranking deve estar ordenado por média decrescente"""
        resultado = relatorio.processar_dados(dados_brutos)
        medias = [t['media_geral'] for t in resultado['ranking']]

        assert medias == sorted(medias, reverse=True)

    def test_ranking_contem_posicao(self, relatorio, dados_brutos):
        """Cada item do ranking deve ter o campo 'posicao'"""
        resultado = relatorio.processar_dados(dados_brutos)

        for i, item in enumerate(resultado['ranking'], start=1):
            assert item['posicao'] == i

    def test_adiciona_melhor_turma(self, relatorio, dados_brutos):
        """Deve identificar a turma com maior média"""
        resultado = relatorio.processar_dados(dados_brutos)

        assert 'melhor_turma' in resultado
        assert resultado['melhor_turma'] == resultado['ranking'][0]['codigo']

    def test_adiciona_turma_mais_critica(self, relatorio, dados_brutos):
        """Deve identificar a turma com maior número de alunos com dificuldade"""
        resultado = relatorio.processar_dados(dados_brutos)

        assert 'turma_mais_critica' in resultado

    def test_turma_mais_critica_valor_correto(self, turma_mock_factory):
        """turma_mais_critica deve ser a turma com mais alunos com dificuldade"""
        # ES001: 0 com dificuldade  |  ES002: 3 com dificuldade
        t1 = turma_mock_factory('ES001', 'Mat', '2025.1', [8.0, 8.0, 8.0])
        t2 = turma_mock_factory('ES002', 'Mat', '2025.1', [4.0, 4.0, 4.0])
        relatorio_local = RelatorioComparativo([t1, t2])

        resultado = relatorio_local.processar_dados(relatorio_local.coletar_dados())

        assert resultado['turma_mais_critica'] == 'ES002'

    def test_turma_mais_critica_empate_desempata_pela_menor_media(self, turma_mock_factory):
        """Em caso de empate em alunos_com_dificuldade, vence a turma de menor média"""
        # Ambas têm 2 alunos com dificuldade (< 7.0);
        # ES001: médias [4.0, 4.0, 8.0, 8.0] → média = 6.0
        # ES002: médias [3.0, 3.0, 7.0, 9.0] → média = 5.5  ← menor, deve vencer
        t1 = turma_mock_factory('ES001', 'Mat', '2025.1', [4.0, 4.0, 8.0, 8.0])
        t2 = turma_mock_factory('ES002', 'Mat', '2025.1', [3.0, 3.0, 7.0, 9.0])
        relatorio_local = RelatorioComparativo([t1, t2])

        resultado = relatorio_local.processar_dados(relatorio_local.coletar_dados())

        assert resultado['turma_mais_critica'] == 'ES002'

    def test_adicionar_grafico_comparativo(self, relatorio, dados_brutos):
        """Deve gerar o gráfico ASCII comparativo"""
        resultado = relatorio.processar_dados(dados_brutos)

        assert 'grafico_ascii' in resultado
        assert isinstance(resultado['grafico_ascii'], str)


class TestRelatorioComparativoFormatarSaida:
    """Testes de formatação do relatório"""

    @pytest.fixture
    def dados_processados(self, relatorio):
        """Fixture com dados já processados pelo hook"""
        brutos = relatorio.coletar_dados()
        return relatorio.processar_dados(brutos)

    def test_retorna_string(self, relatorio, dados_processados):
        """Deve retornar uma string"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert isinstance(resultado, str)

    def test_contem_titulo(self, relatorio, dados_processados):
        """Deve conter o título do relatório"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "RELATÓRIO COMPARATIVO" in resultado

    def test_contem_codigo_de_cada_turma(self, relatorio, dados_processados):
        """Deve conter o código de cada turma analisada"""
        resultado = relatorio.formatar_saida(dados_processados)

        for turma_dados in dados_processados['ranking']:
            assert turma_dados['codigo'] in resultado

    def test_contem_secao_ranking(self, relatorio, dados_processados):
        """Deve conter a seção de ranking"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "RANKING" in resultado

    def test_contem_secao_grafico(self, relatorio, dados_processados):
        """Deve conter a seção do gráfico comparativo"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "GRÁFICO COMPARATIVO" in resultado

    def test_contem_melhor_turma(self, relatorio, dados_processados):
        """Deve destacar a melhor turma"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert dados_processados['melhor_turma'] in resultado

    def test_contem_rodape_com_data(self, relatorio, dados_processados):
        """Deve conter rodapé com data de geração"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "Relatório gerado em" in resultado

    def test_contem_media_global(self, relatorio, dados_processados):
        """Deve exibir a média geral global"""
        resultado = relatorio.formatar_saida(dados_processados)

        assert "Média Global" in resultado


class TestRelatorioComparativoIntegracao:
    """Testes de integração com o template method"""

    def test_gerar_retorna_string(self, relatorio):
        """gerar() deve retornar uma string não vazia"""
        resultado = relatorio.gerar()

        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_gerar_contem_codigos_das_turmas(self, relatorio, duas_turmas):
        """O relatório final deve conter os códigos das turmas"""
        resultado = relatorio.gerar()

        for turma in duas_turmas:
            assert turma.codigo in resultado

    def test_gerar_funciona_com_turma_sem_alunos(self, turma_mock_factory):
        """Turma sem alunos ainda deve gerar relatório sem lançar exceção (média 0.0)"""
        turma_vazia = turma_mock_factory('ES001', 'Mat', '2025.2', [])
        turma_vazia.obter_desempenho_geral = Mock(return_value={
            'media_geral': 0.0,
            'total_alunos': 0,
            'alunos_com_dificuldade': 0,
            'taxa_aprovacao': 0.0,
        })

        relatorio_local = RelatorioComparativo([turma_vazia])
        resultado = relatorio_local.gerar()

        assert isinstance(resultado, str)

    def test_gerar_popula_metadados(self, relatorio):
        """Após gerar(), obter_metadados() deve retornar data_geracao e total_dados > 0"""
        relatorio.gerar()
        metadados = relatorio.obter_metadados()

        assert 'data_geracao' in metadados
        assert 'status' not in metadados  # chave 'status' só existe antes de gerar()
        assert metadados.get('total_dados', 0) > 0


class TestRelatorioComparativoMetodosAuxiliares:
    """Testes unitários dos métodos auxiliares privados"""

    def test_identificar_turma_critica_lista_vazia(self, relatorio):
        """Deve retornar 'N/A' para lista vazia"""
        assert relatorio._identificar_turma_critica([]) == 'N/A'

    def test_identificar_turma_critica_turma_unica(self, relatorio):
        """Com apenas uma turma, deve retornar o código dessa turma"""
        turmas = [{'codigo': 'T1', 'alunos_com_dificuldade': 2, 'media_geral': 5.0}]
        assert relatorio._identificar_turma_critica(turmas) == 'T1'

    def test_gerar_grafico_ascii_lista_vazia(self, relatorio):
        """Deve retornar mensagem informativa para lista vazia"""
        resultado = relatorio._gerar_grafico_ascii([])
        assert resultado == "  (sem turmas para comparar)"

    def test_gerar_grafico_ascii_contem_codigo_e_media(self, relatorio):
        """Cada linha do gráfico deve conter o código e a média da turma"""
        turmas = [
            {'codigo': 'ES001', 'media_geral': 8.0},
            {'codigo': 'ES002', 'media_geral': 5.0},
        ]
        resultado = relatorio._gerar_grafico_ascii(turmas)

        assert 'ES001' in resultado
        assert 'ES002' in resultado
        assert '8.00' in resultado
        assert '5.00' in resultado

    def test_gerar_grafico_ascii_trunca_codigo_longo(self, relatorio):
        """Código com mais de 8 chars deve ser truncado para preservar alinhamento"""
        turmas = [{'codigo': 'CODIGO_MUITO_LONGO', 'media_geral': 7.0}]
        resultado = relatorio._gerar_grafico_ascii(turmas)
        # O código truncado (8 chars) deve estar presente, não o completo
        assert 'CODIGO_M' in resultado
        assert 'CODIGO_MUITO_LONGO' not in resultado

    def test_gerar_grafico_ascii_media_acima_de_10_nao_ultrapassa_largura(self, relatorio):
        """Média > 10.0 não deve gerar barra maior que MAX_LARGURA (clamping)"""
        MAX_LARGURA = 40
        turmas = [{'codigo': 'ES001', 'media_geral': 12.0}]
        resultado = relatorio._gerar_grafico_ascii(turmas)
        # A barra nunca deve ter mais de MAX_LARGURA blocos
        linha = resultado.split('\n')[0]
        barra = linha.split('|')[1].strip().split()[0]
        assert len(barra) <= MAX_LARGURA
