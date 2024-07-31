from game import PatienceGame
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    game = PatienceGame(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()
