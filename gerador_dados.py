import random

# --- Função determinística usada como "ideal"
def decidir_acao(altura, distancia, velocidade, tipo_obstaculo, largura=None):
    if distancia is None or distancia <= 0:
        return "nothing"

    fator = velocidade / 20

    if tipo_obstaculo == 7:  # pássaro baixo
        if distancia <= 315 * fator:
            return "jump"
    elif tipo_obstaculo == 6:  # pássaro médio
        if distancia <= 315 * fator:
            return "duck"
    elif tipo_obstaculo == 5:  # pássaro alto
        if distancia <= 315 * fator:
            return "nothing"
    elif tipo_obstaculo in [0, 1, 2, 3, 4]:
        limiares = {0: 325, 1: 320, 2: 310, 3: 310, 4: 310}
        if distancia <= limiares[tipo_obstaculo] * fator:
            return "jump"
    return "nothing"

# --- Tipos de obstáculos por categoria de ação
TIPOS_PULO = [0, 1, 2, 3, 4]
TIPOS_ABAIXAR = [6]
TIPOS_NADA = [5, 6, 7, 0, 1, 2, 3, 4]

# --- Função que gera um único exemplo
def gerar_exemplo(velocidade, acao_esperada):
    fator = velocidade / 20

    if acao_esperada == "jump":
        tipo = random.choice(TIPOS_PULO)
        distancia = random.uniform(1, {0:325, 1:320, 2:310, 3:310, 4:310}[tipo] * fator * 0.95)

    elif acao_esperada == "duck":
        tipo = 6
        distancia = random.uniform(1, 315 * fator * 0.95)

    else:  # "nothing"
        tipo = random.choice(TIPOS_NADA)
        limiar = {0:325, 1:320, 2:310, 3:310, 4:310, 5:315, 6:315, 7:315}[tipo]
        distancia = random.uniform(limiar * fator * 1.05, 1260)

    altura = random.randint(100, 350)
    largura = random.randint(20, 80)

    saida = decidir_acao(altura, distancia, velocidade, tipo, largura)

    return {
        "velocidade": velocidade,
        "distancia": round(distancia, 2),
        "tipo": tipo,
        "altura": altura,
        "largura": largura,
        "saida": saida
    }

# --- Função para gerar a base inteira com proporção 1/3 para cada ação
def gerar_base_simples(velocidade=20, total=900):
    exemplos = []

    for acao in ["jump", "duck", "nothing"]:
        for _ in range(total // 3):
            exemplos.append(gerar_exemplo(velocidade, acao))

    random.shuffle(exemplos)
    return exemplos
