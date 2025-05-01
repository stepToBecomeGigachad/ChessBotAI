import random




def findRandomMoves(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves)-1)]
    return None

def findBestMove():
    return