#aqui faremos alguns exercicios com funções
#iremos chamar uma função dentro de outra função
#def saudacao(nome):
    #return f"Olá, {nome}!" 
#def boas_vindas(nome):
    #return saudacao(nome) + " Seja bem-vindo(a)!"
#saudacao_usuario = boas_vindas("João")
#print(saudacao_usuario)
#quando se quer que uma função receba as funcionalidades de outra é importante usar o 
#return 
#def calcular_dobro(numero):
    #return numero * 2
#def mostrar_resultado():
    #resultado = calcular_dobro(10)
    #onde calcular_dobro (atribuimos um valor ao seu atributo numero sendo 10)
    #print(f"O dobro é: {resultado}")
#mostrar_resultado()
#sempre usar o lower ou strip em nossos projetos 
def info_paciente(nome,idade,sexo):
    print('Bem vindo ao nosso consultório fictício')
    print(f'dados paciente: {nome},{idade},{sexo}')
    return {'nome':nome , 'idade':idade , 'sexo':sexo}  
def consulta():
    dados_paciente = info_paciente('Ana',22,'F')
    print(dados_paciente)    
    escolha_doenca = input('Diga qual doença tem: ').strip().lower()
    tipos_doenca = {
        'paludismo': {'recomendações': ['remedio x', 'remedio y']},
        'dengue': {'recomendações': ['remedio x', 'remedio y']},
    }
    if escolha_doenca in tipos_doenca:
        return tipos_doenca[escolha_doenca]
    else:
        print('doença não registrada')
        return None

resultado = consulta()
print(resultado)

    
  