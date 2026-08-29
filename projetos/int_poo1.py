#criar uma classe é representar um objeto da vida real.
#numa classe a gente constroi todas as caracteriusticas e comportamentos de um objeto.
#criar um objeto para uma classe é chamado de instância 
#é possível armazenar suas classes em um model e importar classes construidas por outros programadores dentro do seu arquivo.py
#criar uma classe trata-se de orquestar o comportamento de um determinado objeto 
#vamos criar uma classe dog que represente um cão na vida real 
# em python muitos programadores usam (...) três pontos para dizer que o seu código não está completo ou esta no modo in working 

#class Dog():
   # def __init__(self,name,age):
       # self.name = name
       # self.age = age
        
    #def sit(self):
        #return f'{self.name} agora está sentado!'
        
    #def roll_over(self):
        #return f'{self.name} agora está rebolando!'
#sobre_cao = Dog('Max',2)
#print(sobre_cao.roll_over())
#uma função sempre deve nos retornar alguma coisa 
#criando uma classe Car (carro)
#É possível adcionar um valor a um determinado atributo na nossa classe
#ex: metros_corridos , self.metros_corridos = 0 depois no final dizer quantos km o carro já andou.

class Car():
    def __init__(self,marca,modelo,ano):
        self.marca = marca
        self.modelo=modelo
        self.ano=ano 
    def descricao_carro(self):
       return f'Dados sobre o carro {self.marca},{self.modelo},{self.ano}'

meu_carro = Car('Suzuki','Express',2024)
print(meu_carro.descricao_carro())
    