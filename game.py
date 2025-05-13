import pygame
import sys

from board import Board
from player import Player
from Agents.Agent import Agent
from Agents.Alice import Alice
from Agents.Bob import Bob

def main(visual_mode=True, max_turns=300, games = 1):
    player_1 = Bob((8, 4), (226, 37, 37))
    player_2 = Player("Player", (0, 4), (25, 28, 232))
    # player_1 = Player("Player", (0, 4), (25, 28, 232))
    # player_2 = Alice((0, 4), (25, 28, 232))
    while games > 0:
        if visual_mode:
            pygame.init()
            screen = pygame.display.set_mode((1100, 770), pygame.RESIZABLE)
            pygame.display.set_caption("Quoridor Game")
            clock = pygame.time.Clock()
        else:
            screen = None

        player_1.fence_count = player_2.fence_count = 10
        player_1.current_location = (8, 4)
        player_2.current_location = (0, 4)
        board = Board(screen, player_1, player_2)
        agent_calculating = False
        running = True
        turn_count = 0
        move_log = []  # To store logs for moves and decisions
        
        while running and turn_count < max_turns:
            if visual_mode:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.VIDEORESIZE:
                        screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                        board.update_board(screen)
                    elif not isinstance(board.current_player, Agent) and event.type == pygame.MOUSEBUTTONDOWN:
                        # Right click to stop placing the fences
                        if board.block_mode and event.button == 3:
                            board.switch_to_move_mode()
                        elif board.block_mode and board.valid_fence_placement and event.button == 1:
                            board.place_fence()
                        else:
                            board.handle_on_click_event(event.pos)
                    elif not isinstance(board.current_player, Agent) and event.type == pygame.MOUSEMOTION and board.block_mode:
                        board.grab_fence(event.pos)
                    elif not isinstance(board.current_player, Agent) and board.block_mode and event.type == pygame.MOUSEWHEEL:
                        board.switch_fence_orientation()
                    elif event.type == pygame.USEREVENT:
                        if isinstance(board.current_player, Agent):
                            # Log the move and decision
                            move_log.append({
                                "turn": turn_count + 1,
                                "player": board.current_player.name,
                                "player_location": board.current_player.current_location,
                                "move": board.current_player.get_move()
                            })
                            board.current_player.make_move()
                            agent_calculating = False
                            if visual_mode:
                                pygame.time.set_timer(pygame.USEREVENT, 0)

                            turn_count += 1

            if board.winner:
                if visual_mode:
                    screen.fill(board.winner.color)
                board.winner.win_count += 1
                print(f"Winner: {board.winner.name}")
                if board.winner.first_start:
                    board.winner.first_start_wins += 1
                break

            if visual_mode:
                board.update_board()  # Updates the board visually
                pygame.display.flip()
                clock.tick(60)

            if isinstance(board.current_player, Agent) and not agent_calculating:
                player = board.current_player
                print(f"Turn {turn_count + 1}: {player.name} is making a move...")
                agent_calculating = True
                player.make_decision()  # Let the agent decide

                if visual_mode:
                    pygame.time.set_timer(pygame.USEREVENT, 250)
                else:
                    move_log.append({
                        "turn": turn_count + 1,
                        "player": board.current_player.name,
                        "player_location": board.current_player.current_location,
                        "move": board.current_player.get_move()
                    })
                    player.make_move(visual_mode)
                    agent_calculating = False
                    turn_count += 1
        if not visual_mode:
            # If headless mode, you can log the moves or game history
            print("Game over! Final state:")
            for log in move_log:
                print(log)
        games -= 1


    if visual_mode:
        pygame.quit()
        sys.exit()

    for player in [player_1, player_2]:
        print(f"{player.name}: {player.win_count}")
        print(f"{player.name}'s first start games: {player.first_start_games}")
        print(f"{player.name}'s first start wins: {player.first_start_wins}")

if __name__ == "__main__":
    main(visual_mode=True)