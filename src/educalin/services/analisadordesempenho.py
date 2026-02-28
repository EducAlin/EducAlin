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
    
    def definir_estrategia(self, estrategia: EstrategiaAnalise):
        """
        Define a estratégia de análise a ser utilizada.
        
        Este método é uma alternativa ao uso do property setter, oferecendo
        uma interface mais explícita para definir a estratégia de análise.
        
        Args:
            estrategia (EstrategiaAnalise): A estratégia de análise a ser definida.
        
        Raises:
            TypeError: Se a estratégia não for uma instância de EstrategiaAnalise.
        
        Examples:
            >>> analisador = AnalisadorDesempenho()
            >>> estrategia = AnaliseFrequencia()
            >>> analisador.definir_estrategia(estrategia)
            
        Note:
            Este método valida o tipo da estratégia antes de defini-la.
        """
        if not isinstance(estrategia, EstrategiaAnalise):
            raise TypeError("A estratégia deve ser uma instância de EstrategiaAnalise.")
        
        self._estrategia = estrategia
    
    def executar_analise(self, aluno: Aluno) -> Dict[str, Any]:
        """
        Executa a análise de desempenho do aluno usando a estratégia configurada.
        
        Este método extrai o histórico de desempenho do aluno (suas notas) e
        delega a análise para a estratégia atualmente definida. Ele converte
        automaticamente as notas do aluno no formato esperado pelas estratégias.
        
        Args:
            aluno (Aluno): Instância do aluno a ser analisado.
        
        Returns:
            Dict[str, Any]: Resultado da análise conforme a estratégia utilizada.
        
        Raises:
            ValueError: Se nenhuma estratégia foi definida.
            ValueError: Se o aluno não possui notas registradas.
        
        Examples:
            >>> analisador = AnalisadorDesempenho(AnaliseFrequencia())
            >>> resultado = analisador.executar_analise(aluno)
            >>> print(resultado['aluno_nome'])
            João Silva
        
        Note:
            Este método é uma conveniência que abstrai a necessidade de passar
            o histórico explicitamente, extraindo-o diretamente do aluno.
        """
        if self._estrategia is None:
            raise ValueError("Nenhuma estratégia foi definida. Use o método 'definir_estrategia' ou o property 'estrategia' para definir uma.")
        
        # Converte as notas do aluno para o formato de histórico esperado pelas estratégias
        historico = []
        for nota in aluno.desempenho:
            historico.append({
                'nota': nota.valor,
                'valor_maximo': nota.avaliacao.valor_maximo,
                'topico': nota.avaliacao.titulo
            })
        
        if not historico:
            raise ValueError(f"O aluno {aluno.nome} não possui notas registradas para análise.")
        
        return self.analisar(aluno, historico)
    
    def gerar_sugestoes(self) -> List[str]:
        """
        Gera sugestões de conteúdos de estudo baseadas nas dificuldades identificadas.
        
        Este método utiliza as dificuldades identificadas pela estratégia atual
        para gerar sugestões personalizadas de materiais e conteúdos de estudo
        que podem ajudar o aluno a superar suas dificuldades.
        
        Returns:
            List[str]: Lista de sugestões de estudo personalizadas.
        
        Raises:
            ValueError: Se nenhuma estratégia foi definida.
        
        Examples:
            >>> analisador = AnalisadorDesempenho(AnaliseRegressao())
            >>> analisador.executar_analise(aluno)
            >>> sugestoes = analisador.gerar_sugestoes()
            >>> print(sugestoes)
            ['Revisar conceitos básicos de Matemática', 'Praticar exercícios de Física']
        
        Note:
            Este método deve ser chamado após executar_analise() ou analisar(),
            pois utiliza as dificuldades identificadas durante a análise.
        """
        if self._estrategia is None:
            raise ValueError("Nenhuma estratégia foi definida. Use o método 'definir_estrategia' ou o property 'estrategia' para definir uma.")
        
        dificuldades = self.identificar_dificuldades()
        
        if not dificuldades:
            return ["O aluno está com bom desempenho em todas as áreas avaliadas."]
        
        sugestoes = []
        for dificuldade in dificuldades:
            sugestoes.append(f"Revisar conceitos e praticar exercícios de {dificuldade}")
            sugestoes.append(f"Buscar material complementar sobre {dificuldade}")
        
        return sugestoes
