import uuid
from enum import Enum

class Move(Enum):
    COOPERATE = 'C'
    DEFECT = 'D'


class Player:
    def __init__(self):
        self.id = uuid.uuid4()

    def play(self, opponent_id):
        raise NotImplementedError

    def update(self, opponent_id, move):
        """Called to inform the bot about what her opponent did."""
        raise NotImplementedError


class Defector(Player):
    def play(self, _opponent_id):
        return Move.DEFECT

    def update(self, _opponent_id, _move):
        ...  # Defector doesn't care


class TitForTat(Player):
    def __init__(self):
        super().__init__()
        # dictionary to track other players' last moves against self
        self.previously = {}

    def play(self, opponent_id):
        previously = self.previously.get(opponent_id)
        if previously is None:
            return Move.COOPERATE
        return previously

    def update(self, opponent_id, move):
        self.previously[opponent_id] = move


class SimpleMatch:
    def __init__(self, length, player_one, player_two):
        self.length = length
        self.player_one = player_one
        self.player_two = player_two

    def sequence(self):
        results = []
        for _ in range(self.length):
            move_one = self.player_one.play(self.player_two.id)
            move_two = self.player_two.play(self.player_one.id)
            results.append((move_one, move_two))
            self.player_one.update(self.player_two.id, move_two)
            self.player_two.update(self.player_one.id, move_one)
        return results
