from queue import PriorityQueue
import copy
import random

from Agents.Agent import Agent

class Bob(Agent):
    def __init__(self, location, color):
        super().__init__("Bob", location, color)
        self.board = None
        self.ready_to_play = False
    
    def make_decision(self):
        self.opponent = self.board.opponent
        self.game_state = self.board.get_game_state()
        self.fence_pos = self.find_best_fence_placement(copy.deepcopy(self.game_state)) if self.fence_count > 0 else None
        
        best_path = self.find_shortest_path(self.game_state["player_loc"], self.game_state["player_winning_row"], self.game_state["opponent_loc"], self.game_state["fences"])
        if len(best_path) > 0:
            nxt_move = best_path[0]
        else:
            valid_moves = self.board.get_valid_moves(self.game_state["player_loc"], self.game_state["opponent_loc"], self.game_state["fences"])
            nxt_move = random.choice(valid_moves)
        move_score = self.evaluate_game_state(
            nxt_move,
            self.game_state["player_winning_row"],
            self.game_state["opponent_loc"],
            self.game_state["opponent_winning_row"],
            self.game_state["fences"],
            self.game_state["player_fence_count"],
            self.game_state["opponent_fence_count"]
        )

        if self.fence_pos == None or move_score > self.fence_pos["score"]:
            self.nxt_move = {"score": move_score, "move": nxt_move}
            self.fence_pos = None
        else:
            self.nxt_move = None

    def make_move(self, visual_mode=True):
        if self.nxt_move:
            self.board.move_player(self.nxt_move["move"])
        else:
            if visual_mode:
                self.board.set_selected_fence(self.fence_pos["loc"], self.fence_pos["orientation"])
                self.board.place_fence()
            else:
                self.board.place_fence({
                    "fence": None,  # No fence object is needed if not in visual mode
                    "orientation": self.fence_pos["orientation"],
                    "loc": self.fence_pos["loc"]
                })
            self.fence_count -= 1

    def get_move(self):
        return self.nxt_move if self.nxt_move != None else self.fence_pos

    def find_shortest_path(self, start_pos, goal, opponent_loc, fences):
        open_set = PriorityQueue()
        open_set.put((abs(start_pos[0] - goal), start_pos))

        came_from = {}
        g_score = {start_pos: 0}

        while not open_set.empty():
            current = open_set.get()[1]

            if current[0] == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path[1:]

            for neighbor in self.board.get_valid_moves(current, opponent_loc, fences):  # consider fences
                tentative_g = g_score[current] + 1  # each move has cost 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + abs(neighbor[0] - goal)
                    open_set.put((f, neighbor))

    def find_best_fence_placement(self, game_state):
        player_loc = game_state["player_loc"]
        player_fences_left = game_state["player_fence_count"]
        player_winning_row = game_state["player_winning_row"]
        opponent_loc = game_state["opponent_loc"]
        opponent_fences_left = game_state["opponent_fence_count"]
        opponent_winning_row = game_state["opponent_winning_row"]
        fences = game_state["fences"]
        valid_fence_placements = []
        
        for orientation in ["v", "h"]:
            r1, r2 = opponent_loc[0] - 3, opponent_loc[0] + 4
            c1, c2 = opponent_loc[1] - 3, opponent_loc[1] + 4
            for row in range(r1, r2):
                for col in range(c1, c2):
                    if 0 <= row <= 7 and 0<= col <= 7 and self.board.validate_fence_placement(row, col, orientation, fences):
                        temp_fences = copy.deepcopy(fences)
                        temp_fences[orientation].add((row, col))
                        
                        # Ensure path still exists
                        if not (self.board.path_exists(player_loc, player_winning_row, opponent_loc, temp_fences)
                                and self.board.path_exists(opponent_loc, opponent_winning_row, player_loc, temp_fences)):
                            continue

                        # Get shortest paths
                        winning_path = self.find_shortest_path(player_loc, player_winning_row, opponent_loc, temp_fences)
                        opponent_path = self.find_shortest_path(opponent_loc, opponent_winning_row, player_loc, temp_fences)

                        if not winning_path or not opponent_path:
                            continue

                        score = self.evaluate_game_state(
                            player_loc,
                            player_winning_row,
                            opponent_loc,
                            opponent_winning_row,
                            temp_fences,
                            player_fences_left - 1,  # one less fence
                            opponent_fences_left
                        )

                        # Track the best move
                        valid_fence_placements.append({
                            "orientation": orientation,
                            "loc": (row, col),
                            "score": score
                        })
        if len(valid_fence_placements) == 0:
            return None
        best_3_placements = sorted(valid_fence_placements, key=lambda x: x['score'], reverse=True)[:3]
        return random.choice(best_3_placements)
    
    def evaluate_game_state(self, player_loc, player_winning_row, opponent_loc, opponent_winning_row, fences, player_fences_left, opponent_fences_left):
        if player_loc[0] != player_winning_row:
            # Shortest path lengths
            bot_path = self.find_shortest_path(player_loc, player_winning_row, opponent_loc, fences)
            opp_path = self.find_shortest_path(opponent_loc, opponent_winning_row, player_loc, fences)

            if bot_path is None or opp_path is None:
                return float('-inf')  # invalid state (shouldn't happen if path_exists is used properly)

            len_bot_path = len(bot_path)
            len_opp_path = len(opp_path)

            # Heuristic 1: Difference in path lengths
            H1 = len_opp_path - len_bot_path
        else:
            H1 = float('inf')

        # Heuristic 2: Mobility (number of valid moves)
        H2 = len(self.board.get_valid_moves(player_loc, opponent_loc, fences))
        H2_OPPONENT = len(self.board.get_valid_moves(opponent_loc, player_loc, fences))

        # Heuristic 3: Distance from center
        center = (4, 4)
        H3 = abs(player_loc[0] - center[0]) + abs(player_loc[1] - center[1])

        # Heuristic 4: Fence advantage
        H4 = player_fences_left - opponent_fences_left

        # Combine using weights
        score = 4 * H1 + (0.5 * H2 - H2_OPPONENT) + 0.2 * H3 + 1 * H4

        return score

