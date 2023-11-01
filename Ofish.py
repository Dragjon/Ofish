# Requires eval.py with class Evaluation
import chess
import time
from eval import Evaluation

# Global variables for move ordering
killer_moves = [[[None for _ in range(64)] for _ in range(64)] for _ in range(64)]
history_moves = [[0 for _ in range(64)] for _ in range(64)]

# Global variable for transposition table
transposition_table = {}

def negamax(board, depth, alpha, beta, color):
    if depth == 0 or board.is_game_over():
        eval = evaluator.evaluate_board(board)
        return eval

    max_eval = float('-inf')
    legal_moves = list(board.legal_moves)

    # Sort moves based on move ordering heuristics
    legal_moves.sort(key=lambda move: history_moves[move.from_square][move.to_square], reverse=True)

    for move in legal_moves:
        board.push(move)
        eval = -negamax(board, depth - 1, -beta, -alpha, not color)
        board.pop()

        if eval > max_eval:
            max_eval = eval

        alpha = max(alpha, eval)

        if alpha >= beta:
            # Update killer moves and history moves
            killer_moves[depth][move.from_square][move.to_square] = move
            history_moves[move.from_square][move.to_square] += depth
            break

    return max_eval

def get_best_move(board, depth, alpha, beta, color):
    best_move = None
    max_eval = float('-inf')
    legal_moves = list(board.legal_moves)

    for move in legal_moves:
        board.push(move)
        eval = -negamax(board, depth - 1, -beta, -alpha, -color)
        board.pop()
        if eval > max_eval:
            max_eval = eval
            best_move = move
            alpha = max(alpha, eval)

    print("Current best evaluation:", max_eval)  # Print the current best evaluation
    return best_move

def display_board(board):
    print(board)

def play_chess():
    board = chess.Board()
    print('\n')
    print(r"""
   ___  __ _     _     
  /___\/ _(_)___| |__  
 //  // |_| / __| '_ \ 
/ \_//|  _| \__ \ | | |
\___/ |_| |_|___/_| |_|
  
A chess playing bot
                    
        """)
    print("Choose your color (w or b):")
    user_color = input()
    
    # Ask the user for the depth (1-5)
    while True:
        try:
            depth = int(input("Choose AI depth (1-5): "))
            if depth < 1 or depth > 5:
                raise ValueError
            break
        except ValueError:
            print("Invalid depth. Please choose a value between 1 and 5.")
    
    while not board.is_game_over():
        display_board(board)
        if (user_color == "w" and board.turn == chess.WHITE) or (user_color == "b" and board.turn == chess.BLACK):
            print(" ")
            print(">>")
            move = input("Enter your move: ")
            try:
                move = board.parse_san(move)
                if move not in board.legal_moves:
                    raise ValueError
            except:
                print("Invalid move! Try again.")
                continue

        if (user_color == "white" and board.turn == chess.BLACK):
            move = get_best_move(board, depth, alpha=float('-inf'), beta=float('inf'), color=-1)
            print("AI's move:", move)

        if (user_color == "black" and board.turn == chess.WHITE):
            move = get_best_move(board, depth, alpha=float('-inf'), beta=float('inf'), color=1)
            print("AI's move:", move)

        board.push(move)

    display_board(board)
    result = board.result()
    if result == "1-0":
        if user_color == "white":
            print("You win!")
        else:
            print("AI wins!")
    elif result == "0-1":
        if user_color == "white":
            print("AI wins!")
        else:
            print("You win!")
    else:
        print("It's a draw!")


# Create an instance of the Evaluation class
evaluator = Evaluation()

# Call the play_chess function to start the game
play_chess()
