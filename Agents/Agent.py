from player import Player

class Agent(Player):
    def __init__(self, name, location, color):
        super().__init__(name, location, color)
        self.difficulty = 2

    def set_board_context(self, board):
        from board import Board
        self.board: Board = board
    
    def make_decision(self):
        return
    
    def make_move(self, visual_mode):
        return
    
    def get_move(self):
        return