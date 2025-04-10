import pygame
import sys
from quoridor_board import Board

# Constants
BOARD_SIZE = 9
INITIAL_WIDTH, INITIAL_HEIGHT = 1000, 600
FPS = 60
PLAYER_COLORS = [(255, 0, 0), (0, 0, 255)]

# Game initialization
pygame.init()
screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Quoridor Game")
clock = pygame.time.Clock()

# State
board = Board()
def draw_board(screen, cell_size):
    screen.fill((30, 30, 30))  # Background
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = col * cell_size
            y = row * cell_size
            rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

def draw_players(screen, cell_size):
    for i, (col, row) in enumerate(board.get_player_positions()):
        x = col * cell_size + cell_size // 2
        y = row * cell_size + cell_size // 2
        radius = cell_size // 3
        pygame.draw.circle(screen, PLAYER_COLORS[i], (x, y), radius)

def main():
    global screen
    width, height = screen.get_size()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            # Add click movement and wall placement handling here

        # Calculate dynamic cell size
        cell_size = min(width, height) // BOARD_SIZE

        draw_board(screen, cell_size)
        draw_players(screen, cell_size)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
