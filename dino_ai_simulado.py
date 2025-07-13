import random
import os
import math
from dino_simulador import main_offscreen

NUM_DINOS = 50
ARQUIVO_PESOS = "pesos_sinapticos.txt"
NUM_PESOS = 23

def gerar_pesos_aleatorios():
    return [random.uniform(-2, 2) for _ in range(NUM_PESOS)]

def carregar_pesos():
    if not os.path.exists(ARQUIVO_PESOS):
        pesos_iniciais = [gerar_pesos_aleatorios() for _ in range(NUM_DINOS)]
        with open(ARQUIVO_PESOS, "w") as f:
            for pesos in pesos_iniciais:
                f.write(" ".join(str(round(p, 2)) for p in pesos) + "\n")

    pesos_ia = {}
    with open(ARQUIVO_PESOS, "r") as f:
        linhas = f.readlines()
        for idx in range(NUM_DINOS):
            if idx < len(linhas):
                pesos = [float(x) for x in linhas[idx].strip().split()]
            else:
                pesos = gerar_pesos_aleatorios()
            pesos_ia[idx] = pesos
    return pesos_ia

def salvar_quatro_melhores(resultados, pesos_ia):
    melhores = sorted(resultados, key=lambda x: -x[1])[:4]
    with open(ARQUIVO_PESOS, "w") as f:
        for i, _ in melhores:
            base = pesos_ia[i]
            f.write(" ".join(str(round(p, 2)) for p in base) + "\n")
        # Completa com mutações dos melhores
        while len(melhores) < NUM_DINOS:
            base = random.choice(melhores)[0]
            mutado = mutar_pesos(pesos_ia[base])
            f.write(" ".join(str(round(p, 2)) for p in mutado) + "\n")
            melhores.append((len(melhores), 0))  # placeholder
    print("Pesos atualizados com os 4 melhores e variações.")

def sigmoid(x):
    return 1 / (1 + math.exp(-max(min(x, 700), -700)))

def relu(x):
    return max(0, x)

def decidir_acao(entrada, pesos):
    altura, distancia, velocidade = entrada
    hidden1 = []
    for i in range(3):
        soma = sum(entrada[j] * pesos[i * 4 + j] for j in range(3)) + pesos[i * 4 + 3]
        hidden1.append(relu(soma))

    hidden2 = []
    offset = 12
    for i in range(2):
        soma = sum(hidden1[j] * pesos[offset + i * 4 + j] for j in range(3)) + pesos[offset + i * 4 + 3]
        hidden2.append(relu(soma))

    offset = 20
    soma_saida = sum(hidden2[j] * pesos[offset + j] for j in range(2)) + pesos[offset + 2]
    saida = sigmoid(soma_saida)

    if saida < 0.33:
        return -1
    elif saida > 0.66:
        return 1
    else:
        return 0

def mutar_pesos(pesos):
    return [p + random.uniform(-0.5, 0.5) for p in pesos]

def action_generator_factory(pesos_ia):
    def gerar_acoes(jogadores, obstaculos, game_speed, pontos):
        acoes = []
        for idx, dino in enumerate(jogadores):
            if not dino["vivo"] or idx not in pesos_ia:
                acoes.append(0)
                continue
            if not obstaculos:
                acoes.append(0)
                continue
            obs = obstaculos[0]
            altura = dino["y"]
            distancia = obs["x"] - 150  # posição X fixa para todos os dinos
            entrada = [altura, distancia, game_speed]
            acao = decidir_acao(entrada, pesos_ia[idx])
            acoes.append(acao)
        return acoes
    return gerar_acoes

# Execução principal
print("Iniciando simulação offscreen da IA do Dino...")

pesos_ia = carregar_pesos()
action_gen = action_generator_factory(pesos_ia)
vencedor, pontuacao = main_offscreen(action_gen)

print(f"\nÚltimo dino vivo: {vencedor}, velocidade final: {pontuacao}")

# Pontuação de todos os dinos
resultados = []
for i in range(NUM_DINOS):
    if i == vencedor:
        resultados.append((i, pontuacao))
    else:
        resultados.append((i, random.randint(10, pontuacao - 1)))  # simula pontuação intermediária

salvar_quatro_melhores(resultados, pesos_ia)
print("Simulação concluída.")
