# exercício da biblioteca, desafio de lógica

def verificar_disponibilidade(livro, estoque):
    """Devolve a quantidade disponível (0 se não existe ou está zerado)."""
    if livro in estoque:
        return estoque[livro]
    else:
        return 0


def emprestimo_livro(livro, estoque):
    """Usa verificar_disponibilidade para decidir se empresta."""
    quantidade = verificar_disponibilidade(livro, estoque)

    if livro not in estoque:
        return f'O livro "{livro}" não está cadastrado no estoque.'
    elif quantidade > 0:
        estoque[livro] -= 1
        return f'Empréstimo realizado com sucesso! Restam {estoque[livro]} unidade(s).'
    else:
        return f'O livro "{livro}" não está disponível para empréstimo no momento.'


def atendimento_cliente(estoque):
    """Orquestradora: interage com o usuário e delega a lógica."""
    print('Bem-vindo à nossa livraria')
    procurar_livro = input('Que livro você está procurando?\n ')

    resultado = emprestimo_livro(procurar_livro, estoque)
    print(resultado)


estoque_inicial = {
    'O Pequeno Príncipe': 5,
    'Dom Casmurro': 3,
    '1984': 0,
}

atendimento_cliente(estoque_inicial)