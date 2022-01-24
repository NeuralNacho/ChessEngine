from collections import deque

import board as b


class Node:
    def __init__(self, position, evaluation=0):  # default argument 'None'
        self.evaluation = evaluation
        self.children = []
        self.position = position
        self.player_turn = b.find_colour(position)[0]

    def add_child(self, node):
        self.children.append(node)


def find_starting_squares(position):
    # this function should efficiently find rows and columns of all pieces of the side to move
    len_fen_pieces = b.find_colour(position)[2] - 1
    player_turn = b.find_colour(position)[0]
    starting_squares = []
    if player_turn == 'w':
        white_turn = True
    else:
        white_turn = False
    r, c = 0, 0
    for x in range(len_fen_pieces):
        y = position[x]
        if y.isdigit():
            c = c + int(y)
        elif y == "/":
            r += 1
            c = 0
        elif y.isalpha() and white_turn == y.isupper():  # check the piece is the colour of the player's turn
            starting_squares.append((r, c))
            c += 1
    return starting_squares


def evaluate_position(position):
    # all calculations comparative e.g. king safety compared between sides
    def count_material():
        len_fen_pieces = b.find_colour(position)[2] - 1
        piece_dict = {'p': 1, 'k': 2, 'n': 3, 'b': 3.2, 'r': 5, 'q': 9}
        result = 0
        for x in range(len_fen_pieces):
            y = position[x]
            if y.isalpha() and y.isupper():

                value = piece_dict[y.lower()]
                result += value
            elif y.isalpha() and y.islower():
                value = -piece_dict[y]
                result += value
        return result

    def king_safety():
        """" pawn shield
        no open file 
        not in center of board
        luft
        king tropism
        scale based on number of pieces 
        """""
        pass

    def pawn_structure():
        """" look at isolated, passed and double pawns
         count pawn islands and pawn majorities
         advanced : use a hash table of different pawn structures """""
        pass

    def available_moves():
        """" the more moves you have available relative to your opponent the better 
        will need to test this to see how much I want it to affect the evaluation """""
        # I always find when playing the computer it restricts my pieces to the extent just want to resign
        pass

    def quiescence_search():
        """" If there are any captures (not a pawn?) create a tree for these positions 
        and evaluate when there is no longer any captures """""
        pass

    def is_checkmate():  # maybe there's something in board like game_end that can help here
        pass

    evaluation = count_material()

    return evaluation


def minimax(root, depth):
    if depth == 0:
        return root.evaluation
    elif not root.children:
        # need to get the right evaluation for a game ending position which wasn't evaluated when the tree was created
        colour, enemy_colour = b.find_colour(root.position)[0], b.find_colour(root.position)[1]
        if b.square_attacked(b.locate_king(colour, root.position), enemy_colour, root.position) is True:
            return float('inf')
        else:
            return 0  # position is stalemate
    elif b.find_colour(root.position)[0] == 'w':
        value = float('-inf')
        for child in root.children:
            value = max(value, minimax(child, depth - 1))
    else:
        value = float('inf')
        for child in root.children:
            value = min(value, minimax(child, depth - 1))
    return value


def build_tree(root, depth):
    # BFS adding all the positions to a tree
    position_queue = deque()
    depth_queue = deque()
    position_queue.append(root)
    depth_queue.append(0)
    while len(position_queue) != 0:
        current_node = position_queue.popleft()  # popleft so that first in first out
        current_depth = depth_queue.popleft()
        if current_depth == depth:  # won't be adding children to maximum depth nodes
            break
        for starting_square in find_starting_squares(current_node.position):
            for square in b.available_moves(starting_square[0], starting_square[1], current_node.position, True):
                # HAVEN'T CONSIDERED STALEMATE, 3-FOLD REPETITION OR 50 MOVE RULE
                move = [starting_square, square]
                child_fen = b.update_fen(current_node.position, move)
                child = Node(child_fen)
                current_node.add_child(child)
                position_queue.append(child)
                depth_queue.append(current_depth + 1)
    # Evaluating bottom layer of nodes. Notice the only elements in the position_queue are the bottom nodes
    for node in position_queue:
        node.evaluation = round(evaluate_position(node.position), 1)
    return root


def run_evaluation(position):
    depth = 2  # these are half moves
    root = Node(position)
    build_tree(root, depth)
    return minimax(root, depth)
