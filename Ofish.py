import chess
import time
from eval import Evaluation

# Global variables for move ordering
killer_moves = [[[None for _ in range(64)] for _ in range(64)] for _ in range(64)]
history_moves = [[0 for _ in range(64)] for _ in range(64)]

# Create an instance of the Evaluation class
evaluator = Evaluation()

# Initialize UCI-related variables
uci_mode = False
position_fen = None
stop_search = False

# Counter for nodes
nodes = 0

# Define bitboards for each piece type and color
PAWN_BOARDS = {'white': 0, 'black': 0}
KNIGHT_BOARDS = {'white': 0, 'black': 0}
BISHOP_BOARDS = {'white': 0, 'black': 0}
ROOK_BOARDS = {'white': 0, 'black': 0}
QUEEN_BOARDS = {'white': 0, 'black': 0}
KING_BOARDS = {'white': 0, 'black': 0}

# Additional global variables
wtime = 0
btime = 0
remainingtime = 0

# Helper function to initialize piece bitboards
def init_bitboards(board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            color = 'white' if piece.color == chess.WHITE else 'black'
            piece_type = piece.piece_type
            mask = 1 << square
            if piece_type == chess.PAWN:
                PAWN_BOARDS[color] |= mask
            elif piece_type == chess.KNIGHT:
                KNIGHT_BOARDS[color] |= mask
            elif piece_type == chess.BISHOP:
                BISHOP_BOARDS[color] |= mask
            elif piece_type == chess.ROOK:
                ROOK_BOARDS[color] |= mask
            elif piece_type == chess.QUEEN:
                QUEEN_BOARDS[color] |= mask
            elif piece_type == chess.KING:
                KING_BOARDS[color] |= mask

# Helper function to update bitboards after a move
def update_bitboards(move, color):
    from_square = move.from_square
    to_square = move.to_square
    mask = ~(1 << from_square)
    if color == 'white':
        PAWN_BOARDS['white'] = (PAWN_BOARDS['white'] & mask) | (1 << to_square)
        KNIGHT_BOARDS['white'] = (KNIGHT_BOARDS['white'] & mask) | (1 << to_square)
        BISHOP_BOARDS['white'] = (BISHOP_BOARDS['white'] & mask) | (1 << to_square)
        ROOK_BOARDS['white'] = (ROOK_BOARDS['white'] & mask) | (1 << to_square)
        QUEEN_BOARDS['white'] = (QUEEN_BOARDS['white'] & mask) | (1 << to_square)
        KING_BOARDS['white'] = (KING_BOARDS['white'] & mask) | (1 << to_square)
    else:
        PAWN_BOARDS['black'] = (PAWN_BOARDS['black'] & mask) | (1 << to_square)
        KNIGHT_BOARDS['black'] = (KNIGHT_BOARDS['black'] & mask) | (1 << to_square)
        BISHOP_BOARDS['black'] = (BISHOP_BOARDS['black'] & mask) | (1 << to_square)
        ROOK_BOARDS['black'] = (ROOK_BOARDS['black'] & mask) | (1 << to_square)
        QUEEN_BOARDS['black'] = (QUEEN_BOARDS['black'] & mask) | (1 << to_square)
        KING_BOARDS['black'] = (KING_BOARDS['black'] & mask) | (1 << to_square)

def mvvlva(move, color):
    piece_value = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 1000}
    captured_square = move.to_square
    attacker_square = move.from_square

    if not (PAWN_BOARDS[color] & (1 << captured_square)) or not (PAWN_BOARDS[color] & (1 << attacker_square)):
        return 0

    captured_type = chess.PieceType(chess.PAWN)
    attacker_type = chess.PieceType(chess.PAWN)

    return piece_value[chess.piece_symbol(captured_type).lower()] - piece_value[chess.piece_symbol(attacker_type).lower()]

def quiescence(board, alpha, beta, color, depth):
    if depth == 0:
        return evaluator.evaluate_board(board) if color == 'white' else -evaluator.evaluate_board(board)

    stand_pat = evaluator.evaluate_board(board) if color == 'white' else -evaluator.evaluate_board(board)

    if stand_pat >= beta:
        return beta

    if alpha < stand_pat:
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            board.push(move)
            update_bitboards(move, color)
            score = -quiescence(board, -beta, -alpha, 'white' if color == 'black' else 'black', depth - 1)
            board.pop()
            update_bitboards(move, color)

            if score >= beta:
                return beta

            if score > alpha:
                alpha = score

    return alpha

def negamax(board, depth, alpha, beta, color, move_num):
    global nodes

    if depth == 0 or board.is_game_over():
        nodes += 1
        return quiescence(board, alpha, beta, color, 2)  # Limit the quiescence search depth

    # Null move pruning
    null_move_pruning = True
    if null_move_pruning and not board.is_check() and depth >= 3:
        board.push(chess.Move.null())
        eval = -negamax(board, depth - 3, -beta, -beta + 1, 'white' if color == 'black' else 'black', move_num + 1)
        board.pop()

        if eval >= beta:
            return eval  # Null move cutoff

    max_eval = float('-inf')
    legal_moves = list(board.legal_moves)

    # Sort moves based on MVVLVA score
    legal_moves.sort(key=lambda move: mvvlva(move, color), reverse=True)

    best_move = None  # Store the best move
    for move in legal_moves:
        board.push(move)
        update_bitboards(move, color)
        eval = -negamax(board, depth - 1, -beta, -alpha, 'white' if color == 'black' else 'black', move_num + 1)
        board.pop()
        update_bitboards(move, color)

        if eval > max_eval:
            max_eval = eval
            best_move = move

        alpha = max(alpha, eval)

        if alpha >= beta:
            # Update killer moves and history moves
            killer_moves[depth][move.from_square][move.to_square] = move
            history_moves[move.from_square][move.to_square] += depth
            break

    # Aspiration Window: Re-search with a narrower window if necessary
    if alpha < max_eval < beta and best_move is not None:
        # Adjust the window based on the current evaluation
        new_alpha = max(alpha, max_eval - 20)  # Adjust the lower bound
        new_beta = min(beta, max_eval + 20)  # Adjust the upper bound

        # Re-search with the narrowed window
        eval = -negamax(board, depth - 1, -new_beta, -new_alpha, 'white' if color == 'black' else 'black', move_num + 1)

        if eval > max_eval:
            max_eval = eval

    return max_eval

def get_best_move(board, depth, alpha, beta):
    global nodes, stop_search  # Add stop_search

    nodes = 0  # Reset nodes at the beginning of the function
    stop_search = False  # Reset stop_search at the beginning of the function

    best_move = None
    max_eval = float('-inf')
    legal_moves = list(board.legal_moves)
    color = 'white' if board.turn == chess.WHITE else 'black'

    for move_num, move in enumerate(legal_moves):
        if stop_search:  # Check if we should stop the search
            break

        board_copy = board.copy()
        board_copy.push(move)
        if board_copy.is_checkmate():
            best_move = move
            break
        else:
            board.push(move)
            update_bitboards(move, color)
            eval = -negamax(board, depth - 1, -beta, -alpha, 'white' if color == 'black' else 'black', move_num + 1)
            board.pop()
            update_bitboards(move, color)
            if eval > max_eval:
                max_eval = eval
                best_move = move
                alpha = max(alpha, eval)

    return best_move, max_eval


def calculateMaxTime(board, remaining_time):
    if board.fullmove_number < 15:
        return remaining_time / 50
    elif board.fullmove_number < 30:
        return remaining_time / 40
    else:
        return remaining_time / 45

def calculateMaxDepth(board):
    if board.fullmove_number < 15:
        return 3
    elif board.fullmove_number < 30:
        return 3
    else:
        return 3

def uci_loop():
    global uci_mode, position_fen, stop_search, nodes, wtime, btime, remainingtime

    while True:
        input_line = input()
        if input_line == "uci":
            print("id name AspirationFish")
            print("id author Chess123easy")
            # Include any additional information about your engine
            print("uciok")
            uci_mode = True
        elif input_line == "isready":
            print("readyok")
        elif input_line.startswith("position"):
            parts = input_line.split()
            if len(parts) < 2:
                continue
            position_type = parts[1]
            if position_type == "startpos":
                board.set_fen(chess.STARTING_FEN)
                init_bitboards(board)
                if len(parts) > 2 and parts[2] == "moves":
                    for move in parts[3:]:
                        board.push_uci(move)
                        update_bitboards(chess.Move.from_uci(move), 'white' if board.turn == chess.WHITE else 'black')
            elif position_type == "fen":
                if len(parts) < 8:
                    continue
                fen = " ".join(parts[2:8])
                board.set_fen(fen)
                init_bitboards(board)
                if len(parts) > 8 and parts[8] == "moves":
                    for move in parts[9:]:
                        board.push_uci(move)
                        update_bitboards(chess.Move.from_uci(move), 'white' if board.turn == chess.WHITE else 'black')
            position_fen = board.fen()
        elif input_line.startswith("go"):
            if not uci_mode:
                continue

            stop_search = False
            nodes = 0

            # Parse additional parameters for search
            parameters = input_line.split()[1:]
            max_time = float('inf')  # Set a default maximum time
            max_depth = float('inf')  # Set a default maximum depth
            wtime = float('inf')  # White's remaining time
            btime = float('inf')  # Black's remaining time

            for i in range(len(parameters)):
                if parameters[i] == "depth" and i + 1 < len(parameters):
                    max_depth = int(parameters[i + 1])
                elif parameters[i] == "movetime" and i + 1 < len(parameters):
                    max_time = float(parameters[i + 1])
                elif parameters[i] == "wtime" and i + 1 < len(parameters):
                    wtime = float(parameters[i + 1])
                elif parameters[i] == "btime" and i + 1 < len(parameters):
                    btime = float(parameters[i + 1])

            remainingtime = wtime / 1000 if board.turn == chess.WHITE else btime / 1000

            start_time = time.time()  # Start the timer
            depth = 1  # Start with depth 1

            while depth <= calculateMaxDepth(board):
                # Get the best move and score from the existing negamax search
                best_move, score = get_best_move(board, depth, alpha=float('-inf'), beta=float('inf'))

                # Check if the maximum time has been exceeded
                elapsed_time = time.time() - start_time
                if elapsed_time > calculateMaxTime(board, remainingtime):
                    break

                # Replace infinite scores with 99999 and -99999
                if score == float('inf'):
                    score = 99999
                elif score == float('-inf'):
                    score = -99999

                # Output the current search information
                nodes_per_second = int(nodes / elapsed_time)
                print(f"info score cp {score} depth {depth} nodes {nodes} nodespersec {nodes_per_second} wtime {wtime} btime {btime}")

                # Increase the search depth for the next iteration
                depth += 1

            # Output the final result
            print("bestmove", best_move.uci())

        elif input_line == "quit":
            break

if __name__ == "__main__":
    board = chess.Board()
    uci_loop()
