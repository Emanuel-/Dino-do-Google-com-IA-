import tkinter as tk
import threading
import time
import random
import dino_game

jogo_rodando = False  # Controla se o jogo está rodando

def decidir_acao(numero_dino, altura, distancia, velocidade):
    """
    Recebe informações do Dino e retorna a ação:
    -1: abaixar
     0: nada
     1: pular
    """
    return random.choice([-1, 0, 1])

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
        botao_iniciar.config(state=tk.NORMAL)

    threading.Thread(target=rodar_jogo).start()

def atualizar_info():
    global ultimo_vivo, mensagem_vencedor_exibida

    if not hasattr(dino_game, "players"):
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

    janela.after(200, atualizar_info)

def resetar_vencedor(event):
    global ultimo_vivo, mensagem_vencedor_exibida
    if mensagem_vencedor_exibida:
        label_vencedor.config(text="")
        ultimo_vivo = None
        mensagem_vencedor_exibida = False

# Cria janela
janela = tk.Tk()
janela.title("Controle IA - Dino Game")
janela.geometry("400x350")

# Botão iniciar
botao_iniciar = tk.Button(janela, text="Iniciar Jogo", command=iniciar_jogo, font=("Arial", 14))
botao_iniciar.pack(pady=10)

# Labels dos Dinos
labels_dino = []
for i in range(4):
    lbl = tk.Label(janela, text=f"Dino {i+1} - Distância: -  Altura: -", font=("Arial", 12))
    lbl.pack()
    labels_dino.append(lbl)

# Label da velocidade
label_velocidade = tk.Label(janela, text="Velocidade: -", font=("Arial", 12))
label_velocidade.pack(pady=10)

# Label do vencedor
label_vencedor = tk.Label(janela, text="", font=("Arial", 14), fg="green")
label_vencedor.pack(pady=10)

# Inicia atualização periódica
ultimo_vivo = None
mensagem_vencedor_exibida = False
atualizar_info()

# Reseta vencedor ao pressionar tecla
janela.bind("<Key>", resetar_vencedor)

# Loop Tkinter
janela.mainloop()
