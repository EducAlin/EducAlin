from abc import ABC, abstractmethod

class Usuario(ABC):
    @property
    @abstractmethod
    def nome(self):
        pass
    
    @property
    @abstractmethod
    def email(self):
        pass

    @property
    @abstractmethod
    def senha(self):
        pass