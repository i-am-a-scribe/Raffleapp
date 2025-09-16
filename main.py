# =============================
# 🎯 Daily Raffle Picker (Kivy App)
# =============================

import random
import json
import os
from datetime import datetime, timedelta

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

HISTORY_FILE = "raffle_history.json"
historical_frequencies = {i: random.randint(1, 100) for i in range(1, 61)}
common_numbers = {3, 7, 11, 13, 21, 23, 27, 30, 33}


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)


def generate_numbers(fixed_number):
    history = load_history()

    if "last_draw" in history:
        last_time = datetime.fromisoformat(history["last_draw"]["time"])
        if datetime.now() - last_time < timedelta(hours=24):
            return history["last_draw"]["numbers"]

    pool = list(range(1, 61))
    if fixed_number in pool:
        pool.remove(fixed_number)

    weights = [
        historical_frequencies[n] * (0.5 if n in common_numbers else 1.0)
        for n in pool
    ]

    # oversample then dedupe to simulate weighted unique picks
    selected = random.choices(pool, weights=weights, k=20)
    selected = list(dict.fromkeys(selected))[:5]

    result = sorted([fixed_number] + selected)

    history.setdefault("draws", []).append({
        "time": datetime.now().isoformat(),
        "numbers": result
    })
    history["last_draw"] = {"time": datetime.now().isoformat(), "numbers": result}
    save_history(history)

    return result


class RaffleApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)

        self.label = Label(text="Enter your fixed number (1–60):")
        self.add_widget(self.label)

        self.input = TextInput(multiline=False, input_filter="int")
        self.add_widget(self.input)

        self.button = Button(text="Generate Numbers 🎲", size_hint=(1, 0.3))
        self.button.bind(on_press=self.on_generate)
        self.add_widget(self.button)

        self.result_label = Label(text="")
        self.add_widget(self.result_label)

    def on_generate(self, instance):
        try:
            fixed = int(self.input.text)
            if 1 <= fixed <= 60:
                numbers = generate_numbers(fixed)
                self.result_label.text = f"Your numbers: {numbers}"
            else:
                self.result_label.text = "❌ Please enter a number between 1–60."
        except Exception:
            self.result_label.text = "❌ Invalid input."


class DailyRaffleApp(App):
    def build(self):
        return RaffleApp()


if __name__ == "__main__":
    DailyRaffleApp().run()
