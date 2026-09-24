#sobre abstração
#não se pode criar objetos de uma classe abstrata, mas pode-se criar classes filhas que implementem os métodos abstratos

from abc import ABC, abstractmethod

# 1. Definir a Classe Abstrata (o molde)
class ControleRemoto(ABC):
    
    @abstractmethod
    def ligar(self):
        """Este método DEVE ser implementado por qualquer subclasse."""
        pass

    @abstractmethod
    def desligar(self):
        pass

    def carregar_bateria(self):
        """Método concreto: todas as subclasses herdam esta lógica pronta."""
        print("A carregar bateria...")

# 2. Implementar uma Classe Concreta (a execução real)
class ControleTV(ControleRemoto):
    
    def ligar(self):
        print("A ligar a Televisão...")

    def desligar(self):
        print("A desligar a Televisão...")

# Testar o código
# controle = ControleRemoto()  # Erro! Não se pode criar o objeto abstrato diretamente.

meu_controle = ControleTV()
meu_controle.ligar()             # Resultado: A ligar a Televisão...
meu_controle.carregar_bateria()  # Resultado: A carregar bateria...
