#aqui irão constar todas as noções sobre manipulação de arquivos, leitura e escrita de arquivos, etc.

with open('notas.txt', 'r') as arquivo:
    lines = arquivo.read()
    print(lines)
    print(len(lines)) #é possível contar a quantidade de caracteres do arquivo, mas não a quantidade de linhas. Para isso, é necessário utilizar o método readlines().
    
# na minipulação de arquivos, é possível adcionar, remover e alterar o conteúdo do arquivo. Para isso, é necessário abrir o arquivo no modo de escrita ('w') ou no modo de adição ('a'). O modo de escrita irá sobrescrever o conteúdo do arquivo, enquanto o modo de adição irá adicionar o conteúdo ao final do arquivo.
#pode -se utilizar o método write() para escrever no arquivo, e o método writelines() para escrever várias linhas de uma vez. O método writelines() recebe uma lista de strings como argumento, e cada string será escrita em uma linha do arquivo.
# com o readlines é possível ler arquivos muito grandes, pois ele lê o arquivo linha por linha, e não todo de uma vez. O método readlines() retorna uma lista de strings, onde cada string é uma linha do arquivo.

with open('my_produts.txt', 'r', encoding='utf-8') as arquivo:
    text = arquivo.readlines()
    print(text)
for linha in text:
    if linha == 'Produto 1\n':
        print('Produto 1 encontrado!')
        
#encoding resolve problemas de acentuação, como por exemplo, quando o arquivo contém caracteres especiais. Para isso, é necessário abrir o arquivo com o parâmetro encoding='utf-8'.