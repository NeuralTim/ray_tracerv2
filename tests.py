import pygame
import sys

# Inicjalizacja Pygame
pygame.init()

# Rozmiar okna
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mapowanie tekstury na trapez")

# Wczytaj teksturę
texture = pygame.image.load("piesel1.xcf")

# Współrzędne wierzchołków trapezu (w kolejności zgodnej z ruchem wskazówek zegara)
# Format: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
points = [(300, 200), (500, 200), (600, 400), (200, 400)]

# Utwórz maskę do rysowania trapezu
mask = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
pygame.draw.polygon(mask, (255, 255, 255, 255), points)

# Nakładanie tekstury na trapez
texture = pygame.transform.smoothscale(texture, (screen_width, screen_height))

# Zastosuj maskę na teksturze
mask.blit(texture, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Wyczyść ekran
    screen.fill((0, 0, 0))

    # Rysuj trapez z nałożoną teksturą
    screen.blit(mask, (0, 0))

    # Zaktualizuj ekran
    pygame.display.flip()

# Zakończenie gry
pygame.quit()
sys.exit()
