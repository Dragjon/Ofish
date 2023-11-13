# Improved Eval
import chess
import time

class Evaluation:
    def evaluate_board(self, board):
        piece_values_midgame = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 320,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }

        mg_pawn_table = [
            0,   0,   0,   0,   0,   0,   0,   0,
            50,  50,  50,  50,  50,  50,  50,  50,
            10,  10,  20,  30,  30,  20,  10,  10,
            5,   5,  10,  25,  25,  10,   5,   5,
            0,   0,   0,  20,  20,   0,   0,   0,
            5,  -5, -10,   0,   0, -10,  -5,   5,
            5,  10,  10, -20, -20,  10,  10,   5,
            0,   0,   0,   0,   0,   0,   0,   0
        ]

        eg_pawn_table = [
            0,   0,   0,   0,   0,   0,   0,   0,
            80,  80,  80,  80,  80,  80,  80,  80,
            50,  50,  50,  50,  50,  50,  50,  50,
            30,  30,  30,  30,  30,  30,  30,  30,
            20,  20,  20,  20,  20,  20,  20,  20,
            10,  10,  10,  10,  10,  10,  10,  10,
            10,  10,  10,  10,  10,  10,  10,  10,
            0,   0,   0,   0,   0,   0,   0,   0
        ]

        mg_knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50,
        ]

        mg_bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,
        ]

        mg_rook_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]

        mg_queen_table = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]

        mg_king_table = [
            -80, -70, -70, -70, -70, -70, -70, -80, 
            -60, -60, -60, -60, -60, -60, -60, -60, 
            -40, -50, -50, -60, -60, -50, -50, -40, 
            -30, -40, -40, -50, -50, -40, -40, -30, 
            -20, -30, -30, -40, -40, -30, -30, -20, 
            -10, -20, -20, -20, -20, -20, -20, -10, 
            20, 20, -5, -5, -5, -5, 20, 20, 
            20, 30, 10, 0, 0, 10, 30, 20
        ]

        eg_king_table = [
            -20, -10, -10, -10, -10, -10, -10, -20, 
            -5, 0, 5, 5, 5, 5, 0, -5,
            -10, -5, 20, 30, 30, 20, -5, -10, 
            -15, -10, 35, 45, 45, 35, -10, -15, 
            -20, -15, 30, 40, 40, 30, -15, -20, 
            -25, -20, 20, 25, 25, 20, -20, -25, 
            -30, -25, 0, 0, 0, 0, -25, -30, 
            -50, -30, -30, -30, -30, -30, -30, -50
        ]

        if board.is_checkmate():
            return -10000 if board.turn == chess.WHITE else 10000
        elif any([
            board.can_claim_draw(),
            board.can_claim_fifty_moves(),
            board.is_stalemate(),
            board.can_claim_threefold_repetition(),
            board.is_insufficient_material()
        ]):
            return 0

        num_pieces = len(board.piece_map())

        piece_values = piece_values_midgame
        knight_square_table = mg_knight_table
        bishop_square_table = mg_bishop_table
        rook_square_table = mg_rook_table
        queen_square_table = mg_queen_table

        pawn_square_table = eg_pawn_table if num_pieces <= 15 else mg_pawn_table
        king_square_table = eg_king_table if num_pieces <= 15 else mg_king_table

        score = 0
        for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece is not None:
                    if piece.color == chess.WHITE:
        
                        if piece.piece_type == chess.PAWN:
                            score += pawn_square_table[chess.square_mirror(square)]
                        if piece.piece_type == chess.KNIGHT:
                            score += knight_square_table[chess.square_mirror(square)]
                        if piece.piece_type == chess.BISHOP:
                            score += bishop_square_table[chess.square_mirror(square)]
                        if piece.piece_type == chess.ROOK:
                            score += rook_square_table[chess.square_mirror(square)]
                        if piece.piece_type == chess.QUEEN:
                            score += queen_square_table[chess.square_mirror(square)]
                        if piece.piece_type == chess.KING:
                            score += king_square_table[chess.square_mirror(square)]
                        score += piece_values[piece.piece_type]
                    else:
        
                        if piece.piece_type == chess.PAWN:
                            score -= pawn_square_table[square]
                        if piece.piece_type == chess.KNIGHT:
                            score -= knight_square_table[square]
                        if piece.piece_type == chess.BISHOP:
                            score -= bishop_square_table[square]
                        if piece.piece_type == chess.ROOK:
                            score -= rook_square_table[square]
                        if piece.piece_type == chess.QUEEN:
                            score -= queen_square_table[square]
                        if piece.piece_type == chess.KING:
                            score -= king_square_table[square]
                        score -= piece_values[piece.piece_type]

        return score
