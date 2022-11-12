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
        return self.cells if len(self.cells) == self.count else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # CG: A cell if known to be safe when it has no mines in the surroundingss:
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # CG: If cell is in the sentence, remove it and decrement count by one:
        if len(self.cells) > 1:
            if cell in self.cells:
                self.cells.remove(cell)
                self.count -= 1
        # CG: if cells is a single cell, just mark it to be a mine by making count = -1:
        elif self.cells == cell:
            self.count = -1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # CG: If cell is in the sentence, remove it, but do not decrement count:
        if len(self.cells) > 1:
            if cell in self.cells:
                self.cells.remove(cell)
                #self.count = 0
        # CG: if cells is a single cell, just mark it as safe by making count = 0:
        #elif len(self.cells) == 1:
        #    self.count = 0


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
        
        # -------------------------------------------------------------------------
        # CG: helper to find cells surrounding a cell and those which are unplayed:
        # -------------------------------------------------------------------------
        def get_surrounding_cells(cell):
            surrounding_cells = []
            empty_cells = []
            l, c = cell
            # CG: loop over all cells within the cell's quadrant:
            for i in range(l - 1, l + 2):
                for j in range(c - 1, c + 2):
                    # CG: ignore the cell itself:
                    if (i, j) == cell:
                        continue
                    # CG: check if cell is inside the game board limits:
                    if 0 <= i < self.height and 0 <= j < self.width:
                        surrounding_cells.append((i, j))
                        # CG: check if cell is not yet clicked:
                        if (i, j) not in self.moves_made:
                            # CG: also check if cell is not a known mine:
                            if (i, j) not in self.mines:
                                empty_cells.append((i, j))
            # CG: return the lists of surrounding cells and cells not yet clicked ant not known as mines:
            return sorted(surrounding_cells), sorted(empty_cells)

        # ------------------------------------------
        # CG: mark all cells in a given set as safe:
        # ------------------------------------------
        def mark_surrounding_cells_as_safe(cells):
            marked_cells = set()
            for acell in cells:
                if acell not in self.safes:
                    if acell not in self.mines:
                        self.mark_safe(acell)
                        print(F"surrounding {acell} marked as safe")
                        marked_cells.add(acell)
            return marked_cells

        # ---------------------------------------------------
        # CG: return count of mines adjacent to a given cell:
        # ---------------------------------------------------
        def get_bomb_count(cell):
            # CG: initialize bomb count with a value indicating cell status is unknown:
            bomb_count = -9
            acell = set()
            acell.add ((cell))
            # CG: loop over all sentences in the knowledge base:
            for i, sentence in enumerate(self.knowledge):
                # CG: if there's knowledge for the cell, return it's bomb-count:
                ########## print (F"comparing {acell} to {sentence.cells} count {sentence.count}")
                if sentence.cells == acell:
                    # CG: if the cell is not a known mine (count = -1), return count:
                    if sentence.count >= 0:
                        bomb_count = sentence.count
                        break ##### última mexida!
            ######### print (F"Cell {acell} has {bomb_count} bombs")
            return bomb_count

        # ---------------------------------------------------------------------------
        # CG: decrements mine count for all single cells in a quadrant around a mine:
        # ---------------------------------------------------------------------------
        def dec_bomb_count_around(cell):
            # CG: get all cells surrounding given cell:
            surrounding, empty = get_surrounding_cells(cell)
            # CG: ignore empty (unplayed) cells in the list:
            surrounding = set(surrounding) - set(empty)
            # CG: loop over surrounding cells:
            for acell in surrounding:
                # CG: initialize count with a value indicating cell is not yet clicked:
                a_cell=set()
                a_cell.add(acell)
                # CG: loop over all sentences in the knowledge base:
                for i, sentence in enumerate(self.knowledge):
                    # CG: if there's intell for the cell, decrement it's bomb-count:
                    if sentence.cells == a_cell:
                        # CG: but only if count is greater than 0, so to preserve safe cells:
                        if sentence.count > 0:
                            sentence.count -= 1

        # -----------------------------------------------------------------------------------------------
        # CG: helper to loop over the game board and find status of single cells remaining in a quadrant:
        # -----------------------------------------------------------------------------------------------
        def print_game_board(loop, aboard):
            print(F"LOOP {loop}:")
            for i in range(self.height):
                row=""
                sep=""        
                for j in range(self.width):
                    cell = "  " if aboard[i][j] == -10 else "{: }".format(aboard[i][j])
                    row = row + cell + ('|' if j < (self.width - 1) else "")
                    sep = sep + "--" + ('+' if j < (self.width - 1) else "")
                print (sep)
                print (row)
            print (sep)

        # ----------------------------------------------------
        # CG: helper to seek for mine count inside a quadrant:
        # ----------------------------------------------------
        def seek_minecount(cells):
            bomb_count = -9
            for acell in sorted(cells):
                bomb_count = max(bomb_count, get_bomb_count(acell))
            return bomb_count

        # -----------------------------------------------------------------------------
        # CG: helper to emply several strategic rules to infer new mines or safe cells:
        # -----------------------------------------------------------------------------
        def infer_additional_mines_safes():
            # -------------------------------------------------------
            # CG: helper to return surround cells in a virtual board:
            # -------------------------------------------------------
            def get_virtual_surrounding_cells(cell):
                surrounding_cells = []
                empty_cells = []
                l, c = cell
                # CG: loop over all cells within the cell's quadrant:
                for i in range(l - 1, l + 2):
                    for j in range(c - 1, c + 2):
                        # CG: ignore the cell itself:
                        if (i, j) == cell:
                            continue
                        # CG: check if cell is inside the game board limits:
                        if 0 <= i < self.height and 0 <= j < self.width:
                            surrounding_cells.append((i, j))
                            # CG: check if cell is not yet clicked:
                            if (i, j) not in self.moves_made:
                                # CG: also check if cell is not a known mine:
                                if (i, j) not in self.mines:
                                    empty_cells.append((i, j))
                # CG: return the lists of surrounding cells and cells not yet clicked ant not known as mines:
                return sorted(surrounding_cells), sorted(empty_cells)
            # ---------------------------------------
            # CG: helper to get mine count of a cell:
            # ---------------------------------------
            def get_virtual_bomb_count(cell):
                # CG: initialize bomb count with a value indicating cell status is unknown:
                i, j = cell
                bomb_count = -9
                if virtual_board[i][j] != -10:
                    bomb_count = virtual_board[i][j]
                return bomb_count
            # ---------------------------------------------------------------------------
            # CG: decrements mine count for all single cells in a quadrant around a mine:
            # ---------------------------------------------------------------------------
            def dec_virtual_bomb_count_around(cell):
                # CG: get all cells surrounding given cell:
                surrounding, empty = get_virtual_surrounding_cells(cell)
                # CG: loop over surrounding cells:
                for acell in surrounding:
                    i, j = acell
                    if virtual_board[i][j] == -10:
                        virtual_board[i][j] = -1
                    else:
                        virtual_board[i][j] -= 1
           # ----------------------------------------------------
            # CG: helper to seek for mine count inside a quadrant:
            # ----------------------------------------------------
            def seek_virtual_minecount(cells):
                bomb_count = -9
                for acell in sorted(cells):
                    bomb_count = max(bomb_count, get_virtual_bomb_count(acell))
                return bomb_count

            # ---------------------------------------------------------------------------
            # CG: let's compose a virtual board image based on existing knowledge base:
            virtual_board = []
            for i in range(self.height):
                row=[]
                for j in range(self.width):
                    row.append(-10)
                virtual_board.append(row)

            for sentence in self.knowledge:
                # CG: get knowledge from single cells first:
                if len(sentence.cells) == 1:
                    # CG: loop to get i,j for the cell in the set:
                    for acell in sentence.cells:
                        i, j = acell
                        # save the bomb count to the position in the virtual board:
                        virtual_board[i][j] += sentence.count

            sweep_again = True
            loops = 0
            while sweep_again:
                # CG: print out the game board found:
                sweep_again = False
                loops += 1
                print_game_board(loops, virtual_board)
                for acell in sorted(self.moves_made ^ self.mines):
                    surrounding_cells, empty_cells = get_virtual_surrounding_cells(acell)
                    bomb_count = get_virtual_bomb_count(acell)
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
                                virtual_board[i][j] = -1
                                self.mark_mine(empty_cell)
                                print(F"5-infer-2 {empty_cell} marked as mine")
                                self.knowledge.append(Sentence(empty_cell, -1))
                                print (F"5-infer-2 sentence added as {empty_cell}, -1")
                                dec_virtual_bomb_count_around(empty_cell)
                                sweep_again = True
                                break # restart the loop
                        # check if the center of the quadrant is a bomb:
                        elif bomb_count == -1:
                            # CG: center quadrant on empty cell:                            
                            surrounding_cells, empty_cells = get_virtual_surrounding_cells(empty_cell)
                            # CG: seek for any surrounding cell containing mine count > 0
                            bomb_count = seek_virtual_minecount(surrounding_cells)
                            if bomb_count == 0:
                                if empty_cell not in self.safes:
                                    self.mark_safe(empty_cell)
                                    print(F"5-infer-3 {empty_cell} marked as safe")
                                    sweep_again = True
                                    break # restart the loop
                            elif bomb_count > 0:
                                if empty_cell not in self.mines:
                                    i, j = empty_cell
                                    virtual_board[i][j] = -1
                                    self.mark_mine(empty_cell)
                                    print(F"5-infer-4 {empty_cell} marked as mine")
                                    self.knowledge.append(Sentence(empty_cell, -1))
                                    print (F"5-infer-4 sentence added as {empty_cell}, -1")
                                    dec_virtual_bomb_count_around(empty_cell)
                                    sweep_again = True
                                    break
                    # CG: if there are two empty cells in a quadrant, check if they are contiguous in a row or column:
                    elif len(empty_cells) == 2:
                        # CG: determine check if set is at minimum 3X3:
                        if len(surrounding_cells) != 8:
                            break
                        # CG: determine empty cells corner, if any:
                        cell1 = min(empty_cells)
                        cell2 = max(empty_cells)
                        i1, j1 = cell1
                        i2, j2 = cell2
                        # check if they are in the same row or column:
                        if (i1 == i2) or (j1 == j2):
                            same_row = False
                            same_col = False
                            # check if they are contiguous:
                            if (max(i1, i2) - min(i1, i2) == 1) or (max(j1, j2) - min(j1, j2) == 1):
                                x, y = min(surrounding_cells)
                                r, c = max(surrounding_cells)
                                # CG: if they are in the same row:
                                if i1 == i2:
                                    same_row = True
                                    if i1 == x:
                                        # CG: gap is positioned at the top of the quadrant:
                                        if (virtual_board[i1][j-1] != None) and 
                                        if y2 == c:
                                            # CG: gap is at the top right:
                                            r = i1
                                            c = j1
                                        # CG: gap is at the top left:
                                        else:
                                            r = i1
                                            c = j2
                                    elif if i1 == r:
                                        # CG: gap is positioned at the bottom of the quadrant:
                                        x1 = i1 - 1
                                        x2 = x1
                                        y1 = j1
                                        y2 = j2
                                        # CG: gap is at the bottom right:
                                        if y2 == c:
                                            r = i1
                                            c = j1
                                        # CG: gap is at the top left:
                                        else:
                                            r = i1
                                            c = j2
                                    # gap is at the middle row of the quadrant:
                                    else:
                                        break # To Do
                                # CG: check if they are in the same column:
                                if j1 == j2:
                                    same_col = True
                                    if j1 == y:
                                        # CG: gap is positioned at the left of the quadrant:
                                        x1 = i1
                                        x2 = x1
                                        y1 = j1
                                        y2 = j2
                                        if y2 == c:
                                            # CG: gap is at the top right:
                                            r = i1
                                            c = j1
                                        # CG: gap is at the top left:
                                        else:
                                            r = i1
                                            c = j2
                                    elif if i1 == r:
                                        # CG: gap is positioned at the bottom of the quadrant:
                                        x1 = i1 - 1
                                        x2 = x1
                                        y1 = j1
                                        y2 = j2
                                        # CG: gap is at the bottom right:
                                        if y2 == c:
                                            r = i1
                                            c = j1
                                        # CG: gap is at the top left:
                                        else:
                                            r = i1
                                            c = j2
                                # CG: check if they have same count:
                                do_it = False
                                # CG: check if they have same count:
                                if virtual_board[i1][j1-1] != None and virtual_board[i1][y2]:
                                    if same_row:
                                        x = x1
                                        y = min(y1, y2)
                                        if y > 0:
                                            if virtual_board[x][y-1] > 0:
                                                do_it = True
                                        else:
                                            y = max(y1, y2)
                                            if y < self.height:
                                                if virtual_board[x][y+1] > 0:
                                                    do_it = True
                                    if same_col:
                                        y = y1
                                        x = min(x1, x2)
                                        if x > 0:
                                            if virtual_board[x-1][y] > 0:
                                                do_it = True
                                        else:
                                            x = max(x1, x2)
                                            if x < self.height:
                                                if virtual_board[x+1][y] > 0:
                                                    do_it = True
                                # CG: mark corner as mine:
                                if do_it:
                                    virtual_board[i1][j-1] = -1
                                    acell = ((i1, j-1))
                                    self.mark_mine(acell)
                                    print(F"5-infer-5 {acell} marked as mine")
                                    self.knowledge.append(Sentence(acell, -1))
                                    print (F"5-infer-5 sentence added as {acell}, -1")
                                    dec_virtual_bomb_count_around(acell)
                                    sweep_again = True
                                    break
                            
                                           
                                    

 
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
        self.knowledge.append(Sentence([cell], count))
        print (F"3-sentence added as {cell}, {count}")
        # -----------------------------------------------------------------------------------------------------------------------------------

        # CG: 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base:
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: if current cell bomb count is zero then all surrounding cells are safe:
        surrounding_cells, empty_cells = get_surrounding_cells(cell)
        # CG: are there surrounding cells (i.e. not first move)?:
        if len(surrounding_cells) > 0:
            # CG: add all surrounding cells and mine count to knowledge base:
            ############# self.knowledge.append(Sentence(surrounding_cells, count))
            ############# print (F"4a-sentence added as {surrounding_cells}, {count}")
            # CG: if played cell mine count is zero, then all surrounding cells are known to be safe:
            if count == 0:
                # CG: mark all surrounding cells as safe:
                marked_cells = mark_surrounding_cells_as_safe(surrounding_cells)
                print (F"4a-additional cells marked as safe: {marked_cells}")

        # CG: checks if there are only one empty (unplayed/unknown) cell in the surroundings:
        if len(empty_cells) == 1 and count >= 1:
            # CG: if there's only one cell, it's likely to be a mine:
            a_cell = set()
            a_cell.add(empty_cells)
            if a_cell not in self.mines:
                # CG: double-check if the remaining cell is not marked as a safe one:
                if a_cell not in self.safes:
                    # CG: mark the cell as a mine
                    self.mark_mine(a_cell)
                    print(F"4b {a_cell} marked as mine")
                    # CG: add individual knowledge about remaining cells to be a mine to the KB:
                    self.knowledge.append(Sentence(a_cell, -1))
                    print (F"4b sentence added as {a_cell}, -1")
                    # CG: decrement mine count for all surrounding cells:
                    dec_bomb_count_around (a_cell)
        # -----------------------------------------------------------------------------------------------------------------------------------

        # CG: 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge:
        # -----------------------------------------------------------------------------------------------------------------------------------
        # CG: loop over all moves made but this move, if there are no more safe moves to make:
        #if len(self.safes - self.moves_made - self.mines) < 2: 

        infer_additional_mines_safes()
        
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
        print (F'randomly chosen safe move={amove} from {sorted(set_of_moves)}')
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
        print (F"moves made: {sorted(self.moves_made)}")
        print (F'randomly chosen move={amove} from {sorted(set_of_moves)}')
        return amove


    # kown bugs:
    # skipped some mines
    # 