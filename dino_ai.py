import tkinter as tk
import threading
import time
import random
import dino_game
import os
import math


jogo_rodando = False
ciclo_automatico = True  # Controla se o jogo reinicia sozinho
pesos_ia = {}  # dicionário global que armazena os pesos de cada dino
melhor_pontuacao = 0  # Guarda a maior velocidade já atingida
tempo_abaixado = {
    0: 0,
    1: 0,
    2: 0,
    3: 0
}


def carregar_pesos():
    global pesos_ia
    if not os.path.exists("pesos_sinapticos.txt"):
        with open("pesos_sinapticos.txt", "w") as f:
            for _ in range(4):
                linha = " ".join([str(round(random.uniform(-2, 2), 2)) for _ in range(23)])
                f.write(linha + "\n")

    pesos_ia = {}
    with open("pesos_sinapticos.txt", "r") as f:
        for idx, linha in enumerate(f.readlines()):
            numeros = [float(x) for x in linha.strip().split()]
            if len(numeros) != 23:
                raise ValueError(f"Esperado 23 pesos por dino, mas encontrei {len(numeros)} na linha {idx+1}")
            pesos_ia[idx] = numeros



def salvar_pesos(pesos_vencedor):
    with open("pesos_sinapticos.txt", "w") as f:
        for idx in range(4):
            if idx == 0:
                linha = " ".join([str(round(p, 2)) for p in pesos_vencedor])
            else:
                novos_pesos = mutar_pesos(pesos_vencedor)
                linha = " ".join([str(round(p, 2)) for p in novos_pesos])
            f.write(linha + "\n")


def mutar_pesos(pesos):
    novos_pesos = []
    for p in pesos:
        mutacao = round(random.uniform(-2, 2), 3)
        novos_pesos.append(p + mutacao)
    return novos_pesos



import math

import math

def sigmoid(x):
    # Limita o valor de x para evitar overflow
    if x < -700:
        x = -700
    elif x > 700:
        x = 700
    return 1 / (1 + math.exp(-x))


def relu(x):
    return max(0, x)

def decidir_acao(numero_dino, altura, distancia, velocidade):
    pesos = pesos_ia[numero_dino]

    # ------------------------------
    # Primeira camada oculta (3 neurônios)
    entradas = [altura, distancia, velocidade]
    hidden1 = []
    for i in range(3):
        soma = sum(entradas[j] * pesos[i * 4 + j] for j in range(3)) + pesos[i * 4 + 3]
        hidden1.append(relu(soma))

    # ------------------------------
    # Segunda camada oculta (2 neurônios)
    hidden2 = []
    offset = 12
    for i in range(2):
        soma = sum(hidden1[j] * pesos[offset + i * 4 + j] for j in range(3)) + pesos[offset + i * 4 + 3]
        hidden2.append(relu(soma))

    # ------------------------------
    # Camada de saída
    offset = 20
    soma_saida = sum(hidden2[j] * pesos[offset + j] for j in range(2)) + pesos[offset + 2]
    saida = sigmoid(soma_saida)

    # ------------------------------
    # Regra de decisão final
    if saida < 0.33:
        return -1  # abaixar
    elif saida > 0.66:
        return 1   # pular
    else:
        return 0   # correr normal



def iniciar_jogo():
    global jogo_rodando, ultimo_vivo, mensagem_vencedor_exibida

    if jogo_rodando:
        return

    jogo_rodando = True
    ultimo_vivo = None
    mensagem_vencedor_exibida = False
    label_vencedor.config(text="")
    botao_iniciar.config(state=tk.DISABLED)

    def rodar_jogo():
        time.sleep(1)
        dino_game.start_game(modo_ia_param=True)

        global jogo_rodando, melhor_pontuacao
        jogo_rodando = False

        if ultimo_vivo is not None:
            pontuacao = dino_game.velocidade_atual
            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                salvar_pesos(pesos_ia[ultimo_vivo])
                print(f"Novo melhor desempenho: Velocidade {pontuacao}")
            else:
                print(f"Desempenho {pontuacao} não superou o melhor {melhor_pontuacao}")
                carregar_pesos()

        if ciclo_automatico:
            time.sleep(2)
            iniciar_jogo()
        else:
            botao_iniciar.config(state=tk.NORMAL)

    threading.Thread(target=rodar_jogo).start()


def atualizar_info():
    global ultimo_vivo, mensagem_vencedor_exibida

    if not hasattr(dino_game, "players") or len(dino_game.players) < 4:
        janela.after(200, atualizar_info)
        return

    vivos = []
    for i in range(4):
        status = dino_game.dino_status[i]
        vivo = "Vivo" if dino_game.players[i].alive else "Morto"
        texto = f"Dino {i+1} - Distância: {status['distancia']}  Altura: {status['altura']}  Status: {vivo}"
        labels_dino[i].config(text=texto)

        if dino_game.players[i].alive:
            vivos.append(i)

            # Se ainda está no tempo de abaixar, mantém abaixado
            if tempo_abaixado[i] > 0:
                tempo_abaixado[i] -= 1
                dino_game.players[i].dino_duck = True
                dino_game.players[i].dino_run = False
                dino_game.players[i].dino_jump = False
                continue  # Pula o resto do loop e não decide nova ação ainda

            acao = decidir_acao(i, status['altura'], status['distancia'], dino_game.velocidade_atual)

            if acao == 1 and not dino_game.players[i].dino_jump:
                dino_game.players[i].dino_duck = False
                dino_game.players[i].dino_run = False
                dino_game.players[i].dino_jump = True

            elif acao == -1 and not dino_game.players[i].dino_jump:
                tempo_abaixado[i] = 5  # Dino ficará abaixado por 5 ciclos de atualização (~1 segundo)
                dino_game.players[i].dino_duck = True
                dino_game.players[i].dino_run = False
                dino_game.players[i].dino_jump = False

            elif acao == 0 and not dino_game.players[i].dino_jump:
                dino_game.players[i].dino_duck = False
                dino_game.players[i].dino_run = True
                dino_game.players[i].dino_jump = False

    label_velocidade.config(text=f"Velocidade: {dino_game.velocidade_atual}")

    if len(vivos) == 1:
        ultimo_vivo = vivos[0]

    if len(vivos) == 0 and ultimo_vivo is not None and not mensagem_vencedor_exibida:
        label_vencedor.config(text=f"Dino {ultimo_vivo + 1} venceu!")
        mensagem_vencedor_exibida = True

    janela.after(200, atualizar_info)



def parar_ciclo():
    global ciclo_automatico
    ciclo_automatico = False
    botao_iniciar.config(state=tk.NORMAL)

# Interface
janela = tk.Tk()
janela.title("Controle IA - Dino Game")
janela.geometry("400x400")

botao_iniciar = tk.Button(janela, text="Iniciar Jogo", command=iniciar_jogo, font=("Arial", 14))
botao_iniciar.pack(pady=10)

botao_parar = tk.Button(janela, text="Parar Ciclo Automático", command=parar_ciclo, font=("Arial", 12), fg="red")
botao_parar.pack(pady=5)

labels_dino = []
for i in range(4):
    lbl = tk.Label(janela, text=f"Dino {i+1} - Distância: -  Altura: -", font=("Arial", 12))
    lbl.pack()
    labels_dino.append(lbl)

label_velocidade = tk.Label(janela, text="Velocidade: -", font=("Arial", 12))
label_velocidade.pack(pady=10)

label_vencedor = tk.Label(janela, text="", font=("Arial", 14), fg="green")
label_vencedor.pack(pady=10)

ultimo_vivo = None
mensagem_vencedor_exibida = False
carregar_pesos()
atualizar_info()
janela.mainloop()