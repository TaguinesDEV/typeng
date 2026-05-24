import asyncio
import json
import os
import random
import webbrowser
from datetime import datetime

import pygame


pygame.init()
pygame.key.start_text_input()

WIDTH = 430
HEIGHT = 760
FPS = 60
DATA_FILE = "accounts.json"
INSTALL_APP_URL = "https://github.com/TaguinesDEV/typeng/releases"

PHRASES = [
    "the quick brown fox jumps over the lazy dog",
    "typing speed grows with calm and steady practice",
    "accuracy matters more than rushing through each line",
    "small wins every day build strong keyboard confidence",
    "focus on the phrase and let your hands find the rhythm",
    "good posture and relaxed hands make typing easier",
    "great scores come from practice patience and precision",
    "mistakes are normal when you are learning faster skills",
    "the timer rewards clear thinking and careful spelling",
    "confidence grows when you stay calm under pressure",
]

SCREEN_LOGIN = "login"
SCREEN_MENU = "menu"
SCREEN_GAME = "game"
SCREEN_RANKING = "ranking"

WHITE = (245, 247, 250)
INK = (15, 24, 38)
SKY = (110, 173, 255)
SKY_LIGHT = (210, 232, 255)
MINT = (61, 183, 126)
MINT_DARK = (38, 133, 89)
BLUE = (59, 130, 246)
BLUE_DARK = (37, 99, 196)
AMBER = (245, 158, 11)
RED = (220, 78, 78)
RED_DARK = (174, 54, 54)
SLATE = (64, 78, 96)
SLATE_DARK = (33, 43, 58)
PANEL = (255, 255, 255)
PANEL_LINE = (218, 228, 240)
TEXT_MUTED = (97, 111, 128)
INPUT_BG = (245, 248, 252)
INPUT_ACTIVE = (72, 141, 255)

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Master")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont("Verdana", 42, bold=True)
section_font = pygame.font.SysFont("Verdana", 24, bold=True)
body_font = pygame.font.SysFont("Verdana", 20)
small_font = pygame.font.SysFont("Verdana", 15)
button_font = pygame.font.SysFont("Verdana", 19, bold=True)
score_font = pygame.font.SysFont("Verdana", 54, bold=True)

screen = SCREEN_LOGIN
running = True
current_user = None

login_username = ""
login_password = ""
login_focus = "username"

game_phrase = ""
game_input = ""
game_score = 0
game_mistakes = 0
game_end_tick = 0

banner_text = ""
banner_color = MINT_DARK
banner_until = 0
web_login_panel_visible = False
web_game_input_visible = False


def load_accounts():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception:
        return {"users": {}}
    if "users" not in data or not isinstance(data["users"], dict):
        return {"users": {}}
    return data


def save_accounts(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


accounts = load_accounts()


def user_record(username):
    return accounts["users"].get(username, {"best_score": 0, "history": []})


def set_banner(message, color=MINT_DARK, duration_ms=2600):
    global banner_text, banner_color, banner_until

    banner_text = message
    banner_color = color
    banner_until = pygame.time.get_ticks() + duration_ms


def clear_banner_if_needed(now_tick):
    global banner_text

    if banner_text and now_tick >= banner_until:
        banner_text = ""


def open_url(url):
    try:
        browser_platform = __import__("platform")
        browser_window = getattr(browser_platform, "window", None)
        if browser_window is not None:
            browser_window.open(url, "_blank")
            return
    except Exception:
        pass

    try:
        webbrowser.open(url)
    except Exception:
        set_banner("Could not open the install link.", RED_DARK)


def browser_window():
    try:
        browser_platform = __import__("platform")
    except Exception:
        return None

    return getattr(browser_platform, "window", None)


def browser_value_to_python(value):
    if value is None:
        return None

    try:
        value = value.to_py()
    except Exception:
        pass

    if isinstance(value, (str, int, float, bool, dict, list, tuple)):
        return value

    return value


def install_app():
    browser = browser_window()
    if browser is not None:
        try:
            browser.requestInstallApp()
            return
        except Exception:
            pass

    open_url(INSTALL_APP_URL)


def show_web_login_panel():
    global web_login_panel_visible

    browser = browser_window()
    if browser is None:
        return

    try:
        browser.showLoginPanel(login_username, login_password, banner_text)
        web_login_panel_visible = True
    except Exception:
        web_login_panel_visible = False


def hide_web_login_panel():
    global web_login_panel_visible

    browser = browser_window()
    if browser is None:
        return

    try:
        browser.hideLoginPanel()
    except Exception:
        pass
    web_login_panel_visible = False


def sync_web_login_form_values():
    global login_username, login_password

    browser = browser_window()
    if browser is None:
        return

    try:
        values = browser_value_to_python(browser.getLoginFormValues())
    except Exception:
        return

    if isinstance(values, dict):
        username = values.get("username")
        password = values.get("password")
    else:
        username = getattr(values, "username", None)
        password = getattr(values, "password", None)

    if username is not None:
        login_username = str(username)[:22]
    if password is not None:
        login_password = str(password)[:30]


def sync_web_login_message():
    browser = browser_window()
    if browser is None:
        return

    try:
        browser.setLoginMessage(banner_text)
    except Exception:
        return


def show_web_game_input():
    global web_game_input_visible

    browser = browser_window()
    if browser is None:
        return

    try:
        browser.showGameInput(game_input)
        web_game_input_visible = True
    except Exception:
        web_game_input_visible = False


def hide_web_game_input():
    global web_game_input_visible

    browser = browser_window()
    if browser is None:
        return

    try:
        browser.hideGameInput()
    except Exception:
        pass
    web_game_input_visible = False


def sync_web_game_input_value():
    global game_input

    browser = browser_window()
    if browser is None:
        return

    try:
        value = browser_value_to_python(browser.getGameInputValue())
    except Exception:
        return

    if value is not None:
        game_input = str(value)[:120]


def set_web_game_input_value(value):
    browser = browser_window()
    if browser is None:
        return

    try:
        browser.setGameInputValue(value)
    except Exception:
        return


def sync_web_overlay_visibility():
    if browser_window() is None:
        return

    if screen == SCREEN_LOGIN:
        if not web_login_panel_visible:
            show_web_login_panel()
        if web_game_input_visible:
            hide_web_game_input()
    elif screen == SCREEN_GAME:
        if web_login_panel_visible:
            hide_web_login_panel()
        if not web_game_input_visible:
            show_web_game_input()
    else:
        if web_login_panel_visible:
            hide_web_login_panel()
        if web_game_input_visible:
            hide_web_game_input()


def pop_web_overlay_action():
    browser = browser_window()
    if browser is None:
        return None

    try:
        action = browser_value_to_python(browser.popOverlayAction())
    except Exception:
        return None

    if action is None:
        return None

    return str(action).strip().lower()


def rounded_rect(rect, color, radius=18, border_color=None, border_width=0):
    pygame.draw.rect(window, color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(window, border_color, rect, width=border_width, border_radius=radius)


def draw_shadow(rect, alpha=50, radius=20, offset=(0, 6)):
    shadow = pygame.Surface((rect.width + 24, rect.height + 24), pygame.SRCALPHA)
    pygame.draw.rect(
        shadow,
        (14, 22, 35, alpha),
        (12 + offset[0], 12 + offset[1], rect.width, rect.height),
        border_radius=radius,
    )
    window.blit(shadow, (rect.x - 12, rect.y - 12))


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    window.blit(surface, (x, y))
    return surface


def draw_center_text(text, font, color, y):
    surface = font.render(text, True, color)
    window.blit(surface, (WIDTH // 2 - surface.get_width() // 2, y))
    return surface


def wrap_lines(text, font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_multiline(text, font, color, rect, line_gap=8):
    y = rect.y
    for line in wrap_lines(text, font, rect.width):
        surface = font.render(line, True, color)
        window.blit(surface, (rect.x, y))
        y += surface.get_height() + line_gap


def draw_button(rect, text, fill, hover_fill, text_color=WHITE):
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)
    draw_shadow(rect, alpha=42, radius=18, offset=(0, 4))
    rounded_rect(rect, hover_fill if hovered else fill, radius=18)
    label = button_font.render(text, True, text_color)
    window.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))
    return hovered


def draw_input(rect, label, value, active=False, secret=False, placeholder="", show_text=True):
    label_surface = small_font.render(label, True, TEXT_MUTED)
    window.blit(label_surface, (rect.x, rect.y - 22))

    draw_shadow(rect, alpha=26, radius=16, offset=(0, 3))
    rounded_rect(
        rect,
        INPUT_BG,
        radius=16,
        border_color=INPUT_ACTIVE if active else PANEL_LINE,
        border_width=2,
    )

    if not show_text:
        return

    display_value = value
    if secret:
        display_value = "*" * len(value)

    if not display_value:
        surface = body_font.render(placeholder, True, (165, 175, 189))
    else:
        caret = "|" if active and pygame.time.get_ticks() % 900 < 450 else ""
        surface = body_font.render(f"{display_value}{caret}", True, INK)

    clip = pygame.Rect(rect.x + 16, rect.y + 10, rect.width - 32, rect.height - 20)
    window.set_clip(clip)
    text_x = rect.x + 16
    if surface.get_width() > clip.width:
        text_x = clip.right - surface.get_width()
    window.blit(surface, (text_x, rect.y + rect.height // 2 - surface.get_height() // 2))
    window.set_clip(None)


def pointer_position(event):
    if hasattr(pygame, "FINGERDOWN") and event.type == pygame.FINGERDOWN:
        return int(event.x * WIDTH), int(event.y * HEIGHT)
    return pygame.mouse.get_pos()


def login_buttons():
    return {
        "username": pygame.Rect(55, 238, 320, 56),
        "password": pygame.Rect(55, 334, 320, 56),
        "login": pygame.Rect(55, 432, 152, 52),
        "register": pygame.Rect(223, 432, 152, 52),
        "ranking": pygame.Rect(55, 504, 152, 48),
        "install": pygame.Rect(223, 504, 152, 48),
    }


def menu_buttons():
    return {
        "start": pygame.Rect(75, 312, 280, 58),
        "ranking": pygame.Rect(75, 392, 280, 58),
        "logout": pygame.Rect(75, 472, 280, 58),
        "install": pygame.Rect(75, 552, 280, 50),
    }


def game_buttons():
    return {
        "submit": pygame.Rect(45, 610, 160, 52),
        "skip": pygame.Rect(225, 610, 160, 52),
        "menu": pygame.Rect(45, 676, 340, 44),
        "input": pygame.Rect(45, 500, 340, 84),
    }


def ranking_buttons():
    return {
        "back": pygame.Rect(75, 660, 280, 52),
    }


def choose_phrase():
    global game_phrase, game_input

    pool = [phrase for phrase in PHRASES if phrase != game_phrase]
    game_phrase = random.choice(pool or PHRASES)
    game_input = ""
    set_web_game_input_value(game_input)


def score_submission():
    global game_score, game_mistakes

    sync_web_game_input_value()

    typed = game_input.strip()
    if not typed:
        set_banner("Type the phrase before submitting.", RED_DARK)
        return

    target = game_phrase.strip()
    correct_chars = sum(1 for left, right in zip(typed, target) if left == right)
    mismatches = sum(1 for left, right in zip(typed, target) if left != right)
    errors = mismatches + abs(len(typed) - len(target))
    earned = max(correct_chars - errors, 0)

    game_score += earned
    game_mistakes += errors

    if typed == target:
        game_score += 10
        set_banner("Perfect phrase. Bonus +10.", MINT_DARK)
    else:
        set_banner(f"Submitted with {errors} mistake(s).", AMBER)

    choose_phrase()


def start_game():
    global screen, game_score, game_mistakes, game_end_tick

    game_score = 0
    game_mistakes = 0
    game_end_tick = pygame.time.get_ticks() + 60000
    choose_phrase()
    screen = SCREEN_GAME
    set_banner("Game started. Type and submit fast.", BLUE_DARK)


def finish_game():
    global screen

    record = user_record(current_user)
    record.setdefault("history", [])
    record["history"].append(
        {
            "score": game_score,
            "mistakes": game_mistakes,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    record["best_score"] = max(record.get("best_score", 0), game_score)
    accounts["users"][current_user] = record
    save_accounts(accounts)
    screen = SCREEN_MENU
    set_banner(f"Round finished. Score: {game_score}.", BLUE_DARK, 3200)


def login_user():
    global screen, current_user

    username = login_username.strip().lower()
    password = login_password

    if not username or not password:
        set_banner("Enter both username and password.", RED_DARK)
        return

    record = accounts["users"].get(username)
    if not record or record.get("password") != password:
        set_banner("Invalid login credentials.", RED_DARK)
        return

    current_user = username
    screen = SCREEN_MENU
    set_banner(f"Welcome back, {username.title()}.", MINT_DARK)


def register_user():
    global screen, current_user

    username = login_username.strip().lower()
    password = login_password

    if not username or not password:
        set_banner("Enter both username and password.", RED_DARK)
        return

    if username in accounts["users"]:
        set_banner("That username is already taken.", RED_DARK)
        return

    accounts["users"][username] = {
        "password": password,
        "best_score": 0,
        "history": [],
    }
    save_accounts(accounts)
    current_user = username
    screen = SCREEN_MENU
    set_banner("Account created successfully.", MINT_DARK)


def logout_user():
    global current_user, screen, login_password

    current_user = None
    login_password = ""
    screen = SCREEN_LOGIN
    set_banner("Logged out.", BLUE_DARK)


def ranking_rows():
    ranking = sorted(
        (
            (username.title(), details.get("best_score", 0), len(details.get("history", [])))
            for username, details in accounts["users"].items()
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    return ranking[:10]


def current_time_left():
    remaining_ms = max(0, game_end_tick - pygame.time.get_ticks())
    return (remaining_ms + 999) // 1000


def draw_background():
    window.fill(SKY_LIGHT)
    for stripe_index in range(0, HEIGHT, 18):
        alpha = 12 if stripe_index % 36 == 0 else 7
        stripe = pygame.Surface((WIDTH, 18), pygame.SRCALPHA)
        stripe.fill((255, 255, 255, alpha))
        window.blit(stripe, (0, stripe_index))

    sun = pygame.Surface((190, 190), pygame.SRCALPHA)
    pygame.draw.circle(sun, (255, 255, 255, 80), (95, 95), 95)
    window.blit(sun, (-30, -15))


def draw_banner():
    if not banner_text:
        return

    rect = pygame.Rect(28, 26, WIDTH - 56, 42)
    rounded_rect(rect, banner_color, radius=16)
    surface = small_font.render(banner_text, True, WHITE)
    window.blit(surface, (rect.centerx - surface.get_width() // 2, rect.centery - surface.get_height() // 2))


def draw_login():
    draw_background()

    if browser_window() is not None:
        return

    buttons = login_buttons()
    show_canvas_text = True

    draw_center_text("Typing Master", title_font, INK, 92)
    draw_center_text("Log in or register to save your best typing scores.", small_font, TEXT_MUTED, 144)

    card = pygame.Rect(28, 186, WIDTH - 56, 404)
    draw_shadow(card, alpha=55, radius=28, offset=(0, 8))
    rounded_rect(card, PANEL, radius=28, border_color=PANEL_LINE, border_width=1)

    draw_input(
        buttons["username"],
        "USERNAME",
        login_username,
        active=login_focus == "username",
        placeholder="Enter username",
        show_text=show_canvas_text,
    )
    draw_input(
        buttons["password"],
        "PASSWORD",
        login_password,
        active=login_focus == "password",
        secret=True,
        placeholder="Enter password",
        show_text=show_canvas_text,
    )

    draw_button(buttons["login"], "LOG IN", BLUE, BLUE_DARK)
    draw_button(buttons["register"], "REGISTER", MINT, MINT_DARK)
    draw_button(buttons["ranking"], "RANKING", SLATE, SLATE_DARK)
    draw_button(buttons["install"], "INSTALL APP", AMBER, (217, 119, 6))

    draw_multiline(
        "Tip: tap an input field on mobile, then use the on-screen keyboard to type.",
        small_font,
        TEXT_MUTED,
        pygame.Rect(52, 566, 326, 60),
        line_gap=5,
    )
    draw_banner()


def draw_menu():
    buttons = menu_buttons()
    draw_background()

    draw_center_text("Welcome", title_font, INK, 110)
    draw_center_text(current_user.title(), section_font, BLUE_DARK, 164)

    record = user_record(current_user)
    best_score = record.get("best_score", 0)
    history_count = len(record.get("history", []))

    stats = pygame.Rect(40, 220, WIDTH - 80, 122)
    draw_shadow(stats, alpha=45, radius=26, offset=(0, 6))
    rounded_rect(stats, PANEL, radius=26, border_color=PANEL_LINE, border_width=1)

    draw_text("Best Score", small_font, TEXT_MUTED, 68, 250)
    draw_text(str(best_score), score_font, INK, 64, 270)
    draw_text("Games Played", small_font, TEXT_MUTED, 245, 250)
    draw_text(str(history_count), section_font, INK, 245, 274)

    draw_button(buttons["start"], "START TYPING GAME", BLUE, BLUE_DARK)
    draw_button(buttons["ranking"], "VIEW RANKING", MINT, MINT_DARK)
    draw_button(buttons["logout"], "LOG OUT", RED, RED_DARK)
    draw_button(buttons["install"], "INSTALL APP", AMBER, (217, 119, 6))
    draw_banner()


def draw_game():
    buttons = game_buttons()
    draw_background()
    show_canvas_text = browser_window() is None

    header = pygame.Rect(28, 78, WIDTH - 56, 108)
    draw_shadow(header, alpha=42, radius=24, offset=(0, 5))
    rounded_rect(header, PANEL, radius=24, border_color=PANEL_LINE, border_width=1)

    draw_text("Time", small_font, TEXT_MUTED, 52, 104)
    draw_text(str(current_time_left()), section_font, INK, 50, 126)
    draw_text("Score", small_font, TEXT_MUTED, 182, 104)
    draw_text(str(game_score), section_font, INK, 176, 126)
    draw_text("Mistakes", small_font, TEXT_MUTED, 294, 104)
    draw_text(str(game_mistakes), section_font, INK, 290, 126)

    phrase_panel = pygame.Rect(28, 214, WIDTH - 56, 244)
    draw_shadow(phrase_panel, alpha=42, radius=24, offset=(0, 5))
    rounded_rect(phrase_panel, PANEL, radius=24, border_color=PANEL_LINE, border_width=1)

    draw_text("TYPE THIS PHRASE", small_font, TEXT_MUTED, 48, 238)
    draw_multiline(game_phrase, section_font, INK, pygame.Rect(48, 278, WIDTH - 96, 120), line_gap=10)

    draw_input(
        buttons["input"],
        "YOUR INPUT",
        game_input,
        active=True,
        placeholder="Start typing here",
        show_text=show_canvas_text,
    )

    draw_button(buttons["submit"], "SUBMIT", BLUE, BLUE_DARK)
    draw_button(buttons["skip"], "SKIP", SLATE, SLATE_DARK)
    draw_button(buttons["menu"], "END ROUND AND RETURN", RED, RED_DARK)
    draw_banner()


def draw_ranking():
    buttons = ranking_buttons()
    draw_background()

    draw_center_text("Top Typing Masters", title_font, INK, 82)

    panel = pygame.Rect(28, 156, WIDTH - 56, 474)
    draw_shadow(panel, alpha=48, radius=26, offset=(0, 6))
    rounded_rect(panel, PANEL, radius=26, border_color=PANEL_LINE, border_width=1)

    rows = ranking_rows()
    if not rows:
        draw_center_text("No scores yet. Play a round to create the leaderboard.", body_font, TEXT_MUTED, 360)
    else:
        y = 186
        for index, (username, best_score, games_played) in enumerate(rows, start=1):
            row = pygame.Rect(48, y, WIDTH - 96, 52)
            rounded_rect(row, INPUT_BG, radius=16)
            draw_text(f"{index}. {username}", body_font, INK, row.x + 16, row.y + 14)
            draw_text(f"{best_score} pts", body_font, BLUE_DARK, row.x + 188, row.y + 14)
            draw_text(f"{games_played} game(s)", small_font, TEXT_MUTED, row.x + 286, row.y + 17)
            y += 58

    draw_button(buttons["back"], "BACK", BLUE, BLUE_DARK)
    draw_banner()


def handle_login_key(event):
    global login_focus, login_username, login_password, running

    if event.key == pygame.K_TAB:
        login_focus = "password" if login_focus == "username" else "username"
        return

    if event.key == pygame.K_BACKSPACE:
        if login_focus == "username":
            login_username = login_username[:-1]
        else:
            login_password = login_password[:-1]
        return

    if event.key == pygame.K_RETURN:
        login_user()
        return

    if event.key == pygame.K_F2:
        register_user()
        return

    if event.key == pygame.K_ESCAPE:
        running = False


def handle_login_text(event):
    global login_username, login_password

    target = "username" if login_focus == "username" else "password"
    if target == "username":
        if len(login_username) < 22:
            login_username += event.text
    else:
        if len(login_password) < 30:
            login_password += event.text


def handle_login_pointer(position):
    global login_focus, screen

    buttons = login_buttons()
    if buttons["username"].collidepoint(position):
        login_focus = "username"
    elif buttons["password"].collidepoint(position):
        login_focus = "password"
    elif buttons["login"].collidepoint(position):
        sync_web_login_form_values()
        login_user()
    elif buttons["register"].collidepoint(position):
        sync_web_login_form_values()
        register_user()
    elif buttons["ranking"].collidepoint(position):
        screen = SCREEN_RANKING
    elif buttons["install"].collidepoint(position):
        install_app()


def handle_menu_pointer(position):
    global screen

    buttons = menu_buttons()
    if buttons["start"].collidepoint(position):
        start_game()
    elif buttons["ranking"].collidepoint(position):
        screen = SCREEN_RANKING
    elif buttons["logout"].collidepoint(position):
        logout_user()
    elif buttons["install"].collidepoint(position):
        install_app()


def handle_menu_key(event):
    global running, screen

    if event.key == pygame.K_ESCAPE:
        running = False
    elif event.key == pygame.K_RETURN:
        start_game()
    elif event.key == pygame.K_r:
        screen = SCREEN_RANKING
    elif event.key == pygame.K_i:
        install_app()


def handle_game_text(event):
    global game_input

    if len(game_input) < 120:
        game_input += event.text


def handle_game_key(event):
    global game_input

    if event.key == pygame.K_BACKSPACE:
        game_input = game_input[:-1]
    elif event.key == pygame.K_RETURN:
        score_submission()
    elif event.key == pygame.K_ESCAPE:
        finish_game()


def handle_game_pointer(position):
    buttons = game_buttons()
    if buttons["submit"].collidepoint(position):
        sync_web_game_input_value()
        score_submission()
    elif buttons["skip"].collidepoint(position):
        choose_phrase()
        set_banner("Skipped to the next phrase.", BLUE_DARK)
    elif buttons["menu"].collidepoint(position):
        finish_game()


def handle_ranking_pointer(position):
    global screen

    if ranking_buttons()["back"].collidepoint(position):
        screen = SCREEN_MENU if current_user else SCREEN_LOGIN


def handle_ranking_key(event):
    global screen

    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
        screen = SCREEN_MENU if current_user else SCREEN_LOGIN


def update_screen_state():
    if screen == SCREEN_GAME and current_time_left() == 0:
        finish_game()


async def main():
    global running

    while running:
        now_tick = pygame.time.get_ticks()
        clear_banner_if_needed(now_tick)
        update_screen_state()
        sync_web_overlay_visibility()

        if screen == SCREEN_LOGIN:
            sync_web_login_form_values()
            sync_web_login_message()
        elif screen == SCREEN_GAME:
            sync_web_game_input_value()

        web_action = pop_web_overlay_action()
        if web_action == "login" and screen == SCREEN_LOGIN:
            sync_web_login_form_values()
            login_user()
        elif web_action == "register" and screen == SCREEN_LOGIN:
            sync_web_login_form_values()
            register_user()
        elif web_action == "ranking" and screen == SCREEN_LOGIN:
            screen = SCREEN_RANKING
        elif web_action == "submit" and screen == SCREEN_GAME:
            sync_web_game_input_value()
            score_submission()

        if screen in (SCREEN_LOGIN, SCREEN_GAME):
            pygame.key.start_text_input()
        else:
            pygame.key.stop_text_input()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.TEXTINPUT:
                if screen == SCREEN_LOGIN:
                    handle_login_text(event)
                elif screen == SCREEN_GAME:
                    handle_game_text(event)

            if event.type == pygame.KEYDOWN:
                if screen == SCREEN_LOGIN:
                    handle_login_key(event)
                elif screen == SCREEN_MENU:
                    handle_menu_key(event)
                elif screen == SCREEN_GAME:
                    handle_game_key(event)
                elif screen == SCREEN_RANKING:
                    handle_ranking_key(event)

            if event.type == pygame.MOUSEBUTTONDOWN or (
                hasattr(pygame, "FINGERDOWN") and event.type == pygame.FINGERDOWN
            ):
                position = pointer_position(event)
                if screen == SCREEN_LOGIN:
                    handle_login_pointer(position)
                elif screen == SCREEN_MENU:
                    handle_menu_pointer(position)
                elif screen == SCREEN_GAME:
                    handle_game_pointer(position)
                elif screen == SCREEN_RANKING:
                    handle_ranking_pointer(position)

        if screen == SCREEN_LOGIN:
            draw_login()
        elif screen == SCREEN_MENU:
            draw_menu()
        elif screen == SCREEN_GAME:
            draw_game()
        elif screen == SCREEN_RANKING:
            draw_ranking()

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
