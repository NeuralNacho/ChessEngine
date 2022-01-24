import pygame as p


def piece_on_square(row, col, fen):
    counter = 0
    marker = 0
    t = fen_row(fen, row)
    while counter <= col:
        y = fen[t + marker]
        if is_int(y):
            counter = counter + int(y)
        elif y.isalpha():
            counter = counter + 1
        marker = marker + 1
    if is_int(fen[t + marker - 1]):
        square = 'empty'
    else:
        square = fen[t + marker - 1]
    return square


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def fen_row(fen, row):
    i = 0
    x = 0
    t = 0
    while i < row:
        y = fen[x]
        if y == "/":
            t = x + 1
            i = i + 1
        x = x + 1
    return t


def order_column(column_order_1):
    counter = 0
    running_total = 0
    column_order_2 = []
    while counter < 8:
        if column_order_1[counter] != 'empty':
            if running_total != 0:
                column_order_2.append(running_total)
                running_total = 0
            column_order_2.append(column_order_1[counter])
        else:
            running_total = running_total + 1
            if counter == 7:
                column_order_2.append(running_total)
        counter = counter + 1
    return column_order_2


def update_fen(original_fen, move):
    column_order_1 = []
    row_1 = move[0][0]
    col_1 = move[0][1]
    row_2 = move[1][0]
    col_2 = move[1][1]
    for i in range(8):
        column_order_1.append(piece_on_square(row_1, i))
    column_length_1 = len(order_column(column_order_1))
    column_order_1[col_1] = 'empty'
    column_order_2 = order_column(column_order_1)
    new_fen_column_1 = ''
    for i in range(len(column_order_2)):
        new_fen_column_1 = new_fen_column_1 + str(column_order_2[i])
    t = fen_row(original_fen, row_1)
    new_fen_1 = original_fen[:t] + new_fen_column_1 + original_fen[(t + column_length_1):]
    column_order_3 = []
    for i in range(8):
        column_order_3.append(piece_on_square(row_2, i))  # add fen (will be new_fen_1)
    column_length_2 = len(order_column(column_order_3))
    column_order_3[col_2] = piece_on_square(row_1, col_1)
    column_order_4 = order_column(column_order_3)
    new_fen_column_2 = ''
    for i in range(len(column_order_4)):
        new_fen_column_2 = new_fen_column_2 + str(column_order_4[i])
    s = fen_row(new_fen_1, row_2)
    new_fen_2 = new_fen_1[:s] + new_fen_column_2 + new_fen_1[(s + column_length_2):]
    return new_fen_2


fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
print(fen[:fen.find(' ')])
