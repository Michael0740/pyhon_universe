print("--------------------- INFO TECH GLOBAL ------------------------------")

p1 = int(input("Quantos computadores pretende comprar?0 "))
p2 = int(input("Quantos computadores pretendes instalar "))
v1 = int(p1 * 5000)
v2 = int(p2 * 8000)

vt = v1 + v2

print(f"O valor total é de {vt}")
if vt >= 30000:
    desc = float(vt * 10 / 100)
    vp = vt - desc
    print(f"Recebeu um desconto de 10% {desc}")
    print(f"Valor pago de {vp}")
    print("OBRIGADO PELA SUA PREFERÊNCIA")
    print("::::INFO TECH")
    print("O SEU FUTURO COMEÇA AQUI")
    
else:
    print("Sem desconto")
    print(f"Valor pago de {vt}")
    print("")