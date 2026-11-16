
def abrir_aquivo():
    with open('projetos/notas.txt' , 'r') as file: 
        resultado = file.read()
        return resultado.rstrip()
    
open_file = abrir_aquivo()
print(open_file)