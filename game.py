import pygame
import sys

from board import Board

def main():
    WIDTH = 1100
    HEIGHT = 770
    FPS = 60
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    screen.fill((65, 65, 65))
    pygame.display.set_caption("Quoridor Game")
    clock = pygame.time.Clock()


    width, height = screen.get_size()

    board = Board(screen)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                screen.fill((65, 65, 65))
                board.draw_board(screen)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                board.handle_on_click_event(event.pos)

        board.draw_board(screen)
        board.draw_players(screen)
        board.display_current_player_possible_moves(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()