import asyncio
import threading
import puppet
import stockfishapi
import parserFEN
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import os

def run_puppet_in_thread():
    asyncio.run(puppet.main())

puppet_thread = threading.Thread(target=run_puppet_in_thread, daemon=True)
puppet_thread.start()

# === MASTER VARIABLES ===
StartButton = False
GuiCheckbox1 = True
GuiCheckbox2 = False
TimeCheckBox = False
DepthCheckBox = True
SkillCheckBox = False
ColorSelector0 = "#FF0000" 
Slider0 = 1 
ColorSelector1 = "#00FF00" 
Slider1 = 1
ColorSelector2 = "#0000FF" 
Slider2 = 1200
Teacher = False
NoBlunder = False
Engine = True

# === FUNCTION TO UPDATE VARIABLES ===
def update_variables():
    global StartButton, GuiCheckbox1, GuiCheckbox2, TimeCheckBox, DepthCheckBox
    global SkillCheckBox, ColorSelector0, Slider0,ColorSelector1, Slider1,ColorSelector2, Slider2, Teacher, NoBlunder, Engine

    if os.path.exists("gui.txt") and os.path.getsize("gui.txt") > 0:
        try:
            with open("gui.txt", "r") as f:
                lines = f.readlines()
            with open("gui.txt", "w") as f:
                pass  

            for line in lines:
                try:
                    line = (
                        line.strip()
                        .replace("'", "\"") 
                        .replace("True", "true")
                        .replace("False", "false")
                    )

                    if line.startswith("{") and line.endswith("}"):
                        entry = json.loads(line)
                    else:
                        print(f"Skipping invalid line: {line}")
                        continue

                    id_name = entry["id"]
                    value = entry["value"]

                    if id_name == "StartButton":
                        StartButton = not StartButton

                    elif id_name == "GuiCheckbox1":
                        GuiCheckbox1 = bool(value)
                        GuiCheckbox2 = False

                    elif id_name == "GuiCheckbox2":
                        GuiCheckbox2 = bool(value)
                        GuiCheckbox1 = False

                    elif id_name == "TimeCheckBox":
                        TimeCheckBox = bool(value)
                        DepthCheckBox = False
                        SkillCheckBox = False
                        print("TIME CHECKED!")

                    elif id_name == "DepthCheckBox":
                        DepthCheckBox = bool(value)
                        TimeCheckBox = False
                        SkillCheckBox = False

                    elif id_name == "SkillCheckBox":
                        SkillCheckBox = bool(value)
                        TimeCheckBox = False
                        DepthCheckBox = False

                    elif id_name == "ColorSelector0":
                        ColorSelector0 = value

                    elif id_name == "Slider0":
                        Slider0 = int(value)

                    elif id_name == "ColorSelector1":
                        ColorSelector1 = value

                    elif id_name == "Slider1":
                        Slider1 = int(value)

                    elif id_name == "ColorSelector2":
                        ColorSelector2 = value

                    elif id_name == "Slider2":
                        Slider2 = int(value)
                        print(Slider2)

                    elif id_name == "Teacher":
                        Teacher = bool(value)
                        NoBlunder = False
                        Engine = False

                    elif id_name == "NoBlunder":
                        NoBlunder = bool(value)
                        Teacher = False
                        Engine = False

                    elif id_name == "Engine":
                        Engine = bool(value)
                        Teacher = False
                        NoBlunder = False

                except json.JSONDecodeError:
                    print(f"Skipping invalid line: {line}")

        except Exception as e:
            print(f"Error reading gui.txt: {e}")

# === FILE CHANGE LISTENER ===
class FileChangeHandler(FileSystemEventHandler):
	def on_modified(self, event):
		if event.src_path.endswith("gui.txt"):
			update_variables()


# === START MONITORING ===
event_handler = FileChangeHandler()
observer = Observer()
observer.schedule(event_handler, ".", recursive=False)
observer.start()
#---------------------------------------------------------------------------------------------------------------------

def read_chessboard():
    try:
        with open("chessboard.txt", "r") as f:
            lines = f.readlines()

        if not lines:
            print("⚠️ chessboard.txt is empty.")
            return None, None,None, []

        didMove_str = lines[0].strip()
        didMove = (didMove_str == "True")

        WhoNext = lines[1].strip()
        moves = int(lines[2].strip())

        board = [line.strip().split() for line in lines[3:]]

        return didMove, WhoNext,moves ,board

    except FileNotFoundError:
        print("❌ chessboard.txt not found.")
        return None, None, None, []

white_on_bottom=True

stockfish_path = "./stockfish/stockfish-windows-x86-64-avx2.exe"
stockfish = stockfishapi.start_stockfish(stockfish_path)

def isStartBoard(board):
    expected = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]
    expected2 = [
    ['R', 'N', 'B', 'K', 'Q', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['r', 'n', 'b', 'k', 'q', 'b', 'n', 'r']
    ]
    if board == expected or board == expected2:
        return True
    else:
        return False

print("Master did setup!")

time.sleep(1)

while True:

    time.sleep(0.25)
    didMove,WhoNext,moves, board = read_chessboard()
    Restart = isStartBoard(board)
    if Restart:
        moves=0
        WhoNext="white"
        if board[0][0]=='r':
            white_on_bottom = True
        else:
            white_on_bottom = False
        initial_fen = parserFEN.matrix_to_fen(board, moves, WhoNext,white_on_bottom)
    if didMove:
        stockfishapi.stop_current_command(stockfish)
        initial_fen = parserFEN.matrix_to_fen(board, moves, WhoNext,white_on_bottom)
        print(initial_fen)
        score,mate_score,pv1,pv2,pv3 = stockfishapi.get_stockfish_score(stockfish,15,initial_fen)
        stockfishapi.set_position_fen(stockfish, initial_fen)
        print(score)
        print(pv1,pv2,pv3)
        future = asyncio.run_coroutine_threadsafe(
            puppet.update_gui(initial_fen,board,score,mate_score,pv1,pv2,pv3),
            puppet._loop
        )
        future.result()

        best_move = ""
        if(SkillCheckBox==True):
            print("Skill")
            stockfishapi.set_elo_rating(stockfish,Slider2)
            best_move = stockfishapi.get_depth_move(stockfish, 15)
            puppet.show_best_move_sync(best_move,white_on_bottom,ColorSelector2)
        else:
            stockfishapi.reset_elo_rating(stockfish)
        if(DepthCheckBox==True):
            print("Depth")
            best_move = stockfishapi.get_depth_move(stockfish, Slider0)
            puppet.show_best_move_sync(best_move,white_on_bottom,ColorSelector0)
        if(TimeCheckBox==True):
            print("timeCheck")
            best_move = stockfishapi.get_time_move(stockfish, Slider1)
            puppet.show_best_move_sync(best_move,white_on_bottom,ColorSelector1)
        print(best_move)

observer.stop()
observer.join()