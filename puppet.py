import asyncio
import re
from playwright.async_api import async_playwright
from playwright.async_api import Error
import os

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

async def track_moves():
    global _page, _running

    prev_total_moves = 0
    prev_last_color = 'black'
    while _running:
        try:
            content = await _page.content()

            curr_board = parse_chessboard(content)

            total_moves, last_move_color = parse_move_list(content)

            Moved = False
            if total_moves != prev_total_moves:
                Moved = True
                prev_total_moves = total_moves
                prev_last_color = last_move_color

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
            print(f"❌ Error in track_moves: {e}")
        cnt=+1
        await asyncio.sleep(0.25)

async def highlight_best_move(move, White_on_bottom,color):
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
            // Clear old squares
            let old = document.querySelectorAll('.fromSquare, .toSquare');
            old.forEach(el => el.remove());

            // fromSquare
            let fromRow = {from_square[0]};
            let fromCol = {from_square[1]};
            let fromDiv = document.createElement('div');
            fromDiv.classList.add('fromSquare');
            fromDiv.style.position = 'absolute';
            fromDiv.style.top = (fromRow * 12.5) + '%';
            fromDiv.style.left = (fromCol * 12.5) + '%';
            fromDiv.style.width = '12.5%';
            fromDiv.style.height = '12.5%';
            fromDiv.style.cursor = "grab";
            fromDiv.style.border = '4px solid {color}';
            fromDiv.style.zIndex = 0;
            document.querySelector('.board').appendChild(fromDiv);

            // toSquare
            let toRow = {to_square[0]};
            let toCol = {to_square[1]};
            let toDiv = document.createElement('div');
            toDiv.classList.add('toSquare');
            toDiv.style.position = 'absolute';
            toDiv.style.top = (toRow * 12.5) + '%';
            toDiv.style.left = (toCol * 12.5) + '%';
            toDiv.style.width = '12.5%';
            toDiv.style.height = '12.5%';
            toDiv.style.border = '4px solid {color}';
            toDiv.style.zIndex = 0;
            document.querySelector('.board').appendChild(toDiv);

        }})();
        """
        await _page.evaluate(highlight_js)

    except Exception as e:
        print(f"Error highlighting best move: {e}")


def show_best_move_sync(move,White_on_bottom,color):
    global _loop
    if not _loop:
        print("⚠️ No event loop available. Can't show best move.")
        return

    import asyncio
    try:
        future = asyncio.run_coroutine_threadsafe(highlight_best_move(move,White_on_bottom,color), _loop)
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
            await asyncio.sleep(1)  # optional: let the site do any final scripts
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

async def main():

    global _page, _loop
    from playwright.async_api import async_playwright

    _loop = asyncio.get_running_loop()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="chromium-1161/chrome-win/chrome.exe",headless=False)
        _page = await browser.new_page()

        await _page.set_viewport_size({"width": 1920, "height": 950})
        
        await _page.goto("https://www.chess.com/play/computer")
        #await _page.wait_for_load_state("networkidle")

        await listen_for_navigation(_page)
        print("GUI should start now!")
        await inject_gui(_page)

        await track_moves()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
