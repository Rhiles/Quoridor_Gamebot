from queue import PriorityQueue

from Agents.Agent import Agent

class Alice(Agent):
    def __init__(self, location, color):
        super().__init__("Alice", location, color)
        self.board = None
        self.ready_to_play = False
    
    def make_decision(self):
        self.opponent = self.board.opponent
        self.game_state = self.board.get_game_state()
        self.path = self.find_shortest_path(self.game_state["player_loc"], self.game_state["player_winning_row"], self.game_state["opponent_loc"], self.game_state["fences"])
        print("Decision Pending...")
    
    def make_move(self):
        if len(self.path) > 0:
            move_to = self.path.pop(0)
            self.board.move_player(move_to)
        print("Made Move...")

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