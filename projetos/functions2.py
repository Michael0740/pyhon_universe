#def country(pais,cidade):
    # my_country = pais +""+cidade
    # return my_country
#while True: 
   # print('informe o seu País e a sua cidade')
   # print('se desejar finalizar basta digitar, q ')
    #pais = input('informe o sue país: ')
   # if pais == 'q':
    #    break 
   # cidade = input('informe a sua cidade: ')
   # if cidade == 'q':
       # break 
#minha_cidade = country (pais , cidade)
#print(f'bem-vindo(a) {minha_cidade}')    

def meu_album(nome_artista):
    albuns = {
        'Justin': {
            'album': 'Love',
            'Love': ['Song 1', 'Song 2']
        },
        'Drake': {
            'album': 'Scorpion',
            'Scorpion': ['Song 1', 'Song 2']
        },
        'Michael_Jackson':{
            'album': 'Thriller',
            'Thriller': ['Song 1', 'Song 2']
        }
        
    }

    if nome_artista in albuns:
        return albuns[nome_artista]
    else:
        return 'Artista não encontrado'


procurar_artista = input('Informe o nome do artista: ')

print(meu_album(procurar_artista))


    
    
    
    