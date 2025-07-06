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
                linha = " ".join([str(round(random.uniform(-2, 2), 2)) for _ in range(5)])
                f.write(linha + "\n")

    pesos_ia = {}
    with open("pesos_sinapticos.txt", "r") as f:
        for idx, linha in enumerate(f.readlines()):
            numeros = [float(x) for x in linha.strip().split()]
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
        mutacao = round(random.uniform(-1, 1), 3)
        novos_pesos.append(p + mutacao)
    return novos_pesos


def decidir_acao(numero_dino, altura, distancia, velocidade):
    pesos = pesos_ia[numero_dino]
    soma = altura * pesos[0] + distancia * pesos[1] + velocidade * pesos[2] + pesos[3]
    soma = max(0, soma)
    saida = soma * pesos[4]

    
    if saida < -0.33:
        return 1
    elif saida > 0.33:
        return -1
    else:
        return 0


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
        dino_game.start_game()
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
                tempo_abaixado[i] = int(30 - dino_game.velocidade_atual / 2)  # Tempo de abaixar ajustável
                if tempo_abaixado[i] < 5:
                    tempo_abaixado[i] = 5  # Limite mínimo para não zerar
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