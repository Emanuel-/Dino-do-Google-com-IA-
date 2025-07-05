import tkinter as tk
import threading
import time
import random
import dino_game
import os
import math

jogo_rodando = False
ciclo_automatico = True  # Controla se o jogo reinicia sozinho
pesos_ia = {}  # Dicionário global que armazena os pesos de cada dino
ultimo_vivo = None
mensagem_vencedor_exibida = False

def carregar_pesos():
    global pesos_ia
    if not os.path.exists("pesos_sinapticos.txt"):
        with open("pesos_sinapticos.txt", "w") as f:
            for _ in range(4):
                linha = " ".join([str(round(random.uniform(-2, 2), 2)) for _ in range(5)])
                f.write(linha + "\n")

    pesos_ia = {}
    with open("pesos_sinapticos.txt", "r") as f:
        for idx, linha in enumerate(f.readlines()):
            numeros = [float(x) for x in linha.strip().split()]
            pesos_ia[idx] = numeros
            print(f"Pesos Dino {idx}: {pesos_ia[idx]}")

def salvar_pesos():
    with open("pesos_sinapticos.txt", "w") as f:
        for idx in range(4):
            linha = " ".join([str(round(p, 2)) for p in pesos_ia[idx]])
            f.write(linha + "\n")

def mutar_pesos(pesos):
    novos_pesos = []
    for p in pesos:
        mutacao = round(random.uniform(-2, 2), 2)
        novos_pesos.append(p + mutacao)
    return novos_pesos

def decidir_acao(numero_dino, altura, distancia, velocidade):
    pesos = pesos_ia[numero_dino]

    soma = (
        altura * pesos[0] +
        distancia * pesos[1] +
        velocidade * pesos[2] +
        pesos[3]  # Bias escondido
    )

    soma = max(0, soma)  # Ativação ReLU

    saida = soma * pesos[4]

    if saida < -0.33:
        return -1  # Abaixar
    elif saida > 0.33:
        return 1   # Pular
    else:
        return 0   # Fazer nada

def iniciar_jogo():
    global jogo_rodando, ultimo_vivo, mensagem_vencedor_exibida

    if jogo_rodando:
        print("O jogo já está rodando.")
        return

    jogo_rodando = True
    ultimo_vivo = None
    mensagem_vencedor_exibida = False
    label_vencedor.config(text="")
    botao_iniciar.config(state=tk.DISABLED)

    def rodar_jogo():
        time.sleep(1)
        dino_game.start_game()
        global jogo_rodando
        jogo_rodando = False

        if ciclo_automatico:
            time.sleep(6)
            janela.after(0, resetar_vencedor)
            janela.after(0, iniciar_jogo)
        else:
            janela.after(0, botao_iniciar.config, {"state": tk.NORMAL})

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
            acao = decidir_acao(i, status['altura'], status['distancia'], dino_game.velocidade_atual)

            if acao == 1 and not dino_game.players[i].dino_jump:
                dino_game.players[i].dino_duck = False
                dino_game.players[i].dino_run = False
                dino_game.players[i].dino_jump = True

            elif acao == -1 and not dino_game.players[i].dino_jump:
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

        # Atualiza pesos dos dinos
        pesos_vencedor = pesos_ia[ultimo_vivo]
        for i in range(4):
            if i == ultimo_vivo:
                pesos_ia[i] = pesos_vencedor
            else:
                pesos_ia[i] = mutar_pesos(pesos_vencedor)

        salvar_pesos()
        print("Pesos atualizados e salvos.")
        print(pesos_ia)

    janela.after(200, atualizar_info)

def resetar_vencedor(event=None):
    global ultimo_vivo, mensagem_vencedor_exibida
    label_vencedor.config(text="")
    ultimo_vivo = None
    mensagem_vencedor_exibida = False

def parar_ciclo():
    global ciclo_automatico
    ciclo_automatico = False
    botao_iniciar.config(state=tk.NORMAL)

# Interface Tkinter
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

carregar_pesos()
atualizar_info()
janela.bind("<Key>", resetar_vencedor)
janela.mainloop()
