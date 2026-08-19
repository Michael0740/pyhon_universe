#def get_name(names):
    #for name in names : 
        #msg = 'olá' +name+ ''
        #print(msg)
        
#user_name = ['Ana','Mateus','José']
#get_name(user_name)
#treinar exercícios para ter a capacidade de trabalhar com duas funções em simultâneo





def consulta_medica(nome_paciente,idade_paciente,sexo_paciente,doencas): 
    print('---Bem-vindo_(a) ao sistema de consultas---')
    print(f'Dados do paciente, nome: {nome_paciente}, idade:{idade_paciente},sexo: {sexo_paciente}, doença: {doencas}')
    tipos_doenca = ['paludismo','diabetes','Dengue']
    doenca_escolhida = input('informe que tipo de doença você tem?')
    if doenca_escolhida in tipos_doenca: 
        print('você precisa tomar esses remedios:')
        remedios = {
            'paludismo':{
                'recomendação':['paracetamol']
            }
        }
        print(remedios)
    else: 
        print('doença não encontrada')
print(consulta_medica('Ana',20,'F'))

