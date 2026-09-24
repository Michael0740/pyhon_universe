from abc import ABC, abstractmethod


class RegraColegio(ABC):
    @abstractmethod
    def matricular(self):
        pass

    def cartao(self):
        print("Cartao de estudante emitido.")


class MatriculaAluno(RegraColegio):
    def __init__(self, identificacao, certificado):
        self.identificacao = identificacao
        self.certificado = certificado

    def matricular(self):
        return f"Aluno com ID {self.identificacao} matriculado com sucesso."


class CartaoEstudante(RegraColegio):
    def __init__(self, nome, curso):
        self.nome = nome
        self.curso = curso

    def matricular(self):
        return f"Aluno {self.nome} matriculado no curso {self.curso}."

    def emitir_cartao(self):
        return f"Cartao emitido para {self.nome}, do curso {self.curso}."


aluno1 = MatriculaAluno("12345", "Certificado de Conclusao")
print(aluno1.matricular())

cartao1 = CartaoEstudante("Joao", "Engenharia")
print(cartao1.matricular())
print(cartao1.emitir_cartao())
