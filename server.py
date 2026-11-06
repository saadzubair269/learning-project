import json
import re
import sqlite3
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "playroom.sqlite3"
GAMES = {
    "nitro", "duel", "snake", "blaster", "pong", "bricks",
    "tic", "memory", "2048", "reflex", "rps", "word",
}
MAX_BODY_SIZE = 2048
MAX_SCORE = 1_000_000
PLAYER_NAME = re.compile(r"^[\w .'-]{1,20}$", re.UNICODE)


@contextmanager
def connect_database():
    connection = sqlite3.connect(DATABASE, timeout=5)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY,
                game TEXT NOT NULL,
                player TEXT NOT NULL,
                score INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        with connection:
            yield connection
    finally:
        connection.close()


class PlayroomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        request = urlparse(self.path)
        if request.path != "/api/scores":
            return super().do_GET()

        game = parse_qs(request.query).get("game", ["nitro"])[0]
        if not isinstance(game, str) or game not in GAMES:
            return self.send_json(400, {"error": "Choose a valid game."})

        direction = "ASC" if game == "reflex" else "DESC"
        try:
            with connect_database() as connection:
                scores = connection.execute(
                    f"""SELECT player, score, created_at FROM scores
                        WHERE game = ? ORDER BY score {direction}, id ASC LIMIT 10""",
                    (game,),
                ).fetchall()
        except sqlite3.Error:
            self.log_error("Could not read the score database.")
            return self.send_json(500, {"error": "Scores could not be loaded."})

        self.send_json(200, {
            "game": game,
            "scores": [dict(score) for score in scores],
        })

    def do_POST(self):
        if urlparse(self.path).path != "/api/scores":
            return self.send_json(404, {"error": "Endpoint not found."})

        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            return self.send_json(400, {"error": "A valid request length is required."})
        if length < 1 or length > MAX_BODY_SIZE:
            return self.send_json(413, {"error": "The score request is too large."})

        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.send_json(400, {"error": "The request must contain valid JSON."})
        if not isinstance(payload, dict):
            return self.send_json(400, {"error": "A score object is required."})

        game = payload.get("game")
        player = payload.get("player")
        score = payload.get("score")
        if not isinstance(game, str) or game not in GAMES:
            return self.send_json(400, {"error": "Choose a valid game."})
        if not isinstance(player, str) or not PLAYER_NAME.fullmatch(player.strip()):
            return self.send_json(
                400,
                {"error": "Player names must be 1–20 letters, numbers, spaces, or . ' - _"},
            )
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= MAX_SCORE:
            return self.send_json(400, {"error": "Score must be a whole number from 0 to 1,000,000."})

        try:
            direction = "ASC" if game == "reflex" else "DESC"
            with connect_database() as connection:
                connection.execute(
                    "INSERT INTO scores (game, player, score) VALUES (?, ?, ?)",
                    (game, player.strip(), score),
                )
                connection.execute(
                    f"""DELETE FROM scores WHERE game = ? AND id NOT IN (
                        SELECT id FROM scores WHERE game = ?
                        ORDER BY score {direction}, id ASC LIMIT 100
                    )
                    """,
                    (game, game),
                )
        except sqlite3.Error:
            self.log_error("Could not save the score.")
            return self.send_json(500, {"error": "The score could not be saved."})

        self.send_json(201, {"saved": True, "game": game, "player": player.strip(), "score": score})


if __name__ == "__main__":
    address = ("127.0.0.1", 8000)
    print(f"Playroom is ready at http://{address[0]}:{address[1]}")
    print("Press Ctrl+C to stop the server.")
    try:
        ThreadingHTTPServer(address, PlayroomHandler).serve_forever()
    except KeyboardInterrupt:
        print("\nPlayroom server stopped.")
