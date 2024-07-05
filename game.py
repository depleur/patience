import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random


# Card class to represent individual cards
class Card:
    def __init__(self, suit, rank, image):
        self.suit = suit
        self.rank = rank
        self.color = "red" if suit in ["hearts", "diamonds"] else "black"
        self.image = image


# Main application class
class PatienceGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Patience Card Game")
        self.center_window(1024, 768)
        self.create_menu()
        self.create_game_area()
        self.create_status_bar()

        self.card_images = self.load_card_images()
        self.deck = self.create_deck()
        self.houses = [[] for _ in range(10)]
        self.end_houses = [[] for _ in range(4)]
        self.card_labels = {}  # Dictionary to hold card labels
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.setup_game()
        self.display_cards()

    def center_window(self, width, height):
        # Get the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate the position to center the window
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Set the window size and position
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

        # Canvas for the main game area
        self.game_canvas = tk.Canvas(self.game_frame, bg="green")
        self.game_canvas.pack(fill=tk.BOTH, expand=True)

        # Create areas for houses
        self.create_house_areas()

    def create_house_areas(self):
        # Initial 10 houses
        for i in range(10):
            x = 50 + i * 90
            y = 50
            self.game_canvas.create_rectangle(x, y, x + 70, y + 100, outline="white")
            self.game_canvas.create_text(
                x + 35, y + 50, text=f"House {i + 1}", fill="white"
            )

        # Final 4 houses
        for i in range(4):
            x = 250 + i * 90
            y = 500
            self.game_canvas.create_rectangle(x, y, x + 70, y + 100, outline="white")
            self.game_canvas.create_text(
                x + 35, y + 50, text=f"Final {i + 1}", fill="white"
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
        ranks = list(range(1, 14))  # 1 for Ace, 11 for Jack, 12 for Queen, 13 for King
        card_images = {}

        for suit in suits:
            for rank in ranks:
                image_path = f"images/{rank}_of_{suit}.png"
                image = Image.open(image_path)
                image = image.resize(
                    (50, 70), Image.LANCZOS
                )  # Resize to smaller dimensions
                card_images[(suit, rank)] = ImageTk.PhotoImage(image)

        return card_images

    def create_deck(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        ranks = list(range(1, 14))  # 1 for Ace, 11 for Jack, 12 for Queen, 13 for King
        deck = [
            Card(suit, rank, self.card_images[(suit, rank)])
            for suit in suits
            for rank in ranks
        ]
        random.shuffle(deck)
        return deck

    def setup_game(self):
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
        # Clear previous cards
        for label in self.card_labels.values():
            label.destroy()
        self.card_labels.clear()

        # Constants for spacing
        card_width = 50  # Width of a resized card image
        card_height = 70  # Height of a resized card image
        x_spacing = card_width + 10  # Horizontal space between card stacks
        y_spacing = card_height // 4  # Vertical space between cards in a stack

        for house_idx, house in enumerate(self.houses):
            x = 50 + house_idx * x_spacing
            y = 50
            for card in house:
                card_label = tk.Label(
                    self.game_canvas, image=card.image, borderwidth=1, relief="solid"
                )
                card_label.place(x=x, y=y)
                self.card_labels[card] = card_label
                self.bind_card_events(card_label)
                y += y_spacing

    def on_card_press(self, event):
        widget = event.widget
        self.drag_data["item"] = widget
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_card_release(self, event):
        self.drag_data["item"] = None
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def on_card_motion(self, event):
        widget = self.drag_data["item"]
        x = widget.winfo_x() - self.drag_data["x"] + event.x
        y = widget.winfo_y() - self.drag_data["y"] + event.y
        widget.place(x=x, y=y)

    def bind_card_events(self, card_label):
        card_label.bind("<ButtonPress-1>", self.on_card_press)
        card_label.bind("<ButtonRelease-1>", self.on_card_release)
        card_label.bind("<B1-Motion>", self.on_card_motion)


if __name__ == "__main__":
    root = tk.Tk()
    game = PatienceGame(root)
    root.mainloop()
