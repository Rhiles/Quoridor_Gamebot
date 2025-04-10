

from quoridor_board import Board

board = Board()
board.print_board()

print("\nMoving Player 1 to (4,1):")
board.move_pawn('P1', (4, 1))
board.print_board()

print("\nPlacing horizontal fence at (3,3):")
board.place_fence('H', 3, 3)
print("Current horizontal fences:", board.fences['H'])

# Find shortest path for Player 1
p1_pos = board.pawns['P1']
goal_rows_p1 = [8]
path = board.bfs_shortest_path(p1_pos, goal_rows_p1)

print("\nShortest path for Player 1:")
print(path)
