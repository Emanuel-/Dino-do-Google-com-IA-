import tkinter as tk
import threading
import time
import random
import dino_game
import os

jogo_rodando = False
ciclo_automatico = True
pesos_ia = {}
melhor_pontuacao = 0
melhor_pesos = None
ultimo_pesos = None
tempo_abaixado = {0: 0, 1: 0, 2: 0, 3: 0}


def carregar_pesos():
    global melhor_pesos, pesos_ia
    if not os.path.exists("pesos_sinapticos.txt"):
        with open("pesos_sinapticos.txt", "w") as f:
            linha = " ".join([str(round(random.uniform(-2, 2), 2)) for _ in range(5)])
            f.write(linha + "\n")
        melhor_pesos = [random.uniform(-2, 2) for _ in range(5)]
    else:
        with open("pesos_sinapticos.txt", "r") as f:
            linha = f.readline().strip()
            melhor_pesos = [float(x) for x in linha.split()]

    atualizar_pesos()


def atualizar_pesos():
    global pesos_ia
    pesos_ia = {}
    # Melhor histórico
    pesos_ia[0] = melhor_pesos.copy()
    pesos_ia[1] = mutar_pesos(melhor_pesos)

    # Último vencedor
    if ultimo_pesos:
        pesos_ia[2] = ultimo_pesos.copy()
        pesos_ia[3] = mutar_pesos(ultimo_pesos)
    else:
        pesos_ia[2] = [random.uniform(-2, 2) for _ in range(5)]
        pesos_ia[3] = [random.uniform(-2, 2) for _ in range(5)]


def salvar_melhor_pesos(pesos):
    with open("pesos_sinapticos.txt", "w") as f:
        linha = " ".join([str(round(p, 2)) for p in pesos])
        f.write(linha + "\n")


def mutar_pesos(pesos):
    return [p + round(random.uniform(-1, 1), 3) for p in pesos]

'''
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

'''

def decidir_acao(numero_dino, altura, distancia, velocidade):
    pesos = pesos_ia[numero_dino]  # Deve conter todos os pesos do MLP

    # Pesos por estrutura:
    # 3 entradas -> 3 neurônios (3x4 pesos = 12) + bias por neurônio = 15
    # 3 neurônios -> 2 neurônios (3x2 pesos = 6) + bias por neurônio = 8
    # 2 neurônios -> 1 saída (2 pesos) + bias = 3
    # Total: 15 + 8 + 3 = **26 pesos por dino**

    # Entradas normalizadas
    entradas = [altura, distancia, velocidade]

    # Camada 1 (3 neurônios)
    saida_c1 = []
    for i in range(3):
        soma = sum(entradas[j] * pesos[i * 4 + j] for j in range(3)) + pesos[i * 4 + 3]  # Bias
        ativacao = max(0, soma)  # ReLU
        saida_c1.append(ativacao)

    # Camada 2 (2 neurônios)
    saida_c2 = []
    for i in range(2):
        soma = sum(saida_c1[j] * pesos[15 + i * 3 + j] for j in range(3)) + pesos[15 + i * 3 + 2]  # Bias
        ativacao = max(0, soma)  # ReLU
        saida_c2.append(ativacao)

    # Saída final
    soma_final = saida_c2[0] * pesos[23] + saida_c2[1] * pesos[24] + pesos[25]  # Bias final
    saida = soma_final  # Aqui poderia aplicar outra função, mas você já faz saída linear

    if saida < -0.33:
        return 1  # Pular
    elif saida > 0.33:
        return -1  # Abaixar
    else:
        return 0  # Nada

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
        global jogo_rodando, melhor_pontuacao, melhor_pesos, ultimo_pesos

        time.sleep(1)
        dino_game.start_game()
        jogo_rodando = False

        if ultimo_vivo is not None:
            pontuacao = dino_game.velocidade_atual
            vencedor_pesos = pesos_ia[ultimo_vivo]
            ultimo_pesos = vencedor_pesos.copy()

            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_pesos = vencedor_pesos.copy()
                salvar_melhor_pesos(melhor_pesos)
                print(f"Novo melhor desempenho: Velocidade {pontuacao}")
            else:
                print(f"Desempenho {pontuacao} não superou o melhor {melhor_pontuacao}")

        atualizar_pesos()

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
        labels_dino[i].config(text=f"Dino {i+1} - Distância: {status['distancia']}  Altura: {status['altura']}  Status: {vivo}")

        if dino_game.players[i].alive:
            vivos.append(i)

            if tempo_abaixado[i] > 0:
                tempo_abaixado[i] -= 1
                dino_game.players[i].dino_duck = True
                dino_game.players[i].dino_run = False
                dino_game.players[i].dino_jump = False
                continue

            acao = decidir_acao(i, status['altura'], status['distancia'], dino_game.velocidade_atual)

            if acao == 1 and not dino_game.players[i].dino_jump:
                dino_game.players[i].dino_duck = False
                dino_game.players[i].dino_run = False
                dino_game.players[i].dino_jump = True
            elif acao == -1 and not dino_game.players[i].dino_jump:
                tempo_abaixado[i] = max(5, int(30 - dino_game.velocidade_atual / 2))
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
