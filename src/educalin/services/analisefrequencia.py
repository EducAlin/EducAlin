from typing import Dict, List, Any
from educalin.domain.aluno import Aluno
from educalin.services.estrategiaanalise import EstrategiaAnalise


class AnaliseFrequencia(EstrategiaAnalise):
    """
    Estratégia de análise que identifica dificuldades baseada em baixa frequência de acertos.
    
    Esta estratégia verifica a quantidade de avaliações bem-sucedidas por tópico e 
    identifica aqueles que não atingem um mínimo configurável de acertos, indicando
    possíveis dificuldades ou falta de prática.
    
    Attributes:
        _min_avaliacoes (int): Número mínimo de avaliações positivas esperadas.
        _limite_aprovacao (float): Percentual mínimo para considerar aprovado (padrão 60%).
        _dificuldades (List[str]): Lista de tópicos com baixa frequência de acertos.
    
    Examples:
        >>> estrategia = AnaliseFrequencia(min_avaliacoes=3)
        >>> aluno = Aluno(nome="João")
        >>> historico = [
        ...     {"nota": 8.0, "valor_maximo": 10.0, "topico": "Álgebra"},
        ...     {"nota": 7.0, "valor_maximo": 10.0, "topico": "Álgebra"},
        ...     {"nota": 4.0, "valor_maximo": 10.0, "topico": "Geometria"}
        ... ]
        >>> resultado = estrategia.analisar(aluno, historico)
        >>> dificuldades = estrategia.identificar_dificuldades()
    """
    
    def __init__(self, min_avaliacoes: int = 3, limite_aprovacao: float = 60.0):
        """
        Inicializa a estratégia de análise de frequência.
        
        Args:
            min_avaliacoes (int): Número mínimo de avaliações positivas esperadas.
                Padrão é 3.
            limite_aprovacao (float): Percentual mínimo para considerar uma 
                avaliação como positiva (0-100). Padrão é 60.0%.
        
        Raises:
            TypeError: Se min_avaliacoes não for um inteiro.
            ValueError: Se min_avaliacoes for menor que 1.
            TypeError: Se limite_aprovacao não for um número.
            ValueError: Se limite_aprovacao não estiver entre 0 e 100.
        """
        if not isinstance(min_avaliacoes, int):
            raise TypeError("O número mínimo de avaliações deve ser um inteiro.")
        
        if min_avaliacoes < 1:
            raise ValueError("O número mínimo de avaliações deve ser pelo menos 1.")
        
        if not isinstance(limite_aprovacao, (int, float)):
            raise TypeError("O limite de aprovação deve ser um número.")
        
        if not 0 <= limite_aprovacao <= 100:
            raise ValueError("O limite de aprovação deve estar entre 0 e 100.")
        
        self._min_avaliacoes = min_avaliacoes
        self._limite_aprovacao = limite_aprovacao
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
            ValueError: Se valor for menor que 1.
        """
        if not isinstance(valor, int):
            raise TypeError("O número mínimo de avaliações deve ser um inteiro.")
        
        if valor < 1:
            raise ValueError("O número mínimo de avaliações deve ser pelo menos 1.")
        
        self._min_avaliacoes = valor
    
    @property
    def limite_aprovacao(self) -> float:
        """Retorna o limite de aprovação configurado."""
        return self._limite_aprovacao
    
    @limite_aprovacao.setter
    def limite_aprovacao(self, valor: float):
        """
        Define um novo limite de aprovação.
        
        Args:
            valor (float): Novo percentual mínimo (0-100).
        
        Raises:
            TypeError: Se valor não for um número.
            ValueError: Se valor não estiver entre 0 e 100.
        """
        if not isinstance(valor, (int, float)):
            raise TypeError("O limite de aprovação deve ser um número.")
        
        if not 0 <= valor <= 100:
            raise ValueError("O limite de aprovação deve estar entre 0 e 100.")
        
        self._limite_aprovacao = valor
    
    def analisar(self, aluno: Aluno, historico: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa a frequência de acertos do aluno por tópico.
        
        Conta quantas avaliações positivas (>= limite_aprovacao) o aluno teve em cada
        tópico e identifica aqueles que não atingem o mínimo esperado.
        
        Args:
            aluno (Aluno): Instância do aluno a ser analisado.
            historico (List[Dict[str, Any]]): Lista de dicionários contendo:
                - nota (float): Valor da nota obtida
                - valor_maximo (float): Valor máximo possível
                - topico (str): Nome do tópico/disciplina avaliado
        
        Returns:
            Dict[str, Any]: Dicionário com os resultados da análise contendo:
                - aluno_nome (str): Nome do aluno analisado
                - total_avaliacoes (int): Total de avaliações no histórico
                - topicos_analisados (int): Quantidade de tópicos únicos
                - topicos_baixa_frequencia (int): Tópicos com poucos acertos
                - detalhes (List[Dict]): Detalhes por tópico com:
                    - topico (str): Nome do tópico
                    - total (int): Total de avaliações no tópico
                    - acertos (int): Quantidade de acertos
                    - percentual_acerto (float): Percentual de acertos
        
        Examples:
            >>> estrategia = AnaliseFrequencia(min_avaliacoes=2)
            >>> aluno = Aluno(nome="Maria")
            >>> historico = [{"nota": 8.0, "valor_maximo": 10.0, "topico": "Matemática"}]
            >>> resultado = estrategia.analisar(aluno, historico)
            >>> resultado['topicos_baixa_frequencia']
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
                topicos[topico] = {'total': 0, 'acertos': 0}
            
            # Contabiliza
            topicos[topico]['total'] += 1
            if percentual >= self._limite_aprovacao:
                topicos[topico]['acertos'] += 1
        
        # Analisa cada tópico
        detalhes = []
        topicos_problemáticos = 0
        
        for topico, dados in topicos.items():
            percentual_acerto = (dados['acertos'] / dados['total'] * 100) if dados['total'] > 0 else 0
            
            # Verifica se tem poucos acertos
            if dados['acertos'] < self._min_avaliacoes:
                self._dificuldades.append(topico)
                topicos_problemáticos += 1
            
            detalhes.append({
                'topico': topico,
                'total': dados['total'],
                'acertos': dados['acertos'],
                'percentual_acerto': round(percentual_acerto, 2)
            })
        
        return {
            'aluno_nome': aluno.nome,
            'total_avaliacoes': len(historico),
            'topicos_analisados': len(topicos),
            'topicos_baixa_frequencia': topicos_problemáticos,
            'detalhes': detalhes
        }
    
    def identificar_dificuldades(self) -> List[str]:
        """
        Retorna a lista de tópicos com baixa frequência de acertos.
        
        Este método retorna os tópicos que não atingiram o número mínimo de
        avaliações positivas, conforme identificado na última execução do
        método analisar().
        
        Returns:
            List[str]: Lista de tópicos com baixa frequência. Retorna lista vazia
                se nenhuma dificuldade foi identificada ou se analisar() ainda
                não foi executado.
        
        Examples:
            >>> estrategia = AnaliseFrequencia()
            >>> dificuldades = estrategia.identificar_dificuldades()
            >>> print(dificuldades)
            ['Cálculo', 'Física']
        
        Note:
            Este método deve ser chamado após analisar() para obter resultados
            relevantes.
        """
        return self._dificuldades.copy()
