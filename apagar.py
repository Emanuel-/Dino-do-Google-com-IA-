import pygame
import os

pygame.init()

# Carrega imagens dos obstáculos
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", f"SmallCactus{i}.png")) for i in range(1, 4)]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", f"LargeCactus{i}.png")) for i in range(1, 4)]
BIRD = [pygame.image.load(os.path.join("Assets/Bird", f"Bird{i}.png")) for i in range(1, 3)]

# Verifica dimensões dos cactos pequenos
print("=== Small Cactus ===")
for i, img in enumerate(SMALL_CACTUS):
    print(f"SmallCactus{i+1}: {img.get_width()}x{img.get_height()}")

# Verifica dimensões dos cactos grandes
print("\n=== Large Cactus ===")
for i, img in enumerate(LARGE_CACTUS):
    print(f"LargeCactus{i+1}: {img.get_width()}x{img.get_height()}")

# Verifica dimensões dos pássaros
print("\n=== Bird ===")
for i, img in enumerate(BIRD):
    print(f"Bird{i+1}: {img.get_width()}x{img.get_height()}")
