from typing import Dict, List, Any, Tuple
from educalin.domain.aluno import Aluno
from educalin.services.estrategiaanalise import EstrategiaAnalise


class AnaliseRegressao(EstrategiaAnalise):
    """
    Estratégia de análise que detecta regressão temporal no desempenho do aluno.
    
    Esta estratégia identifica tendências negativas no desempenho ao longo do tempo,
    analisando o histórico de avaliações e calculando a inclinação (slope) da linha
    de tendência para cada tópico. Requer um mínimo de 3 avaliações para calcular
    uma tendência estatisticamente significativa.
    
    Attributes:
        _min_avaliacoes (int): Número mínimo de avaliações necessárias para calcular
            a tendência (padrão 3).
        _limite_regressao (float): Limite de slope negativo para considerar regressão
            significativa. Valores mais negativos indicam declínio mais acentuado.
        _dificuldades (List[str]): Lista de tópicos com tendência negativa detectada.
    
    Examples:
        >>> estrategia = AnaliseRegressao(min_avaliacoes=3, limite_regressao=-2.0)
        >>> aluno = Aluno(nome="Carlos")
        >>> historico = [
        ...     {"nota": 9.0, "valor_maximo": 10.0, "topico": "Cálculo", "data": "2024-01-10"},
        ...     {"nota": 7.0, "valor_maximo": 10.0, "topico": "Cálculo", "data": "2024-02-15"},
        ...     {"nota": 5.0, "valor_maximo": 10.0, "topico": "Cálculo", "data": "2024-03-20"}
        ... ]
        >>> resultado = estrategia.analisar(aluno, historico)
        >>> dificuldades = estrategia.identificar_dificuldades()
        >>> print(dificuldades)
        ['Cálculo']
    """
    
    def __init__(self, min_avaliacoes: int = 3, limite_regressao: float = -1.0):
        """
        Inicializa a estratégia de análise de regressão temporal.
        
        Args:
            min_avaliacoes (int): Número mínimo de avaliações necessárias para
                calcular tendência. Padrão é 3.
            limite_regressao (float): Limite de slope (inclinação) abaixo do qual
                considera-se regressão significativa. Valores negativos indicam
                declínio. Padrão é -1.0% por avaliação.
        
        Raises:
            TypeError: Se min_avaliacoes não for um inteiro.
            ValueError: Se min_avaliacoes for menor que 3.
            TypeError: Se limite_regressao não for um número.
        """
        if not isinstance(min_avaliacoes, int):
            raise TypeError("O número mínimo de avaliações deve ser um inteiro.")
        
        if min_avaliacoes < 3:
            raise ValueError("O número mínimo de avaliações deve ser pelo menos 3 para calcular tendência.")
        
        if not isinstance(limite_regressao, (int, float)):
            raise TypeError("O limite de regressão deve ser um número.")
        
        self._min_avaliacoes = min_avaliacoes
        self._limite_regressao = limite_regressao
        self._dificuldades = []
    
    @property
    def min_avaliacoes(self) -> int:
        """Retorna o número mínimo de avaliações configurado."""
        return self._min_avaliacoes
    
    @min_avaliacoes.setter
    def min_avaliacoes(self, valor: int):
        """
        Define um novo número mínimo de avaliações.
        
        Args:
            valor (int): Novo número mínimo de avaliações.
        
        Raises:
            TypeError: Se valor não for um inteiro.
            ValueError: Se valor for menor que 3.
        """
        if not isinstance(valor, int):
            raise TypeError("O número mínimo de avaliações deve ser um inteiro.")
        
        if valor < 3:
            raise ValueError("O número mínimo de avaliações deve ser pelo menos 3.")
        
        self._min_avaliacoes = valor
    
    @property
    def limite_regressao(self) -> float:
        """Retorna o limite de regressão configurado."""
        return self._limite_regressao
    
    @limite_regressao.setter
    def limite_regressao(self, valor: float):
        """
        Define um novo limite de regressão.
        
        Args:
            valor (float): Novo limite de slope negativo.
        
        Raises:
            TypeError: Se valor não for um número.
        """
        if not isinstance(valor, (int, float)):
            raise TypeError("O limite de regressão deve ser um número.")
        
        self._limite_regressao = valor
    
    def calcular_tendencia(self, valores: List[float]) -> Tuple[float, float]:
        """
        Calcula a tendência (slope e intercept) usando regressão linear simples.
        
        Utiliza o método dos mínimos quadrados para calcular a linha de tendência
        que melhor se ajusta aos dados de desempenho ao longo do tempo.
        
        A fórmula do slope é:
        slope = (n*Σ(xy) - Σx*Σy) / (n*Σ(x²) - (Σx)²)
        
        A fórmula do intercept é:
        intercept = (Σy - slope*Σx) / n
        
        Args:
            valores (List[float]): Lista de percentuais de desempenho em ordem cronológica.
        
        Returns:
            Tuple[float, float]: Tupla contendo (slope, intercept) da linha de tendência.
                - slope: Taxa de mudança do desempenho por avaliação (pode ser positiva
                  ou negativa)
                - intercept: Valor inicial projetado da linha de tendência
        
        Raises:
            ValueError: Se a lista de valores tiver menos de 3 elementos.
            ValueError: Se não for possível calcular a tendência (denominador zero).
        
        Examples:
            >>> estrategia = AnaliseRegressao()
            >>> valores = [90.0, 80.0, 70.0]
            >>> slope, intercept = estrategia.calcular_tendencia(valores)
            >>> print(f"Slope: {slope:.2f}")
            Slope: -10.00
        """
        n = len(valores)
        
        if n < 3:
            raise ValueError("São necessários pelo menos 3 valores para calcular tendência.")
        
        # Índices temporais (0, 1, 2, ...)
        x = list(range(n))
        y = valores
        
        # Cálculos para regressão linear
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x_squared = sum(xi ** 2 for xi in x)
        
        # Cálculo do slope (inclinação)
        denominador = n * sum_x_squared - sum_x ** 2
        
        if denominador == 0:
            raise ValueError("Não foi possível calcular a tendência (denominador zero).")
        
        slope = (n * sum_xy - sum_x * sum_y) / denominador
        
        # Cálculo do intercept (intercepto)
        intercept = (sum_y - slope * sum_x) / n
        
        return slope, intercept
    
    def analisar(self, aluno: Aluno, historico: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa a tendência de desempenho do aluno por tópico ao longo do tempo.
        
        Para cada tópico com pelo menos min_avaliacoes avaliações, calcula a linha
        de tendência e identifica se há regressão (declínio) no desempenho.
        
        Args:
            aluno (Aluno): Instância do aluno a ser analisado.
            historico (List[Dict[str, Any]]): Lista de dicionários contendo:
                - nota (float): Valor da nota obtida
                - valor_maximo (float): Valor máximo possível
                - topico (str): Nome do tópico/disciplina avaliado
                - data (str, opcional): Data da avaliação para ordenação
        
        Returns:
            Dict[str, Any]: Dicionário com os resultados da análise contendo:
                - aluno_nome (str): Nome do aluno analisado
                - total_avaliacoes (int): Total de avaliações no histórico
                - topicos_analisados (int): Quantidade de tópicos únicos
                - topicos_com_regressao (int): Tópicos com tendência negativa significativa
                - detalhes (List[Dict]): Detalhes por tópico com:
                    - topico (str): Nome do tópico
                    - total_avaliacoes (int): Quantidade de avaliações no tópico
                    - slope (float): Inclinação da linha de tendência
                    - intercept (float): Intercepto da linha de tendência
                    - media_inicial (float): Média das primeiras avaliações
                    - media_final (float): Média das últimas avaliações
                    - tem_regressao (bool): Se há regressão significativa
        
        Examples:
            >>> estrategia = AnaliseRegressao()
            >>> aluno = Aluno(nome="Ana")
            >>> historico = [
            ...     {"nota": 9.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            ...     {"nota": 7.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            ...     {"nota": 5.0, "valor_maximo": 10.0, "topico": "Álgebra"}
            ... ]
            >>> resultado = estrategia.analisar(aluno, historico)
            >>> resultado['topicos_com_regressao']
            1
        """
        self._dificuldades = []
        
        # Agrupa avaliações por tópico
        topicos = {}
        for item in historico:
            nota = item.get('nota', 0)
            valor_maximo = item.get('valor_maximo', 10)
            topico = item.get('topico', 'Não especificado')
            
            # Calcula o percentual
            percentual = (nota / valor_maximo * 100) if valor_maximo > 0 else 0
            
            # Inicializa tópico se não existir
            if topico not in topicos:
                topicos[topico] = []
            
            # Adiciona o percentual na ordem cronológica
            topicos[topico].append(percentual)
        
        # Analisa cada tópico
        detalhes = []
        topicos_com_regressao = 0
        
        for topico, valores in topicos.items():
            total_avaliacoes = len(valores)
            
            # Só analisa se tiver avaliações suficientes
            if total_avaliacoes >= self._min_avaliacoes:
                try:
                    slope, intercept = self.calcular_tendencia(valores)
                    
                    # Calcula médias inicial e final para contexto
                    media_inicial = sum(valores[:2]) / 2 if len(valores) >= 2 else valores[0]
                    media_final = sum(valores[-2:]) / 2 if len(valores) >= 2 else valores[-1]
                    
                    # Verifica se há regressão significativa
                    tem_regressao = slope < self._limite_regressao
                    
                    if tem_regressao:
                        self._dificuldades.append(topico)
                        topicos_com_regressao += 1
                    
                    detalhes.append({
                        'topico': topico,
                        'total_avaliacoes': total_avaliacoes,
                        'slope': round(slope, 2),
                        'intercept': round(intercept, 2),
                        'media_inicial': round(media_inicial, 2),
                        'media_final': round(media_final, 2),
                        'tem_regressao': tem_regressao
                    })
                    
                except ValueError as e:
                    # Se não for possível calcular, registra sem tendência
                    detalhes.append({
                        'topico': topico,
                        'total_avaliacoes': total_avaliacoes,
                        'erro': str(e)
                    })
            else:
                # Tópicos com poucas avaliações não são analisados
                detalhes.append({
                    'topico': topico,
                    'total_avaliacoes': total_avaliacoes,
                    'slope': None,
                    'intercept': None,
                    'media_inicial': None,
                    'media_final': None,
                    'tem_regressao': False,
                    'nota': 'Avaliações insuficientes para calcular tendência'
                })
        
        return {
            'aluno_nome': aluno.nome,
            'total_avaliacoes': len(historico),
            'topicos_analisados': len(topicos),
            'topicos_com_regressao': topicos_com_regressao,
            'detalhes': detalhes
        }
    
    def identificar_dificuldades(self) -> List[str]:
        """
        Retorna a lista de tópicos com tendência negativa (regressão) detectada.
        
        Este método retorna os tópicos onde foi identificada uma tendência de
        declínio no desempenho ao longo do tempo, conforme identificado na última
        execução do método analisar().
        
        Returns:
            List[str]: Lista de tópicos com regressão temporal. Retorna lista vazia
                se nenhuma regressão foi identificada ou se analisar() ainda
                não foi executado.
        
        Examples:
            >>> estrategia = AnaliseRegressao()
            >>> dificuldades = estrategia.identificar_dificuldades()
            >>> print(dificuldades)
            ['Física Quântica', 'Cálculo III']
        
        Note:
            Este método deve ser chamado após analisar() para obter resultados
            relevantes.
        """
        return self._dificuldades.copy()
