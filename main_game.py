import pygame
from quoridor_board import Board

# Constants
WIDTH, HEIGHT = 720, 720
ROWS, COLS = 9, 9
TILE_SIZE = WIDTH // COLS
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (50, 50, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

# Init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quoridor")
clock = pygame.time.Clock()

# Load board
board = Board()

def draw_grid():
    for x in range(COLS):
        for y in range(ROWS):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_pawns():
    for player, (x, y) in board.pawns.items():
        center = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)
        color = BLUE if player == 'P1' else RED
        pygame.draw.circle(screen, color, center, TILE_SIZE // 3)

def draw_fences():
    for (x, y) in board.fences['H']:
        pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE + TILE_SIZE//2, TILE_SIZE * 2, 10))
    for (x, y) in board.fences['V']:
        pygame.draw.rect(screen, BLACK, (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE, 10, TILE_SIZE * 2))

def redraw_window():
    screen.fill(WHITE)
    draw_grid()
    draw_pawns()
    draw_fences()
    pygame.display.update()

# Game loop
running = True
while running:
    clock.tick(FPS)
    redraw_window()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
