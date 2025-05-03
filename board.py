from pygame import Surface, Rect
import pygame
import os

from player import Player


class Board():
    def __init__(self, screen: Surface):
        self.screen = screen
        self.tile_width = 60
        self.fence_color = (225, 157, 0)
        self.player_1 = Player("Red", (8, 4), (226, 37, 37))
        self.player_2 = Player("Blue", (0, 4), (25, 28, 232))
        self.tiles = []
        self.current_player = self.player_1
        self.block_mode = False
        self.fence_verticall_oriented = True
        self.selected_fence = {
            "loc": (0, 0),
            "fence": None,
            "orientation": "v"
        }

        self.update_board()

    def update_board(self, screen:Surface = None):
        if screen is None:
            screen = self.screen
        self.draw_board(screen)
        self.draw_player_stats(screen)
        self.draw_players(screen)
        if self.block_mode:
            self.draw_fence()
        else:
            self.display_current_player_possible_moves(screen)


    def draw_board(self, screen: Surface):
        screen.fill((65, 65, 65))
        board = Rect(40, 40, 690, 690)
        pygame.draw.rect(screen, (121, 121, 121), board, border_radius=10)
        
        # Draw tiles
        tile_width = 60
        tile_height = 60
        tile_margin = 15
        y = board.top
        for row in range(9):
            x = board.left
            y += tile_margin
            tiles_row = []
            for col in range(9):
                x += tile_margin
                tile = Rect(x, y, tile_width, tile_height)
                pygame.draw.rect(screen, (44, 44, 44), tile, border_radius=5)
                tiles_row.append(tile)    
                x = tile.right
            self.tiles.append(tiles_row)
            y = tile.bottom
    
    def draw_player_stats(self, screen: Surface):
        play_stats = Rect(770, 0, 330, 770)
        pygame.draw.rect(screen, (23, 23, 23), play_stats)

        font = pygame.font.SysFont(None, 50)

        # Draw player stats
        draw_pos = (play_stats.left + 22, play_stats.top + 40)
        for player in [self.player_2, self.player_1]:
            name = font.render(player.name, True, (225, 225, 225))
            name_rect = screen.blit(name, draw_pos)
            x, y = name_rect.midright[0] + 7, name_rect.midright[1]
            radius = 22.5
            icon_rect = pygame.draw.circle(screen, player.color, (x + radius, y), radius)
            
            # Draw fences for each player
            draw_pos = (play_stats.left + 22, icon_rect.bottom + 20)
            for i in range(player.fence_count):
                fence = Rect(draw_pos[0], draw_pos[1], 15, 135)
                pygame.draw.rect(screen, self.fence_color, fence)
                player.fences.append(fence)
                draw_pos = (fence.topright[0] + 15, fence.topright[1])

            # Update draw position for the player 1
            draw_pos = (play_stats.left +22, play_stats.top + 530)

        # Draw Turn label
        draw_pos = (play_stats.left + 22, play_stats.top + 361)
        turn = font.render("Turn: ", True, (255, 255, 255))
        turn_rect = screen.blit(turn, draw_pos)
        x, y = turn_rect.midright[0] + 7, turn_rect.midright[1]
        radius = 22.5
        pygame.draw.circle(screen, self.current_player.color, (x + radius, y), radius)
    
    def display_current_player_possible_moves(self, screen: Surface):
        moves = self.get_current_player_possible_moves()
        
        for x, y in moves:
            tile:Rect = self.tiles[x][y]
            pygame.draw.rect(screen, (44, 145, 49), Rect(tile.left + 5, tile.top + 5, 50, 50), border_radius=5)
    
    def get_current_player_possible_moves(self):
        moves = []
        neighbours = self.current_player.get_neighbour_tiles()
        opponent_position = self.player_2.current_location if self.current_player == self.player_1 else self.player_1.current_location
        
        for index, (x, y) in enumerate(neighbours):
            if (x, y) == opponent_position:
                skip_tiles = self.current_player.get_neighbour_tiles(2)
                x, y = skip_tiles[index][0], skip_tiles[index][1]
            moves.append((x, y))
        return moves

    def draw_players(self, screen: Surface):
        for player in [self.player_1, self.player_2]:
            x, y = player.current_location
            tile: Rect = self.tiles[x][y]
            pygame.draw.circle(screen, player.color, tile.center, 22.5)

    def move_player(self, _from, _to):
        self.current_player.update_current_location(_to)

        self.current_player = self.player_1 if self.current_player == self.player_2 else self.player_2

    def draw_fence(self):
        fence: Rect = self.selected_fence["fence"]
        if fence != None:
            pygame.draw.rect(self.screen, self.fence_color, fence)

    def handle_on_click_event(self, pos):
        if not self.block_mode:
            moves = self.get_current_player_possible_moves()
            for x, y in moves:
                tile:Rect = self.tiles[x][y]
                if tile.collidepoint(pos):
                    self.move_player(self.current_player.current_location, (x, y))
                    return

            for fence in self.current_player.fences:
                if fence.collidepoint(pos):
                    self.block_mode = True
                    self.current_player.update_fence_count()
                    return
                
    def handle_mouse_move_event(self, pos):
        if self.selected_fence["orientation"] == "v":
            x, y = pos[0] - 7.5, pos[1] - 67.5
            self.selected_fence["fence"] = Rect(x, y, 15, 135)
        else:
            x, y = pos[0] -67.5, pos[1] - 7.5
            self.selected_fence["fence"] = Rect(x, y, 135, 15)
        
    def switch_fence_orientation(self):
        if self.selected_fence["orientation"] == "v":
            self.selected_fence["orientation"] = "h"
        else:
            self.selected_fence["orientation"] = "v"