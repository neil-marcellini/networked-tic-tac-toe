# Modified by Neil Marcellini
# 3/5/21
# Created by Kevin Scrivnor
# COMP 429

class TicTacToeEngine:
    def __init__(self):
        self.game_started = False
        self.game_ended = False
        self.p1 = None
        self.p2 = None
        # board is just a list of dashes for blanks. X and O's will fill it eventually.
        self.board = ['-','-','-','-','-','-','-','-','-']
        # is it x's turn?
        self.x_turn = True
        # how many successful turns have we played?
        self.turns = 0


    def restart(self):
        self.board = ['-','-','-','-','-','-','-','-','-']
        self.x_turn = True
        self.turns = 0
        self.game_ended = False
        self.game_started = False
        self.p1 = None
        self.p2 = None


    def display_board(self):
        j = 0
        for i in range(0,9): # for (i = 0; i < 9; i++)
            # print without a new line
            print(self.board[i], end=' ')
            j += 1
            # add a new line every 3 board spaces
            if j % 3 == 0:
                print('')


    def is_game_over(self):
        # winning combos in tic tac toe
        winning_combos = [  (0,1,2),(3,4,5),(6,7,8),
                            (0,3,6),(1,4,7),(2,5,8),
                            (0,4,8),(2,4,6)]

        # for each of the winning combos
        for combo in winning_combos:
            # assume the first piece is a winner
            winner = self.board[combo[0]]
            # if it is not blank
            if winner == 'X' or winner == 'O':
                # and if the next two on the board are the same as the first one
                if winner == self.board[combo[1]] and winner == self.board[combo[2]]:
                    # that piece has won
                    return winner

        # no winning combos and the board is full.
        if self.turns == 9:
            return 'T'

        # not done yet
        return '-'


    def make_move(self, pos, char):
        # make a move if it is valid (between 0 and 8 inclusive)
        # increase number of turns by 1
        # place char at that position on the board
        if self.is_move_valid(pos):
            self.board[pos] = char
            self.turns += 1
            return True
        return False

    def is_move_valid(self, pos):
        # make sure it is on the board and no one has already played there!
        return (pos >= 0 and pos <= 8 and self.board[pos] == '-')
    
    def get_move_from(self, new_state):
        new_board = [char for char in new_state]
        # figure out what move was made based on the new board
        for pos, character in enumerate(new_board):
            if character != self.board[pos]:
                return pos
            


ttte = TicTacToeEngine()
#ttte.display_board()
#print(ttte.is_game_over())
#
#for i in range(0,9):
#    print('='*40)
#    ttte.make_move(i)
#    ttte.display_board()
#    winner = ttte.is_game_over()
#    if winner != '-':
#        print("Winner: " + winner)
#        break
#
#if winner == '-':
#    print("Tie.")
