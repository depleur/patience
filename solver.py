import copy
from typing import List, Tuple


class Card:
    def __init__(self, suit: str, rank: int):
        self.suit = suit
        self.rank = rank
        self.color = "red" if suit in ["hearts", "diamonds"] else "black"


class GameState:
    def __init__(self, houses: List[List[Card]]):
        self.houses = houses


class Solver:
    def __init__(self, initial_state: GameState):
        self.initial_state = initial_state

    def is_valid_move(self, card: Card, target_card: Card) -> bool:
        return (card.rank == target_card.rank - 1) and (card.color != target_card.color)

    def get_possible_moves(self, state: GameState) -> List[Tuple[int, int, Card]]:
        moves = []
        for i, source_house in enumerate(state.houses):
            if not source_house:
                continue
            card = source_house[-1]
            for j, target_house in enumerate(state.houses):
                if i == j:
                    continue
                if not target_house or self.is_valid_move(card, target_house[-1]):
                    moves.append((i, j, card))
        return moves

    def apply_move(self, state: GameState, move: Tuple[int, int, Card]) -> GameState:
        new_state = copy.deepcopy(state)
        source, target, _ = move
        card = new_state.houses[source].pop()
        new_state.houses[target].append(card)
        return new_state

    def evaluate_state(self, state: GameState) -> int:
        score = 0
        for house in state.houses:
            if len(house) == 13 and house[0].rank == 13 and house[-1].rank == 1:
                score += 100  # Big bonus for completed houses
            score += sum(
                1
                for i in range(1, len(house))
                if self.is_valid_move(house[i], house[i - 1])
            )
        return score

    def minimax(
        self, state: GameState, depth: int, alpha: int, beta: int, maximizing: bool
    ) -> int:
        if depth == 0 or not self.get_possible_moves(state):
            return self.evaluate_state(state)

        if maximizing:
            max_eval = float("-inf")
            for move in self.get_possible_moves(state):
                new_state = self.apply_move(state, move)
                eval = self.minimax(new_state, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in self.get_possible_moves(state):
                new_state = self.apply_move(state, move)
                eval = self.minimax(new_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self, max_depth: int = 4) -> Tuple[int, int, Card]:
        best_score = float("-inf")
        best_move = None
        for move in self.get_possible_moves(self.initial_state):
            new_state = self.apply_move(self.initial_state, move)
            score = self.minimax(
                new_state, max_depth - 1, float("-inf"), float("inf"), False
            )
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def is_game_winnable(self, max_depth: int = 6) -> bool:
        score = self.minimax(
            self.initial_state, max_depth, float("-inf"), float("inf"), True
        )
        return score > 0  # You may need to adjust this threshold
