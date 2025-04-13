import subprocess
import sys
import os

def start_stockfish(stockfish_path):
    try:
        CREATE_NO_WINDOW = 0x08000000

        stockfish = subprocess.Popen(
            stockfish_path,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        return stockfish
    except Exception as e:
        print(f"Error starting Stockfish: {e}")
        sys.exit(1)

def send_uci_command(stockfish):
    try:
        stockfish.stdin.write("uci\n")
        stockfish.stdin.flush()
        response = stockfish.stdout.readline()
        return response
    except Exception as e:
        print(f"Error during UCI command: {e}")
        return None

def set_position(stockfish, move):
    try:
        stockfish.stdin.write(f"position moves {move}\n")
        stockfish.stdin.flush()
    except Exception as e:
        print(f"Error setting position: {e}")

def set_position_fen(stockfish, fen):
    try:
        stockfish.stdin.write(f"position fen {fen}\n")
        stockfish.stdin.flush()
    except Exception as e:
        print(f"Error setting FEN: {e}")

def stop_current_command(stockfish):
	try:
		stockfish.stdin.write("stop\n")
		stockfish.stdin.flush()
		print("Stopped stockfish")
	except Exception as e:
		print(f"Error stopping current command: {e}")

def get_stockfish_score(stockfish, depth, fen):
	try:
		stockfish.stdin.write(f"setoption name MultiPV value 3\n")
		stockfish.stdin.flush()

		stockfish.stdin.write(f"position fen {fen}\n")
		stockfish.stdin.flush()

		stockfish.stdin.write(f"go depth {depth}\n")
		stockfish.stdin.flush()

		score = None
		mate_score = None
		pvs = []
		while True:
			line = stockfish.stdout.readline().strip()
			if "info depth" in line:
				parts = line.split()

				if "score" in parts:
					score_index = parts.index("score") + 1
					if parts[score_index] == "cp":
						score = int(parts[score_index + 1]) / 100.0
					elif parts[score_index] == "mate":
						mate_in = int(parts[score_index + 1])
						if mate_in > 0:
							mate_score = f"M{mate_in}"
							score = 9999
						else:
							mate_score = f"M{-mate_in}"
							score = -9999

				if "pv" in parts:
					pv_index = parts.index("pv") + 1
					pv_moves = " ".join(parts[pv_index:])
					if pv_moves and pv_moves not in pvs:
						pvs.append(pv_moves)

			if line.startswith("bestmove"):
				break

		while len(pvs) < 3:
			pvs.append("None")

		if fen:
			turn = fen.split(" ")[1]
			if turn == "b" and score is not None:
				score = -score

		if mate_score is None and score is not None:
			mate_score = "none"

		stockfish.stdin.write("setoption name MultiPV value 1\n")
		stockfish.stdin.flush()

		return score, mate_score, pvs[0], pvs[1], pvs[2]

	except Exception as e:
		print(f"Error getting Stockfish score: {e}")
		return None, "none", "None", "None", "None"

def set_elo_rating(stockfish, elo):
	try:
		stockfish.stdin.write(f"setoption name UCI_LimitStrength value true\n")
		stockfish.stdin.write(f"setoption name UCI_Elo value {elo}\n")
		stockfish.stdin.flush()
	except Exception as e:
		print(f"Error setting Elo rating: {e}")

def reset_elo_rating(stockfish):
	try:
		stockfish.stdin.write("setoption name UCI_LimitStrength value false\n")
		stockfish.stdin.flush()
	except Exception as e:
		print(f"Error resetting Elo rating: {e}")

def get_time_move(stockfish, movetime):
    try:
        stockfish.stdin.write(f"go movetime {movetime}\n")
        stockfish.stdin.flush()
        move = ""
        while True:
            line = stockfish.stdout.readline().strip()
            if line.startswith("bestmove"):
                move = line.split()[1]
                break
        return move
    except Exception as e:
        print(f"Error during time move calculation: {e}")
        return None

def get_depth_move(stockfish, depth):
    try:
        stockfish.stdin.write(f"go depth {depth}\n")
        stockfish.stdin.flush()
        move = ""
        while True:
            line = stockfish.stdout.readline().strip()
            if line.startswith("bestmove"):
                move = line.split()[1]
                break
        return move
    except Exception as e:
        print(f"Error during depth move calculation: {e}")
        return None

def main():
    stockfish_path = "./stockfish/stockfish-windows-x86-64-avx2.exe"
    stockfish = start_stockfish(stockfish_path)

    send_uci_command(stockfish)

    # Example for setting position with FEN
    initial_fen = "r2q1bn1/1b1p4/1pn1p2r/p4p1N/2P1PP1p/PPN4P/2PBQ1B1/R4RK1 b - - 0 1"
    set_position_fen(stockfish, initial_fen)

    # Example to get best move based on time
    best_move = get_time_move(stockfish, 500)
    if best_move:
        print(f"Best move (by time): {best_move}")

    stockfish.stdin.write("quit\n")  # Quit the Stockfish instance
    stockfish.stdin.flush()

if __name__ == "__main__":
    main()
