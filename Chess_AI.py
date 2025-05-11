import random
import Chess_engine

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

def findRandomMoves(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves)-1)]
    return None

def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.white_to_move else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
        
        for opponentMove in opponentMoves:
            gs.makeMove(opponentMove)
            gs.getValidMoves()
            if gs.checkmate:
                score = CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
                
            gs.undoMove()
            
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    
    return bestPlayerMove

# def findBestMove(gs, validMoves): # Minimax algorithm
#     turnMultiplier = 1 if gs.white_to_move else -1
#     maxScore = -CHECKMATE
#     bestMove = None
#     for playerMove in validMoves:
#         gs.makeMove(playerMove)
#         if gs.checkmate:
#             score = CHECKMATE
#         elif gs.stalemate:
#             score = STALEMATE
#         else:
#             score = scoreMaterial(gs.board) * turnMultiplier
#         if score > maxScore:
#             maxScore = score
#             bestMove = playerMove
#         gs.undoMove()
#     return bestMove

#phương thức để gọi đệ quy lần đầu tiên
def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.white_to_move)

    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    if depth == 0:
        return None  # Ở độ sâu 0, không cần trả về nước đi

    if whiteToMove:
        maxScore = -CHECKMATE
        bestMove = None
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            nextMove = findMoveMinMax(gs, nextMoves, depth - 1, False)
            score = scoreMaterial(gs.board)
            gs.undoMove()

            if score > maxScore:
                maxScore = score
                bestMove = move
        return bestMove
    else:
        minScore = CHECKMATE
        bestMove = None
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            nextMove = findMoveMinMax(gs, nextMoves, depth - 1, True)
            score = scoreMaterial(gs.board)
            gs.undoMove()

            if score < minScore:
                minScore = score
                bestMove = move
        return bestMove

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score

# Positive score is good for white and negative score is good for black
def scoreBoard(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE #black win
        else:
            return CHECKMATE #white win
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score