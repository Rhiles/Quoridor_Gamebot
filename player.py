from pygame import Rect

class Player():
    def __init__(self, name, location, color):
        self.name = name
        self.current_location = self.prev_location = location
        self.fence_count = 10
        self.fences: list[Rect] = []
        self.color = color
        self.winning_row = abs(location[0] - 8)
        print(self.name, self.winning_row)

    def update_current_location(self, location):
        self.prev_location = self.current_location
        self.current_location = location

    def update_fence_count(self):
        self.fence_count -= 1
        self.fences.pop()

    def get_neighbour_tiles(self, increment = 1):
        """
        Return a list of neighbours tiles by an increment [Right, Top, Left, Bottom]
        """
        row, col = self.current_location[0], self.current_location[1]
        moves = [(row, col+increment), (row-increment, col), (row, col-increment), (row+increment, col)]
        for index, (row, col) in enumerate(moves):
            if not (0 <= row <= 8 and 0 <= col <= 8):
                moves[index] = None
        return moves