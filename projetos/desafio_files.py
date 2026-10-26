#rb e wb geram dados binários, enquanto r e w geram dados de texto.
from cryptography.fernet import Fernet
import os

arquivo = 'extrato_bancario.txt'
arquivo_chave = 'chave.key'

#agora criar uma função para gerar a chave de criptografia
def carregar_ou_gerar_chave():
    """Gera a chave automaticamente se ainda não existir."""
    if not os.path.exists(arquivo_chave):
        chave = Fernet.generate_key()
        with open(arquivo_chave, "wb") as f:
            f.write(chave)
    with open(arquivo_chave, "rb") as f:
        return f.read()


  