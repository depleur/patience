from tkinter import messagebox


class WinCelebration:
    def __init__(self, game):
        self.game = game

    def show_celebration(self, move_count):
        message = (
            f"Excellent work! You have beaten Patience.\n\n"
            f"You took {move_count} moves to complete this game.\n\n"
            f"Click 'Redeal' if you would like to better your score, \n"
            f"'Yay!' if you want to close this window, or\n"
            f"'Clear Board' if you would like to start afresh."
        )

        result = messagebox.askquestion(
            "Congratulations!", message, type="yesnocancel", icon="info", default="yes"
        )

        if result == "yes":  # Redeal
            self.game.redeal_cards()
        elif result == "no":  # Yay! (close window)
            pass  # Dialog will close automatically
        else:  # Clear Board
            self.game.clear_board()


def create_win_celebration(game):
    return WinCelebration(game)
