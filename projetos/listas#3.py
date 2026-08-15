#players=['ALice','Diana','Sebastião','Adriano']
#print('estes são os três primeiros jogadores do meu team:')
#for player in players[:3]:
    #print(player.title())
    
    
#Em um team de futebol há varios jogadores de diversas nações diferentes.
#criar uma lista de jogadores de um clube e criar uma outra especificando cada jogador numa 
#seleção de futebol 

#jogadores_clube=['José','Marcos','Luís','Carlos','Afonso','Cristiano','Bruno']
#jogador_portugal = jogadores_clube[3:6] 
#print('estes são os jogadores de Portugal que atuam no nosso clube: ')
#for tuga_player in jogador_portugal:
    #print(tuga_player.title())
    
#aliens = ['megatron','vilgax','kaguya','Momoshiki']
#for alien in aliens:
    #print(alien)

#alien_morto = int(input('mate um desses aliens: '))
#alien_morto = aliens.pop(0)
#print(f'voce matou o alien {alien_morto}  ')
aliens = ['megatron', 'vilgax', 'kaguya', 'Momoshiki']

while aliens:
    print("\nAliens disponíveis:")

    for i, alien in enumerate(aliens):
        print(f"{i} - {alien}")

    escolha = int(input("Escolha o alien que quer matar: "))

    alien_morto = aliens.pop(escolha)

    print(f"\n Você matou o alien {alien_morto}!")

    print(f" Faltam {len(aliens)} aliens.")

print("\n Você matou todos os aliens!")
    