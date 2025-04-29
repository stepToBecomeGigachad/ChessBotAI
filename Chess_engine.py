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
        self.in_check = False
        self.pins = []
        self.checks = []
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks, 
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    def makeMove(self, move):
        if self.checkMate:  # If in checkmate, don't allow any moves
            return False
            
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        
        # update king's location
        if move.pieceMoved == "wK":
            self.white_king_location = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.black_king_location = (move.endRow, move.endCol)
            
        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]  # moves the rook
                self.board[move.endRow][move.endCol+1] = "--"  # erase old rook
            else:  # queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]  # moves the rook
                self.board[move.endRow][move.endCol-2] = "--"  # erase old rook
                
        # update castling rights
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs))
        return True

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
        # undo castling rights
        self.castle_rights_log.pop()
        self.current_castling_rights = self.castle_rights_log[-1]

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.pieceMoved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.current_castling_rights.wqs = False
                elif move.startCol == 7: # right rook
                    self.current_castling_rights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.current_castling_rights.bqs = False
                elif move.startCol == 7: # right rook
                    self.current_castling_rights.bks = False
                    

    # All moves considering checks
    def getValidMoves(self):
        """
        All moves considering checks.
        """
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        # advanced algorithm
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllPossibleMoves()
            if self.white_to_move:
                self.getCastleMoves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

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
        # Get all possible moves for the opponent
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    if piece != 'K':  # Skip king moves to avoid recursion
                        self.moveFunctions[piece](row, col, moves)
        self.white_to_move = not self.white_to_move  # switch turn back
        for move in moves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False
    
    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of cols in given row
                turn = self.board[r][c][0]
                if(turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # calls the appropriate move function base on piece type
        return moves

    def getPawnMoves(self, row, col, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.black_king_location

        if 0 <= row + move_amount <= 7 and self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == start_row and 0 <= row + 2 * move_amount <= 7 and self.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))

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

    def getKingMoves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if move is on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)
        self.getCastleMoves(row, col, moves)
    '''
    get all valid castle moves for the king (r,c) and add them to the list of moves
    '''
    def getCastleMoves(self, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if self.squaredUnderAttack(row, col):
            return  # can't castle while in check
            
        if (self.white_to_move and self.current_castling_rights.wks) or (
                not self.white_to_move and self.current_castling_rights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (
                not self.white_to_move and self.current_castling_rights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        """
        Generate all valid kingside castle moves for the king at (row, col) and add them to the list of moves.
        """
        # Check if squares between king and rook are empty
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            # Check if squares are not under attack
            if not self.squaredUnderAttack(row, col + 1) and not self.squaredUnderAttack(row, col + 2):
                # Check if rook is still in its original position
                if (self.white_to_move and self.board[row][col + 3] == "wR") or (
                        not self.white_to_move and self.board[row][col + 3] == "bR"):
                    moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, col, moves):
        """
        Generate all valid queenside castle moves for the king at (row, col) and add them to the list of moves.
        """
        # Check if squares between king and rook are empty
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--":
            # Check if squares are not under attack
            if not self.squaredUnderAttack(row, col - 1) and not self.squaredUnderAttack(row, col - 2):
                # Check if rook is still in its original position
                if (self.white_to_move and self.board[row][col - 4] == "wR") or (
                        not self.white_to_move and self.board[row][col - 4] == "bR"):
                    moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
        

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

    def __init__(self, start_square, end_square,board, isCastleMove=False):
        self.startRow = start_square[0]
        self.startCol = start_square[1]
        self.endRow = end_square[0]
        self.endCol = end_square[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # castle move
        self.isCastleMove = isCastleMove

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


