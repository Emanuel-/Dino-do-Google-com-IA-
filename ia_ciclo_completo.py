import tkinter as tk
import threading
import time
import random
import dino_game
from ag_executor import executar_evolucao
from gp_runtime_utils import converter_em_funcao

jogo_rodando = False
ciclo_automatico = True
melhor_pontuacao = 0
tempo_abaixado = [0 for _ in range(4)]
ultimo_vivo = None
mensagem_vencedor_exibida = False
velocidade_maxima = 60
velocidades_utilizadas = [20]

# --- Carrega as 4 melhores árvores
def carregar_arvores_txt():
    funcoes = []
    for i in range(4):
        caminho = f"melhor_arvore_{i}.txt"
        with open(caminho, "r") as f:
            texto = f.read()
        funcoes.append(converter_em_funcao(texto))
    return funcoes

arvores_melhores = []

def decidir_acao(numero_dino, altura, distancia, velocidade, tipo_obstaculo=None, largura=None):
    if distancia is None or altura is None or tipo_obstaculo is None:
        return 0  # nothing

    try:
        func = arvores_melhores[numero_dino]
        resposta = func(velocidade, distancia, altura, tipo_obstaculo)  # ordem corrigida

        if resposta == "jump":
            return 1
        elif resposta == "duck":
            return -1
        else:
            return 0
    except Exception as e:
        print(f"[ERRO Dino {numero_dino}] {e}")
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
        global jogo_rodando, melhor_pontuacao

        dino_game.start_game(modo_ia_param=True)
        jogo_rodando = False

        pontuacoes = [player.pontos for player in dino_game.players]
        melhor_atual = max(pontuacoes)
        if melhor_atual > melhor_pontuacao:
            melhor_pontuacao = melhor_atual
            print(f"Novo melhor desempenho: Pontuação {melhor_atual}")
        else:
            print(f"Desempenho {melhor_atual} não superou o melhor {melhor_pontuacao}")

        if ciclo_automatico:
            proxima_velocidade()

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
            0: "Cacto Pequeno Simples",
            1: "Cacto Pequeno Duplo",
            2: "Cacto Pequeno Triplo",
            3: "Cacto Grande (solitário)",
            4: "Cacto Grande (largo)",
            5: "Pássaro Alto",
            6: "Pássaro Médio",
            7: "Pássaro Baixo"
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
    print("🛑 Ciclo automático parado.")

def proxima_velocidade():
    global velocidades_utilizadas, arvores_melhores

    if velocidades_utilizadas[-1] >= velocidade_maxima:
        print("✅ Velocidade máxima atingida. Encerrando ciclo.")
        return

    nova_velocidade = velocidades_utilizadas[-1] + 1
    velocidades_utilizadas.append(nova_velocidade)
    print(f"\n🚀 Iniciando nova rodada com velocidades: {velocidades_utilizadas}")

    def treinar_e_reiniciar():
        executar_evolucao(velocidades_utilizadas)
        carregar_novas_arvores()
        time.sleep(1)
        iniciar_jogo()

    threading.Thread(target=treinar_e_reiniciar).start()

def carregar_novas_arvores():
    global arvores_melhores
    arvores_melhores = carregar_arvores_txt()

# Interface Tkinter
janela = tk.Tk()
janela.title("IA com Ciclo Automático - Dino Game")
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

# Início automático
def iniciar_primeira_rodada():
    def treinar_e_iniciar():
        executar_evolucao(velocidades_utilizadas)
        carregar_novas_arvores()
        time.sleep(1)
        iniciar_jogo()

    threading.Thread(target=treinar_e_iniciar).start()

atualizar_info()
iniciar_primeira_rodada()
janela.mainloop()
