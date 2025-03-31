def matrix_to_fen(chessboard, moves, WhoNext, white_on_bottom, last_move=None):

	if not white_on_bottom:
		rotateMatrix(chessboard)
		
	fen_rows = []
	halfmove_clock = 0
	for row in chessboard:
		empty = 0
		row_str = ""
		for square in row:
			if square == ".":
				empty += 1
			else:
				if empty > 0:
					row_str += str(empty)
					empty = 0
				row_str += square

				if square.lower() == 'p' or last_move and chessboard[last_move[1][0]][last_move[1][1]] != ".":
					halfmove_clock = 0
		if empty > 0:
			row_str += str(empty)
		fen_rows.append(row_str)
	board_fen = "/".join(fen_rows)

	if(WhoNext=="white"):
		turn = "w"
	else:
		turn = "b"

	castling = get_castling_rights(chessboard, turn)

	en_passant_target = get_en_passant_target(chessboard,last_move)

	fullmove_number = moves // 2 + 1

	return f"{board_fen} {turn} {castling} {en_passant_target} {halfmove_clock} {fullmove_number}"


def get_castling_rights(chessboard, turn):
	rights = ""

	if chessboard[7][4] == 'K' and not is_king_attacked(chessboard, "w"):
		if chessboard[7][7] == 'R':
			rights += 'K'
		if chessboard[7][0] == 'R':
			rights += 'Q'

	if chessboard[0][4] == 'k' and not is_king_attacked(chessboard, "b"):
		if chessboard[0][7] == 'r':
			rights += 'k'
		if chessboard[0][0] == 'r':
			rights += 'q'

	return rights if rights else "-"


def is_king_attacked(chessboard, color):
	king_symbol = 'K' if color == "w" else 'k'
	king_position = None

	for i in range(8):
		for j in range(8):
			if chessboard[i][j] == king_symbol:
				king_position = (i, j)
				break
		if king_position:
			break

	if not king_position:
		return False

	enemy_color = "b" if color == "w" else "w"
	return is_square_attacked(chessboard, king_position, enemy_color)


def is_square_attacked(chessboard, position, attacker_color):
	attackers = {
		"p": [(1, -1), (1, 1)] if attacker_color == "w" else [(-1, -1), (-1, 1)],
		"n": [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
		"b": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
		"r": [(1, 0), (-1, 0), (0, 1), (0, -1)],
		"q": [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)],
		"k": [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)],
	}

	for dx, dy in attackers["n"]:
		px, py = position[0] + dx, position[1] + dy
		if 0 <= px < 8 and 0 <= py < 8 and chessboard[px][py].lower() == "n" and chessboard[px][py].islower() == (attacker_color == "b"):
			return True

	for piece in ["b", "r", "q"]:
		for dx, dy in attackers[piece]:
			px, py = position
			while True:
				px += dx
				py += dy
				if not (0 <= px < 8 and 0 <= py < 8):
					break
				if chessboard[px][py] != ".":
					if chessboard[px][py].lower() == piece and chessboard[px][py].islower() == (attacker_color == "b"):
						return True
					break

	for dx, dy in attackers["p"]:
		px, py = position[0] + dx, position[1] + dy
		if 0 <= px < 8 and 0 <= py < 8 and chessboard[px][py].lower() == "p" and chessboard[px][py].islower() == (attacker_color == "b"):
			return True

	for dx, dy in attackers["k"]:
		px, py = position[0] + dx, position[1] + dy
		if 0 <= px < 8 and 0 <= py < 8 and chessboard[px][py].lower() == "k" and chessboard[px][py].islower() == (attacker_color == "b"):
			return True

	return False


def get_en_passant_target(chessboard, last_move):
    if not last_move:
        return "-"
    start, end = last_move
    start_x, start_y = start
    end_x, end_y = end

    if abs(start_x - end_x) == 2 and chessboard[end_x][end_y].lower() == 'p':
        en_passant_rank = 5 if chessboard[end_x][end_y].isupper() else 2
        return f"{chr(end_y + 97)}{en_passant_rank}"

    return "-"


def rotateMatrix(mat):
	n = len(mat)
	res = [[0] * n for _ in range(n)]
	for i in range(n):
		for j in range(n):
			res[i][j] = mat[n - i - 1][n - j - 1]
	for i in range(n):
		for j in range(n):
			mat[i][j] = res[i][j]
