import asyncio
import re
from playwright.async_api import async_playwright
from playwright.async_api import Error
import os
import requests

browser= None
_page = None
_loop = None
_running = True 

def parse_chessboard(html_content):
	piece_pattern = re.findall(
		r'<div class="piece (?:square-(\d{2}) )?(\w{2})(?: square-(\d{2}))?"',
		html_content
	)

	board = [['.' for _ in range(8)] for _ in range(8)]

	def square_to_index(square):
		row = 8 - int(square[1])
		col = int(square[0]) - 1
		return row, col

	piece_map = {
		'wp': 'P', 'wn': 'N', 'wb': 'B', 'wr': 'R', 'wq': 'Q', 'wk': 'K',
		'bp': 'p', 'bn': 'n', 'bb': 'b', 'br': 'r', 'bq': 'q', 'bk': 'k'
	}

	player_is_black = bool(re.search(r'<text x="97\.5" y="99" font-size="2\.8" class="coordinate-light">a</text>', html_content))

	for match in piece_pattern:
		square = match[0] or match[2]
		piece = match[1]
		if square and piece in piece_map:
			row, col = square_to_index(square)
			board[row][col] = piece_map[piece]

	if player_is_black:
		board = [row[::-1] for row in board[::-1]]

	return board


def parse_move_list(html_content):
    reg = r'<div data-node="\d+-(\d+)" class="node (white|black)-move main-line-ply">'
    matches = re.findall(reg, html_content)
    if len(matches) == 0:
        return 0, 'black'
    return 1+int(matches[-1][0], 10), matches[-1][1]

def check_Board(Board):
    cnt=0
    K=0
    k=0
    for i in range (0,8,1):
        for j in range(0,8,1):
            if Board[i][j]=='.':
                cnt+=1
            if Board[i][j]=='k':
                k=1
            if Board[i][j]=='K':
                K=1
    if cnt==64:
        return False
    if K!=1 or k!=1:
        return False
    return True

async def track_moves():
    global _page, _running

    prev_total_moves = 0
    prev_last_color = 'black'
    prev_board = None
    while _running:
        try:
            if _page.is_closed():
                handle_browser_close()
            #browser.on("close", handle_browser_close)
            content = await _page.content()
            curr_board = parse_chessboard(content)
            total_moves, last_move_color = parse_move_list(content)
            Moved = False
            
            if total_moves != prev_total_moves:
                await remove_move_sync(1)
                Moved = True
                prev_total_moves = total_moves
                prev_last_color = last_move_color
                CheckValidity = check_Board(curr_board)
                if CheckValidity==False:
                    Moved=False

            if prev_last_color == 'black':
                who_next = 'white'
            else:
                who_next = 'black'
            with open("chessboard.txt", "w") as f:
                f.write(f"{Moved}\n")
                f.write(f"{who_next}\n")
                f.write(f"{total_moves}\n")
                for row in curr_board:
                    f.write(" ".join(row) + "\n")
        except Exception as e:
            print(f"❌{e}")
        await asyncio.sleep(0.2)
    _running=True

async def remove_move_sync(number):
	global _page
	try:
		#print("REMOVE!")
		Remove_js = f"""
		(function() {{
			let oldSvg = document.querySelector('.move-svg{number}');
            if(oldSvg) oldSvg.remove();
		}})();
		"""
		await _page.evaluate(Remove_js)
	except Exception as e:
		print(f"Error removing best move: {e}")


async def highlight_best_move(move, White_on_bottom,color,number):
    global _page
    if not _page:
        print("⚠️ No page reference yet. Can't highlight best move.")
        return

    try:
        if isinstance(move, str):
            if White_on_bottom:
                from_square = (8 - int(move[1]))
                from_col = ord(move[0]) - ord('a')
                to_square = (8 - int(move[3]))
                to_col = ord(move[2]) - ord('a')
                from_square = (from_square, from_col)
                to_square = (to_square, to_col)
            if not White_on_bottom:
                from_square = (int(move[1]) - 1)
                from_col = 7 - (ord(move[0]) - ord('a'))
                to_square = (int(move[3]) - 1)
                to_col = 7 - (ord(move[2]) - ord('a'))
                from_square = (from_square, from_col)
                to_square = (to_square, to_col)
        elif isinstance(move, tuple) and len(move) == 2:
            from_square, to_square = move
        else:
            print("⚠️ Invalid move format.")
            return

        board_locator = _page.locator('.board')
        if not board_locator:
            print("⚠️ Board element not found.")
            return
        highlight_js = f"""
        (function() {{
            let oldSvg = document.querySelector('.move-svg{number}');
            if(oldSvg) oldSvg.remove();

            let board = document.querySelector('.board');
            if (!board) return;

            let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.classList.add('move-svg{number}');
            svg.setAttribute("width", board.offsetWidth);
            svg.setAttribute("height", board.offsetHeight);
            svg.style.position = "absolute";
            svg.style.top = "0";
            svg.style.left = "0";
            svg.style.pointerEvents = "none";
            svg.style.opacity = "1";

            let boardWidth = board.offsetWidth;
            let boardHeight = board.offsetHeight;
            let squareWidth = boardWidth / 8;
            let squareHeight = boardHeight / 8;

            let fromRow = {from_square[0]};
            let fromCol = {from_square[1]};
            let toRow   = {to_square[0]};
            let toCol   = {to_square[1]};

            let centerFromX = fromCol * squareWidth + squareWidth / 2;
            let centerFromY = fromRow * squareHeight + squareHeight / 2;
            let centerToX   = toCol * squareWidth + squareWidth / 2;
            let centerToY   = toRow * squareHeight + squareHeight / 2;

            let dx = centerToX - centerFromX;
            let dy = centerToY - centerFromY;
            let dist = Math.sqrt(dx * dx + dy * dy);
            let u_x = dx / dist;
            let u_y = dy / dist;

            let half = squareWidth / 2;
            let t = half / Math.max(Math.abs(u_x), Math.abs(u_y));
            let newFromX = centerFromX + t * u_x;
            let newFromY = centerFromY + t * u_y;

            // --- Source square rectangle (no z-index; stays under pieces)
            let startRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            startRect.setAttribute("x", fromCol * squareWidth);
            startRect.setAttribute("y", fromRow * squareHeight);
            startRect.setAttribute("width", squareWidth);
            startRect.setAttribute("height", squareHeight);
            startRect.setAttribute("stroke", "{color}");
            startRect.setAttribute("stroke-width", "3");
            startRect.setAttribute("fill", "none");
            startRect.style.pointerEvents = "none";
            svg.appendChild(startRect);

            // --- Group for higher z-index elements: line + destination circle
            let group = document.createElementNS("http://www.w3.org/2000/svg", "g");
            group.style.zIndex = "-1";  // This should visually push these above pieces
            group.style.pointerEvents = "none";

            let line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", newFromX);
            line.setAttribute("y1", newFromY);
            line.setAttribute("x2", centerToX);
            line.setAttribute("y2", centerToY);
            line.setAttribute("stroke", "{color}");
            line.setAttribute("stroke-width", "5");
            line.style.pointerEvents = "none";
            group.appendChild(line);

            let destCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            destCircle.setAttribute("cx", centerToX);
            destCircle.setAttribute("cy", centerToY);
            destCircle.setAttribute("r", Math.min(squareWidth, squareHeight) / 7);
            destCircle.setAttribute("stroke", "{color}");
            destCircle.setAttribute("stroke-width", "3");
            destCircle.setAttribute("fill", "{color}");
            destCircle.style.pointerEvents = "none";
            group.appendChild(destCircle);

            svg.appendChild(group);
            board.appendChild(svg);
        }})();
        """
        
        await _page.evaluate(highlight_js)

    except Exception as e:
        print(f"Error highlighting best move: {e}")


def show_best_move_sync(move,White_on_bottom,color,number):
    global _loop
    if not _loop:
        print("⚠️ No event loop available. Can't show best move.")
        return

    import asyncio
    try:
        future = asyncio.run_coroutine_threadsafe(highlight_best_move(move,White_on_bottom,color,number), _loop)
        future.result()
    except Exception as e:
        print(f"Error in show_best_move_sync: {e}")

#----------------------------------GUI CLIENT --------------------------------------

async def listen_for_navigation(page):
    """
    Attach an event listener that re-injects the GUI after each navigation.
    Call this once, e.g. after you create 'page' in main().
    """
    page.on("framenavigated", lambda frame: asyncio.create_task(_handle_navigation(frame, page)))

async def _handle_navigation(frame, page):
    """
    Called each time any frame navigates. If it's the main frame,
    wait for load, then re-inject the GUI safely.
    """
    if frame == page.main_frame:
        print("🔵 Main frame navigated. Re-injecting GUI soon...")
        try:
            # Wait for the page to be stable
            await page.wait_for_load_state("domcontentloaded")
            # Then do a short delay if needed
            await asyncio.sleep(2)  # optional: let the site do any final scripts
            # Re-inject
            await inject_gui(page)
        except Exception as e:
            print("❌ Error re-injecting GUI after navigation:", e)

#----------------------------------REINJECT GUI------------------------------------

async def on_gui_change(change_data: dict):
    #print("GUI Change Detected:", change_data)
    log_entry = f"{change_data}\n"

    with open("gui.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)


_on_gui_change_registered = False

async def inject_gui(page):
    global _on_gui_change_registered

    # Expose the function only once
    if not _on_gui_change_registered:
        await page.expose_function("onGuiChange", on_gui_change)
        _on_gui_change_registered = True
        print("✅ onGuiChange function exposed.")

    with open("gui.js", "r", encoding="utf-8") as f:
        js_code = f.read()

    await page.evaluate(js_code)
    print("✅ GUI code injected successfully.")

async def safe_evaluate(page, script):
    while True:
        try:
            return await page.evaluate(script)
        except Error as e:
            # If the page navigates mid-eval, context is destroyed
            if "Execution context was destroyed" in str(e):
                print("⚠️ Navigation during update_gui. Waiting, then retrying injection...")
                await page.wait_for_load_state("domcontentloaded")
                continue
            else:
                raise

async def update_gui(new_text: str, matrix,score:float,mate_score:str,pv1:str,pv2:str,pv3:str):
    global _page
    if not _page:
        print("⚠️ No page reference yet. Can't update GUI.")
        return
    matrix_js = str(matrix).replace("'", '"')

    script = f"""
    (function() {{
        let fenDisplay = document.getElementById("fenDisplay");
        if (fenDisplay) {{
            fenDisplay.value ="FEN:{new_text}";
        }}
    }})();
    (function() {{
        if (typeof updateChessboardFromMatrix === 'function') {{
            updateChessboardFromMatrix({matrix_js});
        }}
    }})();
    (function() {{
		if (typeof updateBar === 'function') {{
			updateBar({score},"{mate_score}");
		}}
	}})();
    (function() {{
		if (typeof updatePVS === 'function') {{
			updatePVS("PV1:{pv1}","PV2:{pv2}","PV3:{pv3}");
		}}
	}})();
    """
    await safe_evaluate(_page, script)

def handle_browser_close():
    global _running
    print("Browser is closing. Sending signal to server...")
    with open("chessboard.txt", "w") as f:
        f.write(f"CLOSE\n")
    with open("token.txt", "r") as f:
        tokenlines = f.readlines()
    token = tokenlines[0].strip()
    response = requests.get("https://chess-demo.mihneaspiridon.workers.dev/",
                headers={
                    "Action": "Release",
                    "Token": f"{token}"
                })
    print(response.status_code)
    _running=False

def reset_globals():
    global _page, _loop, _running, _on_gui_change_registered
    _page = None
    _loop = None
    _running = True
    _on_gui_change_registered = False

async def main():
    reset_globals()
    global _page, _loop,browser
    from playwright.async_api import async_playwright

    _loop = asyncio.get_running_loop()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="chromium-1161/chrome-win/chrome.exe",headless=False, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        _page = await browser.new_page(no_viewport=True)

        #await _page.set_viewport_size({"width": 1920, "height": 950})
        
        await _page.goto("https://www.chess.com/play/computer")
        #await _page.wait_for_load_state("networkidle")

        await listen_for_navigation(_page)
        print("GUI should start now!")
        await inject_gui(_page)

        await track_moves()
        browser.on("close", handle_browser_close)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
