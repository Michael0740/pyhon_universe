#desafio do diário, a ideia é criar um diário em que o úsuario possa escrever suas experiências, mas outras pessoas não podem ter acesso a não ser acessando com uma senha que será um atributo protegido da classe. O diário deve ter métodos para escrever, ler e alterar a senha. A senha deve ser alterada apenas se o usuário fornecer a senha atual correta.
#aplicar o atributo @property para criar um getter e setter para a senha, garantindo que ela seja protegida e só possa ser alterada com a senha atual correta.

class Diario:
    """Diário com senha protegida.

    Acesso ao conteúdo somente com a senha correta. A senha é um
    atributo privado e pode ser lida apenas de forma mascarada
    via `senha` (getter). Para alterar a senha, atribua uma tupla
    `(senha_atual, nova_senha)` à property `senha` — o setter
    valida a senha atual antes de atualizar.
    """

    def __init__(self, senha):
        self.__senha = senha
        self.conteudo = []

    @property
    def senha(self):
        return "****"

    @senha.setter
    def senha(self, value):
        # esperamos um par: (senha_atual, nova_senha)
        try:
            senha_atual, nova_senha = value
        except Exception:
            raise ValueError(
                "Para alterar a senha, atribua uma tupla: (senha_atual, nova_senha)"
            )
        if senha_atual != self.__senha:
            raise ValueError("Senha atual incorreta")
        self.__senha = nova_senha

    def _verificar_senha(self, senha):
        return senha == self.__senha

    def escrever(self, texto, senha):
        if not self._verificar_senha(senha):
            raise ValueError("Senha inválida")
        self.conteudo.append(texto)

    def ler(self, senha):
        if not self._verificar_senha(senha):
            raise ValueError("Senha inválida")
        return "\n".join(self.conteudo)

    def __repr__(self):
        return f"<Diario entradas={len(self.conteudo)}>"


if __name__ == "__main__":
    d = Diario("1234")
    # escrever e ler com senha correta
    d.escrever("Minha primeira entrada", "1234")
    print(d.ler("1234"))

    # tentativa de alterar senha com senha incorreta
    try:
        d.senha = ("errada", "9999")
    except Exception as e:
        print("Falha ao alterar senha:", e)

    # alterar senha corretamente
    d.senha = ("1234", "abcd")
    print("Senha alterada com sucesso")
    # ler com nova senha
    print(d.ler("abcd"))
            
            
            
        
    
    
    
    