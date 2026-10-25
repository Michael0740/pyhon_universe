#aqui irão constar todas as noções sobre manipulação de arquivos, leitura e escrita de arquivos, etc.

with open('notas.txt', 'r') as arquivo:
    lines = arquivo.read()
    print(lines)
    print(len(lines)) #é possível contar a quantidade de caracteres do arquivo, mas não a quantidade de linhas. Para isso, é necessário utilizar o método readlines().
    
