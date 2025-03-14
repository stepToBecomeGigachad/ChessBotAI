# This class is responsible for storing all the information about the current state of a chess game. It will also be responsible for determining the valid moves at the current states. It will also keep a move log

class GameState():
    def __init__(self):
        # Board is a 8x8 each element of the list has 2 characters
        # The first character represent the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', or 'P'
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--",],
            ["--", "--", "--", "--", "--", "--", "--", "--",],
            ["--", "--", "--", "--", "--", "--", "--", "--",],
            ["--", "--", "--", "--", "--", "--", "--", "--",],
            ["wP" ,"wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions= {'P': self.getPawnMoves, 'R': self.getRockMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.pieceMoved == "wK":
            self.white_king_location = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.black_king_location = (move.endRow, move.endCol)

    # Undo the last move
    def undoMove(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.white_to_move = not self.white_to_move #switch turns back
            # update the king's position needed
            if move.pieceMoved == "wK":
                self.white_king_location = (move.startRow, move.startRow)
            elif move.pieceMoved == "bK":
                self.black_king_location = (move.startRow, move.startRow)

    # All moves considering checks

    def getValidMoves(self):
        # 1.) generate all possible moves
        moves = self.getAllPosibleMoves()
        # 2.) for each move , make the move
        for i in range(len(moves) - 1, -1, -1):  # when removing from a list go backwards through that list
            self.makeMove(moves[i])
            # 3.) generate all opponent's moves
            # 4.) for each of your opponent's moves, see if they attack your king
            self.white_to_move = not self.white_to_move
            if self.inCheck():
                moves.remove(moves[i])  # 5.) if they do attack your king, not a valid move
            self.white_to_move = not self.white_to_move
            self.undoMove()
        # print("Valid moves: ", [move.getChessNotation() for move in moves])  # Debug
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
                print("Checkmate")
            else:
                self.staleMate = True
                print("Stalemate")
        else:
            self.checkMate = False
            self.staleMate = False

        return moves
        
     # Determine if the current player is in check
    def inCheck(self):

        if self.white_to_move:
            return self.squaredUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.squaredUnderAttack(self.black_king_location[0], self.black_king_location[1])

    # Determine if the enemy can attack the square r,c
    def squaredUnderAttack(self, r, c):
        self.white_to_move = not self.white_to_move  # switch to opponent's move
        oopMoves = self.getAllPosibleMoves()
        self.white_to_move = not self.white_to_move  # switch turn back
        for move in oopMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False
    
    # All moves without considering checks
    def getAllPosibleMoves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of cols in given row
                turn = self.board[r][c][0]
                if(turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # calls the appropriate move function base on piece type
        return moves

    def getPawnMoves(self,r,c,moves):
        if self.white_to_move:
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move((r,c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advencd
                    moves.append(Move((r,c), (r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b': #opponent piece capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: #capture to the right
                if self.board[r-1][c+1][0] == 'b': #opponent piece capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else: #black pawn moves
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advencd
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # capture to left
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':  # opponent piece capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # capture to the right
                if self.board[r + 1][c + 1][0] == 'w':  # opponent piece capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
     

    def getRockMoves(self,r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1)) # up, down ,left, right
        enemyColor = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c +d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol <8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--': # empty space valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor: #enemy piece valid
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else: #friendly piece valid
                        break
                else: #off board
                    break

    def getBishopMoves(self,r,c,moves):
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8): # Bishop can move maximum 7 squares
                endRow = r + d[0] * i
                endCol = c +d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2,1),(-2,-1),(-1,-2),(1,-2),(1,2),(2,1),(2,-1),(1,2))
        allyColor = 'w' if self.white_to_move else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r,c,moves)
        self.getRockMoves(r,c,moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyColor = 'w' if self.white_to_move else 'b'
        for m in kingMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece (empty or enemy piece)
                    moves.append(Move((r,c),(endRow,endCol),self.board))

class Move():
    # maps key to values
    # key: value
    ranksToRows = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }
    rowsToRanks= {
        v:k for k, v in ranksToRows.items()
    }
    filesToCols = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
    }
    colsToFiles ={v: k for k, v in filesToCols.items()}

    def __init__(self, start_square, end_square,board):
        self.startRow = start_square[0]
        self.startCol = start_square[1]
        self.endRow = end_square[0]
        self.endCol = end_square[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return (
                self.moveID == other.moveID
            )
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] +self.rowsToRanks[r]


