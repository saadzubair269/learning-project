# Playroom Arcade

A browser-based arcade with 12 mini-games and a Python-powered local leaderboard.

## Run it

1. Install Python 3 if it is not already installed.
2. Double-click `run.bat`, or run `python server.py` in this folder.
3. Open `http://127.0.0.1:8000` in your browser.

The games also work by opening `index.html` directly, but score saving needs the
Python server. Scores are kept locally in `playroom.sqlite3`; the server only
listens on your own computer.
