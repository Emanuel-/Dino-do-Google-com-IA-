import tkinter as tk
import threading
import pyautogui
import time
import dino_game

def iniciar_jogo():
    def rodar_jogo():
        dino_game.menu(0)
    
    threading.Thread(target=rodar_jogo).start()

    # Aguarda e pressiona espaço
    def pressionar_espaco():
        time.sleep(1)
        pyautogui.press('space')
    
    threading.Thread(target=pressionar_espaco).start()

def atualizar_info():
    if hasattr(dino_game, "players"):
        for i in range(4):
            status = dino_game.dino_status[i]
            vivo = "Vivo" if dino_game.players[i].alive else "Morto"
            texto = f"Dino {i+1} - Distância: {status['distancia']}  Altura: {status['altura']}  Status: {vivo}"
            labels_dino[i].config(text=texto)

        label_velocidade.config(text=f"Velocidade: {dino_game.velocidade_atual}")
    else:
        for i in range(4):
            texto = f"Dino {i+1} - Distância: -  Altura: -  Status: -"
            labels_dino[i].config(text=texto)
        label_velocidade.config(text="Velocidade: -")

    janela.after(500, atualizar_info)  # atualiza a cada 500ms

# Cria janela
janela = tk.Tk()
janela.title("Controle IA - Dino Game")
janela.geometry("400x300")

# Botão iniciar
botao_iniciar = tk.Button(janela, text="Iniciar Jogo", command=iniciar_jogo, font=("Arial", 14))
botao_iniciar.pack(pady=10)

# Labels dos Dinos
labels_dino = []
for i in range(4):
    lbl = tk.Label(janela, text=f"Dino {i+1} - Distância: -  Altura: -  Status: -", font=("Arial", 12))
    lbl.pack()
    labels_dino.append(lbl)

# Label da velocidade
label_velocidade = tk.Label(janela, text="Velocidade: -", font=("Arial", 12))
label_velocidade.pack(pady=10)

# Inicia atualização periódica
atualizar_info()

# Loop Tkinter
janela.mainloop()
