import asyncio
import threading
import puppet
import stockfishapi
import parserFEN
import time
import json
import os
import win32file
import win32con


# === MASTER VARIABLES ===
_running=True
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
Slider2 = 1320
Teacher = False
NoBlunder = False
Engine = True
# === GAME STATE VARIABLES ===
Didmove = False
WhoNext = "white"
Moves = 0
Board = None

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


def read_file_contents(filepath):
    try:
        with open(filepath, "r") as f:
            return f.read()
    except Exception:
        return None
#---------------------------------------------------------------------------------------------------------------------

def update_chessboard():
    global Didmove,WhoNext,Moves,Board,appstart,_running,GuiCheckbox2,GuiCheckbox1
    try:
        with open("chessboard.txt", "r") as f:
            lines = f.readlines()
        if not lines:
            #print("⚠️ chessboard.txt is empty.")
            return None, None,None, []
        didMove_str = lines[0].strip()
        if didMove_str=="CLOSE":
            _running=False
            return None, None, None, []
        Didmove = (didMove_str == "True")

        WhoNext = lines[1].strip()
        Moves = int(lines[2].strip())
        Board = [line.strip().split() for line in lines[3:]]

        if (Didmove == True):
            #RESET CASTLING DACA TREBUIE
            Restart = isStartBoard(Board)
            if Restart:
                parserFEN.ResetCastling()

            DoMove()
        return Didmove, WhoNext,Moves ,Board

    except FileNotFoundError:
        print("❌ chessboard.txt not found.")
        return None, None, None, []

stockfish_path = "./stockfish/stockfish-windows-x86-64-avx2.exe"
stockfish = stockfishapi.start_stockfish(stockfish_path)

def isStartBoard(Board):
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
    if Board == expected or Board == expected2:
        return True
    else:
        return False

def DoMove():
    initial_fen = parserFEN.matrix_to_fen(Board, Moves, WhoNext,GuiCheckbox1)
    if initial_fen =="8/8/8/8/8/8/8/8 w - - 0 1":
        return 0
    score,mate_score,pv1,pv2,pv3 = stockfishapi.get_stockfish_score(stockfish,15,initial_fen)
    stockfishapi.set_position_fen(stockfish, initial_fen)

    #print(initial_fen)
    #print(score)
    #print(pv1,pv2,pv3)

    future = asyncio.run_coroutine_threadsafe(
        puppet.update_gui(initial_fen,Board,score,mate_score,pv1,pv2,pv3),
        puppet._loop
    )
    future.result()

    best_move = None
    if(SkillCheckBox==True):
        #print("Skill")
        stockfishapi.set_elo_rating(stockfish,Slider2)
        best_move = stockfishapi.get_depth_move(stockfish, 15)
        puppet.show_best_move_sync(best_move,GuiCheckbox1,ColorSelector2,1)
    else:
        stockfishapi.reset_elo_rating(stockfish)
    if(DepthCheckBox==True):
        #print("Depth")
        best_move = stockfishapi.get_depth_move(stockfish, Slider0)
        puppet.show_best_move_sync(best_move,GuiCheckbox1,ColorSelector0,1)
    if(TimeCheckBox==True):
        #print("timeCheck")
        best_move = stockfishapi.get_time_move(stockfish, Slider1)
        puppet.show_best_move_sync(best_move,GuiCheckbox1,ColorSelector1,1)
    #print(best_move)

def reset():
    global _running,StartButton,GuiCheckbox1,GuiCheckbox2,TimeCheckBox,DepthCheckBox,SkillCheckBox,ColorSelector0,Slider0,ColorSelector1,Slider1,ColorSelector2,Slider2,Teacher,NoBlunder,Engine,Didmove,WhoNext,Moves,Board
    _running=True
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
    Slider2 = 1320
    Teacher = False
    NoBlunder = False
    Engine = True
    # === GAME STATE VARIABLES ===
    Didmove = False
    WhoNext = "white"
    Moves = 0
    Board = None

def main():
    
    parserFEN.ResetCastling()
    reset()

    def run_puppet_in_thread():
        asyncio.run(puppet.main())

    puppet_thread = threading.Thread(target=run_puppet_in_thread, daemon=True)
    puppet_thread.start()

    # === FILE CHANGE LISTENER ===
    path_to_watch = "."

    last_contents = {
        "gui.txt": None,
        "chessboard.txt": None,
    }

    hDir = win32file.CreateFile(
        path_to_watch,
        win32con.GENERIC_READ,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    # ==== ----------------- ==== 
    print("Master did setup!")
    global _running
    while _running:
        results = win32file.ReadDirectoryChangesW(
            hDir,
            32768*2,
            False,
            win32con.FILE_NOTIFY_CHANGE_SIZE,
            None,
            None
        )

        for action, file in results:
            full_filename = os.path.join(path_to_watch, file)

            if file in last_contents:
                new_content = read_file_contents(full_filename)
                if new_content is None:
                    continue

                if new_content != last_contents[file]:
                    last_contents[file] = new_content

                    if file == "gui.txt":
                        update_variables()
                    elif file == "chessboard.txt":
                        #time.sleep(0.05)
                        update_chessboard()
        time.sleep(0.2)
    _running=True

if __name__ == "__main__":
    main()