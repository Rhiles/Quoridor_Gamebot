from pygame import Surface, Rect
import pygame
import os

from player import Player


class Board():
    def __init__(self, screen: Surface):
        self.grid_size = 9
        self.fence_width = 10
        self.tile_width = 60
        self.player_1 = Player("Red", (4, 8), (226, 37, 37))
        self.player_2 = Player("Blue", (4, 0), (25, 28, 232))
        self.tiles = []
        self.current_player = self.player_1

        self.draw_board(screen)
        # Update implementation to draw the player stats #######################################
        # self.draw_play_stats(screen)

        self.display_current_player_possible_moves(screen)


    def draw_board(self, screen: Surface):
        background = Rect(40, 40, 690, 690)
        pygame.draw.rect(screen, (121, 121, 121), background, border_radius=10)
        
        # Draw tiles
        tile_width = 60
        tile_height = 60
        tile_margin = 15
        x = background.topleft[0]
        for row in range(9):
            x += tile_margin
            y = background.topleft[1]
            tiles_row = []
            for col in range(9):
                y += tile_margin
                tile = Rect(x, y, tile_width, tile_height)
                tile = pygame.draw.rect(screen, (44, 44, 44), tile, border_radius=5)
                tiles_row.append(tile)    
                y += tile_width
            self.tiles.append(tiles_row)
            x += tile_height
    
    def draw_play_stats(self, screen: Surface):
        play_stats = Rect(770, 0, 330, 770)
        pygame.draw.rect(screen, (23, 23, 23), play_stats)

        font = pygame.font.SysFont(None, 50)

        name = self.player_2.name
        players = [self.player_1, self.player_2]
        for i in range(2):
            player = font.render(name, True, (225, 225, 225))
            text_cords = screen.blit(player, (792, 40))
            x, y = text_cords.midright[0] + 7, text_cords.midright[1]
            radius = 22.5
            pygame.draw.circle(screen, (226, 37, 37), (x + radius, y), radius)
    
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

    def handle_on_click_event(self, pos):
        moves = self.get_current_player_possible_moves()
        
        for x, y in moves:
            tile:Rect = self.tiles[x][y]
            if tile.collidepoint(pos):
                self.move_player(self.current_player.current_location, (x, y))