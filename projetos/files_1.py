#aqui irão constar todas as noções sobre manipulação de arquivos, leitura e escrita de arquivos, etc.

with open('notas.txt', 'r') as arquivo:
    notas = arquivo.read()
    print(notas)