#resolvendo problema de física com POO (Hidrostática)

from abc import ABC, abstractmethod

class Fluido():
    def __init__(self, nome ,densidade=float):
        self._nome = nome
        self._densidade = densidade
    @property
    def nome(self):
        return self._nome

    @property
    def densidade(self):
        return self._densidade
    @densidade.setter
    def densidade(self, densidade):
        self._densidade = densidade
        if densidade < 0:
            raise ValueError("A densidade não pode ser negativa")

class TuboEmU(Fluido):
    def __init__(self, nome, densidade, altura_h20=float, fluido_h20=Fluido, fluido_hg=Fluido, calcular_altura_hg=float,calcular_desnivel=float ):
        super().__init__(nome, densidade)
        self._altura_h20 = altura_h20
        self._fluido_h20 = fluido_h20
        self._fluido_hg = fluido_hg
        self.calcular_altura_hg = calcular_altura_hg
        self.calcular_desnivel = calcular_desnivel
    @property
    def altura_h20(self):
        return self._altura_h20
    @altura_h20.getter
    def altura_h20(self):
        return self._altura_h20
    @altura_h20.setter
    def altura_h20(self, altura_h20):
        self._altura_h20 = altura_h20
        if altura_h20 < 0:
            raise ValueError("A altura não pode ser negativa")
        
    @property 
    def fluido_h20(self):
        return self._fluido_h20
    @fluido_h20.setter
    def fluido_h20(self, fluido_h20):
        self._fluido_h20 = fluido_h20
        if not isinstance(fluido_h20, Fluido):
            raise ValueError("O fluido deve ser uma instância da classe Fluido")
    @property
    def fluido_hg(self):
        return self._fluido_hg
    @fluido_hg.setter
    def fluido_hg(self, fluido_hg):
        self._fluido_hg = fluido_hg
        if not isinstance(fluido_hg, Fluido):
            raise ValueError("O fluido deve ser uma instância da classe Fluido")
class CalculoHidrostatico(TuboEmU, ABC):
    def __init__(self, nome, densidade, altura_h20=float, fluido_h20=Fluido, fluido_hg=Fluido, calcular_altura_hg=float,calcular_desnivel=float):
            super().__init__(nome, densidade, altura_h20, fluido_h20, fluido_hg, calcular_altura_hg, calcular_desnivel)
            
    @abstractmethod
    def calcular_altura_hg(self):
        pass
    @abstractmethod
    def calcular_desnivel(self):
        pass
    
def calcular_altura_hg(self):
    altura_hg = (self.fluido_h20.densidade * self.altura_h20) / self.fluido_hg.densidade
    return altura_hg
def calcular_desnivel(self):
    desnivel = self.altura_h20 - self.calcular_altura_hg()
    return desnivel

def main():
    # Criando instâncias de fluido
    agua = Fluido("Água", 1000)  # densidade em kg/m³
    mercurio = Fluido("Mercúrio", 13546)  # densidade em kg/m³

    # Criando instância de TuboEmU
    tubo = TuboEmU("Tubo em U", densidade=2, altura_h20=1.0, fluido_h20=agua, fluido_hg=mercurio)

    # Calculando altura do mercúrio e desnivel
    altura_hg = calcular_altura_hg(tubo)
    desnivel = calcular_desnivel(tubo)

    print(f"Altura do mercúrio: {altura_hg:.2f} m")
    print(f"Desnível: {desnivel:.2f} m")
    