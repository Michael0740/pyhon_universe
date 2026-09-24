#neste arquivo irei treinar o uso de propriedades em python
from aula_poli_abs import Avaliacao

def main():
    avaliacao = Avaliacao('João','Matemática')
    avaliacao.nota = 6
    print(f'Nome: {avaliacao.nome}, Disciplina: {avaliacao.disciplina}, Nota: {avaliacao.nota}')

if __name__ == '__main__':
    main()    