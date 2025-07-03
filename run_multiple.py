import multiprocessing
import dino_game  # Certifique-se de que o arquivo do jogo se chama dino_game.py

if __name__ == "__main__":
    # Processo 1: Teclas Q (pular) e A (abaixar)
    p1 = multiprocessing.Process(target=dino_game.menu, args=(0, dino_game.pygame.K_q, dino_game.pygame.K_a))

    # Processo 2: Teclas W (pular) e S (abaixar)
    p2 = multiprocessing.Process(target=dino_game.menu, args=(0, dino_game.pygame.K_w, dino_game.pygame.K_s))

    # Iniciar os dois processos
    p1.start()
    p2.start()

    # Esperar os dois terminarem
    p1.join()
    p2.join()
