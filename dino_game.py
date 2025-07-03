import pygame
import os
import random
pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1350
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# Variáveis globais de status do jogo
dino_status = [
    {"distancia": 0, "altura": 0} for _ in range(4)
]
velocidade_atual = 0


SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

class Dinosaur:
    JUMP_VEL = 8.5

    def __init__(self, key_up, key_down, run_img, duck_img, jump_img, x_pos, y_pos, y_pos_duck):
        self.duck_img = duck_img
        self.run_img = run_img
        self.jump_img = jump_img

        self.key_up = key_up
        self.key_down = key_down

        self.X_POS = x_pos
        self.Y_POS = y_pos
        self.Y_POS_DUCK = y_pos_duck

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

        self.alive = True  # novo atributo para controlar se o dinossauro está vivo

    def update(self, userInput):
        if not self.alive:
            return  # não atualiza se estiver "morto"

        if self.dino_duck:
            self.duck()
        elif self.dino_run:
            self.run()
        elif self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[self.key_up] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[self.key_down] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[self.key_down]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        if not self.alive:
            return  # não desenha se estiver "morto"
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))



class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, velocidade_atual

    run = True
    clock = pygame.time.Clock()

    

    ####################################################################################################
    # Tamanho desejado para as imagens
    # WIDTH, HEIGHT = 60, 80  # ajuste conforme preferir

    RUNNING1 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino1Run1.png")), (87, 94)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino1Run2.png")), (87, 94))
    ]
    RUNNING2 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino2Run1.png")), (87, 94)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino2Run2.png")), (87, 94))
    ]    
    RUNNING3 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino3Run1.png")), (87, 94)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino3Run2.png")), (87, 94))
    ]
    RUNNING4 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino4Run1.png")), (87, 94)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino4Run2.png")), (87, 94))
    ]    

    JUMPING1 = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino1Jump.png")), (88, 94))
    JUMPING2 = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino2Jump.png")), (88, 94))
    JUMPING3 = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino3Jump.png")), (88, 94))
    JUMPING4 = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino4Jump.png")), (88, 94))

    DUCKING1 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino1Duck1.png")), (118, 60)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino1Duck2.png")), (118, 60))
    ]
    DUCKING2 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino2Duck1.png")), (118, 60)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino2Duck2.png")), (118, 60))
    ]
    DUCKING3 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino3Duck1.png")), (118, 60)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino3Duck2.png")), (118, 60))
    ]
    DUCKING4 = [
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino4Duck1.png")), (118, 60)),
        pygame.transform.scale(pygame.image.load(os.path.join("Assets/Dino", "Dino4Duck2.png")), (118, 60))
    ]

    ####################################################################################################

    # Cria 4 dinossauros com controles diferentes e posições diferentes no eixo X
    players = [
        Dinosaur(pygame.K_q, pygame.K_a, RUNNING1, DUCKING1, JUMPING1, 50, 310, 340),
        Dinosaur(pygame.K_w, pygame.K_s, RUNNING2, DUCKING2, JUMPING2, 150, 310, 340),
        Dinosaur(pygame.K_e, pygame.K_d, RUNNING3, DUCKING3, JUMPING3, 250, 310, 340),
        Dinosaur(pygame.K_r, pygame.K_f, RUNNING4, DUCKING4, JUMPING4, 350, 310, 340),
    ]

    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed = min(game_speed + 1, 60)  # limita a velocidade a no máximo 60

        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)


    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        # Se não tiver obstáculos, cria um novo
        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif choice == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))

        # Atualiza e desenha obstáculos, verifica colisão com jogadores vivos
        for obstacle in obstacles[:]:
            obstacle.update()
            obstacle.draw(SCREEN)

            for player in players:
                if player.alive and player.dino_rect.colliderect(obstacle.rect):
                    player.alive = False  # dinossauro morreu

            if obstacle.rect.x < -obstacle.rect.width:
                obstacles.remove(obstacle)
        
        # Atualiza as variáveis globais de status
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

        # Atualiza e desenha jogadores vivos
        for player in players:
            if player.alive:
                player.update(userInput)
                player.draw(SCREEN)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        # Se todos morreram, termina o jogo
        if all(not player.alive for player in players):
            pygame.time.delay(2000)
            death_count += 1
            menu(death_count)
            run = False  # para sair do loop main e voltar ao menu

        clock.tick(30)
        pygame.display.update()




def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        else:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score_text = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score_text.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score_text, scoreRect)

        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(pygame.image.load(os.path.join("Assets/Dino", "Dino1Run1.png")),
                    (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                main()

if __name__ == "__main__":
    menu(death_count=0)
