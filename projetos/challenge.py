#lista = [1,2,3,4,5]
#print(len(lista))

#def meu_album(nome_artista):
    #albuns = {
       # 'Justin': {
       #     'album': 'Love',
        #    'Love': ['Song 1', 'Song 2']
       # },
       # 'Drake': {
         #   'album': 'Scorpion',
         #   'Scorpion': ['Song 1', 'Song 2']
       # },
        #'Michael_Jackson':{
        #    'album': 'Thriller',
        #    'Thriller': ['Song 1', 'Song 2']
        #}
        
    #}

    #if nome_artista in albuns:
        #return albuns[nome_artista]
    #else:
       # return 'Artista não encontrado'


#procurar_artista = input('Informe o nome do artista: ')

#print(meu_album(procurar_artista))
class album:
    def __init__(self,titulo_album,ano_lancamento,editora,autor):
        self.titulo_album = titulo_album 
        self.ano_lancamento = ano_lancamento 
        self.editora = editora
        self.autor = autor 
    def sobre_artista(self):
        print(f'o nome do artista é {self.autor}')
        
    def meu_album(nome_artista):
     albuns = {
        'Justin': {
           'album': 'Love',
           'Love': ['Song 1', 'Song 2']
         },
    }
       
     if nome_artista in albuns:
        return albuns[nome_artista]
     else:
        return 'Artista não encontrado'

music = album('Triller',2024,'SSmusic','Michael Jackson')
music.sobre_artista()
print(music)