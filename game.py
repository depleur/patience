import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random


class Card:
    def __init__(self, suit, rank, image):
        self.suit = suit
        self.rank = rank
        self.color = "red" if suit in ["hearts", "diamonds"] else "black"
        self.image = image


class PatienceGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Patience Card Game")

        # Define card dimensions at the beginning
        self.card_width = 80
        self.card_height = 120

        self.center_window(1200, 800)
        self.create_menu()
        self.create_game_area()
        self.create_status_bar()

        self.card_images = self.load_card_images()
        self.deck = self.create_deck()
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_items = {}
        self.setup_game()
        self.display_cards()

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
        game_menu.add_separator()
        game_menu.add_command(label="Quit", command=self.master.quit)

    def create_game_area(self):
        self.game_frame = ttk.Frame(self.master, padding="10")
        self.game_frame.pack(fill=tk.BOTH, expand=True)

        self.game_canvas = tk.Canvas(self.game_frame, bg="#076324")
        self.game_canvas.pack(fill=tk.BOTH, expand=True)

        self.create_house_areas()

    def create_house_areas(self):
        for i in range(10):
            x = 60 + i * (self.card_width + 20)
            y = 20
            self.game_canvas.create_rectangle(
                x,
                y,
                x + self.card_width,
                y + self.card_height,
                outline="#FFD700",
                width=2,
            )

        for i in range(4):
            x = 300 + i * (self.card_width + 20)
            y = 600
            self.game_canvas.create_rectangle(
                x,
                y,
                x + self.card_width,
                y + self.card_height,
                outline="#FFD700",
                width=2,
            )

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Welcome to Patience!")
        status_bar = ttk.Label(
            self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def new_game(self):
        self.status_var.set("New game started!")
        self.setup_game()
        self.display_cards()

    def restart_game(self):
        self.status_var.set("Game restarted!")
        self.setup_game()
        self.display_cards()

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

    def setup_game(self):
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.deck = self.create_deck()

        house_card_counts = [8, 8, 8, 7, 6, 5, 4, 3, 2, 1]
        start_from_right = True

        for house_idx, card_count in enumerate(house_card_counts):
            if start_from_right:
                house_position = 9 - house_idx
            else:
                house_position = house_idx

            self.houses[house_position] = [self.deck.pop() for _ in range(card_count)]
            start_from_right = not start_from_right

    def display_cards(self):
        self.game_canvas.delete("card")
        self.card_items.clear()

        x_spacing = self.card_width + 20
        y_spacing = 30

        for house_idx, house in enumerate(self.houses):
            x = 60 + house_idx * x_spacing
            y = 20
            for card in house:
                item = self.game_canvas.create_image(
                    x, y, image=card.image, anchor=tk.NW, tags="card"
                )
                self.card_items[item] = card
                self.game_canvas.tag_bind(item, "<ButtonPress-1>", self.on_card_press)
                self.game_canvas.tag_bind(
                    item, "<ButtonRelease-1>", self.on_card_release
                )
                self.game_canvas.tag_bind(item, "<B1-Motion>", self.on_card_motion)
                y += y_spacing

        # Display cards in end houses
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
        self.game_canvas.tag_raise(item)
        self.drag_data = {"x": event.x, "y": event.y, "item": item}

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
            self.game_canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def is_valid_move(self, card, target_house):
        if not target_house:  # If the target house is empty
            return card.rank == 13  # Only King can be placed on an empty house

        target_card = target_house[-1]
        return (card.rank == target_card.rank - 1) and (card.color != target_card.color)

    def find_card_house(self, card):
        for i, house in enumerate(self.houses):
            if card in house:
                return i, house
        return None, None

    def move_card(self, card, from_house, to_house):
        # Remove the card and all cards on top of it from the source house
        index = from_house.index(card)
        cards_to_move = from_house[index:]
        from_house[index:] = []

        # Add the cards to the target house
        to_house.extend(cards_to_move)

    def update_game_state(self, dragged_item):
        dragged_card = self.card_items[dragged_item]
        x, y = self.game_canvas.coords(dragged_item)

        # Find the target house
        target_house_index = min(9, max(0, int((x - 60) / (self.card_width + 20))))
        target_house = self.houses[target_house_index]

        # Find the source house
        source_house_index, source_house = self.find_card_house(dragged_card)

        if source_house_index != target_house_index and self.is_valid_move(
            dragged_card, target_house
        ):
            self.move_card(dragged_card, source_house, target_house)
            self.display_cards()  # Redraw all cards
        else:
            # If the move is invalid, return the card to its original position
            self.display_cards()

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


if __name__ == "__main__":
    root = tk.Tk()
    game = PatienceGame(root)
    root.mainloop()
