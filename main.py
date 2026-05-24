import json
import os
import random
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager

DATA_FILE = "accounts.json"
PHRASES = [
    "the quick brown fox jumps over the lazy dog",
    "typing speed builds with practice every day",
    "practice makes perfect and confidence grows",
    "kivy makes it easy to create cross platform apps",
    "keep your eyes on the screen and your fingers moving",
    "learn new words and enjoy the challenge",
    "fast fingers win races in typing competitions",
    "accuracy beats speed when you want high scores",
    "use the backspace carefully and correct mistakes",
    "smile as you type and stay calm under pressure",
]


def load_accounts():
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}}


def save_accounts(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class LoginScreen(Screen):
    message = ObjectProperty(None)

    def do_login(self, username, password):
        app = TypingMasterApp.get_running_app()
        username = username.strip().lower()
        if not username or not password:
            self.message.text = "Enter both username and password."
            return

        user = app.accounts["users"].get(username)
        if user and user["password"] == password:
            app.current_user = username
            self.message.text = ""
            app.root.current = "menu"
        else:
            self.message.text = "Invalid login. Please check your credentials."

    def do_register(self, username, password):
        app = TypingMasterApp.get_running_app()
        username = username.strip().lower()
        if not username or not password:
            self.message.text = "Enter both username and password."
            return
        if username in app.accounts["users"]:
            self.message.text = "This username is already taken."
            return

        app.accounts["users"][username] = {
            "password": password,
            "best_score": 0,
            "history": [],
        }
        save_accounts(app.accounts)
        self.message.text = "Account created. You can now log in."


class MenuScreen(Screen):
    welcome_text = StringProperty("")
    best_score_text = StringProperty("")

    def on_pre_enter(self):
        app = TypingMasterApp.get_running_app()
        user = app.accounts["users"].get(app.current_user, {})
        self.welcome_text = f"Welcome, {app.current_user.title()}"
        best_score = user.get("best_score", 0)
        self.best_score_text = f"Best score: {best_score}"

    def logout(self):
        app = TypingMasterApp.get_running_app()
        app.current_user = None
        app.root.current = "login"


class GameScreen(Screen):
    phrase_text = StringProperty("")
    typed_text = StringProperty("")
    timer = NumericProperty(60)
    score = NumericProperty(0)
    mistakes = NumericProperty(0)
    game_active = BooleanProperty(False)
    status_text = StringProperty("Press Start to begin.")
    clock_event = None

    def start_game(self):
        self.timer = 60
        self.score = 0
        self.mistakes = 0
        self.status_text = "Type the phrase below and press Submit."
        self.next_phrase()
        self.game_active = True
        if self.clock_event:
            self.clock_event.cancel()
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)
        self.ids.typing_input.focus = True

    def update_timer(self, dt):
        if not self.game_active:
            return
        self.timer -= 1
        if self.timer <= 0:
            self.timer = 0
            self.finish_game()

    def next_phrase(self):
        self.phrase_text = random.choice(PHRASES)
        self.ids.typing_input.text = ""
        self.ids.typing_input.focus = True

    def submit_text(self):
        if not self.game_active:
            self.status_text = "Start the game first."
            return
        user_text = self.ids.typing_input.text.strip()
        if not user_text:
            self.status_text = "Type something before submitting."
            return

        target = self.phrase_text.strip()
        correct_chars = sum(1 for a, b in zip(user_text, target) if a == b)
        mismatches = sum(1 for a, b in zip(user_text, target) if a != b)
        errors = mismatches + abs(len(user_text) - len(target))
        self.score += max(correct_chars - errors, 0)
        self.mistakes += errors
        if user_text == target:
            self.status_text = "Perfect! Next phrase."
            self.score += 10
        else:
            self.status_text = f"Submitted with {errors} mistake(s). Try the next phrase."
        self.next_phrase()

    def finish_game(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        self.game_active = False
        app = TypingMasterApp.get_running_app()
        user = app.accounts["users"].get(app.current_user)
        if user is not None:
            user["history"].append({
                "score": self.score,
                "mistakes": self.mistakes,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            if self.score > user.get("best_score", 0):
                user["best_score"] = self.score
            save_accounts(app.accounts)
        self.manager.current = "menu"


class ScoreboardScreen(Screen):
    scores = ListProperty([])

    def on_pre_enter(self):
        app = TypingMasterApp.get_running_app()
        users = app.accounts["users"]
        ranking = sorted(
            [(username.title(), data.get("best_score", 0)) for username, data in users.items()],
            key=lambda item: item[1],
            reverse=True,
        )
        self.scores = ranking[:10]
        box = self.ids.ranking_box
        box.clear_widgets()
        if not self.scores:
            box.add_widget(
                self._make_label("No ranking data yet.")
            )
        else:
            for index, (name, score) in enumerate(self.scores, start=1):
                box.add_widget(
                    self._make_label(f"{index}. {name} — {score}")
                )

    def _make_label(self, text):
        from kivy.uix.label import Label
        return Label(text=text, size_hint_y=None, height=40)


class TypingMasterApp(App):
    current_user = None
    accounts = {}

    def build(self):
        self.accounts = load_accounts()
        if "users" not in self.accounts:
            self.accounts = {"users": {}}
        return Builder.load_file("typing_game.kv")


if __name__ == "__main__":
    TypingMasterApp().run()
