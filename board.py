from pygame import Surface, Rect
from collections import deque
import random
import pygame
import copy
import math
import os

from player import Player
from Agents.Agent import Agent


class Board():
    def __init__(self, screen: Surface, player_1:Player, player_2:Player):
        self.screen = screen
        self.tile_width = 60
        self.fence_color = (225, 157, 0)
        self.tiles: list[list[Rect]] = []
        self.player_1 = player_1
        self.player_2 = player_2
        self.current_player: Player =  random.choice([self.player_1, self.player_2])
        self.opponent: Player = player_2 if self.current_player == self.player_1 else self.player_1
        self.current_player.first_start = True
        self.current_player.first_start_games += 1
        self.winner = None
        self.block_mode = False
        self.selected_fence = {
            "loc": (0, 0),
            "fence": None,
            "orientation": "v"
        }

        self.fences: list[Rect] = []
        self.fences_cords = {
            "h": set(),
            "v": set()
        }

        for player in [self.current_player, self.opponent]:
            if isinstance(player, Agent):
                player.set_board_context(self)

    def update_board(self, screen:Surface = None):
        if screen is None:
            screen = self.screen
        self.draw_board()
        self.draw_player_stats()
        self.draw_players()
        self.draw_fences()
        if self.block_mode:
            self.preview_fence()
        else:
            self.display_valid_moves()

    def get_game_state(self):
        state = {
            "player_loc": self.current_player.current_location,
            "player_fence_count": self.current_player.fence_count,
            "player_winning_row": self.current_player.winning_row,
            "opponent_loc": self.opponent.current_location,
            "opponent_fence_count": self.opponent.fence_count,
            "opponent_winning_row": self.opponent.winning_row,
            "fences": copy.deepcopy(self.fences_cords)
        }
        return state

    def switch_turns(self):
        if self.current_player.winning_row == self.current_player.current_location[0]:
            self.winner = self.current_player
        else:
            self.current_player, self.opponent = self.opponent, self.current_player

    def draw_board(self):
        self.screen.fill((65, 65, 65))
        board = Rect(40, 40, 690, 690)
        pygame.draw.rect(self.screen, (121, 121, 121), board, border_radius=10)
        
        # Draw tiles
        tile_width = 60
        tile_height = 60
        tile_margin = 15
        self.tiles = []
        y = board.top
        for row in range(9):
            x = board.left
            y += tile_margin
            tiles_row = []
            for col in range(9):
                x += tile_margin
                tile = Rect(x, y, tile_width, tile_height)
                pygame.draw.rect(self.screen, (44, 44, 44), tile, border_radius=5)
                tiles_row.append(tile)    
                x = tile.right
            self.tiles.append(tiles_row)
            y = tile.bottom
    
    def draw_player_stats(self):
        play_stats = Rect(770, 0, 330, 770)
        pygame.draw.rect(self.screen, (23, 23, 23), play_stats)

        font = pygame.font.SysFont(None, 50)

        # Draw player stats
        draw_pos = (play_stats.left + 22, play_stats.top + 40)
        for player in [self.player_2, self.player_1]:
            name = font.render(player.name, True, (225, 225, 225))
            name_rect = self.screen.blit(name, draw_pos)
            x, y = name_rect.midright[0] + 7, name_rect.midright[1]
            radius = 22.5
            icon_rect = pygame.draw.circle(self.screen, player.color, (x + radius, y), radius)
            
            # Draw fences for each player
            player.fences = []
            draw_pos = (play_stats.left + 22, icon_rect.bottom + 20)
            for i in range(player.fence_count):
                fence = Rect(draw_pos[0], draw_pos[1], 15, 135)
                pygame.draw.rect(self.screen, self.fence_color, fence)
                player.fences.append(fence)
                draw_pos = (fence.topright[0] + 15, fence.topright[1])

            # Update draw position for the player 1
            draw_pos = (play_stats.left +22, play_stats.top + 530)

        # Draw Turn label
        draw_pos = (play_stats.left + 22, play_stats.top + 361)
        turn = font.render("Turn: ", True, (255, 255, 255))
        turn_rect = self.screen.blit(turn, draw_pos)
        x, y = turn_rect.midright[0] + 7, turn_rect.midright[1]
        radius = 22.5
        pygame.draw.circle(self.screen, self.current_player.color, (x + radius, y), radius)
    
    def display_valid_moves(self):
        moves = self.get_valid_moves(self.current_player.current_location, self.opponent.current_location, self.fences_cords)
        
        for x, y in moves:
            tile:Rect = self.tiles[x][y]
            pygame.draw.rect(self.screen, (44, 145, 49), Rect(tile.left + 5, tile.top + 5, 50, 50), border_radius=5)
    
    def is_valid_move(self, _from, _to, fences):
        valid = False
        if 0 <= _to[0] <= 8 and 0 <= _to[1] <= 8:
            if _from[0] == _to[0]:
                valid = fences["v"].isdisjoint({(_to[0], min(_from[1], _to[1])), (_to[0] - 1, min(_from[1], _to[1]))})
            elif _from[1] == _to[1]:
                valid = fences["h"].isdisjoint({(min(_from[0],_to[0]), _to[1]), (min(_from[0],_to[0]), _to[1] - 1)})
        return valid
    
    def get_valid_moves(self, player_loc, opponent_loc, fences):
        valid_moves = set()
        neighbours = [(0, 1), (-1, 0), (0, -1), (1, 0)]

        for dx, dy in neighbours:
            x1, y1 = player_loc
            x2, y2 = x1 + dx, y1 + dy
            if self.is_valid_move((x1, y1), (x2, y2), fences):
                if (x2, y2) == opponent_loc:
                    ox2, oy2 = x2+dx, y2+dy
                    if self.is_valid_move(opponent_loc, (ox2, oy2), fences):
                        valid_moves.add((ox2, oy2))
                    else:
                        ox, oy = opponent_loc
                        for odx, ody in neighbours:
                            ox2, oy2 = ox+odx, oy+ody
                            if (ox2, oy2) != player_loc and self.is_valid_move((ox, oy), (ox2, oy2), fences):
                                valid_moves.add((ox2, oy2))
                else:
                    valid_moves.add((x2, y2))
        return valid_moves

    def draw_players(self):
        for player in [self.current_player, self.opponent]:
            x, y = player.current_location
            tile: Rect = self.tiles[x][y]
            pygame.draw.circle(self.screen, player.color, tile.center, 22.5)

    def move_player(self, _to):
        self.current_player.update_current_location(_to)
        self.switch_turns()

    def preview_fence(self):
        fence: Rect = self.selected_fence["fence"]
        if fence != None:
            pygame.draw.rect(self.screen, self.fence_color, fence)

    def handle_on_click_event(self, pos):
        if not self.block_mode:
            moves = self.get_valid_moves(self.current_player.current_location, self.opponent.current_location, self.fences_cords)
            for x, y in moves:
                tile:Rect = self.tiles[x][y]
                if tile.collidepoint(pos):
                    self.move_player((x, y))

            for fence in self.current_player.fences:
                if fence.collidepoint(pos):
                    self.block_mode = True
                    self.current_player.update_fence_count()
                    self.grab_fence(pos)
    
    def switch_to_move_mode(self):
        self.block_mode = False
        self.current_player.fence_count += 1

    def grab_fence(self, pos):
        if self.selected_fence["orientation"] == "v":
            x, y = pos[0] - 7.5, pos[1] - 67.5
            (x, y), loc = self.snap_fence_to_grid(x, y)
            self.selected_fence["fence"] = Rect(x, y, 15, 135)
            self.selected_fence["loc"] = loc
        else:
            x, y = pos[0] -67.5, pos[1] - 7.5
            (x, y), loc = self.snap_fence_to_grid(x, y)
            self.selected_fence["fence"] = Rect(x, y, 135, 15)
            self.selected_fence["loc"] = loc
    
    def set_selected_fence(self, loc, orientation):
        row, col = loc
        if orientation == "v":
            tile: Rect = self.tiles[row][col]
            x, y = tile.topright
            self.selected_fence["fence"] = Rect(x, y, 15, 135)
            self.selected_fence["loc"] = loc
            self.selected_fence["orientation"] = orientation
        else:
            tile: Rect = self.tiles[row][col]
            x, y = tile.bottomleft
            self.selected_fence["fence"] = Rect(x, y, 135, 15)
            self.selected_fence["loc"] = loc
            self.selected_fence["orientation"] = orientation

    def place_fence(self, non_visual_fence = None):
        if non_visual_fence == None:
            fence = self.selected_fence["fence"]
            self.fences.append(fence)
            self.fences_cords[self.selected_fence["orientation"]].add(self.selected_fence["loc"])
            self.block_mode = False
        else:
            self.fences_cords[non_visual_fence["orientation"]].add(non_visual_fence["loc"])
        
        self.switch_turns()
    
    def draw_fences(self):
        for fence in self.fences:
            pygame.draw.rect(self.screen, self.fence_color, fence)
    
    def snap_fence_to_grid(self, x1, y1):
            loc = (x1, y1)
            self.valid_fence_placement = False

            for row, tile_rows in enumerate(self.tiles[:-1]):
                for col, tile in enumerate(tile_rows[:-1]):
                    if self.selected_fence["orientation"] == "v":
                        (x2, y2) = tile.topright
                    else:
                        (x2, y2) = tile.bottomleft
                    distance = math.hypot(x2 - x1, y2 - y1)
                    if distance <= 25 and self.validate_fence_placement(row, col, self.selected_fence["orientation"], self.fences_cords):
                        temp_fences = copy.deepcopy(self.fences_cords)
                        temp_fences[self.selected_fence["orientation"]].add((row, col))
                        path_exist = (self.path_exists(self.current_player.current_location, self.current_player.winning_row, self.opponent.current_location, temp_fences)
                                      and self.path_exists(self.opponent.current_location, self.opponent.winning_row, self.current_player.current_location, temp_fences))
                        if path_exist:
                            loc = (x2, y2)
                            self.valid_fence_placement = True
                            return loc, (row, col)
            return loc, (row, col)

    def switch_fence_orientation(self):
        if self.selected_fence["orientation"] == "v":
            self.selected_fence["orientation"] = "h"
        else:
            self.selected_fence["orientation"] = "v"

    def validate_fence_placement(self, row, col, orientation, fences_on_board):
        if orientation == "v":
            valid = fences_on_board["v"].isdisjoint({(row -1, col), (row, col), (row + 1, col)}) and (row, col) not in fences_on_board["h"]
            return valid
        else:
            valid = fences_on_board["h"].isdisjoint({(row, col - 1), (row, col), (row, col + 1)}) and (row, col) not in fences_on_board["v"]
            return valid
        
    def path_exists(self, player_loc, winning_row, opponent_loc, fences):
        """
        Validates if there exist a path to the winning row on placing the selected fence
        Uses Breadth First Search (BFS) algorithm to find the path existance
        """
        queue = deque([player_loc])
        visited = set()

        while queue:
            curr = queue.popleft()
            if curr in visited:
                continue
            visited.add(curr)

            # If player reaches any cell in the final row, path exists
            if curr[0] == winning_row:
                return True

            for neighbor in self.get_valid_moves(curr, opponent_loc, fences):
                if neighbor not in visited:
                    queue.append(neighbor)

        return False  # No path found