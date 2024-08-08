import tkinter as tk
from tkinter import ttk
import json
import os


class RulesManager:
    def __init__(self, master):
        self.master = master
        self.show_rules_on_startup = tk.BooleanVar(value=True)
        self.zoom_factor = tk.DoubleVar(value=1.0)
        self.is_fullscreen = tk.BooleanVar(value=False)
        self.is_muted = tk.BooleanVar(value=False)  # Add this line
        self.preferences_file = os.path.join(
            os.path.expanduser("~"), ".patience_preferences.json"
        )
        self.load_preferences()

    def show_rules(self):
        if not self.show_rules_on_startup.get():
            return

        rules_window = tk.Toplevel(self.master)
        rules_window.title("Patience Rules")
        rules_window.geometry("400x450")

        # Make the window modal
        rules_window.grab_set()
        rules_window.transient(self.master)

        # Center the rules window on the game window
        rules_window.withdraw()  # Temporarily hide the window
        self.master.update_idletasks()  # Update "requested size" from geometry manager

        # Calculate position x, y
        x = (
            self.master.winfo_x()
            + (self.master.winfo_width() // 2)
            - (rules_window.winfo_reqwidth() // 2)
        )
        y = (
            self.master.winfo_y()
            + (self.master.winfo_height() // 2)
            - (rules_window.winfo_reqheight() // 2)
        )

        # Set the window's position
        rules_window.geometry(f"+{x}+{y}")
        rules_window.deiconify()  # Show the window

        rules_text = """Welcome to Patience!

Rules of the game:
1. The game is played with a standard 52-card deck.
2. Cards are dealt into 13 columns (houses).
3. The goal is to build up four foundation piles, one for each suit, from Ace to King.
4. In the columns, cards must be placed in descending order and alternating colors.
5. You can move single cards or stacks of correctly sequenced cards between columns.
6. The game is won when all cards are moved to the foundation piles.
7. Redeal the cards, or undo the moves (upto 5) if you get stuck.

Good luck and enjoy the game!"""

        text_widget = tk.Text(rules_window, wrap=tk.WORD, width=50, height=20)
        text_widget.insert(tk.END, rules_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(padx=10, pady=10)

        show_again_var = tk.BooleanVar(value=self.show_rules_on_startup.get())
        show_again_check = ttk.Checkbutton(
            rules_window,
            text="Show rules on startup",
            variable=show_again_var,
            command=lambda: self.show_rules_on_startup.set(show_again_var.get()),
        )
        show_again_check.pack(pady=5)

        def on_close():
            self.save_preferences()
            rules_window.destroy()

        ok_button = ttk.Button(rules_window, text="OK", command=on_close)
        ok_button.pack(pady=10)

        # Bind the window close event
        rules_window.protocol("WM_DELETE_WINDOW", on_close)

        # Wait for the window to be closed
        self.master.wait_window(rules_window)

    def load_preferences(self):
        try:
            with open(self.preferences_file, "r") as f:
                prefs = json.load(f)
                self.show_rules_on_startup.set(prefs.get("show_rules_on_startup", True))
                self.zoom_factor.set(prefs.get("zoom_factor", 1.0))
                self.is_fullscreen.set(prefs.get("is_fullscreen", False))
                self.is_muted.set(prefs.get("is_muted", False))
        except FileNotFoundError:
            pass  # Use default values if file doesn't exist

    def save_preferences(self):
        prefs = {
            "show_rules_on_startup": self.show_rules_on_startup.get(),
            "zoom_factor": self.zoom_factor.get(),
            "is_fullscreen": self.is_fullscreen.get(),
            "is_muted": self.is_muted.get(),
        }
        with open(self.preferences_file, "w") as f:
            json.dump(prefs, f)

    def get_zoom_factor(self):
        return self.zoom_factor.get()

    def set_zoom_factor(self, value):
        self.zoom_factor.set(value)
        self.save_preferences()

    def get_is_fullscreen(self):
        return self.is_fullscreen.get()

    def set_is_fullscreen(self, value):
        self.is_fullscreen.set(value)
        self.save_preferences()

    def get_is_muted(self):
        return self.is_muted.get()

    def set_is_muted(self, value):
        self.is_muted.set(value)
        self.save_preferences()
