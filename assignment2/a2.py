# CMPUT 455 Assignment 2 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a2.html

import sys
import random
import cProfile
import time

# player 1 = OR
# player 0 = AND

class CommandInterface:

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "game" : self.game,
            "show" : self.show,
            "play" : self.play,
            "legal" : self.legal,
            "genmove" : self.genmove,
            "winner" : self.winner,
            "timelimit" : self.timelimit,
            "solve" : self.solve,
            "undo" : self.undo
        }
        self.board = [[None]]
        self.player = 1
        self.moves = []
        self.order = 0
    
    #===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    #===============================================================================================

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        converted_args = []
        if len(args) < len(template.split(" ")):
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                converted_args.append(int(arg))
            except ValueError:
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                return False
        args = converted_args
        return True

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF PREDEFINED FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV START OF ASSIGNMENT 2 FUNCTIONS. ADD/REMOVE/MODIFY AS NEEDED. VVVVVVVV
    #===============================================================================================

    def game(self, args):
        '''
        Resets a new game for a given n by m board
        '''
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False
        
        self.board = [] #lists of lists which will contain who occupies which space
        for i in range(m):
            self.board.append([None]*n)
        self.player = 1
        return True
    
    def opponent(self):
        '''
        Returns the OPP of the given player
        '''
        assert self.player == 1 or self.player == 2
        return 3 - self.player
    
    def switch_player(self):
        '''
        Switches the current player
        '''
        self.player = self.opponent()

    def show(self, args):
        '''
        Prints the board
        '''
        for row in self.board:
            for x in row:
                if x is None:
                    print(".", end="")
                else:
                    print(x, end="")
            print()
        print(self.board)                    
        return True

    def undo(self, args):
        '''
        Undoes a move and switches the player
        '''
        # print("before")
        # print(self.moves)
        # print(self.board)
        order, player, x, y, num = self.moves.pop()
        self.board[y][x] = None
        self.switch_player()
        self.order -= 1
        # print(self.moves)
        # print(self.board)
        return True

    def is_legal_reason(self, x, y, num):
        '''
        Given an x,y position and digit "num" to play,
        plays the given moves and returns why the move was
        valid or not
        '''
        if self.board[y][x] is not None:
            return False, "occupied"
        #CHECKING COLUMNS
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a col"
            else:
                consecutive = 0
        too_many = count > len(self.board) // 2 + len(self.board) % 2
        #CHECKING ROWS
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        if too_many or count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            print(self.board)
            self.board[y][x] = None
            return False, "overhalf" + str(num)

        self.board[y][x] = None
        return True, ""
    
    def is_legal(self, x, y, num):
        '''
        Given a x,y position on the board and digit "num" to play,
        "plays" the move and then checks the constraints on the rows
        and columns. Makes sure the 3 conseucutive rule and not over half
        in a row/col is not violated.
        '''
        if self.board[y][x] is not None:
            return False
        #CHECKING THE COLUMNS AGAINST THE RULES
        consecutive = 0
        count = 0
        self.board[y][x] = num
        # checks for consecutive rule
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None #resetting board bc not valid
                    return False
            else:
                consecutive = 0
        # checks for the must not occupy half the row
        if count > len(self.board) // 2 + len(self.board) % 2:
            self.board[y][x] = None #resetting board
            return False
        #CHECKING THE ROWS AGAINST THE RULES
        consecutive = 0
        count = 0
        # checks for consecutive rule
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None #resetting board
                    return False
            else:
                consecutive = 0
        # checks for the must not occupy half the column
        if count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None #resetting board bc not valid
            return False 
        #PASSED ALL CHECKS, IS VALID
        self.board[y][x] = None #resetting board
        return True
    
    def valid_move(self, x, y, num):
        '''
        Checks if a move is valid by checking bounds and then checking
        game rule constraints
        '''
        return  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1) and\
                self.is_legal(x, y, num)

    def play(self, args):
        '''
        Given an x,y and binary "num" to play,
        plays the given move, updating the board
        and switching players.
        '''
        err = ""
        if len(args) != 3:
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            print("= illegal move: " + " ".join(args) + " wrong binary num\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal_reason(x, y, num)
        if not legal:
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.moves.append([self.order, "player"+str(self.player), x, y, num])
        self.board[y][x] = num
        self.switch_player()
        self.order += 1
        # self.show(args)
        # print("moves")
        # print(self.moves)
        # print("board by rows")
        # print(self.board)
        return True
    
    def legal(self, args):
        '''
        Checks if given x,y position and player "num"
        to play is a legal (open and not violating) move.
        '''
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            print("yes")
        else:
            print("no")
        return True
    
    def get_legal_moves(self):
        '''
        Returns all legal moves for ALL players
        In list str format [x, y, digit]
        '''
        moves = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                for num in range(2):
                    if self.is_legal(x, y, num):
                        # moves.append([x, y, num])
                        moves.append([str(x), str(y), str(num)]) #was str really necessaRY?
        return moves

    def genmove(self, args):
        '''
        Gets a random possible move, 
        prints "resign" if not possible moves are left
        '''
        moves = self.get_legal_moves()
        if len(moves) == 0:
            print("resign")
        else:
            rand_move = moves[random.randint(0, len(moves)-1)]
            self.play(rand_move)
            print(" ".join(rand_move))
        return True
    
    # CODE GIVEN WINNER FUNCTION
    # def winner(self, args):
    #     '''
    #     Returns either the winning player or prints
    #     "unfinshed" if game is not over
    #     '''
    #     if len(self.get_legal_moves()) == 0:
    #         if self.player == 1:
    #             print(2)
    #         else:
    #             print(1)
    #     else:
    #         print("unfinished")
    #     return True
    
    def is_winner(self, player):
        '''
        Checks if the given player is the winner
        '''
        if len(self.get_legal_moves()) == 0:
            if self.player == player:
                print(self.moves)
                self.show(self)
                return True
            else:
                return False
        else:
            return "not over yet"
    
    def winner(self):
        '''
        Returns who the winner is
        '''
        if self.is_winner(1) == True:
            return 1
        if self.is_winner(2) == True:
            return 2
        return None
    
    def minimax_or(self):
        try:
            assert self.player == 1
            if self.winner() != None:
                return self.is_winner(1)
            for move in self.get_legal_moves():
                # print("minimax_OR move for loop",move)
                self.play(move)
                is_win = self.minimax_and()
                self.undo(self)
                if is_win:
                    return True
            return False
        except Exception as e:
            print("hmmmm it", e)

    def minimax_and(self):
        assert self.player == 2
        if self.winner() != None:
            return self.is_winner(2)
        for move in self.get_legal_moves():
            # print("minimax_AND move for loop",move)
            self.play(move)
            is_loss = self.minimax_or()
            self.undo(self)
            if is_loss:
                return False
        return True
    
    # new function to be implemented for assignment 2
    def timelimit(self, args):
        raise NotImplementedError("This command is not yet implemented.")
        return True
    
    # new function to be implemented for assignment 2
    def solve(self, args):
        try:
            win = False
            start = time.process_time()
            if self.player == 1:
                win = self.minimax_or()
            else:
                win = self.minimax_and()
            timespent = time.process_time() - start
            print("FINAL BOARD GAME")
            self.show(args)
            print(self.moves)
            print(timespent, win)
            return True
        except Exception as e:
            print("AHHHHHHHHHH", e)
    
    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 2 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================
    
if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()