# 8x8 matrix
# define each piece
# define rules - castling, promotion, check, checkmate, en passant, captures, can't pass through piece, repetition
# highlight piece, optional highlight available moves, undo/redo move, drag pieces, pawn promotion selection
# create graphics - display board from FEN
# play game


import pygame as p
import evaluation as ev
p.font.init()
p.display.set_caption('Chess Engine')
icon = p.image.load('pictures/wN.png')
p.display.set_icon(icon)

alpha_to_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
index_to_alpha = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}


def available_rook_moves(row, col, fen):
    a = []
    distances = [7-col, col, row, 7-row]  # number of squares to edge of board in each direction
    t = piece_on_square(row, col, fen).islower()  # for comparison later
    for x in range(4):  # x is index in the list
        i = 1
        while i < distances[x] + 1:
            if x == 0:
                r, c = row, col + i  # right
            elif x == 1:
                r, c = row, col - i  # left
            elif x == 2:
                r, c = row - i, col  # up
            else:
                r, c = row + i, col  # down
            if piece_on_square(r, c, fen) == 'empty':
                a.append((r, c))
                i += 1
            elif piece_on_square(r, c, fen).isupper() == t:  # if the pieces are different colours
                a.append((r, c))
                break
            else:
                break

    return a


def available_knight_moves(row, col, fen):
    a = [(row+1, col+2), (row-1, col+2), (row+1, col-2), (row-1, col-2),
         (row+2, col+1), (row-2, col+1), (row+2, col-1), (row-2, col-1)]
    b = a.copy()  # need to remove from copied list because can't modify it while iterating over it
    t = piece_on_square(row, col, fen).isupper()  # For comparison later
    for square in b:
        r, c = square
        if -1 < r < 8 and -1 < c < 8 and piece_on_square(r, c, fen).isupper() == t \
                and piece_on_square(r, c, fen) != 'empty':  # empty is lower case
            # Python won't check last condition if earlier conditions are false so
            # won't get an error from piece_on_square function with invalid input
            a.remove(square)
    return a


def available_bishop_moves(row, col, fen):
    a = []
    gaps = [7 - col, col, row, 7 - row]  # number of squares to edge of board in each direction
    diagonal_distances = [min(gaps[0], gaps[2]), min(gaps[0], gaps[3]), min(gaps[1], gaps[3]), min(gaps[1], gaps[2])]
    t = piece_on_square(row, col, fen).islower()  # for comparison later
    for x in range(4):
        i = 1
        while i < diagonal_distances[x] + 1:
            if x == 0:
                r, c = row-i, col+i  # north east
            elif x == 1:
                r, c = row+i, col+i  # south east
            elif x == 2:
                r, c = row+i, col-i  # south west
            else:
                r, c = row-i, col-i
            if piece_on_square(r, c, fen) == 'empty':
                a.append((r, c))
                i += 1
            elif piece_on_square(r, c, fen).isupper() == t:  # if the pieces are different colours
                a.append((r, c))
                break
            else:
                break
    return a


def available_queen_moves(row, col, fen):
    return available_rook_moves(row, col, fen) + available_bishop_moves(row, col, fen)


def available_king_moves(row, col, fen):
    def king_blocked(side):
        blocked = True  # False means the path for the king is clear
        if side == 'K' and piece_on_square(7, 5, fen) == 'empty' and piece_on_square(7, 6, fen) == 'empty':
            blocked = False
        elif side == 'Q' and piece_on_square(7, 3, fen) == 'empty' and piece_on_square(7, 2, fen) == 'empty' \
                and piece_on_square(7, 1, fen) == 'empty':
            blocked = False
        elif side == 'k' and piece_on_square(0, 5, fen) == 'empty' and piece_on_square(0, 6, fen) == 'empty':
            blocked = False
        elif piece_on_square(0, 3, fen) == 'empty' and piece_on_square(0, 2, fen) == 'empty' \
                and piece_on_square(0, 1, fen) == 'empty':
            blocked = False
        return blocked

    def king_checked(side):  # checks all the empty squares as well
        checked = True
        if side == 'K' and square_attacked((7, 4), 'b', fen) is False and square_attacked((7, 5), 'b', fen) is False \
                and square_attacked((7, 6), 'b', fen) is False:  # enemy colour is black
            checked = False
        elif side == 'Q' and square_attacked((7, 4), 'b', fen) is False and square_attacked((7, 3), 'b', fen) is False \
                and square_attacked((7, 2), 'b', fen) is False:
            checked = False
        elif side == 'k' and square_attacked((0, 4), 'w', fen) is False and square_attacked((0, 5), 'w', fen) is False \
                and square_attacked((0, 6), 'w', fen) is False:
            checked = False
        elif side == 'q' and square_attacked((0, 4), 'w', fen) is False and square_attacked((0, 3), 'w', fen) is False \
                and square_attacked((0, 2), 'w', fen) is False:
            checked = False
        return checked

    def castling(move_list):
        index = find_colour(fen)[2]  # index of the colour to move in the FEN
        rights = fen[index+2:index+6]  # string of castling rights from FEN. May include '-' but doesn't matter
        if piece_on_square(row, col, fen).isupper():  # if the colour to move is white
            if 'K' in rights and king_blocked('K') is False and king_checked('K') is False:
                # notice you don't need to check the square since if not on starting square 'K' not in rights
                move_list.append((7, 6))
            if 'Q' in rights and king_blocked('Q') is False and king_checked('Q') is False:
                move_list.append((7, 2))
        if piece_on_square(row, col, fen).islower():
            if 'k' in rights and king_blocked('k') is False and king_checked('k') is False:
                move_list.append((0, 6))
            if 'q' in rights and king_blocked('q') is False and king_checked('q') is False:
                move_list.append((0, 2))
        return move_list

    a = [(row-1, col+1), (row, col+1), (row+1, col+1), (row+1, col),
         (row+1, col-1), (row, col-1), (row-1, col-1), (row-1, col)]
    b = a.copy()
    # need to remove from copied list because can't modify it while iterating over it. Notice b = a would not work
    t = piece_on_square(row, col, fen).isupper()  # For comparison later
    for square in b:
        r, c = square
        if -1 < r < 8 and -1 < c < 8 and piece_on_square(r, c, fen).isupper() == t \
                and piece_on_square(r, c, fen) != 'empty':  # 'empty' is lower case
            a.remove(square)
    a = castling(a)
    return a


def available_pawn_moves(row, col, fen):
    a = []
    if piece_on_square(row, col, fen) == 'p':
        colour = 'b'
    else:
        colour = 'w'
    if colour == 'w' and row != 0:
        if piece_on_square(row-1, col, fen) == 'empty':
            a.append((row-1, col))  # Top left square is (0,0)
        if col != 0 and piece_on_square(row-1, col-1, fen) != 'empty' and piece_on_square(row-1, col-1, fen).islower():
            # col != 0 makes sure we're not checking the piece on col -1 (could get an error)
            a.append((row-1, col-1))  # ^ square has to have a piece on it 'empty' is lower
        if col != 7 and piece_on_square(row-1, col+1, fen) != 'empty' and piece_on_square(row-1, col+1, fen).islower():
            a.append((row-1, col+1))
    if colour == 'b' and row != 7:
        if piece_on_square(row+1, col, fen) == 'empty':
            a.append((row+1, col))
        if col != 0 and piece_on_square(row+1, col-1, fen).isupper():
            a.append((row+1, col-1))
        if col != 7 and piece_on_square(row+1, col+1, fen).isupper():
            a.append((row+1, col+1))
    if row == 6 and colour == 'w' and piece_on_square(row-1, col, fen) == 'empty' \
            and piece_on_square(row-2, col, fen) == 'empty':
        a.append((row-2, col))
    if row == 1 and colour == 'b' and piece_on_square(row+1, col, fen) == 'empty' \
            and piece_on_square(row+2, col, fen) == 'empty':
        a.append((row+2, col))
    # if the en passant square in the fen and pawn diagonal to that square add the square to the available moves
    index = find_colour(fen)[2]
    fen_list = []
    characters_to_remove = ['K', 'Q', 'k', 'q', ' ']
    for char in fen[index+2:index+9]:
        if char not in characters_to_remove:
            fen_list.append(char)  # this list will have the en passant square as the first two entries (if it exists)
    if fen_list[0] != '-':
        en_passant_square = (8 - int(fen_list[1]), alpha_to_index[fen_list[0]])  # KEY ERROR
        # 8- since row counted from top of board
        if en_passant_square[0] == 2:
            enemy_colour = 'b'  # colour of side which en passant paw can be taken from
            row_to_check = 3  # for checking is there is an enemy pawn on the adjacent squares
        else:
            enemy_colour = 'w'
            row_to_check = 4
        if colour != enemy_colour and row_to_check == row \
                and (col == en_passant_square[1] + 1 or col == en_passant_square[1] - 1):
            a.append(en_passant_square)

    return a


def available_moves(row, col, fen, check_check):
    a = []
    piece_inspected = piece_on_square(row, col, fen).lower()
    pieces = {1: ['r', available_rook_moves], 2: ['n', available_knight_moves],
              3: ['k', available_king_moves], 4: ['b', available_bishop_moves],
              5: ['p', available_pawn_moves], 6: ['q', available_queen_moves]}
    # Shorter than writing out the code for each piece
    for piece in pieces:
        if piece_inspected == pieces[piece][0]:
            a = pieces[piece][1](row, col, fen)  # calls available move functions
            break

    if piece_on_square(row, col, fen).isupper():  # now start checking for check
        colour, enemy_colour = 'w', 'b'
    else:
        colour, enemy_colour = 'b', 'w'
    if check_check:
        # check_check True means we are examining the check condition, we don't want to do this if we are using the
        # square_attacked function because this would create an infinite loop
        b = a.copy()
        for square in b:
            if square[0] < 0 or square[0] > 7 or square[1] < 0 or square[1] > 7:
                # ^ to make sure update_fen won't cause an error
                a.remove(square)
        d = a.copy()
        for square in d:  # sees if the new move king is in check
            move = [(row, col), square]
            new_fen = update_fen(fen, move)
            new_king_location = locate_king(colour, new_fen)  # not the same as previous if there was a king move
            if square_attacked(new_king_location, enemy_colour, new_fen) is True:  # king is attacked
                a.remove(square)
    return a


def valid_move(player_clicks, fen):
    start_square = player_clicks[0]
    end_square = player_clicks[1]
    row, col = start_square
    if piece_on_square(row, col, fen).isupper():
        colour = 'w'  # for comparison with player to move
    else:
        colour = 'b'
    valid = False
    if find_colour(fen)[0] == colour and end_square in available_moves(row, col, fen, True):
        # first condition checks player to move
        valid = True
    return valid


images = {}


def sq_size(window):  # finds square size based on the size of the screen
    width = window.get_height()  # can't use width since extra side panel
    square_size = width // 8  # height is set to be a multiple of 8 since loading images requires an integer square size
    return square_size


def main():
    clock = p.time.Clock()
    width, height = 1200, 800
    window = p.display.set_mode((width, height), p.RESIZABLE)
    window.fill(p.Color("white"))
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    load_images(window)
    square_selected = ()
    player_clicks = []
    highlight = True
    held = False  # will be used for dragging pieces
    fen_list = [fen]
    pawn_promotion = None
    move_made = False  # use this to check things like checkmate so that it's mot constantly being checked
    game_in_play = True  # for seeing if we are in a draw or checkmate
    # will be used for undo/redo moves and checking for repetitions
    evaluation = 0  # this is the evaluation at the start of the game
    running = True
    while running:
        old_width, old_height = window.get_size()
        for event in p.event.get():
            square_size = sq_size(window)
            if event.type == p.QUIT:
                running = False

            elif event.type == p.VIDEORESIZE:  # allows the screen to be resized
                new_width = 8 * (event.w // 8)
                # want multiple of 8 so that square_size is a multiple of 8 to load images
                new_height = 8 * (event.h // 8)
                change = (abs(new_width - old_width), abs(new_height - old_height))
                # the window is square so want the new window to have the size of the new width or new height
                # depending on which one changed the most
                if change[0] > change[1]:
                    length = 8 * (int(0.66 * new_width) // 8)  # want 2/3 of the width to be the new height
                else:
                    length = new_height
                window = p.display.set_mode((int(length * 1.5), length), p.RESIZABLE)
                window.fill(p.Color("white"))
                # want ratio of 12:8 = 3:2 for side panel
                load_images(window)  # loads images with new size
                game_in_play = True  # will refresh ending screen if necessary - otherwise would be a white screen

            elif event.type == p.MOUSEBUTTONDOWN and p.mouse.get_pos()[0]//square_size < 8 and game_in_play:
                # ^ col < 8. game_in_play means we are not at a draw or checkmate
                location = p.mouse.get_pos()
                col = location[0]//square_size
                row = location[1]//square_size
                if square_selected == (row, col):
                    player_clicks = []
                    square_selected = ()
                    global calculated
                    calculated = False  # resets highlighted available moves
                elif len(player_clicks) == 0 and piece_on_square(row, col, fen) != 'empty':
                    # can't select piece from an empty square
                    square_selected = (row, col)
                    player_clicks.append(square_selected)  # adds selection to player clicks
                    held = True  # this means they are 'holding' a piece - we want to drag this piece
                elif len(player_clicks) == 1:  # square you place a piece can be empty
                    square_selected = (row, col)
                    player_clicks.append(square_selected)
                    if row == 0 and valid_move(player_clicks, fen) \
                            and piece_on_square(player_clicks[0][0], player_clicks[0][1], fen) == 'P':
                        pawn_promotion = 'w'
                    elif row == 7 and valid_move(player_clicks, fen) \
                            and piece_on_square(player_clicks[0][0], player_clicks[0][1], fen) == 'p':
                        pawn_promotion = 'b'
                if len(player_clicks) == 2 and pawn_promotion is None:
                    if valid_move(player_clicks, fen):
                        fen_index = fen_list.index(fen)
                        fen_list = fen_list[:fen_index + 1]  # removes redo moves if a move is made after an undo
                        fen = update_fen(fen, player_clicks)
                        square_selected = ()
                        player_clicks = []
                        fen_list.append(fen)
                        move_made = True
                    elif piece_on_square(row, col, fen) != 'empty':  # can immediately select a new square
                        square_selected = (row, col)
                        player_clicks = [square_selected]  # will still be holding a piece after this elif
                        held = True
                    else:
                        square_selected = ()
                        player_clicks = []
                    calculated = False  # resets highlighted available moves

            elif event.type == p.MOUSEBUTTONDOWN and p.mouse.get_pos()[0]//square_size > 7:  # in the panel
                x = p.mouse.get_pos()[0]
                y = p.mouse.get_pos()[1]
                square_size = sq_size(window)

                sqx, sqy = (x - int(11.5 * square_size))**2, (y - int(6.5 * square_size))**2
                radius = int(0.2 * square_size)  # radius of optional highlight button
                if sqx + sqy < radius**2:  # Pythagoras to see if mouse click inside circle
                    highlight = not highlight  # inverts boolean

                elif fen_list.index(fen) > 0 and 7.1 * square_size < y < 7.1 * square_size + 0.7 * square_size \
                        and 8.8 * square_size < x < 8.8 * square_size + 0.7 * square_size:  # undo move
                    pawn_promotion = None  # these three lines for when they undo move midway through promotion
                    square_selected = ()
                    player_clicks = []
                    fen_index = fen_list.index(fen)
                    fen = fen_list[fen_index-1]
                    game_in_play = True  # if you undo a checkmate or draw you are back in play

                elif fen != fen_list[-1] and 7.1 * square_size < y < 7.1 * square_size + 0.7 * square_size \
                        and 10.6 * square_size < x < 10.4 * square_size + 0.7 * square_size:  # redo move
                    pawn_promotion = None  # these three lines for when they redo move midway through promotion
                    square_selected = ()
                    player_clicks = []
                    fen_index = fen_list.index(fen)  # finds index of fen
                    fen = fen_list[fen_index + 1]  # changes fen to the next index in the list
                    move_made = True
                    # ^ means that if they undo and redo a game ending move game_end will still be called

                elif pawn_promotion is not None and 0 < y < square_size:  # if you are selecting the pawn promotion
                    promotion_pieces = ()
                    if 8 * square_size < x < 9 * square_size:
                        promotion_pieces = ('Q', 'q')
                    elif 9 * square_size < x < 10 * square_size:
                        promotion_pieces = ('B', 'b')
                    elif 10 * square_size < x < 11 * square_size:
                        promotion_pieces = ('N', 'n')
                    elif 11 * square_size < x < 12 * square_size:
                        promotion_pieces = ('R', 'r')
                    if pawn_promotion == 'w':
                        promotion_piece = promotion_pieces[0]
                    else:
                        promotion_piece = promotion_pieces[1]
                    pawn_promotion = None  # resets pawn_promotion
                    fen_index = fen_list.index(fen)
                    fen_list = fen_list[:fen_index + 1]  # removes redo moves if a move is made after an undo
                    fen = update_promotion_fen(fen, player_clicks[0], promotion_piece)
                    fen = update_fen(fen, player_clicks)
                    fen_list.append(fen)
                    square_selected = ()
                    player_clicks = []

            elif event.type == p.MOUSEBUTTONUP and p.mouse.get_pos()[0]//square_size < 8:  # col < 8:
                held = False  # will stop dragging piece
                location = p.mouse.get_pos()
                col = location[0] // square_size
                row = location[1] // square_size
                square_dropped = (row, col)
                if len(player_clicks) == 1 and square_dropped != square_selected:
                    # if they drop piece on the same square player clicks unchanged
                    player_clicks.append(square_dropped)
                    if row == 0 and valid_move(player_clicks, fen) \
                            and piece_on_square(player_clicks[0][0], player_clicks[0][1], fen) == 'P':
                        pawn_promotion = 'w'
                    elif row == 7 and valid_move(player_clicks, fen) \
                            and piece_on_square(player_clicks[0][0], player_clicks[0][1], fen) == 'p':
                        pawn_promotion = 'b'
                    if valid_move(player_clicks, fen) and pawn_promotion is None:
                        fen_index = fen_list.index(fen)
                        fen_list = fen_list[:fen_index + 1]  # removes redo moves if a move is made after an undo
                        fen = update_fen(fen, player_clicks)
                        fen_list.append(fen)
                        square_selected = ()
                        player_clicks = []
                        move_made = True
                    elif pawn_promotion is None:  # won't change player clicks if promoting a pawn
                        square_selected = ()
                        player_clicks = []
                    calculated = False  # resets highlighted available moves

            elif event.type == p.MOUSEBUTTONUP and p.mouse.get_pos()[0]//square_size > 7:
                held = False
                square_selected = ()
                player_clicks = []
                calculated = False
        if game_in_play:  # will not cover over checkmate or draw if in end position
            draw_game(window, fen, square_selected, highlight, held, pawn_promotion, evaluation)
        if move_made and game_in_play:  # will not keep an end checking position if already checked once
            print(fen)
            evaluation = ev.run_evaluation(fen)  # Only called when a move is made.
            # DOES IT WORK ON PAWN PROMOTION??
            move_made = game_end(window, fen, fen_list)
            # ^ two functions: runs the function and gives a value to move_made
        if move_made:
            game_in_play = False
        clock.tick(60)  # this means the maximum fps is 30
        p.display.flip()


def load_images(window):
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    square_size = sq_size(window)
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("pictures/" + piece + ".png"), (square_size, square_size))
    arrows = ['left arrow', 'right arrow']
    for arrow in arrows:
        images[arrow] = p.transform.scale(p.image.load("pictures/" + arrow + ".png"),
                                          (int(0.7 * square_size), int(0.7 * square_size)))


def draw_game(window, fen, square_selected, highlight, held, pawn_promotion, evaluation):
    window.fill("white")
    # ^ covers over pawn selection and makes sure that pawns dragged over the panel are covered up on the next tick
    draw_board(window)
    highlight_square(window, fen, square_selected, highlight)
    draw_pieces(window, fen)
    draw_panel(window, highlight, pawn_promotion, evaluation)
    if held:  # will drag a piece if it is being held, do this after draw game so image not hidden behind board
        r, c = square_selected[0], square_selected[1]
        drag_piece(window, piece_on_square(r, c, fen), (r, c))


def draw_board(window):
    colours = [p.Color("white"), p.Color(90, 170, 70)]
    dimension = 8
    square_size = sq_size(window)
    for r in range(dimension):
        for c in range(dimension):
            colour = colours[(r+c) % 2]
            p.draw.rect(window, colour, p.Rect(c * square_size, r * square_size, square_size, square_size))


calculated = False
possible_moves = []


def highlight_square(window, fen, square_selected, highlight):
    if square_selected != ():
        square_size = sq_size(window)
        row, col = square_selected
        s = p.Surface((square_size, square_size))  # creates a surface which represents an image (a square in this case)
        s.set_alpha(150)  # transparency value from 0 -> 255
        s.fill(p.Color("yellow"))
        window.blit(s, (col * square_size, row * square_size))  # notice column first. highlights piece selected
        # WONT HIGHLIGHT SELECTED SQUARE WHEN MOUSE STILL HELD DOWN
        t = p.Surface((square_size, square_size))
        t.set_alpha(100)
        t.fill(p.Color(0, 100, 255))

        if highlight:  # can toggle highlighting available moves
            global calculated  # using global variables to stop it calculating the available moves every tick
            global possible_moves
            if calculated is False:
                possible_moves = available_moves(row, col, fen, True)
                calculated = True
            if piece_on_square(row, col, fen).isupper():
                colour = 'w'
            else:
                colour = 'b'
            if colour == find_colour(fen)[0]:  # only highlights moves if its is the right player's turn
                for square in possible_moves:  # highlights available moves
                    r, c = square
                    window.blit(t, (c * square_size, r * square_size))


def draw_panel(window, highlight, pawn_promotion, evaluation):
    square_size = sq_size(window)  # the panel is four times wider than the square size
    window.blit(images['left arrow'], (int(8.8 * square_size), 7.1 * square_size))  # buttons for undo/redo
    window.blit(images['right arrow'], (int(10.6 * square_size), 7.1 * square_size))

    if highlight:  # toggle for available moves
        circle_colour = "grey"  # (0, 128, 255) for nice blue
    else:
        circle_colour = "white"
    p.draw.circle(window, circle_colour, (int(11.5 * square_size), int(6.5 * square_size)), (int(0.2 * square_size)))
    p.draw.circle(window, 'black', (int(11.5 * square_size), int(6.5 * square_size)), int(0.2 * square_size), 2)
    # (window, colour, centre, radius)
    font = p.font.SysFont('franklingothicmedium', int(0.27 * square_size))  # 2nd entry is square size
    text = font.render('Highlight available moves', False, (0, 0, 0))
    # True is for antialias. render creates a new surface
    window.blit(text, (int(8.2 * square_size), int(6.35 * square_size)))

    font = p.font.SysFont('Comic Sans MS', 30)
    label = font.render(str(evaluation), True, (0, 0, 0))  # blue colour
    window.blit(label, (9.8 * square_size, 3 * square_size))

    if pawn_promotion is not None:
        colour = pawn_promotion
        pieces = ['Q', 'B', 'N', 'R']
        pos_x = p.mouse.get_pos()[0]
        pos_y = p.mouse.get_pos()[1]
        for x, piece in enumerate(pieces):
            if 0 < pos_y < square_size and (8 + x) * square_size < pos_x < (9 + x) * square_size:
                p.draw.rect(window, (248, 70, 0), p.Rect((8 + x) * square_size, 0, square_size, square_size))
            piece_image = colour + piece
            window.blit(images[piece_image], ((8 + x) * square_size, 0))
            p.draw.rect(window, "black", p.Rect((8 + x) * square_size, 0, square_size, square_size), 2)
            # last entry is thickness


def game_end(window, fen, fen_list):  # checks for ending the game would go on panel
    move_made = False  # resets this for the main function unless we have a game end
    square_size = sq_size(window)
    font = p.font.SysFont('franklingothicmedium', int(0.27 * square_size))

    half_move_index = fen.rfind(' ', 0, fen.rfind(' ')) + 1  # index after the second last space
    full_move_index = fen.rfind(' ') + 1  # index after the last space
    half_move_number = int(fen[half_move_index:full_move_index - 1])
    if half_move_number == 50:  # 50-move rule
        text = font.render('Draw by Fifty-Move Rule', False, (0, 0, 0))
        window.blit(text, (int(8.2 * square_size), int(5.35 * square_size)))
        move_made = True

    repetitions = 0  # Three-fold repetition
    for position in fen_list:
        if fen[:fen.find(' ')] == position[:position.find(' ')]:
            repetitions += 1
            if repetitions == 3:  # fen is the last entry on the fen_list so will always be 1
                text = font.render('Draw by Threefold Repetition', False, (0, 0, 0))
                window.blit(text, (int(8.2 * square_size), int(5.35 * square_size)))
                move_made = True

    available_move = False  # Code for checkmate and stalemate
    r, c = 0, 0
    for character in fen[:fen.find(' ')]:  # not checking extra characters at the end of the FEN
        if is_int(character):
            c = c + int(character)
        elif character == "/":
            r = r + 1
            c = 0
        elif character.isalpha():
            if character.isupper():
                colour = 'w'
            else:
                colour = 'b'
            if colour == find_colour(fen)[0] and available_moves(r, c, fen, True) != []:
                # ^ if the piece is the colour of the player's turn. True means we are checking for checks
                available_move = True
                break
            c = c + 1
    if not available_move:
        move_made = True
        colour, enemy_colour = find_colour(fen)[0], find_colour(fen)[1]
        font = p.font.SysFont('franklingothicmedium', int(0.5 * square_size))
        if square_attacked(locate_king(colour, fen), enemy_colour, fen) is True:  # king is attacked
            text = font.render('CHECKMATE', False, (0, 0, 0))
            window.blit(text, (int(8.2 * square_size), int(5.35 * square_size)))
        else:
            text = font.render('STALEMATE', False, (0, 0, 0))
            window.blit(text, (int(8.2 * square_size), int(5.35 * square_size)))
    return move_made  # will still execute everything else


def drag_piece(window, piece, square):
    square_colours = [p.Color("white"), p.Color(90, 170, 70)]
    r, c = square
    square_colour = square_colours[(r+c) % 2]
    square_size = sq_size(window)
    p.draw.rect(window, square_colour, p.Rect(c * square_size, r * square_size, square_size, square_size))
    # removes piece from square
    s = p.Surface((square_size, square_size))  # need to rehighlight the square
    s.set_alpha(150)  # transparency value from 0 -> 255
    s.fill(p.Color("yellow"))
    window.blit(s, (c * square_size, r * square_size))
    square_size = sq_size(window)
    mouse_position = p.mouse.get_pos()
    if piece.isupper():
        piece_colour = 'w'
    else:
        piece_colour = 'b'
    piece_image = piece_colour + piece.capitalize()
    window.blit(images[piece_image], (mouse_position[0] - 0.5 * square_size, mouse_position[1] - 0.5 * square_size))


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def draw_pieces(window, fen):
    row = 0
    col = 0
    square_size = sq_size(window)
    len_fen_pieces = find_colour(fen)[2] - 1  # Don't want extra characters at the end of the FEN
    for x in range(len_fen_pieces):
        y = fen[x]
        if is_int(y):
            col = col + int(y)
        if y == "/":
            row = row + 1
            col = 0
        if y.isalpha():
            if y.isupper():
                colour = 'w'
            else:
                colour = 'b'
            piece = colour + y.capitalize()
            window.blit(images[piece], p.Rect(col * square_size, row * square_size, square_size, square_size))
            col = col + 1


def fen_row(fen, row):  # Finds the index in the FEN of the first character in a row
    no_slashes_counted = 0
    index_in_fen = 0
    while no_slashes_counted < row:
        y = fen[index_in_fen]
        if y == "/":
            no_slashes_counted += 1
        index_in_fen += 1
    return index_in_fen


def piece_on_square(row, col, fen):  # Finds the piece on a square or if it is empty
    row_position = 0
    marker = 0  # Marks position in the FEN
    t = fen_row(fen, row)  # t is the index in the FEN of the first character in a row
    while row_position <= col:
        y = fen[t + marker]
        if is_int(y):
            row_position += int(y)
        elif y.isalpha():
            row_position += 1
        marker += 1
    if is_int(fen[t + marker - 1]):
        square = 'empty'
    else:
        square = fen[t + marker - 1]
    return square


def order_row(row_order):
    # Shortens list of pieces on a row by turning a sequence of empty squares into an integer
    row_position = 0
    running_total = 0
    new_row_order = []
    while row_position < 8:
        if row_order[row_position] != 'empty':
            if running_total != 0:
                new_row_order.append(running_total)
                running_total = 0
            new_row_order.append(row_order[row_position])
        else:
            running_total += 1
            if row_position == 7:
                new_row_order.append(running_total)
        row_position += 1
    return new_row_order


def update_fen_row(row, col, fen, piece):
    # Changes the FEN when a piece is moved to/from a square
    old_row_order = []  # Order of the squares in the row
    for i in range(8):
        old_row_order.append(piece_on_square(row, i, fen))
    row_length = len(order_row(old_row_order))
    old_row_order[col] = piece  # Removes/places piece on a square
    new_row_order = order_row(old_row_order)
    new_fen_row = ''
    for char in new_row_order:
        new_fen_row += str(char)
    s = fen_row(fen, row)
    new_fen = fen[:s] + new_fen_row + fen[s + row_length:]  # Changes FEN between two slashes
    return new_fen


def update_fen(original_fen, move):  # Updates the FEN when a move is made
    row_1, col_1, row_2, col_2 = move[0][0], move[0][1], move[1][0], move[1][1]
    piece_moved = piece_on_square(row_1, col_1, original_fen)
    new_fen_1 = update_fen_row(row_1, col_1, original_fen, 'empty')  # removes piece from square
    new_fen_2 = update_fen_row(row_2, col_2, new_fen_1, piece_moved)  # places piece

    index = find_colour(new_fen_2)[2]
    new_colour = find_colour(new_fen_2)[1]
    new_fen_2 = new_fen_2[:index] + new_colour + new_fen_2[index+1:]  # changes player turn

    def update_castling(fen):
        castling_fen_list = []  # will put into list to edit then put back into string
        castling_index = find_colour(fen)[2] + 2
        rights = fen[castling_index:castling_index+4]
        for letter in rights:
            castling_fen_list.append(letter)
        if piece_moved == 'K':  # checks for king move
            if 'K' in castling_fen_list:
                castling_fen_list.remove('K')
            if 'Q' in castling_fen_list:
                castling_fen_list.remove('Q')
        elif piece_moved == 'k':
            if 'k' in castling_fen_list:
                castling_fen_list.remove('k')
            if 'q' in castling_fen_list:
                castling_fen_list.remove('q')
        elif piece_moved == 'R':  # checks for rook move
            if move[0] == (7, 7) and 'K' in castling_fen_list:
                castling_fen_list.remove('K')
            elif move[0] == (7, 0) and 'Q' in castling_fen_list:
                castling_fen_list.remove('Q')
        elif piece_moved == 'r':
            if move[0] == (0, 7) and 'k' in castling_fen_list:
                castling_fen_list.remove('k')
            elif move[0] == (0, 0) and 'q' in castling_fen_list:
                castling_fen_list.remove('q')

        new_rights = ''
        for i in castling_fen_list:
            new_rights += str(i)
        castled_fen = fen[:castling_index] + new_rights + fen[castling_index+4:]

        castling_moves = [((7, 4), (7, 6), 'K'), ((7, 4), (7, 2), 'K'), ((0, 4), (0, 6), 'k'), ((0, 4), (0, 2), 'k')]
        if (move[0], move[1], piece_moved) in castling_moves:  # moving the the rook
            # won't create function loop because of if condition
            castle_squares = [((7, 6), (7, 7), (7, 5), 'R'), ((7, 2), (7, 0), (7, 3), 'R'),
                              ((0, 6), (0, 7), (0, 5), 'r'), ((0, 2), (0, 0), (0, 3), 'r')]
            for castle in castle_squares:
                if move[1] == castle[0]:
                    castled_fen = update_fen_row(castle[1][0], castle[1][1], castled_fen, 'empty')
                    castled_fen = update_fen_row(castle[2][0], castle[2][1], castled_fen, castle[3])
                    break  # no need to update the colour

        return castled_fen

    def update_en_passant(fen):
        fen_list = []
        characters_to_remove = ['K', 'Q', 'k', 'q', ' ']
        en_passant_index = find_colour(fen)[2] + 2
        no_removed_chars = 0
        for char in fen[en_passant_index:en_passant_index+7]:
            if char in ['K', 'Q', 'k', 'q']:
                no_removed_chars += 1
            if char not in characters_to_remove:
                fen_list.append(char)
                # this list will have the en passant square as the first two entries (if it exists)
        old_en_passant_square = ()
        if fen_list[0] == '-':
            len_old_en_passant_square = 1
        else:
            len_old_en_passant_square = 2
            old_en_passant_square = (8 - int(fen_list[1]), alpha_to_index[fen_list[0]])
            # for checking for en passant capture later
        new_en_passant_square = '-'
        if piece_moved.lower() == 'p' and abs(row_2 - row_1) == 2:  # if pawn pushed forward two squares
            if row_1 == 1:
                fen_list[0] = 6  # puts in row of en passant square
            else:
                fen_list[0] = 3
            fen_list.insert(0, index_to_alpha[col_1])  # puts in col of en passant square
            new_en_passant_square = str(fen_list[0]) + str(fen_list[1])
        en_passant_fen = (fen[:en_passant_index+no_removed_chars+1] + new_en_passant_square +
                          fen[en_passant_index+no_removed_chars+1+len_old_en_passant_square:])
        if piece_moved.lower() == 'p' and move[1] == old_en_passant_square:  # if captures en passant
            if row_2 == 2:
                captured_row = 3  # row of captured pawn 2->3, 5->4
            else:
                captured_row = 4
            en_passant_fen = update_fen_row(captured_row, col_2, en_passant_fen, 'empty')  # removes captured pawn

        return en_passant_fen

    def update_digits(fen):  # fifty move rule and full move counter
        full_move_index = fen.rfind(' ') + 1  # index after the last space
        half_move_index = fen.rfind(' ', 0, fen.rfind(' ')) + 1  # index after the second last space
        full_move_number = int(fen[full_move_index:])
        half_move_number = int(fen[half_move_index:full_move_index-1])
        if find_colour(fen)[0] == 'w':  # colour already changed so this occurs when black have just moved
            new_full_move_number = str(full_move_number + 1)
        else:
            new_full_move_number = str(full_move_number)
        if piece_moved.lower() != 'p' and piece_on_square(row_2, col_2, original_fen) == 'empty':
            new_half_move_number = str(half_move_number + 1)
        else:
            new_half_move_number = '0'
        digits_fen = fen[:half_move_index] + new_half_move_number + ' ' + new_full_move_number
        return digits_fen

    new_fen_3 = update_castling(new_fen_2)
    new_fen_4 = update_en_passant(new_fen_3)
    new_fen_5 = update_digits(new_fen_4)

    return new_fen_5


def find_colour(fen):  # finds the player who's turn it is from the FEN
    if fen.rfind('w') != -1:  # no piece names star with a w
        colour, opposite_colour = 'w', 'b'
        index = fen.rfind('w')
    else:
        colour, opposite_colour = 'b', 'w'
        index = fen.find(' ') + 1  # can't use rfind('b') since could be an en passant square with b
    return colour, opposite_colour, index  # some of the functions need the colour as well as the index


def square_attacked(square, enemy_colour, fen):
    # Sees if the square is in the available squares of any enemy piece (maybe not most efficient but easy)
    attacked = False
    r, c = 0, 0  # for cycling through all the squares
    len_fen_pieces = find_colour(fen)[2] - 1  # Don't want extra characters at the end of the FEN
    for x in range(len_fen_pieces):
        y = fen[x]
        if is_int(y):
            c = c + int(y)
        elif y == "/":
            r = r + 1
            c = 0
        elif y.isalpha():
            if y.isupper():
                colour = 'w'
            else:
                colour = 'b'
            if colour == enemy_colour and y.lower() != 'k' and square in available_moves(r, c, fen, False):
                # checks the piece is not a king to avoid loop between available_king_moves and square_attacked
                # pawn is special because a pawn push forward is not attacking
                if y.lower() == 'p' and c == square[1]:  # no change in column i.e. pushed forward
                    pass
                else:
                    attacked = True
                break
            elif colour == enemy_colour and y == 'K':
                index = find_colour(fen)[2]
                if 'K' not in fen[index+2:index+6] and square in available_king_moves(r, c, fen):
                    """ what this does is make sure when the king moves are checked it will not call square_attacked
                    again since square attacked only gets call in available_king_moves if 'K' is in the castling rights
                    But it also means an unmoved king cannot attack a square
                    (doesn't matter for now since only using this function for castling) """
                    attacked = True
                    break
            elif colour == enemy_colour and y == 'k':
                index = find_colour(fen)[2]
                if 'k' not in fen[index+2:index+6] and square in available_king_moves(r, c, fen):
                    attacked = True
                    break
            c = c + 1
    return attacked


def locate_king(colour, fen):
    first_space_index = fen.index(' ')
    fen = fen[:first_space_index]  # don't want castling rights affecting if a king is found
    split_fen = fen.split('/')  # split fen on the slashes to create a list
    if colour == 'w':
        king = 'K'
    else:
        king = 'k'
    row = 0
    square = ()
    for i in range(len(split_fen)):
        if king in split_fen[i]:
            row = i  # row with the king in it
    for col in range(8):
        if piece_on_square(row, col, fen) == king:
            square = (row, col)
            break
    return square


def update_promotion_fen(fen, square, piece):  # swaps pawn for promotion piece on the pawn's original square
    row, col = square
    new_fen = update_fen_row(row, col, fen, piece)  # places piece
    half_move_index = new_fen.rfind(' ', 0, fen.rfind(' ')) + 1
    # need to make the half move number -1 so that it is set to 0 when the fen is updated in main
    full_move_index = new_fen.rfind(' ') + 1
    full_move_number = int(new_fen[full_move_index:])
    new_half_move_number = '-1'
    new_fen = new_fen[:half_move_index] + new_half_move_number + ' ' + str(full_move_number)
    return new_fen
