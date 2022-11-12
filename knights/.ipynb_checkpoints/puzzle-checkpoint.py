from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Game Rule: 'A' can be either a Knight or a Knave, but not both:
    Or(AKnight,AKnave), 
    Not(And(AKnight,AKnave)),
    # Knaves lie, so 'A' being a Knave could say it is both a Knight and a Knave:
    Or(AKnave,(And(AKnight,AKnave))),
    # Knights don't lie, so he could not say he is both a Knight and a Knave:
    Or(AKnight,(Not(And(AKnight,AKnave))))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # Game Rule: 'A' can be either a Knight or a Knave, but not both:
    Or(AKnight,AKnave), 
    Not(And(AKnight,AKnave)),
    # Game Rule: 'B' can be either a Knight or a Knave, but not both:
    Or(BKnight,BKnave), 
    Not(And(BKnight,BKnave)),
    # Game Rule: if 'A' is a Knight, 'B' must be a Knave:
    Implication(AKnight,BKnave),
    Implication(BKnight,AKnave),
    # Knaves lie, so 'A' being a Knave could say both are Knaves:
    Or(AKnave,(And(AKnave,BKnave))),
    # Knights don't lie, so he could not say both are Knaves:
    Or(AKnight,(Not(And(AKnave,BKnave))))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Game Rule: 'A' can be either a Knight or a Knave, but not both:
    Or(AKnight,AKnave), 
    Not(And(AKnight,AKnave)),
    # Game Rule: 'B' can be either a Knight or a Knave, but not both:
    Or(BKnight,BKnave), 
    Not(And(BKnight,BKnave)),
    # Game Rule: if 'A' is a Knight, 'B' must be a Knave:
    Implication(AKnight,BKnave),
    # Game Rule: if 'B' is a Knight, 'A' must be a Knave:
    Implication(BKnight,AKnave),
    # A says 'we are the same kind' - check if A is na Knave:
    Or(AKnave,(And(AKnave,BKnave))),
    # B Says 'we are different kinds' - check if B could be a Knight:
    Or(AKnight,(And(AKnave,BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # Game Rule: 'A' can be either a Knight or a Knave, but not both:
    Or(AKnight,AKnave), 
    Not(And(AKnight,AKnave)),
    # Game Rule: 'B' can be either a Knight or a Knave, but not both:
    Or(BKnight,BKnave), 
    Not(And(BKnight,BKnave)),
    # Game Rule: 'C' can be either a Knight or a Knave, but not both:
    Or(CKnight,CKnave), 
    Not(And(CKnight,CKnave)),
    # We don't know what A said, so it could be either Knive or Knave:
    Or(AKnight,AKnave), 
    # 'B' says 'A' and 'C' are Knaves:
    Implication(BKnight, And(AKnave, CKnave)),
    # But if 'B' is a Knave it is telling lies, so 'A' and 'C' should be Knights:
    And(BKnave, And(AKnight,CKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
