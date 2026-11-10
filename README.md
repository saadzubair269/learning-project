# Playroom Arcade

A browser-based arcade with 12 mini-games and a Python-powered local leaderboard.

## Run it

1. Install Python 3 if it is not already installed.
2. Double-click `run.bat`, or run `python server.py` in this folder.
3. Open `http://127.0.0.1:8000` in your browser.

The games also work by opening `index.html` directly, but score saving needs the
Python server. Scores are kept locally in `playroom.sqlite3`; the server only
listens on your own computer.

## Find and play games

- Use the category filters, search box, or sort menu to find a game.
- Press `/` or `Ctrl+K` to jump to search; use the star button to pick a random game.
- Save favorites with the heart buttons. Favorites and recently played games stay
  in this browser.
- The featured daily challenge rotates between all 12 games. Finish a round in
  today's featured game to grow your streak; your current and best streaks are
  saved in this browser.
- Temple Run 2, Subway Surfers, and 4D Car Game are listed separately as in
  progress; they are not playable yet.
- Game dialogs can be closed with `Esc`. Snake and Merge Up also include touch
  direction controls on smaller screens.
