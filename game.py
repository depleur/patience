import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import time


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

        self.card_width = 80
        self.card_height = 120

        self.center_window(1200, 800)
        self.create_menu()
        self.create_game_area()
        self.create_status_bar()
        self.create_deal_button()

        self.card_images = self.load_card_images()
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_items = {}
        self.drag_data = {"x": 0, "y": 0, "item": None}

        self.status_var.set("Welcome to Patience! Click 'Deal Cards' to begin.")

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
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_items.clear()
        self.game_canvas.delete("card")
        self.status_var.set("New game started. Click 'Deal Cards' to begin.")
        self.deal_button.config(state=tk.NORMAL)

    def restart_game(self):
        self.new_game()
        self.status_var.set("Game restarted. Click 'Deal Cards' to begin.")

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
        self.deal_button.config(state=tk.DISABLED)  # Disable the button during dealing
        self.status_var.set("Dealing cards...")

        # Clear existing cards
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.deck = self.create_deck()

        house_card_counts = [8, 8, 8, 7, 6, 5, 4, 3, 2, 1]

        # Deal cards from right to left for the first iteration
        for i in range(9, -1, -1):
            for _ in range(house_card_counts[9 - i]):
                self.houses[i].append(self.deck.pop())
                self.display_cards()
                self.master.update()
                time.sleep(0.1)

        # Deal remaining cards from left to right
        current_house = 0
        left_to_right = True
        while self.deck:
            if len(self.houses[current_house]) < 8:
                self.houses[current_house].append(self.deck.pop())
                self.display_cards()
                self.master.update()
                time.sleep(0.1)

            if left_to_right:
                current_house = (current_house + 1) % 10
                if current_house == 0:
                    left_to_right = False
            else:
                current_house = (current_house - 1) % 10
                if current_house == 9:
                    left_to_right = True

        self.status_var.set("Cards dealt. Good luck!")
        self.deal_button.config(
            state=tk.DISABLED
        )  # Keep the button disabled after dealing

    # def setup_game(self):
    #     self.houses = [[] for _ in range(10)]
    #     self.end_houses = [[] for _ in range(4)]
    #     self.deck = self.create_deck()
    #     self.status_var.set("Welcome to Patience! Click 'Deal Cards' to begin.")

    #     house_card_counts = [8, 8, 8, 7, 6, 5, 4, 3, 2, 1]

    #     # Deal cards from right to left for the first iteration
    #     for i in range(9, -1, -1):
    #         self.houses[i] = [self.deck.pop() for _ in range(house_card_counts[9 - i])]

    #     # Deal remaining cards from left to right
    #     current_house = 0
    #     while self.deck:
    #         if len(self.houses[current_house]) < 8:
    #             self.houses[current_house].append(self.deck.pop())
    #         current_house = (current_house + 1) % 10

    def display_cards(self):
        self.game_canvas.delete("card")
        self.card_items.clear()

        x_spacing = self.card_width + 20
        y_spacing = 30

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

                # Only the top card of each pile should be fully visible
                if card_idx < len(house) - 1:
                    y += 15  # Smaller vertical spacing for stacked cards
                else:
                    y += y_spacing  # Larger spacing for the top card

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
        target_house_index = min(9, max(0, int((x - 60) / (self.card_width + 20))))
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
            return card.rank == 13  # Only King can be placed on an empty house

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


if __name__ == "__main__":
    root = tk.Tk()
    game = PatienceGame(root)
    root.mainloop()
