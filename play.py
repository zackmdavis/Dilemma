import uuid
import random
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


# above was just a santity-check exercise; hierarchical tit-for-tat simulation
# below makes somewhat different coding-convention choices; we can refactor
# later if we want to keep using this code

def defy(status):
    return 1/(1 + status)

def exploit(status):
    return 1 - 1/(1 + status)

def standoff(status):
    return status/(status + 1)


class HierarchicalTitForTat:
    def __init__(self, status=0, first_move=Move.COOPERATE):
        self.status = status
        # The motivation for writing this code is to simulate the subsequent
        # cycles when hTFT bots are stipulated to C/D each other, so the first
        # move needs to be specifiable
        self.first_move = first_move
        # In this simulation, `previously` will be a tuple of
        # `(my last move, their last move)`
        self.previously = None

    def play(self, opponent_status):
        # special-case first move to start the cycle
        if self.previously is None:
            return self.first_move

        if self.previously == (Move.COOPERATE, Move.COOPERATE):
            return Move.COOPERATE  # nice good good nice
        elif self.previously == (Move.COOPERATE, Move.DEFECT):
            # If she defected on me last time ...
            if self.status > opponent_status:
                # and I have higher status, then punish.
                return Move.DEFECT
            else:
                # But if not, decide whether to appease her based on my status.
                if random.random() < defy(self.status):
                    # standing up for yourself is punished in status terms, but
                    # let's assume there's a status floor in order to prevent
                    # the `defy`/`exploit` probability functions from
                    # blowing up on status −1
                    if self.status > 0:
                        self.status -= 1
                    return Move.DEFECT
                else:
                    self.status += 1  # appeasement is rewarded
                    return Move.COOPERATE
        elif self.previously == (Move.DEFECT, Move.COOPERATE):
            # If I defected on her last time ...
            if self.status < opponent_status:
                return Move.COOPERATE  # I'm sorry! It was an accident!
            else:
                # Otherwise, I may continue to exploit my advantage depending
                # on how high status I am
                if random.random() < exploit(self.status):
                    self.status += 1
                    return Move.DEFECT
                else:
                    if self.status > 0:  # again, assume a status floor
                        self.status -= 1
                    return Move.COOPERATE  # withdraw
        elif self.previously == (Move.DEFECT, Move.DEFECT):
            self.status += 1
            # XXX: confirm with model author!!! For now, I'm assuming that the
            # `status/(status + 1)` function that I'm calling `standoff` gives
            # a probability of defection (the ms. said it was a probability of
            # cooperation, but that sounds doubtful to me
            if random.random() < standoff(self.status):
                return Move.DEFECT
            else:
                return Move.COOPERATE
        else:
            assert False, "All cases covered; this branch should never happen."


class SimpleHierarchicalMatch:
    def __init__(self, length, player_one, player_two):
        self.length = length
        self.player_one = player_one
        self.player_two = player_two

    def sequence(self):
        results = []
        for _ in range(self.length):
            prior_status_one = self.player_one.status
            prior_status_two = self.player_two.status
            move_one = self.player_one.play(self.player_two.status)
            move_two = self.player_two.play(self.player_one.status)
            results.append(((move_one, prior_status_one), (move_two, prior_status_two)))
            self.player_one.previously = (move_one, move_two)
            self.player_two.previously = (move_two, move_one)
        return results

    def display_sequence(self):
        print(
            ' → '.join(
                '{}{}/{}{}'.format(
                    tick[0][0].value, tick[0][1], tick[1][0].value, tick[1][1]
                ) for tick in self.sequence()
            )
        )


if __name__ == "__main__":
    for _ in range(10):
        p1 = HierarchicalTitForTat(status=2, first_move=Move.COOPERATE)
        p2 = HierarchicalTitForTat(status=1, first_move=Move.DEFECT)
        m = SimpleHierarchicalMatch(10, p1, p2)
        m.display_sequence()
