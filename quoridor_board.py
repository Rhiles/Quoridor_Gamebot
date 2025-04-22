from collections import deque

class Board:
    def __init__(self):
        self.size = 9
        self.pawns = {
            'P1': (4, 0),  # Starting position for Player 1 (bottom middle)
            'P2': (4, 8)   # Starting position for Player 2 (top middle)
        }
        self.fences = {
            'H': set(),  # Horizontal fences
            'V': set()   # Vertical fences
        }

    def is_within_bounds(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def get_player_positions(self):
        return list(self.pawns.values())

    def move_pawn(self, player, new_pos):
        if self.is_within_bounds(*new_pos):
            self.pawns[player] = new_pos
            return True
        return False

    def is_valid_wall_placement(self, orientation, position):
        x, y = position
        if orientation == 'H':
        # Bounds check: horizontal wall spans two horizontal cells
            if x >= self.size - 1 or y >= self.size - 1:
                return False
        # Collision check
            if position in self.fences['H']:
                 False
            if (x, y) in self.fences['V'] or (x + 1, y) in self.fences['V']:
                return True  # they can intersect
        # Check for overlapping horizontal walls
            if (x - 1, y) in self.fences['H'] or (x + 1, y) in self.fences['H']:
                return True  # adjacent is allowed
        elif orientation == 'V':
        # Bounds check: vertical wall spans two vertical cells
            if x >= self.size - 1 or y >= self.size - 1:
                return False
            if position in self.fences['V']:
                return False
            if (x, y) in self.fences['H'] or (x, y + 1) in self.fences['H']:
                return True
            if (x, y - 1) in self.fences['V'] or (x, y + 1) in self.fences['V']:
                return True
        return True

    def place_wall(self, orientation, position):
        if self.is_valid_wall_placement(orientation, position):
            self.fences[orientation].add(position)
            return True
        return False


    def print_board(self):
        for y in range(self.size):
            row = ''
            for x in range(self.size):
                p1 = self.pawns['P1']
                p2 = self.pawns['P2']
                if (x, y) == p1:
                    row += '1 '
                elif (x, y) == p2:
                    row += '2 '
                else:
                    row += '. '
            print(row)

    def get_neighbors(self, pos, opponent_pos):
        #Returns valid adjacent squares, handling jumps over the opponent.
        x, y = pos
        ox, oy = opponent_pos
        neighbors = []

        # Directions: (dx, dy)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if not self.is_within_bounds(nx, ny):
                continue
            if self.is_move_blocked((x, y), (nx, ny)):
                continue

            # If neighbor is opponent — check jump or sidestep
            if (nx, ny) == opponent_pos:
                jx, jy = nx + dx, ny + dy  # Attempt jump over opponent

                if self.is_within_bounds(jx, jy) and not self.is_move_blocked((nx, ny), (jx, jy)):
                    neighbors.append((jx, jy))  # Successful jump
                else:
                    # Diagonal sidestep options
                    if dx == 0:  # Opponent is above/below
                        for sidestep_dx in [-1, 1]:
                            sx, sy = nx + sidestep_dx, ny
                            if self.is_within_bounds(sx, sy) and not self.is_move_blocked((nx, ny), (sx, sy)):
                                neighbors.append((sx, sy))
                    elif dy == 0:  # Opponent is left/right
                        for sidestep_dy in [-1, 1]:
                            sx, sy = nx, ny + sidestep_dy
                            if self.is_within_bounds(sx, sy) and not self.is_move_blocked((nx, ny), (sx, sy)):
                                neighbors.append((sx, sy))
            else:
                neighbors.append((nx, ny))

        return neighbors


    def is_move_blocked(self, from_pos, to_pos):
        #Returns True if a fence blocks movement between two adjacent squares.
        x1, y1 = from_pos
        x2, y2 = to_pos

        if abs(x1 - x2) + abs(y1 - y2) != 1:
            return True  # Not adjacent

        # Horizontal move
        if x1 != x2:
            fence_x = min(x1, x2)
            if ('V', fence_x, y1) in self._fence_set():
                return True
        # Vertical move
        else:
            fence_y = min(y1, y2)
            if ('H', x1, fence_y) in self._fence_set():
                return True

        return False

    def _fence_set(self):
        #Returns a unified set with orientation info for easy lookup.
        return {('H', x, y) for (x, y) in self.fences['H']} | \
               {('V', x, y) for (x, y) in self.fences['V']}

    def bfs_shortest_path(self, start, goal_rows, opponent_pos):
        #BFS considering jumping over opponent.
        queue = deque([(start, [start])])
        visited = set()

        while queue:
            current_pos, path = queue.popleft()
            if current_pos in visited:
                continue
            visited.add(current_pos)

            x, y = current_pos
            if y in goal_rows:
                return path

            for neighbor in self.get_neighbors(current_pos, opponent_pos):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return None

