import tkinter as tk
import threading
import time
import random
import dino_game
from treinador import get_proxima_quadra, registrar_resultados, evoluir_populacao

arvores_gp = get_proxima_quadra()  # 4 funções (1 por Dino)
jogo_rodando = False
ciclo_automatico = True
melhor_pontuacao = 0
tempo_abaixado = {i: 0 for i in range(4)}
ultimo_vivo = None
mensagem_vencedor_exibida = False


def decidir_acao(numero_dino, altura, distancia, velocidade, tipo_obstaculo=None, largura=None):
    if not arvores_gp or numero_dino >= len(arvores_gp):
        return 0




    velocidade_norm = (velocidade - 20) / 40
    min_distancia = -440
    max_distancia = 1260
    distancia_norm = (distancia - min_distancia) / (max_distancia - min_distancia)
    distancia_norm = min(max(distancia_norm, 0), 1)

    tipo = int(tipo_obstaculo) if tipo_obstaculo is not None else 0

    acao_str = arvores_gp[numero_dino](velocidade_norm, distancia_norm, tipo)

    if acao_str == "jump":
        return 1
    elif acao_str == "duck":
        return -1
    return 0


def iniciar_jogo():
    global jogo_rodando, ultimo_vivo, mensagem_vencedor_exibida, arvores_gp

    if jogo_rodando:
        return

    jogo_rodando = True
    ultimo_vivo = None
    mensagem_vencedor_exibida = False
    label_vencedor.config(text="")
    botao_iniciar.config(state=tk.DISABLED)

    def rodar_jogo():
        global jogo_rodando, melhor_pontuacao, arvores_gp

        time.sleep(1)
        dino_game.start_game(modo_ia_param=True)
        jogo_rodando = False

        # Coleta de pontuação e velocidade final de cada Dino
        pontuacoes = [player.pontos for player in dino_game.players]
        velocidades = [dino_game.velocidade_atual] * 4

        # Atualiza melhor pontuação
        melhor_atual = max(pontuacoes)
        if melhor_atual > melhor_pontuacao:
            melhor_pontuacao = melhor_atual
            print(" "*70, end="\r")
            print(f"Novo melhor desempenho: Pontuação {melhor_atual}", end="\r")
        else:
            print(" "*70, end="\r")
            print(f"Desempenho {melhor_atual} não superou o melhor {melhor_pontuacao}", end="\r")

        # Registrar os resultados (pontuação + velocidade)
        registrar_resultados(pontuacoes, velocidades)

        # Solicita próxima quadra de árvores
        arvores_gp = get_proxima_quadra()
        if arvores_gp is None:
            print("Fim da geração. Evoluindo população...")
            evoluir_populacao()
            arvores_gp = get_proxima_quadra()

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
    obstaculo_atual = dino_game.obstacles[0] if hasattr(dino_game, "obstacles") and dino_game.obstacles else None

    for i in range(4):
        status = dino_game.dino_status[i]
        player = dino_game.players[i]
        vivo = "Vivo" if player.alive else "Morto"
        tipo_txt = {
            0: "Cacto Pequeno",
            1: "Cacto Grande (solitário)",
            2: "Cacto Grande (largo)",
            3: "Pássaro Alto",
            4: "Pássaro Médio",
            5: "Pássaro Baixo"
        }.get(status.get("tipo"), "Nenhum")

        texto = (
            f"Dino {i+1} - {vivo}\n"
            f"  Pontos: {player.pontos}\n"
            f"  Distância: {status.get('distancia', '-')} px\n"
            f"  Tipo Obstáculo: {tipo_txt}"
        )
        labels_dino[i].config(text=texto)

        if player.alive:
            vivos.append(i)

            if tempo_abaixado[i] > 0:
                tempo_abaixado[i] -= 1
                player.dino_duck = True
                player.dino_run = False
                player.dino_jump = False
                continue

            acao = decidir_acao(
                i,
                status['altura'],
                status['distancia'],
                dino_game.velocidade_atual,
                tipo_obstaculo=status.get("tipo"),
                largura=status.get("largura")
            )

            if acao == 1 and not player.dino_jump:
                player.dino_duck = False
                player.dino_run = False
                player.dino_jump = True

            elif acao == -1 and not player.dino_jump:
                tempo_abaixado[i] = 5
                player.dino_duck = True
                player.dino_run = False
                player.dino_jump = False

            elif acao == 0 and not player.dino_jump:
                player.dino_duck = False
                player.dino_run = True
                player.dino_jump = False

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
janela.geometry("400x500")

botao_iniciar = tk.Button(janela, text="Iniciar Jogo", command=iniciar_jogo, font=("Arial", 14))
botao_iniciar.pack(pady=10)

botao_parar = tk.Button(janela, text="Parar Ciclo Automático", command=parar_ciclo, font=("Arial", 12), fg="red")
botao_parar.pack(pady=5)

labels_dino = []
for i in range(4):
    lbl = tk.Label(janela, text=f"Dino {i+1} - Distância: -  Tipo Obstáculo: -", font=("Arial", 12))
    lbl.pack()
    labels_dino.append(lbl)

label_velocidade = tk.Label(janela, text="Velocidade: -", font=("Arial", 12))
label_velocidade.pack(pady=10)

label_vencedor = tk.Label(janela, text="", font=("Arial", 14), fg="green")
label_vencedor.pack(pady=10)

atualizar_info()
janela.mainloop()
