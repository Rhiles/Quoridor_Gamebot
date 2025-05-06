from queue import PriorityQueue
import random
import copy

from Agents.Agent import Agent

class Alice(Agent):
    def __init__(self, location, color):
        super().__init__("Alice", location, color)
        self.board = None
        self.ready_to_play = False
        self.nxt_move = self.fence_pos = None
    
    def make_decision(self):
        self.opponent = self.board.opponent
        self.game_state = self.board.get_game_state()
        _, best_state = self.minimax(self.game_state, depth=self.difficulty, alpha=float('-inf'), beta=float('inf'), maximizing_player=True)

        # Determine move or fence difference between self.game_state and best_state
        if best_state["player_loc"] != self.game_state["player_loc"]:
            self.nxt_move = {"score": _, "move": best_state["player_loc"]}
            self.fence_pos = None
        else:
            # Find which fence was added
            for orient in ["v", "h"]:
                new_fences = best_state["fences"][orient] - self.game_state["fences"][orient]
                if new_fences:
                    loc = list(new_fences)[0]
                    self.fence_pos = {"loc": loc, "orientation": orient, "score": _}
                    self.nxt_move = None


    def make_move(self, visual_mode):
        if self.fence_pos == None:
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

    def game_over(self, game_state):
        player_row = game_state["player_loc"]
        opponent_row = game_state["opponent_loc"]
        
        # Check if the bot (current player) has reached the winning row
        if player_row[0] == game_state["player_winning_row"]:
            return True

        # Check if the opponent has reached their winning row
        if opponent_row[0] == game_state["opponent_winning_row"]:
            return True

        return False

    def minimax(self, state, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.game_over(state):
            return self.evaluate_game_state(
                state["player_loc"],
                state["player_winning_row"],
                state["opponent_loc"],
                state["opponent_winning_row"],
                state["fences"],
                state["player_fence_count"],
                state["opponent_fence_count"]
            ), state

        best_states = []

        if maximizing_player:
            max_eval = float('-inf')
            for child in self.generate_child_states(state, is_bot=True):
                eval_score, _ = self.minimax(child, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_states = [child]
                elif eval_score == max_eval:
                    best_states.append(child)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, random.choice(best_states)

        else:
            min_eval = float('inf')
            for child in self.generate_child_states(state, is_bot=False):
                eval_score, _ = self.minimax(child, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_states = [child]
                elif eval_score == min_eval:
                    best_states.append(child)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, random.choice(best_states)


    def generate_child_states(self, game_state, is_bot):
        child_states = []

        player_key = "player_loc" if is_bot else "opponent_loc"
        opponent_key = "opponent_loc" if is_bot else "player_loc"
        player_fences = "player_fence_count" if is_bot else "opponent_fence_count"
        opponent_fences = "opponent_fence_count" if is_bot else "player_fence_count"
        player_winning = "player_winning_row" if is_bot else "opponent_winning_row"
        opponent_winning = "opponent_winning_row" if is_bot else "player_winning_row"

        curr_loc = game_state[player_key]
        opponent_loc = game_state[opponent_key]
        fences = game_state["fences"]
        fences_left = game_state[player_fences]

        # 1. All move options
        for move in self.board.get_valid_moves(curr_loc, opponent_loc, fences):
            new_state = copy.deepcopy(game_state)
            new_state[player_key] = move
            child_states.append(new_state)

        # 2. All valid fence placements
        if fences_left > 0:
            for orientation in ["v", "h"]:
                for row in range(8):
                    for col in range(8):
                        if self.board.validate_fence_placement(row, col, orientation, fences):
                            temp_fences = copy.deepcopy(fences)
                            temp_fences[orientation].add((row, col))

                            # Ensure both players still have valid paths
                            if not (
                                self.board.path_exists(game_state["player_loc"], game_state["player_winning_row"], game_state["opponent_loc"], temp_fences) and
                                self.board.path_exists(game_state["opponent_loc"], game_state["opponent_winning_row"], game_state["player_loc"], temp_fences)
                            ):
                                continue

                            new_state = copy.deepcopy(game_state)
                            new_state["fences"] = temp_fences
                            new_state[player_fences] -= 1
                            child_states.append(new_state)

        return child_states

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
        best_score = 0
        best_placement = None
        
        for orientation in ["v", "h"]:
            for row in range(8):
                for col in range(8):
                    if self.board.validate_fence_placement(row, col, orientation, fences):
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
                        if score > best_score:
                            best_score = score
                            best_placement = {
                                "orientation": orientation,
                                "loc": (row, col),
                                "score": score
                            }
        return best_placement
    
    def evaluate_game_state(self, player_loc, player_winning_row, opponent_loc, opponent_winning_row, fences, player_fences_left, opponent_fences_left):
        if player_loc != player_winning_row:
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
        H2_opponent = len(self.board.get_valid_moves(opponent_loc, player_loc, fences))

        # Heuristic 3: Distance from center
        center = (4, 4)
        H3 = abs(player_loc[0] - center[0]) + abs(player_loc[1] - center[1])

        # Heuristic 4: Fence advantage
        H4 = player_fences_left - opponent_fences_left

        # Combine using weights
        score = 3 * H1 + 1 * H2 + 0.5 * H3 + 1 * H4

        return score

