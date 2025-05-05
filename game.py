import pygame
import sys

from board import Board
from player import Player
from Agents.Agent import Agent
from Agents.Alice import Alice

def main():
    WIDTH = 1100
    HEIGHT = 770
    FPS = 60
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Quoridor Game")
    clock = pygame.time.Clock()


    width, height = screen.get_size()

    player_1 = Player("Red", (8, 4), (226, 37, 37))
    player_2 = Alice((0, 4), (25, 28, 232))
    board = Board(screen, player_1, player_2)
    agent_calculating = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                board.update_board(screen)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Right click to stop placing the fences
                if board.block_mode and event.button == 3:
                    board.switch_to_move_mode()
                elif board.block_mode and board.valid_fence_placement and event.button == 1:
                    board.place_fence()
                else:
                    board.handle_on_click_event(event.pos)
            elif event.type == pygame.MOUSEMOTION and board.block_mode:
                board.grab_fence(event.pos)
            elif board.block_mode and event.type == pygame.MOUSEWHEEL:
                board.switch_fence_orientation()
            elif event.type == pygame.USEREVENT:
                if isinstance(board.current_player, Agent):
                    board.current_player.make_move()
                    agent_calculating = False
                    pygame.time.set_timer(pygame.USEREVENT, 0)
        if board.winner:
            # Update winning logic properly
            screen.fill(board.winner.color)
            running = False
        else:
            board.update_board()
            pygame.display.flip()
            clock.tick(FPS)

            if isinstance(board.current_player, Agent) and not agent_calculating:
                agent_calculating = True
                board.current_player.make_decision()
                pygame.time.set_timer(pygame.USEREVENT, 100)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()