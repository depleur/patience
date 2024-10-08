import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
from rules import RulesManager
import os
import sys
import pygame
from updater import Updater
from tkinter import messagebox
from win_celebration import create_win_celebration


# from solver import Solver, GameState
import signal
import json

CURRENT_VERSION = "v1.0.26-alpha"


class Card:
    def __init__(self, suit, rank, image):
        self.suit = suit
        self.rank = rank
        self.color = "red" if suit in ["hearts", "diamonds"] else "black"
        self.image = image
        self.cards_above = []  # Cards stacked on top of this card


class PatienceGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Patience Card Game")

        self.updater = Updater(CURRENT_VERSION, self.master)
        self.updater.start_update_check_thread()

        pygame.mixer.init()
        sound_path = self.resource_path("sounds/card_deal.mp3")
        self.deal_sound = pygame.mixer.Sound(sound_path)

        self.rules_manager = RulesManager(self.master)

        self.card_width = 80
        self.card_height = 120

        self.center_window(1200, 800)
        self.create_menu()
        self.create_game_area()
        self.create_status_bar()
        self.move_history = []
        self.move_count = 0

        self.high_score = self.rules_manager.get_high_score()
        self.create_high_score_label()

        self.card_images = self.load_card_images()
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_items = {}
        self.drag_data = {"x": 0, "y": 0, "item": None}

        self.initial_deck = None
        self.interrupt_flag = False

        self.status_var.set("Welcome to Patience! Click 'Deal Cards' to begin.")

        self.highlight_rectangles = []
        self.strobe_after_id = None

        self.zoom_factor = self.rules_manager.get_zoom_factor()
        self.create_control_buttons()

        self.master.after(100, self.rules_manager.show_rules)

        self.master.bind("<Escape>", self.handle_escape)
        self.master.bind("<F11>", lambda event: self.toggle_fullscreen())

        self.rules_manager = RulesManager(self.master)
        self.zoom_factor = self.rules_manager.get_zoom_factor()
        self.apply_zoom()

        self.win_celebration = create_win_celebration(self)

        # Apply fullscreen preference
        if self.rules_manager.get_is_fullscreen():
            self.master.attributes("-fullscreen", True)

        if not self.rules_manager.get_is_fullscreen():
            self.master.overrideredirect(False)

        self.is_muted = self.rules_manager.get_is_muted()
        self.update_mute_button_text()

        self.apply_mute_state()

    @staticmethod
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def load_card_images(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = list(range(1, 14))
        card_images = {}

        for suit in suits:
            for rank in ranks:
                image_path = self.resource_path(f"images/{rank}_of_{suit}.png")
                image = Image.open(image_path)
                image = image.resize((self.card_width, self.card_height), Image.LANCZOS)
                card_images[(suit, rank)] = ImageTk.PhotoImage(image)

        return card_images

    def load_high_score(self):
        try:
            with open("patience_preferences.json", "r") as f:
                preferences = json.load(f)
                return preferences.get("high_score", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        try:
            with open("patience_preferences.json", "r") as f:
                preferences = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            preferences = {}

        preferences["high_score"] = max(self.high_score, self.move_count)

        with open("patience_preferences.json", "w") as f:
            json.dump(preferences, f)

    def create_high_score_label(self):
        self.high_score_label = ttk.Label(
            self.master, text=f"High Score: {self.high_score}"
        )
        self.high_score_label.pack(side=tk.TOP, pady=5)

    def update_high_score(self):
        if self.move_count < self.high_score or self.high_score == 0:
            self.high_score = self.move_count
            self.rules_manager.set_high_score(self.high_score)
            self.high_score_label.config(text=f"High Score: {self.high_score}")

    def quit_game(self):
        os.kill(os.getpid(), signal.SIGTERM)

    def update_move_count(self):
        self.move_count += 1
        self.move_counter_label.config(text=f"Moves: {self.move_count}")

    def create_clear_button(self):
        self.clear_button = ttk.Button(
            self.master, text="Clear Board", command=self.clear_board
        )
        self.clear_button.pack(side=tk.BOTTOM, pady=5)

    def create_update_check_button(self):
        self.update_check_button = ttk.Button(
            self.master, text="Check for Updates", command=self.manual_update_check
        )
        self.update_check_button.pack(side=tk.BOTTOM, pady=5)

    def manual_update_check(self):
        if not self.updater.check_for_updates():
            messagebox.showinfo("No Updates", "You are running the latest version.")

    def create_zoom_buttons(self):
        zoom_frame = ttk.Frame(self.master)
        zoom_frame.pack(side=tk.BOTTOM, pady=5)

        self.zoom_in_button = ttk.Button(
            zoom_frame, text="Zoom In", command=self.zoom_in
        )
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

        self.zoom_out_button = ttk.Button(
            zoom_frame, text="Zoom Out", command=self.zoom_out
        )
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

    def apply_zoom(self):
        self.card_width = int(80 * self.zoom_factor)
        self.card_height = int(120 * self.zoom_factor)
        self.card_images = self.load_card_images()
        self.create_house_areas()
        self.display_cards()

        # Ensure window decorations are shown when not in fullscreen
        if not self.master.attributes("-fullscreen"):
            self.master.overrideredirect(False)

    def zoom_in(self):
        if self.zoom_factor < 2.0:  # Limit max zoom
            self.zoom_factor *= 1.2
            self.rules_manager.set_zoom_factor(self.zoom_factor)
            self.resize_cards()
            self.display_cards()

    def zoom_out(self):
        if self.zoom_factor > 0.5:  # Limit min zoom
            self.zoom_factor /= 1.2
            self.rules_manager.set_zoom_factor(self.zoom_factor)
            self.resize_cards()
            self.display_cards()

    def resize_cards(self):
        self.card_width = int(80 * self.zoom_factor)
        self.card_height = int(120 * self.zoom_factor)
        self.card_images = self.load_card_images()
        self.create_house_areas()  # Add this line

    def center_window(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        game_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Restart", command=self.restart_game)
        game_menu.add_command(label="Show Rules", command=self.rules_manager.show_rules)
        game_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen)
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.on_closing)

    def on_closing(self):
        pygame.mixer.stop()
        self.rules_manager.save_preferences()
        self.master.destroy()

    def create_game_area(self):
        self.game_frame = ttk.Frame(self.master, padding="10")
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        self.game_canvas = tk.Canvas(self.game_frame, bg="#076324")
        self.game_canvas.pack(fill=tk.BOTH, expand=True)

        self.create_house_areas()

    def create_house_areas(self):
        self.game_canvas.delete("house_area")
        for i in range(10):  # Change back to 10 houses
            x = 60 + i * (self.card_width + 20)
            y = 20
            self.game_canvas.create_rectangle(
                x,
                y,
                x + self.card_width,
                y + self.card_height,
                outline="#FFD700",
                width=2,
                tags="house_area",
            )

    def create_status_bar(self):
        status_frame = ttk.Frame(self.master)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar()
        self.status_var.set("Welcome to Patience!")
        status_bar = ttk.Label(
            status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.move_counter_label = ttk.Label(status_frame, text="Moves: 0", anchor=tk.E)
        self.move_counter_label.pack(side=tk.RIGHT, padx=5)

    def new_game(self):
        self.clear_board()
        self.initial_deck = None
        self.status_var.set("New game started. Click 'Deal Cards' to begin.")
        self.redeal_button.config(state=tk.DISABLED)  # Disable redeal button
        self.move_history.clear()
        self.undo_button.config(state=tk.DISABLED)
        self.move_count = 0
        self.move_counter_label.config(text="Moves: 0")

    def create_control_buttons(self):
        control_frame = ttk.Frame(self.master)
        control_frame.pack(side=tk.BOTTOM, pady=10)

        self.deal_button = ttk.Button(
            control_frame, text="Deal Cards", command=self.animated_deal
        )
        self.deal_button.pack(side=tk.LEFT, padx=5)

        self.redeal_button = ttk.Button(
            control_frame, text="Redeal", command=self.redeal_cards
        )
        self.redeal_button.pack(side=tk.LEFT, padx=5)
        self.redeal_button.config(state=tk.DISABLED)  # Initially disabled

        # self.hint_button = ttk.Button(
        #     control_frame, text="Hint", command=self.show_hint
        # )
        # self.hint_button.pack(side=tk.LEFT, padx=5)

        self.undo_button = ttk.Button(
            control_frame, text="Undo", command=self.undo_move, state=tk.DISABLED
        )
        self.undo_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(
            control_frame, text="Clear Board", command=self.clear_board
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(side=tk.LEFT, padx=5)

        self.zoom_in_button = ttk.Button(
            zoom_frame, text="Zoom In", command=self.zoom_in
        )
        self.zoom_in_button.pack(side=tk.LEFT, padx=2)

        self.zoom_out_button = ttk.Button(
            zoom_frame, text="Zoom Out", command=self.zoom_out
        )
        self.zoom_out_button.pack(side=tk.LEFT, padx=2)

        self.mute_button = ttk.Button(
            control_frame, text="Mute", command=self.toggle_mute
        )
        self.mute_button.pack(side=tk.LEFT, padx=5)

        self.fullscreen_button = ttk.Button(
            control_frame, text="Fullscreen", command=self.toggle_fullscreen
        )
        self.fullscreen_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = ttk.Button(
            control_frame, text="Quit", command=self.quit_game
        )
        self.quit_button.pack(side=tk.LEFT, padx=5)

        self.create_update_check_button()

    def restart_game(self):
        self.new_game()
        self.initial_deck = None
        self.status_var.set("Game restarted. Click 'Deal Cards' to begin.")
        # self.hint_button.config(state=tk.DISABLED)
        self.redeal_button.config(state=tk.DISABLED)  # Disable redeal button

    def create_deck(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = list(range(1, 14))
        deck = [
            Card(suit, rank, self.card_images[(suit, rank)])
            for suit in suits
            for rank in ranks
        ]
        random.shuffle(deck)
        return deck

    def create_deal_button(self):
        self.deal_button = tk.Button(
            self.master, text="Deal Cards", command=self.animated_deal
        )
        self.deal_button.pack(side=tk.BOTTOM, pady=10)
        self.deal_button.config(state=tk.NORMAL)

    def clear_board(self):
        self.interrupt_flag = True
        self.master.after_cancel(
            self.master.after_id
        )  # Cancel any ongoing after() calls

        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_items.clear()
        self.game_canvas.delete("card")
        self.move_history.clear()

        self.move_count = 0
        self.move_counter_label.config(text="Moves: 0")

        self.status_var.set("Board cleared. Click 'Deal Cards' to start a new game.")
        self.undo_button.config(state=tk.DISABLED)
        if self.initial_deck is None:
            self.redeal_button.config(state=tk.DISABLED)
        else:
            self.redeal_button.config(state=tk.NORMAL)
        # self.clear_highlights()

        # Add a small delay before re-enabling the deal button
        self.master.after(500, self.enable_deal_button)

    def enable_deal_button(self):
        self.interrupt_flag = False
        self.deal_button.config(state=tk.NORMAL)

    def animated_deal(self):
        if self.interrupt_flag:
            return  # Don't start a new deal if an interrupt is in progress

        self.deal_button.config(state=tk.DISABLED)
        self.status_var.set("Dealing cards...")

        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.deck = self.create_deck()

        self.initial_deck = self.deck.copy()

        house_card_counts = [8, 8, 8, 7, 6, 5, 4, 3, 2, 1]

        def deal_card(house_index, card_count):
            if self.interrupt_flag:
                pygame.mixer.stop()  # Stop the sound if interrupted
                return

            if card_count > 0 and self.deck:
                self.houses[house_index].append(self.deck.pop())
                self.display_cards()
                self.master.update()
                self.play_sound(self.deal_sound)
                self.master.after_id = self.master.after(
                    100, deal_card, house_index, card_count - 1
                )
            elif house_index < 9:
                self.master.after_id = self.master.after(
                    100, deal_card, house_index + 1, house_card_counts[house_index + 1]
                )
            else:
                pygame.mixer.stop()  # Stop the sound when dealing is finished
                self.finish_deal()

        deal_card(0, house_card_counts[0])

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.rules_manager.set_is_muted(self.is_muted)
        self.update_mute_button_text()
        self.apply_mute_state()

    def update_mute_button_text(self):
        self.mute_button.config(text="Unmute" if self.is_muted else "Mute")

    def apply_mute_state(self):
        volume = 0.0 if self.is_muted else 1.0
        self.deal_sound.set_volume(volume)
        # Apply to other sounds if there are any

    def play_sound(self, sound):
        if not self.is_muted:
            sound.play()

    def finish_deal(self):
        self.status_var.set("Cards dealt. Good luck!")
        self.deal_button.config(state=tk.DISABLED)
        # self.hint_button.config(state=tk.NORMAL)
        self.redeal_button.config(state=tk.NORMAL)
        self.undo_button.config(state=tk.NORMAL)

    def redeal_cards(self):
        if self.initial_deck is None:
            self.status_var.set("No previous deal available. Start a new game first.")
            return

        # Reset move count at the beginning of redeal
        self.move_count = 0
        self.move_counter_label.config(text="Moves: 0")

        self.deal_button.config(state=tk.DISABLED)
        self.status_var.set("Redealing cards...")

        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.deck = self.initial_deck.copy()

        house_card_counts = [8, 8, 8, 7, 6, 5, 4, 3, 2, 1]

        def redeal_card(house_index, card_count):
            if self.interrupt_flag:
                if pygame.mixer.get_busy():
                    pygame.mixer.stop()  # Stop the sound if interrupted
                return

            if card_count > 0 and self.deck:
                self.houses[house_index].append(self.deck.pop())
                self.display_cards()
                self.master.update()
                self.play_sound(self.deal_sound)
                self.master.after_id = self.master.after(
                    100, redeal_card, house_index, card_count - 1
                )
            elif house_index < 9:
                self.master.after_id = self.master.after(
                    100,
                    redeal_card,
                    house_index + 1,
                    house_card_counts[house_index + 1],
                )
            else:
                pygame.mixer.stop()  # Stop the sound when dealing is finished
                self.finish_redeal()

        redeal_card(0, house_card_counts[0])

    def handle_escape(self, event):
        if self.master.attributes("-fullscreen"):
            self.toggle_fullscreen()

    def finish_redeal(self):
        self.status_var.set("Cards redealt. Good luck!")
        self.deal_button.config(state=tk.DISABLED)
        # self.hint_button.config(state=tk.NORMAL)
        self.redeal_button.config(state=tk.NORMAL)
        self.undo_button.config(state=tk.NORMAL)

        if self.is_muted:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()

    def display_cards(self):
        self.game_canvas.delete("card")
        self.card_items.clear()

        x_spacing = self.card_width + 20
        y_spacing = int(30 * self.zoom_factor)  # Adjust this value to increase spacing
        stack_spacing = int(
            25 * self.zoom_factor
        )  # New variable for spacing between stacked cards

        for house_idx, house in enumerate(self.houses):
            x = 60 + house_idx * x_spacing
            y = 20
            for card_idx, card in enumerate(house):
                item = self.game_canvas.create_image(
                    x, y, image=card.image, anchor=tk.NW, tags="card"
                )
                self.card_items[item] = card
                self.game_canvas.tag_bind(item, "<ButtonPress-1>", self.on_card_press)
                self.game_canvas.tag_bind(
                    item, "<ButtonRelease-1>", self.on_card_release
                )
                self.game_canvas.tag_bind(item, "<B1-Motion>", self.on_card_motion)

                # Increase the spacing between stacked cards
                y += stack_spacing

        # Display cards in end houses (if implemented)
        for house_idx, house in enumerate(self.end_houses):
            x = 300 + house_idx * x_spacing
            y = 600
            for card in house:
                item = self.game_canvas.create_image(
                    x, y, image=card.image, anchor=tk.NW, tags="card"
                )
                self.card_items[item] = card
                y += y_spacing

    def on_card_press(self, event):
        item = self.game_canvas.find_closest(event.x, event.y)[0]
        card = self.card_items[item]
        house_index, house = self.find_card_house(card)
        if house:
            card_index = house.index(card)
            movable_stack = self.get_movable_stack(house, card_index)
            if movable_stack:
                self.drag_data = {
                    "x": event.x,
                    "y": event.y,
                    "item": item,
                    "cards": movable_stack,
                    "source_house": house,
                    "source_index": card_index,
                    "start_positions": [
                        (self.game_canvas.coords(self.get_card_item(c)))
                        for c in movable_stack
                    ],
                }
                for drag_card in movable_stack:
                    self.game_canvas.tag_raise(self.get_card_item(drag_card))
            else:
                self.drag_data = {"x": 0, "y": 0, "item": None}
        else:
            self.drag_data = {"x": 0, "y": 0, "item": None}

    def get_movable_stack(self, house, card_index):
        if card_index < len(house) - 1:
            # Check if the cards below follow the rule (descending rank, alternating color)
            for i in range(card_index + 1, len(house)):
                if (
                    house[i].rank != house[i - 1].rank - 1
                    or house[i].color == house[i - 1].color
                ):
                    return None  # Can't move this card as it's not at the bottom of a valid stack

        # If we reach here, we can move the card and any valid cards above it
        movable_stack = house[card_index:]
        return movable_stack if len(movable_stack) > 0 else None

    def update_game_state(self, dragged_item):
        self.save_move()

        dragged_cards = self.drag_data["cards"]
        x, y = self.game_canvas.coords(dragged_item)

        source_house = self.drag_data["source_house"]
        target_house, target_house_index = self.find_nearest_house(x, y)

        if source_house != target_house and self.is_valid_move(
            dragged_cards, target_house
        ):
            self.move_card(dragged_cards, source_house, target_house)
            self.update_move_count()

        self.display_cards()

        if self.check_win():
            self.status_var.set("Congratulations! You've won the game!")
            self.deal_button.config(state=tk.NORMAL)
        elif self.is_game_over():
            self.status_var.set("Game over. No more moves possible. Try again!")
            self.deal_button.config(state=tk.NORMAL)

    def find_nearest_house(self, x, y):
        min_distance = float("inf")
        nearest_house = None
        nearest_index = -1

        for i, house in enumerate(self.houses):
            house_x = 60 + i * (self.card_width + 20)
            house_y = 20
            distance = ((x - house_x) ** 2 + (y - house_y) ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                nearest_house = house
                nearest_index = i

        return nearest_house, nearest_index

    def on_card_release(self, event):
        if self.drag_data["item"] and self.drag_data["cards"]:
            self.update_game_state(self.drag_data["item"])
            self.undo_button.config(state=tk.NORMAL)
            if self.check_win():
                self.status_var.set("Congratulations! You've won the game!")
        self.drag_data = {
            "x": 0,
            "y": 0,
            "item": None,
            "cards": None,
            "start_positions": None,
        }

    def on_card_motion(self, event):
        if self.drag_data["item"] and self.drag_data["cards"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            for i, card in enumerate(self.drag_data["cards"]):
                item = self.get_card_item(card)
                start_x, start_y = self.drag_data["start_positions"][i]
                self.game_canvas.moveto(item, start_x + dx, start_y + dy)
            self.game_canvas.update_idletasks()  # Force immediate update

    def is_valid_move(self, cards, target_house):
        if not isinstance(cards, list):
            cards = [cards]  # Convert single card to a list

        if not target_house:  # If the target house is empty
            return True  # Any card can be placed on an empty house

        target_card = target_house[-1]
        moving_card = cards[0]  # The bottom card of the moving stack

        # Check if the bottom card of the moving stack can be placed on the target card
        if (moving_card.rank == target_card.rank - 1) and (
            moving_card.color != target_card.color
        ):
            # If it's a valid move, check if all cards in the stack maintain the alternating color and descending rank
            for i in range(1, len(cards)):
                if not (
                    cards[i].rank == cards[i - 1].rank - 1
                    and cards[i].color != cards[i - 1].color
                ):
                    return False
            return True
        return False

    def find_card_house(self, card):
        for i, house in enumerate(self.houses):
            if card in house:
                return i, house
        return None, None

    def save_move(self):
        if len(self.move_history) >= 5:
            self.move_history.pop(0)
        self.move_history.append([house.copy() for house in self.houses])

    def move_card(self, cards, from_house, to_house):
        if not isinstance(cards, list):
            cards = [cards]  # Convert single card to a list

        # Find the index of the first card in the source house
        index = from_house.index(cards[0])

        # Remove these cards from the source house
        from_house[index:] = []

        # Add the cards to the target house
        to_house.extend(cards)

        # Update the cards_above attribute for the cards
        for i in range(len(cards) - 1):
            cards[i].cards_above = [cards[i + 1]]
        cards[-1].cards_above = []

        # If the target house is not empty, update the cards_above of the previous top card
        if len(to_house) > len(cards):
            to_house[-len(cards) - 1].cards_above = [cards[0]]

    def check_win(self):
        valid_house_count = 0

        for house in self.houses:
            if len(house) == 13:
                if house[0].rank == 13 and house[-1].rank == 1:
                    if all(
                        house[i].rank == house[i - 1].rank - 1 for i in range(1, 13)
                    ):
                        valid_house_count += 1

        if valid_house_count == 4:
            self.win_celebration.show_celebration(self.move_count)
            return True

        return False

    def get_card_item(self, card):
        for item, c in self.card_items.items():
            if c == card:
                return item
        return None

    def is_game_over(self):
        # Check if any moves are possible
        for i, source_house in enumerate(self.houses):
            if not source_house:
                continue
            for j, target_house in enumerate(self.houses):
                if i != j and self.is_valid_move([source_house[-1]], target_house):
                    return False
        # Check if any cards can be moved to end houses
        for house in self.houses:
            if house and self.can_move_to_end_house(house[-1]):
                return False
        return True

    def can_move_to_end_house(self, card):
        for end_house in self.end_houses:
            if not end_house and card.rank == 1:  # Ace can be moved to empty end house
                return True
            if (
                end_house
                and card.suit == end_house[-1].suit
                and card.rank == end_house[-1].rank + 1
            ):
                return True
        return False

    # def create_hint_button(self):
    #     self.hint_button = tk.Button(self.master, text="Hint", command=self.show_hint)
    #     self.hint_button.pack(side=tk.BOTTOM, pady=10)

    # FIXME: Better hints.

    # def check_game_winnable(self):
    #     current_state = GameState(
    #         [[Card(card.suit, card.rank) for card in house] for house in self.houses]
    #     )
    #     solver = Solver(current_state)
    #     if not solver.is_game_winnable():
    #         self.status_var.set("Warning: The game may no longer be winnable.")

    # def get_hint(self):
    #     current_state = GameState(
    #         [[Card(card.suit, card.rank) for card in house] for house in self.houses]
    #     )
    #     solver = Solver(current_state)
    #     best_move = solver.find_best_move()
    #     return best_move

    # def is_game_winnable(self):
    #     current_state = GameState(
    #         [[Card(card.suit, card.rank) for card in house] for house in self.houses]
    #     )
    #     solver = Solver(current_state)
    #     return solver.is_game_winnable()

    # def show_hint(self):
    #     self.clear_highlights()
    #     best_move = self.get_hint()

    #     if best_move:
    #         source, target, card = best_move
    #         source_house = self.houses[source]
    #         target_house = self.houses[target]  # Not used.

    #         # Highlight the card to move
    #         self.highlight_card(source_house[-1])

    #         # Update status bar with hint message
    #         self.status_var.set(
    #             f"Hint: Move {card.rank} of {card.suit} from house {source + 1} to house {target + 1}"
    #         )
    #     else:
    #         self.status_var.set(
    #             "No hints available. The game may be in an unwinnable state."
    #         )

    #     # Check if the game is still winnable
    #     if not self.is_game_winnable():
    #         self.status_var.set("Warning: The game may no longer be winnable.")

    # FIXME: Make better card highlighting. Try highlighting the card entirely instead of just the border.

    # def highlight_card(self, card):
    #     self.clear_highlights()  # Clear existing highlights
    #     item = self.get_card_item(card)
    #     x, y = self.game_canvas.coords(item)

    #     # Create a semi-transparent rectangle over the entire card
    #     highlight = self.game_canvas.create_rectangle(
    #         x,
    #         y,
    #         x + self.card_width,
    #         y + self.card_height,
    #         fill="yellow",
    #         stipple="gray50",
    #         outline="",
    #         tags="highlight",
    #     )

    #     self.highlight_rectangles.append(highlight)
    #     self.game_canvas.tag_raise(highlight)
    #     self.game_canvas.tag_raise(item)

    #     # Start the strobing effect
    #     self.strobe_highlight(highlight, 5)  # 5 seconds of strobing

    # def strobe_highlight(self, highlight, duration):
    #     start_time = time.time()

    #     def update_opacity():
    #         elapsed = time.time() - start_time
    #         if elapsed < duration:
    #             # Calculate opacity using a sine wave for smooth pulsing
    #             opacity = int(sin(elapsed * pi) * 63 + 64)  # Reduced opacity range
    #             color = f"#{opacity:02x}ffff"  # Yellow with varying opacity
    #             self.game_canvas.itemconfig(highlight, fill=color)
    #             self.strobe_after_id = self.master.after(
    #                 50, update_opacity
    #             )  # Update every 50ms
    #         else:
    #             self.game_canvas.delete(highlight)
    #             self.highlight_rectangles.remove(highlight)
    #             self.strobe_after_id = None

    #     update_opacity()

    # def clear_highlights(self):
    #     for rect in self.highlight_rectangles:
    #         self.game_canvas.delete(rect)
    #     self.highlight_rectangles.clear()
    #     if self.strobe_after_id is not None:
    #         self.master.after_cancel(self.strobe_after_id)
    #         self.strobe_after_id = None

    def toggle_fullscreen(self):
        is_fullscreen = self.master.attributes("-fullscreen")
        if is_fullscreen:
            self.master.attributes("-fullscreen", False)
            self.master.overrideredirect(
                False
            )  # This brings back the window decorations
        else:
            self.master.attributes("-fullscreen", True)
        self.rules_manager.set_is_fullscreen(not is_fullscreen)
        if not is_fullscreen:
            self.status_var.set("Fullscreen mode enabled. Press F11 or ESC to exit.")
        else:
            self.status_var.set("Fullscreen mode disabled.")

    def undo_move(self):
        if not self.move_history:
            self.show_undo_alert()
            return

        self.houses = self.move_history.pop()
        self.display_cards()
        self.status_var.set("Move undone.")

        self.move_count = max(
            0, self.move_count - 1
        )  # Ensure move count doesn't go below 0
        self.move_counter_label.config(text=f"Moves: {self.move_count}")

        if not self.move_history:
            self.undo_button.config(state=tk.DISABLED)

    def show_undo_alert(self):
        tk.messagebox.showwarning(
            "Undo Limit Reached", "You can only undo up to 5 moves."
        )

    # TODO: Add timer.

    # TODO: Add gamestate check to make sure game is winnable after each move, and warn player if not. (Minimax maybe? A-B Pruning)


if __name__ == "__main__":
    root = tk.Tk()
    game = PatienceGame(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()
