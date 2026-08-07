bicicletas = ['trek','cannondale','redline']
#bicicletas[0]='Redbull', neste caso estamos substituindo um valor pelo outro.
#contrariamente a este caso, temos a opção de adcionar o item novo a lista com o append
bicicletas.append('Redbull')
#del bicicletas[0], remover o elemento de uma lista caso a gente saiba a sua posição
#o método pop permite eliminar o último iten de uma lista, também é posivel remover de qualquer posição
#sorte ordenar uma lista, reverse=true => apresenta a lista na ordem contraria
#len permite saber o número de elementos de uma lista.
first_bike = bicicletas.pop(0)
print(f'a minha primeira bicicleta foi um {first_bike}')


#lista =[]
#itens = str(input('digite um item para a lista: '))
#lista.append(itens)
#print(lista)
