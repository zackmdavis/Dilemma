import unittest

from play import Move, Defector, TitForTat, SimpleMatch


class DefectorVsTitForTatTestCase(unittest.TestCase):
    def test_sequence(self):
        tft = TitForTat()
        d = Defector()
        m = SimpleMatch(3, tft, d)
        self.assertEqual(
            [(Move.COOPERATE, Move.DEFECT),
             (Move.DEFECT, Move.DEFECT),
             (Move.DEFECT, Move.DEFECT)],
            m.sequence()
        )


if __name__ == "__main__":
    unittest.main()
