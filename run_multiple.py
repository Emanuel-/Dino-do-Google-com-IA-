import multiprocessing
import dino_game  # Certifique-se de que o arquivo do jogo se chama dino_game.py

if __name__ == "__main__":
    # Processo 1: Teclas Q (pular) e A (abaixar)
    p1 = multiprocessing.Process(target=dino_game.menu, args=(0, dino_game.pygame.K_q, dino_game.pygame.K_a))

    # Processo 2: Teclas W (pular) e S (abaixar)
    p2 = multiprocessing.Process(target=dino_game.menu, args=(0, dino_game.pygame.K_w, dino_game.pygame.K_s))

    # Processo 3: Teclas E (pular) e D (abaixar)
    p3 = multiprocessing.Process(target=dino_game.menu, args=(0, dino_game.pygame.K_e, dino_game.pygame.K_d))

    # Processo 4: Teclas R (pular) e F (abaixar)
    p4 = multiprocessing.Process(target=dino_game.menu, args=(0, dino_game.pygame.K_r, dino_game.pygame.K_f))

    # Iniciar os dois processos
    p1.start()
    p2.start()
    p3.start()
    p4.start()

    # Esperar os dois terminarem
    p1.join()
    p2.join()
    p3.join()
    p4.join()
