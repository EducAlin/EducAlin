"""
Testes para a estratégia AnaliseNotasBaixas.
"""
import pytest
from educalin.services.analisenotasbaixas import AnaliseNotasBaixas
from educalin.domain.aluno import Aluno


class TestAnaliseNotasBaixas:
    """Testes para a estratégia AnaliseNotasBaixas."""
    
    @pytest.fixture
    def aluno(self):
        """Fixture que cria um aluno para os testes."""
        return Aluno(nome="João Silva", email="joao@email.com", senha="senha123", matricula="12345")
    
    @pytest.fixture
    def estrategia_padrao(self):
        """Fixture que cria uma estratégia com limite padrão (60%)."""
        return AnaliseNotasBaixas()
    
    @pytest.fixture
    def estrategia_customizada(self):
        """Fixture que cria uma estratégia com limite customizado (70%)."""
        return AnaliseNotasBaixas(limite_nota=70.0)
    
    # Testes de Inicialização
    
    def test_inicializacao_padrao(self):
        """Testa inicialização com limite padrão de 60%."""
        estrategia = AnaliseNotasBaixas()
        assert estrategia.limite_nota == 60.0
        assert estrategia.identificar_dificuldades() == []
    
    def test_inicializacao_customizada(self):
        """Testa inicialização com limite customizado."""
        estrategia = AnaliseNotasBaixas(limite_nota=75.0)
        assert estrategia.limite_nota == 75.0
    
    def test_inicializacao_com_limite_invalido_tipo(self):
        """Testa que limite de nota deve ser numérico."""
        with pytest.raises(TypeError, match="O limite de nota deve ser um número"):
            AnaliseNotasBaixas(limite_nota="60")
    
    def test_inicializacao_com_limite_negativo(self):
        """Testa que limite de nota não pode ser negativo."""
        with pytest.raises(ValueError, match="O limite de nota deve estar entre 0 e 100"):
            AnaliseNotasBaixas(limite_nota=-10)
    
    def test_inicializacao_com_limite_acima_100(self):
        """Testa que limite de nota não pode ser maior que 100."""
        with pytest.raises(ValueError, match="O limite de nota deve estar entre 0 e 100"):
            AnaliseNotasBaixas(limite_nota=150)
    
    # Testes do Property limite_nota
    
    def test_getter_limite_nota(self, estrategia_padrao):
        """Testa o getter do atributo limite_nota."""
        assert estrategia_padrao.limite_nota == 60.0
    
    def test_setter_limite_nota_valido(self, estrategia_padrao):
        """Testa o setter com valor válido."""
        estrategia_padrao.limite_nota = 80.0
        assert estrategia_padrao.limite_nota == 80.0
    
    def test_setter_limite_nota_invalido_tipo(self, estrategia_padrao):
        """Testa que setter valida o tipo."""
        with pytest.raises(TypeError):
            estrategia_padrao.limite_nota = "70"
    
    def test_setter_limite_nota_invalido_valor(self, estrategia_padrao):
        """Testa que setter valida o valor."""
        with pytest.raises(ValueError):
            estrategia_padrao.limite_nota = 200
    
    # Testes do Método analisar() - Casos Normais
    
    def test_analisar_com_todas_notas_acima_limite(self, estrategia_padrao, aluno):
        """Testa análise quando todas as notas estão acima do limite."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 7.5, "valor_maximo": 10.0, "topico": "Português"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "História"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['aluno_nome'] == "João Silva"
        assert resultado['total_avaliacoes'] == 3
        assert resultado['notas_baixas'] == 0
        assert resultado['percentual_dificuldade'] == 0.0
        assert resultado['detalhes'] == []
    
    def test_analisar_com_todas_notas_abaixo_limite(self, estrategia_padrao, aluno):
        """Testa análise quando todas as notas estão abaixo do limite."""
        historico = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 3.5, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Química"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['aluno_nome'] == "João Silva"
        assert resultado['total_avaliacoes'] == 3
        assert resultado['notas_baixas'] == 3
        assert resultado['percentual_dificuldade'] == 100.0
        assert len(resultado['detalhes']) == 3
    
    def test_analisar_com_notas_mistas(self, estrategia_padrao, aluno):
        """Testa análise com notas acima e abaixo do limite."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Geografia"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 5.5, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "História"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['total_avaliacoes'] == 4
        assert resultado['notas_baixas'] == 2
        assert resultado['percentual_dificuldade'] == 50.0
        assert len(resultado['detalhes']) == 2
    
    def test_analisar_identifica_topicos_corretos(self, estrategia_padrao, aluno):
        """Testa que os tópicos corretos são identificados."""
        historico = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Geometria"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert len(resultado['detalhes']) == 1
        assert resultado['detalhes'][0]['topico'] == "Álgebra"
        assert resultado['detalhes'][0]['nota'] == 4.0
        assert resultado['detalhes'][0]['percentual'] == 40.0
    
    def test_analisar_com_valores_maximos_diferentes(self, estrategia_padrao, aluno):
        """Testa análise com valores máximos diferentes."""
        historico = [
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Prova 1"},  # 50%
            {"nota": 10.0, "valor_maximo": 20.0, "topico": "Prova 2"}, # 50%
            {"nota": 3.0, "valor_maximo": 5.0, "topico": "Prova 3"}    # 60%
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Apenas Prova 1 e Prova 2 têm menos de 60%
        assert resultado['notas_baixas'] == 2
        assert resultado['detalhes'][0]['topico'] == "Prova 1"
        assert resultado['detalhes'][1]['topico'] == "Prova 2"
    
    def test_analisar_com_limite_customizado(self, estrategia_customizada, aluno):
        """Testa análise com limite de 70%."""
        historico = [
            {"nota": 6.5, "valor_maximo": 10.0, "topico": "Teste 1"},  # 65%
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Teste 2"}   # 80%
        ]
        
        resultado = estrategia_customizada.analisar(aluno, historico)
        
        # Com limite de 70%, apenas Teste 1 (65%) está abaixo
        assert resultado['notas_baixas'] == 1
        assert resultado['detalhes'][0]['topico'] == "Teste 1"
    
    def test_analisar_calcula_percentuais_corretamente(self, estrategia_padrao, aluno):
        """Testa que os percentuais são calculados e arredondados corretamente."""
        historico = [
            {"nota": 5.5, "valor_maximo": 10.0, "topico": "Teste"}  # 55%
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['detalhes'][0]['percentual'] == 55.0
        assert resultado['percentual_dificuldade'] == 100.0
    
    # Testes do Método analisar() - Casos Extremos
    
    def test_analisar_com_historico_vazio(self, estrategia_padrao, aluno):
        """Testa análise com histórico vazio."""
        resultado = estrategia_padrao.analisar(aluno, [])
        
        assert resultado['total_avaliacoes'] == 0
        assert resultado['notas_baixas'] == 0
        assert resultado['percentual_dificuldade'] == 0.0
        assert resultado['detalhes'] == []
    
    def test_analisar_com_nota_zero(self, estrategia_padrao, aluno):
        """Testa análise com nota zero."""
        historico = [
            {"nota": 0.0, "valor_maximo": 10.0, "topico": "Prova"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['notas_baixas'] == 1
        assert resultado['detalhes'][0]['percentual'] == 0.0
    
    def test_analisar_com_nota_maxima(self, estrategia_padrao, aluno):
        """Testa análise com nota máxima."""
        historico = [
            {"nota": 10.0, "valor_maximo": 10.0, "topico": "Prova"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['notas_baixas'] == 0
    
    def test_analisar_com_nota_no_limite_exato(self, estrategia_padrao, aluno):
        """Testa análise com nota exatamente no limite."""
        historico = [
            {"nota": 6.0, "valor_maximo": 10.0, "topico": "Prova"}  # Exatamente 60%
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Nota no limite não deve ser considerada baixa (< 60%, não <=)
        assert resultado['notas_baixas'] == 0
    
    def test_analisar_com_topico_nao_especificado(self, estrategia_padrao, aluno):
        """Testa análise quando tópico não é fornecido."""
        historico = [
            {"nota": 4.0, "valor_maximo": 10.0}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['notas_baixas'] == 1
        assert resultado['detalhes'][0]['topico'] == "Não especificado"
    
    def test_analisar_com_valor_maximo_zero(self, estrategia_padrao, aluno):
        """Testa análise quando valor máximo é zero (edge case)."""
        historico = [
            {"nota": 5.0, "valor_maximo": 0, "topico": "Teste"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Com valor_maximo = 0, percentual deve ser 0
        assert resultado['notas_baixas'] == 1
        assert resultado['detalhes'][0]['percentual'] == 0.0
    
    def test_analisar_com_limite_zero(self, aluno):
        """Testa análise com limite de 0% (todas as notas devem passar)."""
        estrategia = AnaliseNotasBaixas(limite_nota=0.0)
        historico = [
            {"nota": 0.0, "valor_maximo": 10.0, "topico": "Teste"}
        ]
        
        resultado = estrategia.analisar(aluno, historico)
        
        # Com limite 0%, mesmo nota 0 não é "menor que 0%"
        assert resultado['notas_baixas'] == 0
    
    def test_analisar_com_limite_100(self, aluno):
        """Testa análise com limite de 100% (todas as notas devem falhar)."""
        estrategia = AnaliseNotasBaixas(limite_nota=100.0)
        historico = [
            {"nota": 9.9, "valor_maximo": 10.0, "topico": "Teste"}
        ]
        
        resultado = estrategia.analisar(aluno, historico)
        
        # Com limite 100%, até 99% é considerado baixo
        assert resultado['notas_baixas'] == 1
    
    # Testes do Método identificar_dificuldades()
    
    def test_identificar_dificuldades_apos_analisar(self, estrategia_padrao, aluno):
        """Testa identificação de dificuldades após análise."""
        historico = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Cálculo"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Geometria"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades = estrategia_padrao.identificar_dificuldades()
        
        assert len(dificuldades) == 2
        assert "Álgebra" in dificuldades
        assert "Cálculo" in dificuldades
        assert "Geometria" not in dificuldades
    
    def test_identificar_dificuldades_sem_analisar(self, estrategia_padrao):
        """Testa identificação antes de executar análise."""
        dificuldades = estrategia_padrao.identificar_dificuldades()
        assert dificuldades == []
    
    def test_identificar_dificuldades_retorna_copia(self, estrategia_padrao, aluno):
        """Testa que o método retorna uma cópia da lista."""
        historico = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Matemática"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades1 = estrategia_padrao.identificar_dificuldades()
        dificuldades2 = estrategia_padrao.identificar_dificuldades()
        
        # Modificar uma lista não deve afetar a outra
        dificuldades1.append("Teste")
        assert len(dificuldades2) == 1
        assert "Teste" not in dificuldades2
    
    def test_identificar_dificuldades_atualiza_apos_nova_analise(self, estrategia_padrao, aluno):
        """Testa que dificuldades são atualizadas em nova análise."""
        historico1 = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Matemática"}
        ]
        
        estrategia_padrao.analisar(aluno, historico1)
        dificuldades1 = estrategia_padrao.identificar_dificuldades()
        
        assert len(dificuldades1) == 1
        assert "Matemática" in dificuldades1
        
        # Nova análise com histórico diferente
        historico2 = [
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Física"}
        ]
        
        estrategia_padrao.analisar(aluno, historico2)
        dificuldades2 = estrategia_padrao.identificar_dificuldades()
        
        # Dificuldades devem ser substituídas, não acumuladas
        assert len(dificuldades2) == 1
        assert "Física" in dificuldades2
        assert "Matemática" not in dificuldades2
    
    def test_identificar_dificuldades_sem_dificuldades(self, estrategia_padrao, aluno):
        """Testa identificação quando não há dificuldades."""
        historico = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Matemática"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades = estrategia_padrao.identificar_dificuldades()
        
        assert dificuldades == []
    
    # Testes de Integração
    
    def test_fluxo_completo_analise(self, estrategia_padrao, aluno):
        """Testa o fluxo completo de análise."""
        historico = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Português"},
            {"nota": 5.5, "valor_maximo": 10.0, "topico": "Ciências"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "História"}
        ]
        
        # Realiza a análise
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Verifica o resultado da análise
        assert resultado['aluno_nome'] == "João Silva"
        assert resultado['total_avaliacoes'] == 4
        assert resultado['notas_baixas'] == 2  # Matemática (40%) e Ciências (55%)
        assert resultado['percentual_dificuldade'] == 50.0
        
        # Verifica os detalhes
        topicos_baixos = [d['topico'] for d in resultado['detalhes']]
        assert "Matemática" in topicos_baixos
        assert "Ciências" in topicos_baixos
        
        # Verifica as dificuldades identificadas
        dificuldades = estrategia_padrao.identificar_dificuldades()
        assert len(dificuldades) == 2
        assert "Matemática" in dificuldades
        assert "Ciências" in dificuldades
    
    def test_multiplas_analises_sequenciais(self, estrategia_padrao, aluno):
        """Testa múltiplas análises sequenciais com o mesmo objeto."""
        # Primeira análise
        historico1 = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Teste 1"}
        ]
        resultado1 = estrategia_padrao.analisar(aluno, historico1)
        assert resultado1['notas_baixas'] == 1
        
        # Segunda análise
        historico2 = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Teste 2"}
        ]
        resultado2 = estrategia_padrao.analisar(aluno, historico2)
        assert resultado2['notas_baixas'] == 0
        
        # Verifica que dificuldades foram limpas
        dificuldades = estrategia_padrao.identificar_dificuldades()
        assert len(dificuldades) == 0
