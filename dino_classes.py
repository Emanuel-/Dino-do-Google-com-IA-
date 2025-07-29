import pygame
import os
import random

# Carregamento de imagens
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", f"SmallCactus{i}.png")) for i in range(1, 4)]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", f"LargeCactus{i}.png")) for i in range(1, 4)]
BIRD = [pygame.image.load(os.path.join("Assets/Bird", f"Bird{i}.png")) for i in range(1, 3)]
CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

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
        self.pontos = 0

        self.alive = True
        self.tempo_abaixado_ia = 0
        self.pode_pular = True

    def update(self, userInput, modo_ia):
        if not self.alive:
            return

        if modo_ia and self.tempo_abaixado_ia > 0:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
            self.tempo_abaixado_ia -= 1
        else:
            if self.dino_duck:
                self.duck()
            elif self.dino_run:
                self.run()
            elif self.dino_jump:
                self.jump()

            if self.step_index >= 10:
                self.step_index = 0

            if not modo_ia:
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
            self.dino_rect.y = self.Y_POS

    def draw(self, screen):
        if not self.alive:
            return
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self, screen_width):
        self.x = screen_width + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self, game_speed, screen_width):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = screen_width + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type, screen_width):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = screen_width

    def update(self, game_speed):
        self.rect.x -= game_speed

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, screen_width):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, screen_width)
        self.rect.y = 325
        self.tipo_unificado = self.type  # 0, 1, 2


class LargeCactus(Obstacle):
    def __init__(self, image, screen_width):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type, screen_width)
        self.rect.y = 300
        self.tipo_unificado = 3 if self.type == 0 else 4  # 3 ou 4


class Bird(Obstacle):
    def __init__(self, image, screen_width):
        self.type = 0
        super().__init__(image, self.type, screen_width)
        alturas = [200, 250, 320]
        self.rect.y = random.choice(alturas)
        self.index = 0

        # Define tipo_unificado baseado na altura
        if self.rect.y <= 210:
            self.tipo_unificado = 5  # Pássaro alto
        elif self.rect.y <= 270:
            self.tipo_unificado = 6  # Pássaro médio
        else:
            self.tipo_unificado = 7  # Pássaro baixo

    def draw(self, screen):
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[self.index // 5], self.rect)
        self.index += 1
