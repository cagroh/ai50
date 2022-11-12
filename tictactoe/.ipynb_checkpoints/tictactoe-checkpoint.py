"""
Tic Tac Toe Player
"""

import math
import copy
import numpy  as np  # used to compute a numeric array from a given board to assess winners
import random as rnd # used to randomly choose a starting point when ai is playing as 'X'

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    ttt_board = [[EMPTY, EMPTY, EMPTY],
                 [EMPTY, EMPTY, EMPTY],
                 [EMPTY, EMPTY, EMPTY]]
    return ttt_board


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_o = 0
    count_x = 0
    aux_board = board
    next_turn = ''
    
    # next player is the one with fewer movements:
    for i in range(3):
        for j in range(3):
            if aux_board[i][j] == O: count_o += 1
            if aux_board[i][j] == X: count_x += 1

    if count_o < count_x:
        next_turn = O
    else: next_turn = X
    return next_turn


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    result=[]#set()
    aux_board = board
    for i in range(3):
        for j in range(3):
            if aux_board[i][j] == EMPTY:
                result.append((i,j))
    return result


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = tuple(action)
    aux_board = copy.deepcopy(board)
    if aux_board[i][j] != EMPTY: raise Exception(F"Sorry, invalid move [{i},{j}]")
    aux_player = player(aux_board)
    aux_board[i][j]=aux_player
    return aux_board
        

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    winner = utility(board)
    if   winner ==  1: return X
    elif winner == -1: return O
    else: return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # The game ends when there are no more options left or if there's a winner:
    game_over = (actions(board) == []) or (utility(board) != 0)
    return game_over


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    def verify_winner (board, player):
        a_board = np.array([[0,0,0],[0,0,0],[0,0,0]])
        has_winner = False

        for i in range(3):
            for j in range(3):
                if board[i][j] == player: 
                    a_board[i][j] = 1
                else:
                    a_board[i][j] = 0
                    
            # if a row sums 3, there's a winner:
            if sum(a_board[i]) == 3: has_winner = True
            
        # if a column sums 3, there's a winner:
        for i in range(3):
            if (sum(row[i] for row in a_board)) == 3: has_winner = True
       
        # if a diagonal sums 3, there's a winner:
        if a_board[0,0]+a_board[1,1]+a_board[2,2] == 3: has_winner = True
        if a_board[0,2]+a_board[1,1]+a_board[2,0] == 3: has_winner = True
        
        return has_winner
    
    if   verify_winner (board, X): return  1
    elif verify_winner (board, O): return -1
    else: return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    # assesses the max value of a move:
    def max_value(board):
        global ai_user

        # the resultant utility of a terminal board depends on who's playing for max:
        if terminal(board):
            return utility(board) if ai_user == X else -utility(board)
        
        # initializes the return value to the lowest possible:
        v = -math.inf

        # get the maximum utility from all moves:
        for action in actions(board):
            v = max(v, min_value(result(board, action)))
        return v

    # assesses the min value of a move:
    def min_value(board):
        global ai_user
        
        # the resultant utility of a terminal board depends on who's playing for max:
        if terminal(board):
            return utility(board) if ai_user == X else -utility(board)

        # initializes the return value to the highest possible:
        v = math.inf

        # get the minimum utility from all moves:
        for action in actions(board):
            v = min(v, max_value(result(board, action)))
        return v

    #------------------------------------------------------------------                
    # main loop of the minimax function:
    global ai_user
    
    # return None if no longer actions left:
    if terminal(board): return None

    # save board state before evaluating next moves:
    a_board = copy.deepcopy(board)

    # get the marker for ai:
    ai_user = player(a_board)

    # if ai plays as X and it's the begining og the game, shortcuts 
    # to a random move for one of the corners of the board:
    if ai_user == X and len(actions(a_board)) == 9:
        return (rnd.choice([[0,0],[2,2],[0,2],[2,0]]))
    
    # initializes variables:
    v = -math.inf
    best_minimax = v
    best_move = tuple()

    # loop to assess all valid moves in a given board:
    for action in actions(a_board):
        # starts minimax computing:
        v = max(v, min_value(result(a_board, action)))

        # if resulting value is better, save the action:
        if v > best_minimax:
            best_minimax = v
            best_move=action

    # return the best choice:
    return best_move
