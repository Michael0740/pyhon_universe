#aplicaremos aqui os conceitos fundamentais de abstração e polimorfismo 
#class Produto:
   # def __init__(self,nome,preco):
        #self.nome = nome 
       # self.__preco = preco 

   # @property
    #def preco(self):
    #    return self.__preco 
#produto = Produto('Casaco',2000)
#print(produto.preco)
class Avaliacao:
    def __init__(self,nome,disciplina,nota = 0):
        self.nome = nome
        self.disciplina = disciplina
        self._nota = nota #atributo protegido, não é privado, mas não deve ser acessado diretamente fora da classe
    # métodos acessores (getters e setters)
    @property
    def nota(self):
        return self._nota
    @nota.setter
    def nota(self,valor):
        if valor < 0 or valor > 10:
            raise ValueError('Nota deve estar entre 0 e 10')
        self._nota = valor
        
# é bem melhor usar o property do que criar métodos get e set, pois o property permite acessar o atributo como se fosse um atributo normal, sem a necessidade de chamar um método.

    

        
    

        