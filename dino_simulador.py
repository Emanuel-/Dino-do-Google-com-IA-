import random

def main_offscreen(action_generator):
    """
    Simula o jogo do Dino offline, recebendo as ações para cada dino.

    Parâmetros:
    - action_generator: função que recebe (jogadores, obstaculos, game_speed, pontos)
                        e retorna uma lista de 4 ações (um para cada dino): 
                        -1 = abaixar, 0 = correr, 1 = pular

    Retorna:
    - vencedor: índice do último dino vivo, ou None se nenhum sobreviveu
    - pontuacao: pontuação final (velocidade do jogo)
    """

    num_dinos=50

    jogadores = [
        {"y": 310, "vel": 8.5, "estado": "correndo", "vivo": True, "tempo_abaixado": 0}
        for _ in range(num_dinos)
    ]
    game_speed = 20
    pontos = 0
    obstaculos = []

    while True:
        # Gera obstáculos se necessário
        if not obstaculos or obstaculos[-1]["x"] < 600:
            tipo = random.choice(["cacto_pequeno", "cacto_grande", "passaro"])
            if tipo == "cacto_pequeno":
                altura = 325
                largura = 50
            elif tipo == "cacto_grande":
                altura = 300
                largura = 60
            else:
                altura = random.choice([200, 250, 320])
                largura = 60
            obstaculos.append({"x": 1350, "y": altura, "tipo": tipo, "largura": largura})

        # Move obstáculos
        for ob in obstaculos:
            ob["x"] -= game_speed

        # Remove obstáculos que saíram da tela
        if obstaculos and obstaculos[0]["x"] < -100:
            obstaculos.pop(0)

        # Obtenha ações para todos os jogadores da função fornecida
        acoes = action_generator(jogadores, obstaculos, game_speed, pontos)
        if len(acoes) != len(jogadores):
            raise ValueError(f"Action generator must return {len(jogadores)} actions, but got {len(acoes)}.")


        vivos = 0
        for idx, dino in enumerate(jogadores):
            if not dino["vivo"]:
                continue
            vivos += 1

            acao = acoes[idx]

            # Executa ação somente se não estiver pulando
            if dino["estado"] != "pulando":
                if acao == 1:
                    dino["estado"] = "pulando"
                    dino["vel"] = 8.5
                elif acao == -1:
                    dino["estado"] = "abaixado"
                    dino["tempo_abaixado"] = 5
                else:
                    dino["estado"] = "correndo"

            # Simula física do pulo
            if dino["estado"] == "pulando":
                dino["y"] -= dino["vel"] * 4
                dino["vel"] -= 0.8
                if dino["vel"] < -8.5:
                    dino["estado"] = "correndo"
                    dino["y"] = 310
                    dino["vel"] = 8.5

            # Simula tempo abaixado
            if dino["estado"] == "abaixado":
                dino["tempo_abaixado"] -= 1
                if dino["tempo_abaixado"] <= 0:
                    dino["estado"] = "correndo"

            # Verifica colisão simples
            if obstaculos:
                obs = obstaculos[0]
                distancia = obs["x"] - 150  # mesmo valor para todos

                if 0 <= distancia <= obs["largura"]:
                    dino_altura = dino["y"] + (30 if dino["estado"] == "abaixado" else 0)
                    if abs(dino_altura - obs["y"]) < 40:
                        dino["vivo"] = False

        if vivos == 0:
            break
        else:
            print(" " * 50, end='\r')
            print(f"Número de dinos vivos: {vivos}    ", end='\r')
            

        pontos += 1
        if pontos % 100 == 0:
            game_speed = min(game_speed + 1, 60)

    for i, dino in enumerate(jogadores):
        if dino["vivo"]:
            return i, game_speed

    return None, game_speed
