from pygame import Rect

class Player():
    def __init__(self, name, location, color):
        self.name = name
        self.current_location = self.prev_location = location
        self.fence_count = 10
        self.fences: list[Rect] = []
        self.color = color
        self.winning_row = abs(location[0] - 8)
        self.win_count = 0
        self.first_start = False
        self.first_start_games = 0
        self.first_start_wins = 0

    def update_current_location(self, location):
        self.prev_location = self.current_location
        self.current_location = location

    def update_fence_count(self):
        self.fence_count -= 1
        self.fences.pop()