#aqui irá constar todos os desafios de orientação objeto com o python 
#iremos rever alguns conceitos de funções 
#iremos também praticar conceitos de herança 

class Pai():
    def __init__(self,nome,idade):
        self.nome = nome 
        self.idade = idade 


class Guarda_roupa():
    def __init__(self,camisa='lacoste',tenis='nike',terno='terno azul'):
        self.camisa = camisa
        self.tenis = tenis
        self.terno = terno 
        
    def sobre_armario(self): 
        return f'no meu armario tem {self.camisa}, {self.tenis}, {self.terno} '


        
class Filho(Pai):
    def __init__(self, nome, idade):
        super().__init__(nome, idade)
        #este é o método para chamar uma função dentro da outra
        self.armario = Guarda_roupa()
  
    def about_me(self):
        return f'olá o meu nome é {self.nome} , estou com {self.idade} anos de idade '

#meus_dados = Filho('Alberto',21)
#print(meus_dados.about_me())
#print(meus_dados.armario.sobre_armario())




    
    

        