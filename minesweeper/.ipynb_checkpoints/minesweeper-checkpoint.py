import itertools
import random



class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: when count matches number of cells, they are all mines:
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()
        # -----------------------------------------------------------------------------------------------------------------------------------

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: when count is equal to zero, all cells are safe:
        if self.count == 0:
            return self.cells
        else: 
            return set()
        # -----------------------------------------------------------------------------------------------------------------------------------

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: 1) mark the cell as a move that has been made:
        # -----------------------------------------------------------------------------------------------------------------------------------
        print (F"    1-adding cell {cell} to moves made")
        self.moves_made.add (cell)
        # -----------------------------------------------------------------------------------------------------------------------------------
        
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: 2) mark the cell as safe, if not already marked:
        # -----------------------------------------------------------------------------------------------------------------------------------
        if cell not in self.safes:
            print (F"    2-marking cell {cell} as safe")
            self.mark_safe(cell)
        # -----------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`:
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: get adjusted count and all empty cells surrounding played cell
        empty, new_count = self.get_surrounding_empty_cells(cell, count)

        # CG: build a sentence with the data found:
        if len(empty) > 0:
            new_sentence=Sentence(sorted(empty), new_count)

            print (F"    3-adding sentence {new_sentence.cells}={new_sentence.count}")

            # CG: add the sentence to the knowledge base:
            self.knowledge.append(new_sentence)
        # -----------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base:
        # -----------------------------------------------------------------------------------------------------------------------------------

        # CG: initialize loop indicator as true:
        sweep_again = True

        # CG: loop until there are no new mines or safe cells identified:
        while sweep_again:

            # CG: let's say there are no new mines or safe cells
            sweep_again = False

            # CG: loop over the knowledge base:
            for asentence in self.knowledge:

                # CG: ignore and remove empty sentences from knowledge:
                if len(asentence.cells) == 0:

                    # CG: empty knowledge found - remove it from the list:
                    self.knowledge.remove(asentence)

                    # continue to next sentence:
                    continue

                # CG: if current cell bomb count is zero then all cells in sentence are safe:
                if len(asentence.cells) > 0 and asentence.count == 0:

                    print (F"    4a-marking additional cells {asentence.cells} as safe")

                    # CG: mark block of cells as safe:
                    self.mark_cells_safe(asentence.cells)

                    # CG: signal the loop to continue because changes where made:
                    sweep_again = True

                # CG: if number of cells matches count, all cells are mines:
                if len(asentence.cells) == asentence.count > 0:

                    print (F"    4b-marking additional cells {asentence.cells} as mine")

                    # CG: mark block of cells as mines:
                    self.mark_cells_mine(asentence.cells)

                    # CG: signal the loop to continue because changes where made:
                    sweep_again = True

        # -----------------------------------------------------------------------------------------------------------------------------------

        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge:
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: loop over all sentences in the knowledge:
        for set1 in self.knowledge:

            # CG: ignore empty cells:
            if len(set1.cells) == 0:
                continue

            # CG: inner loop to get set to compare with first set:
            for set2 in self.knowledge:

                # CG: ignore empty cells:
                if len(set2.cells) == 0:
                    continue

                # CG: Ignore identical sentences:
                if set1.cells == set2.cells:
                    continue

                # CG: check if set1 is a subset of set2:
                if set1.cells.issubset(set2.cells):

                    # CG: compute new set based on the differences between the two sets:
                    new_cells = set2.cells - set1.cells
                    new_count = abs(set2.count - set1.count)

                    # CG: build the new sentence:
                    new_sentence = Sentence(sorted(new_cells), new_count)

                    # CG: check if sentence is a valid sentence (not empty one):
                    if len(new_sentence.cells) > 0:

                        # CG: check if the new sentence is not already in the knowledge base:
                        if new_sentence not in self.knowledge:

                            # CG: add the new sentence data to the knowledge base:
                            self.knowledge.append(new_sentence)

                            print(F"    5a-adding inferred sentence: {sorted(new_sentence.cells)}={new_sentence.count} from {sorted(set1.cells)}={set1.count} and  {sorted(set2.cells)}={set2.count} ")

                        # CG: check if the new sentence could be a set of safe cells:
                        if len(new_sentence.cells) > 0 and new_sentence.count == 0:

                            print(F"    5b-marking cells as safe: {sorted(new_sentence.cells)}={new_sentence.count}")

                            # CG: mark the new set as safe:
                            self.mark_cells_safe(new_sentence.cells)

                        # CG: check if the new sentence could be a set of mine cells:
                        elif len(new_sentence.cells) == new_sentence.count > 0:

                            print(F"    5c-marking cells as mine: {sorted(new_sentence.cells)}={new_sentence.count}")

                            # CG: mark the new set as mine:
                            self.mark_cells_mine(new_sentence.cells)

        #print (F"safes: {sorted(self.safes)}")
        #print (F"    mines found: {sorted(self.mines)}")
        #print (F"    safes left:  {sorted(self.safes - self.moves_made - self.mines)}")
        #print ("KB:")
        #for i, sentence in enumerate(self.knowledge):
        #    print (F"KB{i}-'{sentence}'")
    # -----------------------------------------------------------------------------------------------------------------------------------


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: Compute a list of possible safe moves:
        set_of_moves = self.safes - self.moves_made - self.mines

        # if no moves where computed, return None:
        if len(set_of_moves) == 0: return None

        # CG: Choose a move from the list of safe moves:
        amove = random.choice(list(set_of_moves))

        #print (F"randomly chosen safe move {amove} from {sorted(set_of_moves)}")

        # CG: return chosen move:
        return amove
        # -----------------------------------------------------------------------------------------------------------------------------------


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: initialize set of moves with safe choices not used first:
        set_of_moves = set()

        # CG: iterate thru the board to gather all possible moves:
        for i in range(self.height):

            for j in range(self.width):

                # CG: check if the tuple is in the set of moves made:
                if (i, j) not in self.moves_made:

                    # CG: check if the tuple is in the set of known mines:
                    if (i, j) not in self.mines:

                        # CG: add the tuple to the list:
                        set_of_moves.add((i, j))

        # CG: if no safe moves are available, return None:
        if len(set_of_moves) == 0: return None

        # CG: randomly chooses a tuple from the list of possible moves, prefferably a safe one:
        amove = random.choice(list(set_of_moves))

        #print (F"randomly chosen move {amove} from {sorted(set_of_moves)}")
        
        # CG: return chosen move:
        return amove
        # -----------------------------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------------------------------
    # CG: helper to gather intell about all surrounding cells in a cell's quadrant taht are empty (not moved, not mines, not known to be safe):
    # -----------------------------------------------------------------------------------------------------------------------------------------
    def get_surrounding_empty_cells(self, cell, count):

        # CG: initialize variables:
        empty_cells = []
        l, c = cell

        # CG: loop over all rows:
        for i in range(l - 1, l + 2):

            # CG: loop over all columns:
            for j in range(c - 1, c + 2):

                # CG: ignore the cell itself:
                if (i, j) == cell:
                    continue

                # CG: check if cell is inside the game board limits:
                if 0 <= i < self.height and 0 <= j < self.width:

                    # CG: check if it is not a known mine:
                    if (i, j) not in self.mines:

                        # CG: check if it is not known to be safe:
                        if (i, j) not in self.safes:

                            # CG: add the cell to the list:
                            empty_cells.append((i, j))

                    # CG: if cell is a known mine, decrement count:
                    if ((i,j)) in self.mines:
                        count -= 1

        # CG: return the list and count:
        return sorted(empty_cells), count
    # -----------------------------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------------------------
    # CG: helper to mark a block of cells as safe:
    # -----------------------------------------------------------------------------------------------------------------------------------
    def mark_cells_safe(self, cells):

        # CG: iterate thru the block:
        for acell in cells.copy():

            # CG: check if cell is already marked as safe or not:
            if acell not in self.safes:

                # CG: if not, add cell to the safe cells list:
                self.mark_safe(acell)


    # -----------------------------------------------------------------------------------------------------------------------------------
    # CG: helper to mark a block of cells as mines:
    # -----------------------------------------------------------------------------------------------------------------------------------
    def mark_cells_mine(self, cells):

        # CG: iterate thru the block:
        for acell in cells.copy():

            # CG: check if cell is already marked as a mine or not:
            if acell not in self.mines:

                # CG: if not, check if cell is already marked as safe or not:
                if acell not in self.safes:

                    # CG: if not, check if cell is already marked as played or not:
                    #if acell not in self.moves_made:

                    # CG: if not, add cell to the safe cells list:
                    self.mark_mine(acell)
    # -----------------------------------------------------------------------------------------------------------------------------------
