class MaterialEstudo:
    """Classe base para materiais de estudo - stub temporário"""
    
    def __init__(self, titulo: str, tipo: str = "generico", **kwargs):
        self.titulo = titulo
        self.tipo = tipo
        # Permite atributos adicionais sem erro
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __eq__(self, other):
        """Permite comparação por identidade para testes"""
        return self is other
    
    def __hash__(self):
        """Permite uso em sets/dicts"""
        return id(self)
