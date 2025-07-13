import pygame
import os
import random
from dino_classes import Dinosaur, SmallCactus, LargeCactus, Bird, Cloud, SMALL_CACTUS, LARGE_CACTUS, BIRD

pygame.init()

# Constantes da tela
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1350
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Game")

# Imagem de fundo
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

# Variáveis globais
players = []
dino_status = [{"distancia": -1, "altura": -1} for _ in range(4)]
velocidade_atual = 0
ultimo_vivo = None
modo_ia = False
points = 0



def main(modo_ia_param=False):
    global players, dino_status, velocidade_atual, modo_ia, points

    modo_ia = modo_ia_param
    run = True
    clock = pygame.time.Clock()
    font = pygame.font.Font('freesansbold.ttf', 20)

    # Carrega sprites dos Dinos
    RUNNING = []
    DUCKING = []
    JUMPING = []

    for i in range(1, 5):
        RUNNING.append([
            pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", f"Dino{i}Run1.png")), (87, 94)),
            pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", f"Dino{i}Run2.png")), (87, 94))
        ])
        DUCKING.append([
            pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", f"Dino{i}Duck1.png")), (118, 60)),
            pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", f"Dino{i}Duck2.png")), (118, 60))
        ])
        JUMPING.append(pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", f"Dino{i}Jump.png")), (88, 94)))

    # Criação dos jogadores
    players = [
        Dinosaur(pygame.K_q, pygame.K_a, RUNNING[0], DUCKING[0], JUMPING[0], 50, 310, 340),
        Dinosaur(pygame.K_w, pygame.K_s, RUNNING[1], DUCKING[1], JUMPING[1], 150, 310, 340),
        Dinosaur(pygame.K_e, pygame.K_d, RUNNING[2], DUCKING[2], JUMPING[2], 250, 310, 340),
        Dinosaur(pygame.K_r, pygame.K_f, RUNNING[3], DUCKING[3], JUMPING[3], 350, 310, 340),
    ]

    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    obstacles = []
    cloud = Cloud(SCREEN_WIDTH)
    proxima_geracao_obstaculo = 0

    def score():
        global points 
        nonlocal game_speed
        points += 1
        if points % 100 == 0:
            game_speed = min(game_speed + 1, 60)
        text = font.render(f"Points: {points}", True, (0, 0, 0))
        SCREEN.blit(text, (1000, 40))

    def background():
        nonlocal x_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed() if not modo_ia else [False] * 512

        # Geração de obstáculos
        if proxima_geracao_obstaculo <= 0:
            if len(obstacles) == 0 or obstacles[-1].rect.x < 600:
                choice = random.randint(0, 2)
                if choice == 0:
                    obstacles.append(SmallCactus(SMALL_CACTUS, SCREEN_WIDTH))
                elif choice == 1:
                    obstacles.append(LargeCactus(LARGE_CACTUS, SCREEN_WIDTH))
                else:
                    obstacles.append(Bird(BIRD, SCREEN_WIDTH))
                proxima_geracao_obstaculo = random.randint(30, 50)
        else:
            proxima_geracao_obstaculo -= 1

        # Atualiza obstáculos
        for obstacle in obstacles[:]:
            obstacle.update(game_speed)
            obstacle.draw(SCREEN)

            for player in players:
                if player.alive and player.dino_rect.colliderect(obstacle.rect):
                    player.alive = False

            if obstacle.rect.x < -obstacle.rect.width:
                obstacles.remove(obstacle)

        # Atualiza status para IA ou interface
        if obstacles:
            obstaculo = obstacles[0]
            altura = obstaculo.rect.y
            distancia = obstaculo.rect.x
            for idx, player in enumerate(players):
                dino_status[idx]["distancia"] = distancia - player.dino_rect.x
                dino_status[idx]["altura"] = altura
        else:
            for status in dino_status:
                status["distancia"] = -1
                status["altura"] = -1

        velocidade_atual = game_speed

        # Atualiza e desenha jogadores
        for player in players:
            if player.alive:
                player.update(userInput, modo_ia)
                player.draw(SCREEN)

        background()
        cloud.draw(SCREEN)
        cloud.update(game_speed, SCREEN_WIDTH)
        score()

        if all(not player.alive for player in players):
            pygame.time.delay(2000)
            return

        clock.tick(30)
        pygame.display.update()


def menu(death_count):
    global modo_ia
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        else:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score_text = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            SCREEN.blit(score_text, scoreRect)

        textRect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(text, textRect)
        SCREEN.blit(pygame.image.load(os.path.join("Assets/Dino", "Dino1Run1.png")),
                    (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                start_game()


def start_game(modo_ia_param=False):
    main(modo_ia_param)


if __name__ == "__main__":
    menu(death_count=0)
