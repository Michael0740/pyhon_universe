# Estudo de classes em Python
# Objetivo:
# - Criar a classe Produto para representar um item da loja
# - Criar a classe Compras para representar uma compra de cliente

class Produto:
    def __init__(self, nome_produto, tipo, preco, validade, estoque):
        self.nome_produto = nome_produto
        self.tipo = tipo
        self.preco = preco
        self.validade = validade
        self.estoque = estoque

    def info_produto(self):
        return (
            f"Nome: {self.nome_produto}\n"
            f"Tipo: {self.tipo}\n"
            f"Preço: R$ {self.preco:.2f}\n"
            f"Validade: {self.validade}\n"
            f"Estoque: {self.estoque}"
        )

    def disponibilidade(self):
        if self.estoque > 0:
            return f"O produto {self.nome_produto} está disponível em estoque."
        return f"O produto {self.nome_produto} não está disponível em estoque."

    def __str__(self):
        return self.info_produto()


class Compras:
    def __init__(self, comprador, produtos=None):
        self.comprador = comprador
        self.produtos = produtos if produtos is not None else []
        self.quantidade = len(self.produtos)
        self.valor_total = sum(produto.preco for produto in self.produtos)

    def compra_info(self):
        return (
            f"Comprador: {self.comprador}\n"
            f"Itens: {self.quantidade}\n"
            f"Valor total: R$ {self.valor_total:.2f}"
        )

    def adicionar_produto(self, produto):
        self.produtos.append(produto)
        self.quantidade += 1
        self.valor_total += produto.preco
        return (
            f"Produto {produto.nome_produto} adicionado à compra.\n"
            f"Total de itens: {self.quantidade}\n"
            f"Valor total: R$ {self.valor_total:.2f}"
        )

    def __str__(self):
        return self.compra_info()


# Criando objetos da classe Produto
casaco = Produto("Casaco", "roupa", 2000, "02/12/25", 24)
bota = Produto("Bota", "calçado", 5000, "10/12/25", 3)

# Exibindo o objeto com print(casaco)
print("=== Produto ===")
print(casaco)
print()

# Verificando disponibilidade
print(casaco.disponibilidade())
print()

# Criando uma compra
minha_compra = Compras("Maria", [casaco, bota])
print("=== Compra ===")
print(minha_compra)
print()

# Adicionando mais um item
print(minha_compra.adicionar_produto(Produto("Camisa", "roupa", 150, "10/09/26", 18)))
    