#rb e wb geram dados binários, enquanto r e w geram dados de texto.
from cryptography.fernet import Fernet

with open('extrato_bancario.txt', 'rb') as arquivo:
    ...
  