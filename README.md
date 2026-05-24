# Typing Master

A `pygame` typing game with login, registration, score tracking, and a browser-friendly GitHub Pages entrypoint.

## Features

- Create an account or log in with saved local data
- Play a 60-second typing challenge with rotating phrases
- Track best scores and per-user history
- View a top-10 ranking board
- Install the web app on supported mobile and desktop browsers

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

- Set `Settings > Pages > Build and deployment > Source` to `GitHub Actions`
- The live game URL is `https://taguinesdev.github.io/typeng/`
- The browser launcher loads `assets/main.py` through the `pygame-web` runtime
- The workflow in `.github/workflows/deploy-pages.yml` validates the Python files and deploys the site automatically on every push to `main`
- `Install App` uses the browser install prompt when available and shows fallback instructions when the current browser cannot install directly

## Notes

- User accounts are stored in `accounts.json`
- Browsers like Chrome can install the site as a web app after the manifest and service worker are deployed
- If you want Android or iPhone installs next, we can add a proper APK/TestFlight delivery flow on top of this
