from typing import Dict, List, Any, Optional
from educalin.domain.aluno import Aluno
from educalin.services.estrategiaanalise import EstrategiaAnalise


class AnalisadorDesempenho:
    """
    Classe Context do padrão Strategy para análise de desempenho de alunos.
    
    Esta classe atua como o contexto no padrão Strategy, permitindo que diferentes
    estratégias de análise sejam utilizadas de forma intercambiável. O AnalisadorDesempenho
    delega a lógica de análise para a estratégia configurada, facilitando a extensão
    e manutenção do código.
    
    O padrão Strategy é implementado aqui permitindo:
    - Definir uma família de algoritmos de análise (estratégias)
    - Encapsular cada algoritmo
    - Tornar os algoritmos intercambiáveis
    - Permitir que a estratégia varie independentemente do contexto
    
    Attributes:
        _estrategia (Optional[EstrategiaAnalise]): A estratégia de análise atualmente configurada.
    
    Examples:
        >>> from educalin.services.analisefrequencia import AnaliseFrequencia
        >>> estrategia = AnaliseFrequencia(min_avaliacoes=3)
        >>> analisador = AnalisadorDesempenho(estrategia)
        >>> resultado = analisador.analisar(aluno, historico)
        >>> dificuldades = analisador.identificar_dificuldades()
        
        >>> # Trocar estratégia em tempo de execução
        >>> from educalin.services.analiseregressao import AnaliseRegressao
        >>> analisador.estrategia = AnaliseRegressao()
        >>> resultado = analisador.analisar(aluno, historico)
    
    Note:
        A estratégia pode ser definida no construtor ou posteriormente via property.
        É necessário ter uma estratégia definida antes de chamar os métodos de análise.
    """
    
    def __init__(self, estrategia: Optional[EstrategiaAnalise] = None):
        """
        Inicializa o analisador de desempenho com uma estratégia opcional.
        
        Args:
            estrategia (Optional[EstrategiaAnalise]): Estratégia inicial de análise.
                Se None, a estratégia deve ser definida antes de realizar análises.
        
        Raises:
            TypeError: Se a estratégia fornecida não for uma instância de EstrategiaAnalise.
        
        Examples:
            >>> # Com estratégia inicial
            >>> analisador = AnalisadorDesempenho(AnaliseFrequencia())
            
            >>> # Sem estratégia inicial
            >>> analisador = AnalisadorDesempenho()
            >>> analisador.estrategia = AnaliseNotasBaixas()
        """
        if estrategia is not None and not isinstance(estrategia, EstrategiaAnalise):
            raise TypeError("A estratégia deve ser uma instância de EstrategiaAnalise.")
        
        self._estrategia = estrategia
    
    @property
    def estrategia(self) -> Optional[EstrategiaAnalise]:
        """
        Retorna a estratégia de análise atualmente configurada.
        
        Returns:
            Optional[EstrategiaAnalise]: A estratégia atual ou None se nenhuma foi definida.
        
        Examples:
            >>> analisador = AnalisadorDesempenho(AnaliseFrequencia())
            >>> print(type(analisador.estrategia).__name__)
            AnaliseFrequencia
        """
        return self._estrategia
    
    @estrategia.setter
    def estrategia(self, valor: Optional[EstrategiaAnalise]):
        """
        Define uma nova estratégia de análise.
        
        Permite trocar a estratégia de análise em tempo de execução, um dos principais
        benefícios do padrão Strategy.
        
        Args:
            valor (Optional[EstrategiaAnalise]): Nova estratégia a ser utilizada.
                Pode ser None para remover a estratégia atual.
        
        Raises:
            TypeError: Se o valor não for None nem uma instância de EstrategiaAnalise.
        
        Examples:
            >>> analisador = AnalisadorDesempenho()
            >>> analisador.estrategia = AnaliseFrequencia()
            >>> # Trocar estratégia
            >>> analisador.estrategia = AnaliseRegressao()
        """
        if valor is not None and not isinstance(valor, EstrategiaAnalise):
            raise TypeError("A estratégia deve ser uma instância de EstrategiaAnalise.")
        
        self._estrategia = valor
    
    def analisar(self, aluno: Aluno, historico: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa o desempenho do aluno usando a estratégia configurada.
        
        Delega a análise para a estratégia atualmente definida. A estrutura do
        resultado depende da estratégia utilizada.
        
        Args:
            aluno (Aluno): Instância do aluno a ser analisado.
            historico (List[Dict[str, Any]]): Lista de dicionários contendo o histórico
                de avaliações do aluno.
        
        Returns:
            Dict[str, Any]: Resultado da análise conforme a estratégia utilizada.
        
        Raises:
            ValueError: Se nenhuma estratégia foi definida.
        
        Examples:
            >>> analisador = AnalisadorDesempenho(AnaliseFrequencia())
            >>> historico = [
            ...     {"nota": 8.0, "valor_maximo": 10.0, "topico": "Matemática"},
            ...     {"nota": 7.0, "valor_maximo": 10.0, "topico": "Matemática"}
            ... ]
            >>> resultado = analisador.analisar(aluno, historico)
            >>> print(resultado['aluno_nome'])
            João Silva
        """
        if self._estrategia is None:
            raise ValueError("Nenhuma estratégia foi definida. Use o property 'estrategia' para definir uma.")
        
        return self._estrategia.analisar(aluno, historico)
    
    def identificar_dificuldades(self) -> List[str]:
        """
        Identifica as dificuldades do aluno usando a estratégia configurada.
        
        Delega a identificação de dificuldades para a estratégia atualmente definida.
        
        Returns:
            List[str]: Lista de áreas/tópicos com dificuldades identificadas.
        
        Raises:
            ValueError: Se nenhuma estratégia foi definida.
        
        Examples:
            >>> analisador = AnalisadorDesempenho(AnaliseRegressao())
            >>> analisador.analisar(aluno, historico)
            >>> dificuldades = analisador.identificar_dificuldades()
            >>> print(dificuldades)
            ['Cálculo', 'Física']
        
        Note:
            Este método geralmente deve ser chamado após analisar(), pois as
            estratégias identificam dificuldades com base na análise realizada.
        """
        if self._estrategia is None:
            raise ValueError("Nenhuma estratégia foi definida. Use o property 'estrategia' para definir uma.")
        
        return self._estrategia.identificar_dificuldades()
