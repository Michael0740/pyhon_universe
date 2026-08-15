#mover os itens de uma lista para outra 
#suponhamos que alguém cadastre-se num site como fazer com que este user saia dos usuarios 
#inativos para os ativos ? 
#user_inativo = ['Domingas','Josemar','Dercio','Adriano']
#user_ativos =[]
#while user_inativo : 
    #user_atual = user_inativo.pop()
    #print(f'verificando o usuario {user_atual.title()}')
    #user_ativos.append(user_atual)
    #print('estes são os users confirmados \n')
    #for user_ativo in user_ativos: 
        #print(user_ativo)

#uma loja com alguns produtos 
produtos = {'capa-iphone':5000 , 'pelicula':4500 , 'fones':8000}
compras ={}
print('---bem vindo a kambaStore---')
for produto in produtos: 
    print(produto)
    
nome = input('Informe o seu nome: ')
print(f'bem vindo(a) a Kambastore Sr(a) {nome} ')
    
    
while True : 
   
    escolha =input('que produto deseja comprar: ')
    if escolha in produtos : 
        preco = produtos[escolha]
        print(f'o produto {escolha} custa {preco} Kz')
        quantidade = int(input('quantas unidades tenciona levar:'))
        total = preco * quantidade 
        print(f'o senhor(a){nome} irá pagar {total} pelo produto {escolha}')
        compras[escolha]=quantidade
        
        print(f'compra do produto {escolha} concluido')
        print(f'finalizado {compras}')
        
        continuar = input('tenciona continuar comprando? (s/n)')
        
        if continuar == 'n':
            break
            
    else: 
        print('Não temos este produto')
   
 
    
    

    