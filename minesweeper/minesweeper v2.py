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
        # CG: A cell if known to be a mine when the number of cells is equal to the number of mines:
        if self.count == -9:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # CG: A cell if known to be safe when it has no mines in the surroundingss:
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # CG: If cell is in the sentence, remove it and decrement count by one:
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # CG: If cell is in the sentence, remove it, but do not decrement count
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

        # CG: helper to loop over all surrounding cells in a cell's quadrant:
        def get_surrounding_cells(cell):
            surrounding_cells = []
            empty_cells = []
            l, c = cell
            # CG: loop over all cells within the cell's quadrant:
            for i in range(l - 1, l + 2):
                for j in range(c - 1, c + 2):
                    # Ignore the cell itself
                    if (i, j) == cell:
                        continue
                    # CG: check if cell is inside the game board limits:
                    if 0 <= i < self.height and 0 <= j < self.width:
                        surrounding_cells.append((i, j))
                        # CG: check if cell is not yet clicked:
                        if (i, j) not in self.moves_made:
                            empty_cells.append((i, j))
            # CG: return the lists of surrounding cells and cells not yet clicked ant not known as mines:
            return sorted(surrounding_cells), sorted(empty_cells)
        
        # CG: check for any unmoved cell in a quadrant and return count of bonbs and count of unmoved cells:
        def get_bomb_count(cell):
            # CG: initialize count with a value indicating cell is not yet clicked:
            acell=set()
            acell.add(cell)
            bomb_count = -10
            # CG: loop over all sentences in the knowledge base:
            for i, sentence in enumerate(self.knowledge):
                # CG: if there's intell for the cell, return it's bomb-count:
                ########### print (F"comparing {sentence.cells} to {acell} - {sentence.count}")
                if sentence.cells == acell:
                    bomb_count=sentence.count
                    break
            return bomb_count
        
        # CG: decrements mine count for all cells in a quadrant of a mine found:
        def dec_bomb_count(cell):
            # CG: get all cells surrounding a bomb
            print (F"            decrementing bomb count surrounding {cell}")
            surrounding, empty = get_surrounding_cells(cell)
            # CG: clean all empty cells from the list:
            surrounding = set(surrounding) - set(empty)
            for acell in surrounding:
                # CG: initialize count with a value indicating cell is not yet clicked:
                a_cell=set()
                a_cell.add(acell)
                # CG: loop over all sentences in the knowledge base:
                for i, sentence in enumerate(self.knowledge):
                    # CG: if there's intell for the cell, decrement it's bomb-count:
                    if sentence.cells == a_cell:
                        # CG: but only if count is greater than 0:
                        if sentence.count > 0:
                            print (F"                decrementing bomb count for {a_cell} from {sentence.count} to {sentence.count - 1}")
                            sentence.count -= 1
            # CG: if a cell if empty, add it to knowledge base with count = -1:
            for acell in (empty):
                # CG: initialize count with a value indicating cell is not yet clicked:
                a_cell=set()
                a_cell.add(acell)
                # CG: loop over all sentences in the knowledge base:
                ############ print(F"5-infer-2 {empty_cell} marked as mine")
                self.knowledge.append(Sentence(a_cell, -1))
                

        def review_safe_cells():
            # CG: loop over all played cells and review any safe ones:
            for acell in (self.moves_made ^ self.mines):
                surrounding_cells, empty_cells = get_surrounding_cells(acell)
                bomb_count = get_bomb_count(acell)
                print (F"reviwing {acell} - {bomb_count}")
                if len(surrounding_cells) > 0: 
                    for a_cell in surrounding_cells:
                        a_cell_bomb_count = get_bomb_count(a_cell)
                        print (F"     checking surrounding cell {a_cell} - {a_cell_bomb_count}")
                        if a_cell_bomb_count == 0:
                            # CG: if current cell bomb count is zero then all surrounding cells are safe:
                            if a_cell not in self.safes:
                                if a_cell not in self.mines:
                                    self.mark_safe(a_cell)
                                    #self.knowledge.append(Sentence([a_cell], 0))
                                    print (F"        1-cell reviwed as safe: {a_cell}")
                        # if surrounding is an unplayed cell, it's probably a safe one:
                        elif a_cell_bomb_count == -10 and bomb_count == 0:
                            if a_cell not in self.safes:
                                self.mark_safe(a_cell)
                                #self.knowledge.append(Sentence([a_cell], 0))
                                print (F"        2-cell reviwed as safe: {a_cell}")
                

        def mark_surrounding_cells_as_safe(cell):
            surrounding_cells, empty_cells = get_surrounding_cells(cell)
            for acell in (surrounding_cells):
                if acell not in self.safes:
                    if acell not in self.mines:
                        self.mark_safe(acell)
                        print (F"        3-cell reviwed as safe: {acell}")

        # ----------------------------------------------------
        # CG: helper to seek for mine count inside a quadrant:
        # ----------------------------------------------------
        def seek_minecount(cells):
            bomb_count = -10
            for acell in sorted(cells):
                bomb_count = max(bomb_count, get_bomb_count(acell))
            return bomb_count

        def append_or_update_knowledge(cell, count):
            acell=set()
            acell.add(cell)
            updated = False
            for i, sentence in enumerate(self.knowledge):
                print (F" ***** comparing {sentence.cells} to {acell}")
                if sentence.cells == acell:
                    self.knowledge[i].count += count
                    print (F"knowledge updated: {acell},{count}, {self.knowledge[i].count}")
                    updated = True
            if not updated:
                self.knowledge.append(Sentence(acell, count))
                print (F"knowledge appended: {acell},{count}")
        # ---------------------------------------------------------------------------
        # CG: decrements mine count for all single cells in a quadrant around a mine:
        # ---------------------------------------------------------------------------
        def dec_bomb_count_around(cell):
            # CG: get all cells surrounding given cell:
            surrounding, empty = get_surrounding_cells(cell)
            # CG: loop over surrounding cells:
            for acell in surrounding:
                i, j = acell
                if get_bomb_count(acell) < -8:
                    append_or_update_knowledge(acell, -1)

        def infer_additional_mines_or_safes ():
            """
            sweep_again = True
            loops = 0
            while sweep_again:
                # CG: print out the game board found:
                sweep_again = False
                loops += 1
                ########### print_game_board(loops, virtual_board)
                for acell in sorted(self.moves_made ^ self.mines):
                    surrounding_cells, empty_cells = get_surrounding_cells(acell)
                    bomb_count = get_bomb_count(acell)
                    # CG: if there's only one empty cell, it's easy to point it out as mine or safe:
                    if len(empty_cells) == 1:
                        empty_cell = empty_cells[0]
                        if bomb_count == 0:
                            if empty_cell not in self.safes:
                                self.mark_safe(empty_cell)
                                print(F"5-infer-1 {empty_cell} marked as safe")
                                sweep_again = True
                                break
                        elif bomb_count > 0:
                            if empty_cell not in self.mines:
                                i, j = empty_cell
                                self.mark_mine(empty_cell)
                                print(F"5-infer-2 {empty_cell} marked as mine")
                                self.knowledge.append(Sentence(empty_cell, -9))
                                dec_bomb_count_around(empty_cell)
                                sweep_again = True
                                break # restart the loop
                        # check if the center of the quadrant is a bomb:
                        elif bomb_count == -9:
                            # CG: center quadrant on empty cell:                            
                            surrounding_cells, empty_cells = get_surrounding_cells(empty_cell)
                            # CG: seek for any surrounding cell containing mine count > 0
                            bomb_count = seek_minecount(surrounding_cells)
                            if bomb_count == 0:
                                if empty_cell not in self.safes:
                                    self.mark_safe(empty_cell)
                                    print(F"5-infer-3 {empty_cell} marked as safe")
                                    sweep_again = True
                                    break # restart the loop
                            elif bomb_count > 0:
                                if empty_cell not in self.mines:
                                    i, j = empty_cell
                                    self.mark_mine(empty_cell)
                                    print(F"5-infer-4 {empty_cell} marked as mine")
                                    self.knowledge.append(Sentence(empty_cell, -9))
                                    print (F"5-infer-4 sentence added as {empty_cell}, -1")
                                    dec_bomb_count_around(empty_cell)
                                    sweep_again = True
                                    break
            """


        print ("-----------------------------------------------------------------------------------------------------------------------------------")
        print (F"Adding Knowledge for move {cell}")

        # CG: 1) mark the cell as a move that has been made:
        # -----------------------------------------------------------------------------------------------------------------------------------
        self.moves_made.add (tuple(cell))
        print ("1-cell added to moves made")
        # -----------------------------------------------------------------------------------------------------------------------------------
        
        # CG: 2) mark the cell as safe, if not already marked:
        # -----------------------------------------------------------------------------------------------------------------------------------
        if cell not in self.safes:
            self.mark_safe(tuple(cell))
            print ("2-cell marked as safe")
        # -----------------------------------------------------------------------------------------------------------------------------------

        # CG: 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`:
        # -----------------------------------------------------------------------------------------------------------------------------------
        append_or_update_knowledge(cell, count)
        #self.knowledge.append(Sentence([cell], count))
        print (F"3-sentence added as {cell}, {count}")
        # -----------------------------------------------------------------------------------------------------------------------------------

        # CG: 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base:
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: if current cell bomb count is zero then all surrounding cells are safe:
        surrounding_cells, empty_cells = get_surrounding_cells(cell)
        # CG: loop over all surrounding cells:
        if len(surrounding_cells) > 0: 
            for acell in surrounding_cells:
                if count == 0:
                    # CG: if current cell bomb count is zero then all surrounding cells are safe:
                    if acell not in self.safes:
                        self.mark_safe(acell)
                        #self.knowledge.append(Sentence([acell], 0))
                        print (F"4a-additional cell marked as safe: {acell}")
        # CG: loop over all empty surrounding cells:
        found_mines = False
        if len(empty_cells) > 0: 
            for acell in empty_cells:
                # CG: if there's only one cell remaining and mine count is >= 1, mark it as a known mine if cell is not marked as safe:
                if len(empty_cells) == 1 and count >= 1:
                    if acell not in self.mines:
                        if acell not in self.safes:
                            self.mark_mine(acell)
                            self.knowledge.append(Sentence([acell], -9))
                            print (F"4b-cell marked as mine: {acell}")
                            found_mines = True
        if found_mines: dec_bomb_count (acell)
        review_safe_cells ()

        # -----------------------------------------------------------------------------------------------------------------------------------

        # CG: 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge:
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: loop over all moves made but this move:
        """
        current_move = set()
        current_move.add (cell)
        found_mines = False
        for acell in sorted(self.moves_made - current_move):
            # CG: get bomb count for current cell:
            bomb_count = get_bomb_count(acell)
            # CG: get all cells surrounding current cell:
            surrounding_cells, empty_cells = get_surrounding_cells(acell)
            # CG: loop over all surrounding cells:
            for a_cell in surrounding_cells:
                # CG: if current cell bomb count is zero then all surrounding cells are safe:
                if bomb_count == 0:
                    if a_cell not in self.safes:
                        self.mark_safe(a_cell)
                        #self.knowledge.append(Sentence([a_cell], 0))
                        print (F"5a-additional cell marked as safe: {a_cell}")
            # CG: loop over all empty surrounding cells:
            for a_cell in empty_cells:
                # CG: if there's only one cell remaining and mine count >= 1, mark it as a known mine:
                if len(empty_cells) == bomb_count >= 1:
                    if a_cell not in self.mines:
                        if a_cell not in self.safes:
                            self.mark_mine(a_cell)
                            self.knowledge.append(Sentence([a_cell], -9))
                            print (F"5b-cell marked as mine: {a_cell}")
                            found_mines = True
        if found_mines: dec_bomb_count (a_cell)
        review_safe_cells ()
        """
        #infer_additional_mines_or_safes()
        sweep_again = True
        loops = 0
        while sweep_again:
            # CG: print out the game board found:
            sweep_again = False
            loops += 1
            ########### print_game_board(loops, virtual_board)
            for acell in sorted(self.moves_made ^ self.mines):
                surrounding_cells, empty_cells = get_surrounding_cells(acell)
                bomb_count = get_bomb_count(acell)
                # CG: if there's only one empty cell, it's easy to point it out as mine or safe:
                if len(empty_cells) == 1:
                    empty_cell = empty_cells[0]
                    if bomb_count == 0:
                        if empty_cell not in self.safes:
                            self.mark_safe(empty_cell)
                            print(F"5-infer-1 {empty_cell} marked as safe")
                            sweep_again = True
                            break
                    elif bomb_count > 0:
                        if empty_cell not in self.mines:
                            i, j = empty_cell
                            self.mark_mine(empty_cell)
                            print(F"5-infer-2 {empty_cell} marked as mine")
                            self.knowledge.append(Sentence(empty_cell, -9))
                            dec_bomb_count_around(empty_cell)
                            sweep_again = True
                            break # restart the loop
                    # check if the center of the quadrant is a bomb:
                    elif bomb_count == -9:
                        # CG: center quadrant on empty cell:                            
                        surrounding_cells, empty_cells = get_surrounding_cells(empty_cell)
                        # CG: seek for any surrounding cell containing mine count > 0
                        bomb_count = seek_minecount(surrounding_cells)
                        if bomb_count == 0:
                            if empty_cell not in self.safes:
                                self.mark_safe(empty_cell)
                                print(F"5-infer-3 {empty_cell} marked as safe")
                                sweep_again = True
                                break # restart the loop
                        elif bomb_count > 0:
                            if empty_cell not in self.mines:
                                i, j = empty_cell
                                self.mark_mine(empty_cell)
                                print(F"5-infer-4 {empty_cell} marked as mine")
                                self.knowledge.append(Sentence(empty_cell, -9))
                                print (F"5-infer-4 sentence added as {empty_cell}, -1")
                                dec_bomb_count_around(empty_cell)
                                sweep_again = True
                                break
        # seek for known "barrages":
        for i in range(0, self.height):
            for j in range(0, self.width):
                surrounding_cells, empty_cells, surrounding_count = get_surrounding_cells_and_counts((i, j))
                bomb_count = get_bomb_count ((i,j))
                # CG check if cell if empty:
                if ((i, j)) not in self.moves_made:
                    surrounded_by = True
                    for k in range (surrounding_count):
                        surrounded_by = surrounded_by and (surrounding_count[k] > 0)
                    if surrounded_by:
                        self.mark_mine((i, j))
                        print(F"5-infer-5 ({i}, {j}) marked as mine")
                # CG: check surroundings of a mine for safe cells:
                if bomb_count == -9:
                    for acell in surrounding_cells:
                        bomb_count = get_bomb_count(acell)
                        if bomb_count <= 1 and bomb_count > -9:
                            mark_surrounding_cells_as_safe(acell)
                            print(F"5-infer-6 {acell} marked as safe")
                            
                
                                
                                
        # CG: evaluate additional minesweeping known strategies:
        #if get_bomb_count([0, 1]) == 2 and get_bomb_count([0, 2]) == 0

        print ("safes:   ", sorted(self.safes))
        print ("Mines:   ", sorted(self.mines))
        print ("secures: ", sorted(self.safes - self.moves_made - self.mines))
        print ("-----------------------------------------------------------------------------------------------------------------------------------")

        # -----------------------------------------------------------------------------------------------------------------------------------


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # CG: Compute a list of possible safe moves:
        set_of_moves = self.safes - self.moves_made - self.mines
        
        # if no moves where computed, probably the game has just began. In this case, go thru the board and pick any valid move:
        if len(set_of_moves) == 0: return None
    
        # CG: Choose a move from the list of safe moves:
        amove = random.choice(list(set_of_moves))
        print (F'randomly chosen safe move={amove} from {set_of_moves}')
        return amove


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # CG: initialize set of moves with safe choices not used first:
        set_of_moves = self.safes - self.moves_made - self.mines

        # CG: iterate thru the board to gather all possible moves:
        for i in range(self.height):
            for j in range(self.width):
                # CG: check if the tuple is in the set of moves made:
                if (i, j) not in self.moves_made:
                    # CG: check if the tuple is in the set of known mines:
                    if (i, j) not in self.mines:
                        # CG: add the tuple to the list:
                        set_of_moves.add((i, j))

        # CG: randomly chooses a tuple from the list of possible moves, prefferably a safe one:
        amove = random.choice(list(set_of_moves))
        print (F"moves made: {self.moves_made}")
        print (F'randomly chosen move={amove} from {set_of_moves}')
        return amove


    # kown bugs:
    # failed to mark some safe cells
    # 