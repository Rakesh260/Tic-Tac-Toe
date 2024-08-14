
from django.shortcuts import render, redirect
from .models import Player, Game, Leaderboard
import random


def index(request):
    if request.method == "POST":
        name = request.POST.get('name')
        player, created = Player.objects.get_or_create(name=name)
        return redirect('play', player_id=player.id)
    return render(request, 'index.html')


def play(request, player_id):
    player = Player.objects.get(id=player_id)
    level = None
    result = None
    winning_board_indices = []
    csrf_token = request.COOKIES.get('csrftoken')
    if request.method == "POST":
        board = request.POST.get('board')
        move = int(request.POST.get('move'))
        level = request.POST.get('level')
        board = board[:move] + "X" + board[move + 1:]
        result, winning_board_indices = check_winner(board)
        if result == "X":
            result = "win"
        elif result == "draw":
            result = "draw"
        else:
            ai_index = ai_move(board, level)
            if ai_index is not None:
                board = board[:ai_index] + "O" + board[ai_index + 1:]

            result, winning_board_indices = check_winner(board)
            if result == "O":
                result = "loss"
            elif result == "draw":
                result = "draw"
            else:
                result = "ongoing"

        cells = [{'index': i, 'value': board[i]} for i in range(9)]
        rows = [cells[i * 3:(i + 1) * 3] for i in range(3)]

        context = {
            'player': player,
            'result': result,
            'board': board,
            'rows': rows,
            'range': range(3),
            'is_game_ongoing': result == "ongoing",
            'winning_board_indices': winning_board_indices
        }
        if result != "ongoing":
            Game.objects.create(player=player, board=board, status=result)
            update_leaderboard(player, result)
            return render(request, 'board.html', context)
    else:
        board = " " * 9
    cells = [{'index': i, 'value': board[i]} for i in range(9)]
    rows = [cells[i * 3:(i + 1) * 3] for i in range(3)]
    context = {
        'player': player,
        'board': board,
        'rows': rows,
        'level': level,
        'is_game_ongoing': result,
        'csrfmiddlewaretoken': csrf_token,
        'result': result,
        'winning_board_indices': winning_board_indices,
    }

    return render(request, 'board.html', context)


def leaderboard(request, player_id=None):
    leaders = Leaderboard.objects.all().order_by('-wins')[:10]
    return render(request, 'leaderboard.html', {'leaders': leaders, 'player_id': player_id})


def update_leaderboard(player, result):
    leaderboard, created = Leaderboard.objects.get_or_create(player=player)
    if result == 'win':
        leaderboard.wins += 1
    elif result == 'loss':
        leaderboard.losses += 1
    elif result == 'draw':
        leaderboard.draws += 1
    leaderboard.save()


def check_winner(board):
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    winning_board_indices = []
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] and board[a] != " ":
            winning_board_indices.extend([a, b, c])
            return board[a], winning_board_indices
    if " " not in board:
        return "draw", []
    return "ongoing", []


def minimax(board, is_maximizing):
    winner, winning_board_indices = check_winner(board)
    if winner == "X":
        return -10
    elif winner == "O":
        return 10
    elif winner == "draw":
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == " ":
                board = board[:i] + "O" + board[i+1:]
                score = minimax(board, False)
                board = board[:i] + " " + board[i+1:]
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == " ":
                board = board[:i] + "X" + board[i+1:]
                score = minimax(board, True)
                board = board[:i] + " " + board[i+1:]
                best_score = min(score, best_score)
        return best_score


def best_move(board):
    best_score = -float('inf')
    move = -1
    for i in range(9):
        if board[i] == " ":
            board = board[:i] + "O" + board[i+1:]
            score = minimax(board, False)
            board = board[:i] + " " + board[i+1:]
            if score > best_score:
                best_score = score
                move = i
    return move


def ai_move(board, level, optimal_percentage=0.6):
    if level == 'easy':
        return random_move(board)
    elif level == 'medium':
        val = random.random()
        if val < optimal_percentage:
            return best_move(board)
        else:
            return random_move(board)
    else:
        return best_move(board)


def random_move(board):
    available_moves = [i for i in range(9) if board[i] == " "]
    return random.choice(available_moves) if available_moves else None

