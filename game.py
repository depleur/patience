import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import time
from math import sin, pi
from rules import RulesManager


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

        self.rules_manager = RulesManager(self.master)

        self.card_width = 80
        self.card_height = 120

        self.center_window(1200, 800)
        self.create_menu()
        self.create_game_area()
        self.create_status_bar()

        self.card_images = self.load_card_images()
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_items = {}
        self.drag_data = {"x": 0, "y": 0, "item": None}

        self.status_var.set("Welcome to Patience! Click 'Deal Cards' to begin.")

        self.highlight_rectangles = []
        self.strobe_after_id = None

        self.zoom_factor = self.rules_manager.get_zoom_factor()
        self.create_control_buttons()

        self.master.after(100, self.rules_manager.show_rules)

        self.master.bind("<F11>", lambda event: self.toggle_fullscreen())

        self.rules_manager = RulesManager(self.master)
        self.zoom_factor = self.rules_manager.get_zoom_factor()
        self.apply_zoom()

        # Apply fullscreen preference
        if self.rules_manager.get_is_fullscreen():
            self.master.attributes("-fullscreen", True)

    def create_clear_button(self):
        self.clear_button = ttk.Button(
            self.master, text="Clear Board", command=self.clear_board
        )
        self.clear_button.pack(side=tk.BOTTOM, pady=5)

    def clear_board(self):
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_items.clear()
        self.game_canvas.delete("card")
        self.status_var.set("Board cleared. Click 'Deal Cards' to start a new game.")
        self.deal_button.config(state=tk.NORMAL)
        self.hint_button.config(state=tk.DISABLED)
        self.clear_highlights()

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

    def on_closing(self):
        self.rules_manager.save_preferences()
        self.master.destroy()

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
        self.status_var = tk.StringVar()
        self.status_var.set("Welcome to Patience!")
        status_bar = ttk.Label(
            self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def new_game(self):
        self.clear_board()
        self.status_var.set("New game started. Click 'Deal Cards' to begin.")

    def create_control_buttons(self):
        control_frame = ttk.Frame(self.master)
        control_frame.pack(side=tk.BOTTOM, pady=10)

        self.deal_button = ttk.Button(
            control_frame, text="Deal Cards", command=self.animated_deal
        )
        self.deal_button.pack(side=tk.LEFT, padx=5)

        self.hint_button = ttk.Button(
            control_frame, text="Hint", command=self.show_hint
        )
        self.hint_button.pack(side=tk.LEFT, padx=5)

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

        self.fullscreen_button = ttk.Button(
            control_frame, text="Fullscreen", command=self.toggle_fullscreen
        )
        self.fullscreen_button.pack(side=tk.LEFT, padx=5)

    def restart_game(self):
        self.new_game()
        self.status_var.set("Game restarted. Click 'Deal Cards' to begin.")
        self.hint_button.config(state=tk.DISABLED)

    def load_card_images(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = list(range(1, 14))
        card_images = {}

        for suit in suits:
            for rank in ranks:
                image_path = f"images/{rank}_of_{suit}.png"
                image = Image.open(image_path)
                image = image.resize((self.card_width, self.card_height), Image.LANCZOS)
                card_images[(suit, rank)] = ImageTk.PhotoImage(image)

        return card_images

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

    def animated_deal(self):
        self.deal_button.config(state=tk.DISABLED)
        self.status_var.set("Dealing cards...")

        # Clear existing cards
        self.houses = [[] for _ in range(10)]  # Change back to 10 houses
        self.end_houses = [[] for _ in range(4)]
        self.deck = self.create_deck()

        # Adjust house_card_counts for 10 houses
        house_card_counts = [8, 8, 8, 7, 6, 5, 4, 3, 2, 1]

        # Deal cards from left to right for the first iteration
        for i in range(10):  # Change back to 10 houses
            for _ in range(house_card_counts[i]):
                if self.deck:
                    self.houses[i].append(self.deck.pop())
                    self.display_cards()
                    self.master.update()
                    time.sleep(0.1)
                else:
                    break

        self.status_var.set("Cards dealt. Good luck!")
        self.deal_button.config(state=tk.DISABLED)
        self.hint_button.config(state=tk.NORMAL)

        self.status_var.set("Cards dealt. Good luck!")
        self.deal_button.config(state=tk.DISABLED)
        self.hint_button.config(state=tk.NORMAL)

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
            self.drag_data = {
                "x": event.x,
                "y": event.y,
                "item": item,
                "cards": house[card_index:],
                "source_house": house,
                "source_index": card_index,
            }
            for drag_card in self.drag_data["cards"]:
                self.game_canvas.tag_raise(self.get_card_item(drag_card))

    def update_game_state(self, dragged_item):
        dragged_card = self.card_items[dragged_item]
        x, y = self.game_canvas.coords(dragged_item)

        # Find the target house
        target_house_index = min(
            9, max(0, int((x - 60) / (self.card_width + 20)))
        )  # Change back to 9 (10 houses - 1)
        target_house = self.houses[target_house_index]

        source_house = self.drag_data["source_house"]
        source_index = self.drag_data["source_index"]

        if source_house != target_house and self.is_valid_move(
            dragged_card, target_house
        ):
            cards_to_move = source_house[source_index:]
            self.move_card(dragged_card, source_house, target_house)
            self.display_cards()  # Redraw all cards
        else:
            # If the move is invalid, return the cards to their original position
            self.display_cards()
        if self.check_win():
            self.status_var.set("Congratulations! You've won the game!")
            self.deal_button.config(state=tk.NORMAL)
        elif self.is_game_over():
            self.status_var.set("Game over. No more moves possible. Try again!")
            self.deal_button.config(state=tk.NORMAL)

    def on_card_release(self, event):
        if self.drag_data["item"]:
            self.update_game_state(self.drag_data["item"])
            if self.check_win():
                self.status_var.set("Congratulations! You've won the game!")
        self.drag_data = {"x": 0, "y": 0, "item": None}

    def on_card_motion(self, event):
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            for card in self.drag_data["cards"]:
                item = self.get_card_item(card)
                self.game_canvas.move(item, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def is_valid_move(self, card, target_house):
        if not target_house:  # If the target house is empty
            return True  # Allow any card to be placed on an empty house

        target_card = target_house[-1]

        # Check if the bottom card of the moving unit can be placed on the target card
        if (card.rank == target_card.rank - 1) and (card.color != target_card.color):
            # If it's a valid move, check if all cards in the unit maintain the alternating color and descending rank
            current = card
            for above_card in card.cards_above:
                if not (
                    above_card.rank == current.rank - 1
                    and above_card.color != current.color
                ):
                    return False
                current = above_card
            return True
        return False

    def find_card_house(self, card):
        for i, house in enumerate(self.houses):
            if card in house:
                return i, house
        return None, None

    def move_card(self, card, from_house, to_house):
        # Find the index of the card in the source house
        index = from_house.index(card)

        # Get all cards from this card to the top of the pile
        cards_to_move = from_house[index:]

        # Remove these cards from the source house
        from_house[index:] = []

        # If the target house is not empty, update the cards_above of the top card
        if to_house:
            to_house[-1].cards_above = cards_to_move

        # Add the cards to the target house
        to_house.extend(cards_to_move)

        # Clear the cards_above for all moved cards except the bottom one
        for moved_card in cards_to_move[:-1]:
            moved_card.cards_above = []

    def on_card_motion(self, event):
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            for card in self.drag_data["cards"]:
                item = self.get_card_item(card)
                self.game_canvas.move(item, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def check_win(self):
        for house in self.end_houses:
            if len(house) != 13:
                return False
            if house[0].rank != 1 or house[-1].rank != 13:
                return False
            if not all(house[i].rank == house[i - 1].rank + 1 for i in range(1, 13)):
                return False
            if not all(house[i].color != house[i - 1].color for i in range(1, 13)):
                return False
        return True

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
                if i != j and self.is_valid_move(source_house[-1], target_house):
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

    def create_hint_button(self):
        self.hint_button = tk.Button(self.master, text="Hint", command=self.show_hint)
        self.hint_button.pack(side=tk.BOTTOM, pady=10)

    # FIXME: Better hints.

    def show_hint(self):
        self.clear_highlights()
        hint_found = False

        for i, source_house in enumerate(self.houses):
            if not source_house:
                continue
            for j, target_house in enumerate(self.houses):
                if i != j and self.is_valid_move(source_house[-1], target_house):
                    self.highlight_card(source_house[-1])
                    hint_found = True
                    break
            if hint_found:
                break

        # Check for moves to end houses
        if not hint_found:
            for house in self.houses:
                if house and self.can_move_to_end_house(house[-1]):
                    self.highlight_card(house[-1])
                    hint_found = True
                    break

        if not hint_found:
            self.status_var.set(
                "No hints available. Try moving cards to reveal new options."
            )

    # FIXME: Make better card highlighting. Try highlighting the card entirely instead of just the border.

    def highlight_card(self, card):
        self.clear_highlights()  # Clear existing highlights
        item = self.get_card_item(card)
        x, y = self.game_canvas.coords(item)

        # Create a semi-transparent rectangle over the entire card
        highlight = self.game_canvas.create_rectangle(
            x,
            y,
            x + self.card_width,
            y + self.card_height,
            fill="yellow",
            stipple="gray50",
            outline="",
            tags="highlight",
        )

        self.highlight_rectangles.append(highlight)
        self.game_canvas.tag_raise(highlight)
        self.game_canvas.tag_raise(item)

        # Start the strobing effect
        self.strobe_highlight(highlight, 5)  # 5 seconds of strobing

    def strobe_highlight(self, highlight, duration):
        start_time = time.time()

        def update_opacity():
            elapsed = time.time() - start_time
            if elapsed < duration:
                # Calculate opacity using a sine wave for smooth pulsing
                opacity = int(sin(elapsed * pi) * 63 + 64)  # Reduced opacity range
                color = f"#{opacity:02x}ffff"  # Yellow with varying opacity
                self.game_canvas.itemconfig(highlight, fill=color)
                self.strobe_after_id = self.master.after(
                    50, update_opacity
                )  # Update every 50ms
            else:
                self.game_canvas.delete(highlight)
                self.highlight_rectangles.remove(highlight)
                self.strobe_after_id = None

        update_opacity()

    def clear_highlights(self):
        for rect in self.highlight_rectangles:
            self.game_canvas.delete(rect)
        self.highlight_rectangles.clear()
        if self.strobe_after_id is not None:
            self.master.after_cancel(self.strobe_after_id)
            self.strobe_after_id = None

    def toggle_fullscreen(self):
        is_fullscreen = self.master.attributes("-fullscreen")
        self.master.attributes("-fullscreen", not is_fullscreen)
        self.rules_manager.set_is_fullscreen(not is_fullscreen)
        if not is_fullscreen:
            self.status_var.set("Fullscreen mode enabled. Press F11 to exit.")
        else:
            self.status_var.set("Fullscreen mode disabled.")

    # TODO: Add dialog box with rules at the beginning of the game, with optional checkbox to not show again.

    # TODO: Add scoring system and timer.

    # TODO: Add undo button.

    # TODO: Add gamestate check to make sure game is winnable after each move, and warn player if not.


if __name__ == "__main__":
    root = tk.Tk()
    game = PatienceGame(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()
