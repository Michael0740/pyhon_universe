#saber importar modulos 
#antes de importar uma determinada função é necessario criar um modulo
#modulo refere-se a um arquivo.py que a gente cria para depois captar a sua função 
#em um outro projeto sem a necessidade de voltar a criar a função.
# exemplo: from functions3 import consulta_medica 
#é possível criar mais de uma função e chamar sempre que necessario em um outro projeto.
#att para que isto aconteça há necessidade do arquivo estar no mesmo diretorio se possível
#há diferença entre importar uma função específica de toda uma função de um código
#import functions4 => importa todo o código e funcionalidade do arquivo 
#from functions4 import make_pizza => neste caso estamos importando uma função específica
#normalmente quando estamos trabalhando com projetos muito grandes pode se dar o caso da função
#que estamos importando tenha o mesmo nome de uma já existente neste caso podemos 
#dar um apelido a nossa função usando o "as" => significa "como/ tal que"
#exemplo: from functions4 import make_pizza as mp (ou um outro nome qualquer)
#formula : from module_name import function_name as fn
#import pizza as p
#form pizza import * => permite importar todas as funções de um código (mas é melhor especificar que função você quer usar para não causar erros futuros)
#em uma função não se pode exceder mais de 79 linhas de código
def make_pizza(size, *toppings):
#"""Summarize the pizza we are about to make."""
  print("\nMaking a " + str(size) + "-inch pizza with the following toppings:")
  for topping in toppings:
    print("- " + topping)
    
