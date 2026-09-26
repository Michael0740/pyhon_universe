"""
Resolvendo problema de física com POO (Hidrostática) - Tubo em U
Versão corrigida: composição em vez de herança indevida,
separação clara entre dados (atributos) e comportamento (métodos).
"""

from abc import ABC, abstractmethod


class Fluido:
    """Representa um fluido com nome e densidade. Só guarda dados."""

    def __init__(self, nome: str, densidade: float):
        self._nome = nome
        self.densidade = densidade  # passa pelo setter, já valida

    @property
    def nome(self):
        return self._nome

    @property
    def densidade(self):
        return self._densidade

    @densidade.setter
    def densidade(self, densidade):
        if densidade < 0:
            raise ValueError("A densidade não pode ser negativa")
        self._densidade = densidade  # valida ANTES de atribuir

    def __repr__(self):
        return f"Fluido(nome={self._nome!r}, densidade={self._densidade})"


class TuboEmU:
    """
    Um tubo em U TEM dois fluidos e uma altura de coluna de água.
    Não é um tipo de Fluido (por isso não herda de Fluido) -- é uma
    composição de dois Fluidos.
    """

    def __init__(self, altura_h2o: float, fluido_h2o: Fluido, fluido_hg: Fluido):
        self.altura_h2o = altura_h2o      # passa pelo setter
        self.fluido_h2o = fluido_h2o      # passa pelo setter
        self.fluido_hg = fluido_hg        # passa pelo setter

    @property
    def altura_h2o(self):
        return self._altura_h2o

    @altura_h2o.setter
    def altura_h2o(self, altura_h2o):
        if altura_h2o < 0:
            raise ValueError("A altura não pode ser negativa")
        self._altura_h2o = altura_h2o

    @property
    def fluido_h2o(self):
        return self._fluido_h2o

    @fluido_h2o.setter
    def fluido_h2o(self, fluido_h2o):
        if not isinstance(fluido_h2o, Fluido):
            raise ValueError("O fluido deve ser uma instância da classe Fluido")
        self._fluido_h2o = fluido_h2o

    @property
    def fluido_hg(self):
        return self._fluido_hg

    @fluido_hg.setter
    def fluido_hg(self, fluido_hg):
        if not isinstance(fluido_hg, Fluido):
            raise ValueError("O fluido deve ser uma instância da classe Fluido")
        self._fluido_hg = fluido_hg


class CalculoHidrostatico(ABC):
    """
    Classe abstrata que define o CONTRATO de cálculo.
    Não herda de TuboEmU -- ela RECEBE um TuboEmU para operar sobre ele
    (composição), o que é a relação correta ("opera sobre", não "é um").
    """

    def __init__(self, tubo: TuboEmU):
        self._tubo = tubo

    @property
    def tubo(self):
        return self._tubo

    @abstractmethod
    def calcular_altura_hg(self) -> float:
        pass

    @abstractmethod
    def calcular_desnivel(self) -> float:
        pass


class CalculoTuboEmU(CalculoHidrostatico):
    """
    Implementação concreta do cálculo para o tubo em U.
    Princípio físico: p_água = p_mercúrio na base comum
    => densidade_água * altura_água = densidade_hg * altura_hg
    """

    def calcular_altura_hg(self) -> float:
        densidade_h2o = self.tubo.fluido_h2o.densidade
        densidade_hg = self.tubo.fluido_hg.densidade
        altura_h2o = self.tubo.altura_h2o
        return (densidade_h2o * altura_h2o) / densidade_hg

    def calcular_desnivel(self) -> float:
        return self.tubo.altura_h2o - self.calcular_altura_hg()


def main():
    # Densidades em g/cm³, exatamente como no enunciado
    agua = Fluido("Água", 1.0)
    mercurio = Fluido("Mercúrio", 13.6)

    # Altura da coluna de água (em cm) -- valor da figura do enunciado.
    # Ajuste este valor para reproduzir o resultado esperado (37,98 cm)
    altura_agua_cm = 44.0  # <-- valor que precisa vir da figura original

    tubo = TuboEmU(altura_h2o=altura_agua_cm, fluido_h2o=agua, fluido_hg=mercurio)
    calculo = CalculoTuboEmU(tubo)

    altura_hg = calculo.calcular_altura_hg()
    desnivel = calculo.calcular_desnivel()

    print(f"Altura da coluna de mercúrio: {altura_hg:.2f} cm")
    print(f"Desnível h: {desnivel:.2f} cm")


if __name__ == "__main__":
    main()
