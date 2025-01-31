"""
6.101 Lab:
Mines
"""
#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    nearby_offsets = [-1, 0, 1]

    board = []
    visible = []
    for r in range(nrows):
        board_row = []
        visible_row = []
        for c in range(ncolumns):
            # add to visible
            visible_row.append(False)
            
            # add to board
            if (r, c) in mines:
                board_row.append(".")
            else:
                nearby_mines = 0
                for r_offset in nearby_offsets:
                    for c_offset in nearby_offsets:
                        if (r + r_offset, c + c_offset) in mines:
                            nearby_mines += 1
                board_row.append(nearby_mines)

        board.append(board_row)
        visible.append(visible_row)

    return {
        "dimensions": (nrows, ncolumns),
        "board": board,
        "visible": visible,
        "state": "ongoing",
    }


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """

    # game already over
    if game["state"] == "defeat" or game["state"] == "victory":
        return 0

    # pressing on a cell that's already revealed
    if game["visible"][row][col] == True:
        return 0

    game["visible"][row][col] = True
    nearby_offsets = [-1, 0, 1]
    revealed = 1

    # pressed on a mine
    if game["board"][row][col] == ".":
        game["state"] = "defeat"
        return revealed

    # recursive reveal if no nearby bad squares    
    if game["board"][row][col] == 0:
        for row_offset in nearby_offsets:
            for col_offset in nearby_offsets:
                if (row + row_offset >= 0) and (row + row_offset < game["dimensions"][0]) and (col + col_offset >= 0) and (col + col_offset < game["dimensions"][1]) and (game["board"][row + row_offset][col + col_offset] != ".") and (not game["visible"][row + row_offset][col + col_offset]):
                    revealed += dig_2d(game, row + row_offset, col + col_offset)

    # victory check
    victory_flag = True
    for r in range(game["dimensions"][0]):
        if not victory_flag:
            break       
        for c in range(game["dimensions"][1]):
            if game["board"][r][c] == ".":
                continue
            if not game["visible"][r][c]:
                victory_flag = False
                break
    if victory_flag:
        game["state"] = "victory"

    return revealed


def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    out = []
    for r in range(game["dimensions"][0]):
        temp = []
        for c in range(game["dimensions"][1]):
            if all_visible or game["visible"][r][c]:
                if game["board"][r][c] == 0:
                    temp.append(" ")
                else:
                    temp.append(str(game["board"][r][c]))
            else:
                temp.append("_")
        out.append(temp)

    return out


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    out = ""
    for r in range(game["dimensions"][0]):
        for c in range(game["dimensions"][1]):
            if all_visible or game["visible"][r][c]:
                if game["board"][r][c] == 0:
                    out += " "
                else:
                    out += str(game["board"][r][c])
            else:
                out += ("_")

        if r != game["dimensions"][0] - 1:
            out += "\n"

    return out



# N-D IMPLEMENTATION

def get_neighbors(dimensions, coord):
    """
    Gets all the valid neighbors for a given coordinate (including itself)
    
    Args:
        coord (tuple): the coordinate we want to get the neighbors of
    
    Returns:
        a set of neighbor coordinates
    """
    neighbors = set()

    def dfs(coord, level):
        if level >= len(coord):
            return

        prev = tuple()
        next = tuple()
        for i in range(len(coord)):
            if i == level:
                prev += (coord[i]-1,)
                next += (coord[i]+1,)
            else:
                prev += (coord[i],)
                next += (coord[i],)

        # add current coordinate
        neighbors.add(coord)
        dfs(coord, level+1)

        # add the -1 offset to our coordinate (if it's in bounds)
        if prev not in neighbors:
            in_bounds = True
            for i in range(len(prev)):
                if prev[i] < 0 or prev[i] >= dimensions[i]:
                    in_bounds = False
                    break
            if in_bounds:
                neighbors.add(prev)
                dfs(prev, level+1)

        # add the +1 offset to our coordinate (if it's in bounds)
        if next not in neighbors:
            in_bounds = True
            for i in range(len(next)):
                if next[i] < 0 or next[i] >= dimensions[i]:
                    in_bounds = False
                    break
            if in_bounds:
                neighbors.add(next)
                dfs(next, level+1)

    dfs(coord, 0)
    return neighbors


def get_value(l, coord):
    """
    Gets the value for a given coordinate.

    Args:
        l (list of lists): the list of list structure we want to index into
        coord (tuple): the coordinate we want to get the value of

    Returns:
        the value at that coordinate in our list of lists.
    """
    dim = len(coord)

    def r(l, coord, level):
        if level == (dim - 1):
            return l[coord[-1]]

        return r(l[coord[level]], coord, level+1)

    return r(l, coord, 0)


def set_value(l, coord, value):
    """
    Sets the value for a given coordinate.

    Args:
        l (list of lists): the list of list structure we want to index into
        coord (tuple): the coordinate we want to set the value of
        value (any): the value we want to set
    """
    dim = len(coord)

    def r(l, coord, level):
        if level == (dim - 1):
            l[coord[-1]] = value
            return

        r(l[coord[level]], coord, level+1)

    r(l, coord, 0)


def victory_check(game):
    """
    Checks if we've won the game.

    Args:
        game: our game representation
    
    Returns:
        boolean for whether we won the game or not
    """
    
    dim = len(game["dimensions"])

    def r(board, visible, level):
        if level == 1:
            for i in range(len(board)):
                if board[i] != "." and not visible[i]:
                    return False
            return True
        else:
            for i in range(game["dimensions"][dim-level]):
                if not r(board[i], visible[i], level-1):
                    return False
            return True

    return r(game["board"], game["visible"], dim)                


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    dim = len(dimensions)
    mines = set(mines)

    board = []
    visible = []

    def build_board(board, visible, coord):
        if len(coord) == dim - 1:
            for k in range(dimensions[-1]):
                new_coord = coord + (k,)

                # add cell to board
                if new_coord in mines:
                    board.append(".")
                else:
                    board.append(0)

                # add cell to visible
                visible.append(False)

            return
        
        for _ in range(dimensions[len(coord)]):
            board.append([])
            visible.append([])

        for k in range(dimensions[len(coord)]):
            build_board(board[k], visible[k], coord + (k,))

    build_board(board, visible, tuple())

    # fill in mine neighbors
    for mine in mines:
        for coord in get_neighbors(dimensions, mine):
            old_val = get_value(board, coord)
            if old_val != ".":
                set_value(board, coord, old_val + 1)

    out = {
        "board": board,
        "dimensions": dimensions,
        "state": "ongoing",
        "visible": visible
    }

    return out


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    
    def r(game, coordinates):
        # game already over
        if game["state"] == "defeat" or game["state"] == "victory":
            return 0

        # already seen
        if get_value(game["visible"], coordinates):
            return 0
        set_value(game["visible"], coordinates, True)

        # pressed on a mine
        board_value = get_value(game["board"], coordinates)
        if board_value == ".":
            game["state"] = "defeat"
            return 1

        # recursive reveal if no nearby bad squares
        revealed = 1
        if board_value == 0:
            for neighbor in get_neighbors(game["dimensions"], coordinates):
                # if get_value(game["board"], neighbor) != ".":
                revealed += r(game, neighbor)

        return revealed

    revealed = r(game, coordinates)

    # victory check
    if victory_check(game):
        game["state"] = "victory"

    return revealed


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    dimensions = game["dimensions"]
    dim = len(dimensions)

    board = []

    def build_board(board, coord):
        if len(coord) == dim - 1:
            for k in range(dimensions[-1]):
                new_coord = coord + (k,)

                if all_visible or get_value(game["visible"], new_coord):
                    cell = get_value(game["board"], new_coord)
                    if cell == 0:
                        board.append(" ")
                    else:
                        board.append(str(cell))
                else:
                    board.append("_")
            return

        for _ in range(dimensions[len(coord)]):
            board.append([])

        for k in range(dimensions[len(coord)]):
            build_board(board[k], coord + (k,))

    build_board(board, tuple())
    return board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )

    # g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # dig_nd(g, (0, 3, 0))

    pass
