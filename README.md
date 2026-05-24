# Typing Master

A `pygame` typing game with login, registration, score tracking, and a browser-friendly GitHub Pages entrypoint.

## Features

- Create an account or log in with saved local data
- Play a 60-second typing challenge with rotating phrases
- Track best scores and per-user history
- View a top-10 ranking board
- Open an install link from inside the app

## Project Structure

- `main.py` launches the `pygame` app locally
- `assets/main.py` contains the actual game
- `index.html` is the GitHub Pages browser launcher

## Local Run

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Start the game:

```powershell
python main.py
```

## GitHub Pages

- Publish the repository root from the `main` branch
- The live game URL is `https://taguinesdev.github.io/typeng/`
- The browser launcher loads `assets/main.py` through the `pygame-web` runtime

## Notes

- User accounts are stored in `accounts.json`
- The in-app `Install App` button opens the GitHub Releases page by default
- If you want Android or iPhone installs next, we can add a proper APK/TestFlight delivery flow on top of this
