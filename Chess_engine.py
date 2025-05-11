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
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks, 
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]
        self.en_passant_possible = ()  # tọa độ ô có thể en passant
        self.en_passant_log = [self.en_passant_possible]

    def makeMove(self, move):
        if self.checkmate:  # If in checkmate, don't allow any moves
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

        # Check if king is captured (checkmate)
        if move.pieceCaptured == "wK":
            self.checkmate = True
            self.white_to_move = True  # Set back to white's turn to show black wins
        elif move.pieceCaptured == "bK":
            self.checkmate = True
            self.white_to_move = False  # Set back to black's turn to show white wins
            
        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]  # moves the rook
                self.board[move.endRow][move.endCol+1] = "--"  # erase old rook
            else:  # queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]  # moves the rook
                self.board[move.endRow][move.endCol-2] = "--"  # erase old rook
                
        # en passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        # en passant move
        #if hasattr(move, "isEnpassantMove") and move.isEnpassantMove:
        #    self.board[move.startRow][move.endCol] = "--"  # bắt tốt

        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.en_passant_possible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.en_passant_possible = ()

        self.en_passant_log.append(self.en_passant_possible)

        # update castling rights
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs))
        
        #pawn promotion
        if move.isPawnPromotion:
            # Chỉ phong cấp nếu là tốt và đi đến hàng cuối
            if (move.pieceMoved == "wP" and move.endRow == 0) or (move.pieceMoved == "bP" and move.endRow == 7):
                promoted_piece = move.promoteTo if hasattr(move, "promoteTo") and move.promoteTo else ("wQ" if self.white_to_move else "bQ")
                self.board[move.endRow][move.endCol] = promoted_piece

    # Undo the last move
    def undoMove(self):
        """
        Undo the last move
        """
        if len(self.move_log) != 0:  # make sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.white_to_move = not self.white_to_move  # swap players
            
            # update the king's position if needed
            if move.pieceMoved == "wK":
                self.white_king_location = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.black_king_location = (move.startRow, move.startCol)
            
            # undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # restore captured pawn
            
            # undo pawn promotion
            if move.isPawnPromotion:
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # restore original pawn
            
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king-side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queen-side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            
            # restore en passant possible
            self.en_passant_log.pop()
            self.en_passant_possible = self.en_passant_log[-1]
            
            # restore castling rights
            self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]
            
            # reset checkmate and stalemate
            self.checkmate = False
            self.stalemate = False

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
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.white_to_move:
            kingRow = self.white_king_location[0]
            kingCol = self.white_king_location[1]
        else:
            kingRow = self.black_king_location[0]
            kingCol = self.black_king_location[1]

        if self.inCheck:
            if len(self.checks) == 1:  # chỉ 1 quân chiếu -> chặn hoặc di chuyển vua
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # các ô có thể di chuyển tới

                if pieceChecking[1] == "N":  # nếu bị mã chiếu -> phải bắt mã hoặc di chuyển vua
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i,
                                       kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                # xóa các nước đi không chặn được chiếu hoặc di chuyển vua
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":  # không phải di chuyển vua
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # bị chiếu kép -> phải di chuyển vua
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # không bị chiếu -> tất cả nước đi đều hợp lệ
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        if self.white_to_move:
            self.getCastleMoves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)

        return moves

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

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == start_row and self.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, isEnpassantMove=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, isEnpassantMove=True))

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
        knightMoves = ((-2,1),(-2,-1),(-1,-2),(1,-2),(1,2),(2,1),(2,-1),(-1,2))
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
        inCheck = False

        # Xác định màu quân và vị trí vua
        if self.white_to_move:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.white_king_location[0]
            startCol = self.white_king_location[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.black_king_location[0]
            startCol = self.black_king_location[1]

        # Kiểm tra theo 8 hướng từ vua
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),  # ngang và dọc
                      (-1, -1), (-1, 1), (1, -1), (1, 1))  # chéo

        for j, direction in enumerate(directions):
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i

                if not (0 <= endRow <= 7 and 0 <= endCol <= 7):
                    break  # ngoài bàn cờ

                endPiece = self.board[endRow][endCol]

                if endPiece[0] == allyColor and endPiece[1] != "K":
                    if possiblePin == ():  # quân đồng minh đầu tiên - có thể bị ghim
                        possiblePin = (endRow, endCol, direction[0], direction[1])
                    else:  # quân đồng minh thứ hai - không thể có ghim từ hướng này
                        break

                elif endPiece[0] == enemyColor:
                    enemyType = endPiece[1]
                    # Kiểm tra từng loại quân có thể tạo ghim hoặc chiếu
                    isValidThreat = (
                        # Xe có thể ghim/chiếu theo hướng ngang dọc
                            (0 <= j <= 3 and enemyType == "R") or
                            # Tượng có thể ghim/chiếu theo đường chéo
                            (4 <= j <= 7 and enemyType == "B") or
                            # Tốt có thể chiếu trong khoảng cách 1 theo đường chéo
                            (i == 1 and enemyType == "P" and (
                                    (enemyColor == "w" and 6 <= j <= 7) or
                                    (enemyColor == "b" and 4 <= j <= 5))) or
                            # Hậu có thể ghim/chiếu theo mọi hướng
                            (enemyType == "Q") or
                            # Vua có thể chiếu trong khoảng cách 1 theo mọi hướng
                            (i == 1 and enemyType == "K")
                    )

                    if isValidThreat:
                        if possiblePin == ():  # không có quân chắn -> chiếu
                            inCheck = True
                            checks.append((endRow, endCol, direction[0], direction[1]))
                            break
                        else:  # có quân chắn -> ghim
                            pins.append(possiblePin)
                            break
                    else:  # quân địch không thể tạo ghim/chiếu
                        break

        # Kiểm tra chiếu bởi mã
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2),
                       (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))

        return inCheck, pins, checks

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

    def __init__(self, start_square, end_square, board, isCastleMove=False, isEnpassantMove=False, promoteTo=None):
        self.startRow = start_square[0]
        self.startCol = start_square[1]
        self.endRow = end_square[0]
        self.endCol = end_square[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # castle move
        self.isCastleMove = isCastleMove
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "bP" if self.pieceMoved == "wP" else "wP"
        # pawn promotion
        self.promoteTo = promoteTo

        self.isCapture = (self.pieceCaptured != "--")
    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return (
                self.moveID == other.moveID
            )
        return False

    def getChessNotation(self):
        #return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        if self.isPawnPromotion:
            return self.getRankFile(self.endRow, self.endCol) + "Q"
        if self.isCastleMove:
            if self.endCol == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.isEnpassantMove:
            return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow,
                                                                                                self.endCol) + " e.p."
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow,
                                                                                                    self.endCol)
            else:
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        else:
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] +self.rowsToRanks[r]

    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"

        end_square = self.getRankFile(self.endRow, self.endCol)

        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + end_square
            else:
                return end_square + "Q" if self.isPawnPromotion else end_square

        move_string = self.pieceMoved[1]
        if self.isCapture:
            move_string += "x"
        return move_string + end_square

