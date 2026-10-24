print('--BEM-VINDO A NOSSA LOJA TECH--')

class vendas:
    def __init__(self,produto,preco,desconto):
        self.produto = produto 
        self.preco = preco 
        self.desconto = desconto
    def info_vendas(self):
        return f'produto:{self.produto}, preco:{self.preco}, desconto:{self.desconto}'
    
    def descontos(self):
        if self.preco > 300:
            
          print(f'você recebeu um desconto de 10%  ')
          total_preco = self.preco/0.1 
          print('você vai pagar',+total_preco )
        else: 
            print('Não há desconto')
            
        
resultado = vendas('HP elitBook',400, '10%')
print(resultado.descontos())
     