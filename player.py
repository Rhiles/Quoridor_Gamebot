class Player():
    def __init__(self, name, location, color):
        self.name = name
        self.current_location = self.prev_location = location
        self.fences = 10
        self.color = color

    def update_current_location(self, location):
        self.prev_location = self.current_location
        self.current_location = location

    def update_fence_count(self, fences):
        self.fences = fences

    def get_neighbour_tiles(self, increment = 1):
        """
        Return a list of neighbours tiles by an increment [Right, Top, Left, Bottom]
        """
        x, y = self.current_location[0], self.current_location[1]
        moves = [(x+increment, y), (x, y+increment), (x-increment, y), (x, y-increment)]
        valid_moves = [(i, j) for i, j in moves if 0 <= i <= 8 and 0 <= j <= 8]
        return valid_moves