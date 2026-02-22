"""
Testes para a estratégia AnaliseRegressao.
"""
import pytest
from educalin.services.analiseregressao import AnaliseRegressao
from educalin.domain.aluno import Aluno


class TestAnaliseRegressao:
    """Testes para a estratégia AnaliseRegressao."""
    
    @pytest.fixture
    def aluno(self):
        """Fixture que cria um aluno para os testes."""
        return Aluno(nome="Carlos Silva", email="carlos@email.com", senha="senha123", matricula="12345")
    
    @pytest.fixture
    def estrategia_padrao(self):
        """Fixture que cria uma estratégia com configuração padrão."""
        return AnaliseRegressao()
    
    @pytest.fixture
    def estrategia_customizada(self):
        """Fixture que cria uma estratégia com configuração customizada."""
        return AnaliseRegressao(min_avaliacoes=4, limite_regressao=-2.0)
    
    # Testes de Inicialização
    
    def test_inicializacao_padrao(self):
        """Testa inicialização com valores padrão."""
        estrategia = AnaliseRegressao()
        assert estrategia.min_avaliacoes == 3
        assert estrategia.limite_regressao == -1.0
        assert estrategia.identificar_dificuldades() == []
    
    def test_inicializacao_customizada(self):
        """Testa inicialização com valores customizados."""
        estrategia = AnaliseRegressao(min_avaliacoes=5, limite_regressao=-3.0)
        assert estrategia.min_avaliacoes == 5
        assert estrategia.limite_regressao == -3.0
    
    def test_inicializacao_min_avaliacoes_tipo_invalido(self):
        """Testa que min_avaliacoes deve ser inteiro."""
        with pytest.raises(TypeError, match="O número mínimo de avaliações deve ser um inteiro"):
            AnaliseRegressao(min_avaliacoes=3.5)
    
    def test_inicializacao_min_avaliacoes_menor_que_tres(self):
        """Testa que min_avaliacoes deve ser pelo menos 3."""
        with pytest.raises(ValueError, match="O número mínimo de avaliações deve ser pelo menos 3"):
            AnaliseRegressao(min_avaliacoes=2)
    
    def test_inicializacao_limite_regressao_tipo_invalido(self):
        """Testa que limite_regressao deve ser numérico."""
        with pytest.raises(TypeError, match="O limite de regressão deve ser um número"):
            AnaliseRegressao(limite_regressao="valor")
    
    # Testes dos Properties
    
    def test_getter_min_avaliacoes(self, estrategia_padrao):
        """Testa o getter do atributo min_avaliacoes."""
        assert estrategia_padrao.min_avaliacoes == 3
    
    def test_setter_min_avaliacoes_valido(self, estrategia_padrao):
        """Testa o setter com valor válido."""
        estrategia_padrao.min_avaliacoes = 5
        assert estrategia_padrao.min_avaliacoes == 5
    
    def test_setter_min_avaliacoes_tipo_invalido(self, estrategia_padrao):
        """Testa que setter valida o tipo."""
        with pytest.raises(TypeError, match="O número mínimo de avaliações deve ser um inteiro"):
            estrategia_padrao.min_avaliacoes = 4.5
    
    def test_setter_min_avaliacoes_valor_invalido(self, estrategia_padrao):
        """Testa que setter valida o valor mínimo."""
        with pytest.raises(ValueError, match="O número mínimo de avaliações deve ser pelo menos 3"):
            estrategia_padrao.min_avaliacoes = 2
    
    def test_getter_limite_regressao(self, estrategia_padrao):
        """Testa o getter do atributo limite_regressao."""
        assert estrategia_padrao.limite_regressao == -1.0
    
    def test_setter_limite_regressao_valido(self, estrategia_padrao):
        """Testa o setter com valor válido."""
        estrategia_padrao.limite_regressao = -2.5
        assert estrategia_padrao.limite_regressao == -2.5
    
    def test_setter_limite_regressao_tipo_invalido(self, estrategia_padrao):
        """Testa que setter valida o tipo."""
        with pytest.raises(TypeError, match="O limite de regressão deve ser um número"):
            estrategia_padrao.limite_regressao = "valor"
    
    # Testes do método calcular_tendencia
    
    def test_calcular_tendencia_regressao_linear(self, estrategia_padrao):
        """Testa cálculo de tendência com declínio linear."""
        valores = [90.0, 80.0, 70.0, 60.0]
        slope, intercept = estrategia_padrao.calcular_tendencia(valores)
        
        # Slope deve ser negativo (declínio de ~10% por avaliação)
        assert slope < 0
        assert abs(slope - (-10.0)) < 0.1  # Aproximadamente -10
        assert intercept > 0
    
    def test_calcular_tendencia_melhoria_linear(self, estrategia_padrao):
        """Testa cálculo de tendência com melhoria linear."""
        valores = [60.0, 70.0, 80.0, 90.0]
        slope, intercept = estrategia_padrao.calcular_tendencia(valores)
        
        # Slope deve ser positivo (melhoria de ~10% por avaliação)
        assert slope > 0
        assert abs(slope - 10.0) < 0.1  # Aproximadamente +10
    
    def test_calcular_tendencia_estavel(self, estrategia_padrao):
        """Testa cálculo de tendência com desempenho estável."""
        valores = [75.0, 75.0, 75.0, 75.0]
        slope, intercept = estrategia_padrao.calcular_tendencia(valores)
        
        # Slope deve ser próximo de zero (sem mudança significativa)
        assert abs(slope) < 0.1
        assert abs(intercept - 75.0) < 0.1
    
    def test_calcular_tendencia_minimo_valores(self, estrategia_padrao):
        """Testa com exatamente 3 valores (mínimo necessário)."""
        valores = [90.0, 70.0, 50.0]
        slope, intercept = estrategia_padrao.calcular_tendencia(valores)
        
        # Deve calcular sem erros
        assert slope < 0  
        assert intercept > 0
    
    def test_calcular_tendencia_valores_insuficientes(self, estrategia_padrao):
        """Testa erro com menos de 3 valores."""
        valores = [90.0, 80.0]
        
        with pytest.raises(ValueError, match="São necessários pelo menos 3 valores"):
            estrategia_padrao.calcular_tendencia(valores)
    
    def test_calcular_tendencia_lista_vazia(self, estrategia_padrao):
        """Testa erro com lista vazia."""
        valores = []
        
        with pytest.raises(ValueError, match="São necessários pelo menos 3 valores"):
            estrategia_padrao.calcular_tendencia(valores)
    
    # Testes do método analisar
    
    def test_analisar_detecta_regressao(self, aluno, estrategia_padrao):
        """Testa que o método analisar detecta regressão significativa."""
        historico = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Cálculo"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Cálculo"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Cálculo"},
            {"nota": 3.0, "valor_maximo": 10.0, "topico": "Cálculo"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['aluno_nome'] == "Carlos Silva"
        assert resultado['total_avaliacoes'] == 4
        assert resultado['topicos_analisados'] == 1
        assert resultado['topicos_com_regressao'] == 1
        
        # Verifica detalhes
        detalhes = resultado['detalhes'][0]
        assert detalhes['topico'] == "Cálculo"
        assert detalhes['slope'] < 0
        assert detalhes['tem_regressao'] is True
        assert detalhes['media_final'] < detalhes['media_inicial']
    
    def test_analisar_nao_detecta_melhoria(self, aluno, estrategia_padrao):
        """Testa que melhoria não é detectada como regressão."""
        historico = [
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Física"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['topicos_com_regressao'] == 0
        
        detalhes = resultado['detalhes'][0]
        assert detalhes['slope'] > 0
        assert detalhes['tem_regressao'] is False
        assert detalhes['media_final'] > detalhes['media_inicial']
    
    def test_analisar_desempenho_estavel(self, aluno, estrategia_padrao):
        """Testa análise com desempenho estável."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Química"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Química"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Química"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['topicos_com_regressao'] == 0
        
        detalhes = resultado['detalhes'][0]
        assert abs(detalhes['slope']) < 0.5  # Próximo de zero
        assert detalhes['tem_regressao'] is False
    
    def test_analisar_multiplos_topicos(self, aluno, estrategia_padrao):
        """Testa análise com múltiplos tópicos."""
        historico = [
            # Álgebra - regressão
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            # Geometria - melhoria
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Geometria"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Geometria"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Geometria"},
            # Trigonometria - estável
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Trigonometria"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Trigonometria"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Trigonometria"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['topicos_analisados'] == 3
        assert resultado['topicos_com_regressao'] == 1
        
        # Verifica que apenas Álgebra tem regressão
        topicos_regressao = [
            d['topico'] for d in resultado['detalhes'] if d.get('tem_regressao')
        ]
        assert "Álgebra" in topicos_regressao
        assert "Geometria" not in topicos_regressao
        assert "Trigonometria" not in topicos_regressao
    
    def test_analisar_avaliacoes_insuficientes(self, aluno, estrategia_padrao):
        """Testa comportamento com avaliações insuficientes por tópico."""
        historico = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "História"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "História"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Não deve calcular tendência
        assert resultado['topicos_com_regressao'] == 0
        
        detalhes = resultado['detalhes'][0]
        assert detalhes['slope'] is None
        assert detalhes['tem_regressao'] is False
        assert 'nota' in detalhes  
    
    def test_analisar_historico_vazio(self, aluno, estrategia_padrao):
        """Testa análise com histórico vazio."""
        historico = []
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['total_avaliacoes'] == 0
        assert resultado['topicos_analisados'] == 0
        assert resultado['topicos_com_regressao'] == 0
        assert resultado['detalhes'] == []
    
    def test_analisar_com_diferentes_valores_maximos(self, aluno, estrategia_padrao):
        """Testa análise com diferentes valores máximos por avaliação."""
        historico = [
            {"nota": 18.0, "valor_maximo": 20.0, "topico": "Redação"},  # 90%
            {"nota": 14.0, "valor_maximo": 20.0, "topico": "Redação"},  # 70%
            {"nota": 10.0, "valor_maximo": 20.0, "topico": "Redação"}   # 50%
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['topicos_com_regressao'] == 1
        
        detalhes = resultado['detalhes'][0]
        assert detalhes['slope'] < 0
        assert detalhes['tem_regressao'] is True
    
    def test_analisar_com_limite_customizado(self, aluno):
        """Testa análise com limite de regressão customizado."""
        # Limite mais rigoroso (-2.0)
        estrategia = AnaliseRegressao(limite_regressao=-2.0)
        
        historico = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Biologia"},
            {"nota": 8.8, "valor_maximo": 10.0, "topico": "Biologia"},
            {"nota": 8.6, "valor_maximo": 10.0, "topico": "Biologia"}
        ]
        
        resultado = estrategia.analisar(aluno, historico)
        
        # Slope é negativo mas pequeno (~-1% por avaliação), não deve detectar regressão
        assert resultado['topicos_com_regressao'] == 0
    
    def test_analisar_preserva_ordem_cronologica(self, aluno, estrategia_padrao):
        """Testa que a ordem dos dados é preservada para cálculo correto."""
        historico = [
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Programação"},
            {"nota": 6.0, "valor_maximo": 10.0, "topico": "Programação"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Programação"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Programação"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        detalhes = resultado['detalhes'][0]
        assert detalhes['slope'] > 0  # Tendência positiva
        assert detalhes['media_final'] > detalhes['media_inicial']
    
    # Testes do método identificar_dificuldades
    
    def test_identificar_dificuldades_com_regressao(self, aluno, estrategia_padrao):
        """Testa identificação de dificuldades após análise com regressão."""
        historico = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Estatística"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Estatística"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Estatística"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades = estrategia_padrao.identificar_dificuldades()
        
        assert len(dificuldades) == 1
        assert "Estatística" in dificuldades
    
    def test_identificar_dificuldades_sem_regressao(self, aluno, estrategia_padrao):
        """Testa que não identifica dificuldades quando não há regressão."""
        historico = [
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Literatura"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Literatura"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Literatura"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades = estrategia_padrao.identificar_dificuldades()
        
        assert len(dificuldades) == 0
    
    def test_identificar_dificuldades_multiplos_topicos(self, aluno, estrategia_padrao):
        """Testa identificação de múltiplos tópicos com regressão."""
        historico = [
            # Matemática - regressão
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Matemática"},
            # Física - regressão
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 6.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Física"},
            # Química - sem regressão
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Química"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Química"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Química"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades = estrategia_padrao.identificar_dificuldades()
        
        assert len(dificuldades) == 2
        assert "Matemática" in dificuldades
        assert "Física" in dificuldades
        assert "Química" not in dificuldades
    
    def test_identificar_dificuldades_antes_analisar(self, estrategia_padrao):
        """Testa que identificar_dificuldades retorna lista vazia antes de analisar."""
        dificuldades = estrategia_padrao.identificar_dificuldades()
        assert dificuldades == []
    
    def test_identificar_dificuldades_retorna_copia(self, aluno, estrategia_padrao):
        """Testa que identificar_dificuldades retorna uma cópia da lista."""
        historico = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Astronomia"},
            {"nota": 6.0, "valor_maximo": 10.0, "topico": "Astronomia"},
            {"nota": 3.0, "valor_maximo": 10.0, "topico": "Astronomia"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades1 = estrategia_padrao.identificar_dificuldades()
        dificuldades2 = estrategia_padrao.identificar_dificuldades()
        
        # Modificar uma não deve afetar a outra
        dificuldades1.append("Teste")
        assert len(dificuldades2) == 1
        assert "Teste" not in dificuldades2
    
    # Testes de Integração
    
    def test_reanalise_atualiza_dificuldades(self, aluno, estrategia_padrao):
        """Testa que uma nova análise atualiza as dificuldades."""
        # Primeira análise - com regressão
        historico1 = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Inglês"},
            {"nota": 6.0, "valor_maximo": 10.0, "topico": "Inglês"},
            {"nota": 3.0, "valor_maximo": 10.0, "topico": "Inglês"}
        ]
        
        estrategia_padrao.analisar(aluno, historico1)
        dificuldades1 = estrategia_padrao.identificar_dificuldades()
        assert len(dificuldades1) == 1
        
        # Segunda análise - sem regressão
        historico2 = [
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Espanhol"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Espanhol"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Espanhol"}
        ]
        
        estrategia_padrao.analisar(aluno, historico2)
        dificuldades2 = estrategia_padrao.identificar_dificuldades()
        assert len(dificuldades2) == 0
    
    def test_calculo_percentual_com_valor_maximo_zero(self, aluno, estrategia_padrao):
        """Testa tratamento correto quando valor_maximo é zero."""
        historico = [
            {"nota": 0.0, "valor_maximo": 0.0, "topico": "Teste"},
            {"nota": 0.0, "valor_maximo": 0.0, "topico": "Teste"},
            {"nota": 0.0, "valor_maximo": 0.0, "topico": "Teste"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Não deve lançar exceção
        assert resultado['topicos_analisados'] == 1
        detalhes = resultado['detalhes'][0]
        # Todos os percentuais devem ser zero
        assert abs(detalhes['slope']) < 0.1  
