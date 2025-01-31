"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def copy_game(game):
    out = {}
    out["height"] = game["height"]
    out["width"] = game["width"]
    out["player"] = game["player"]
    out["computers"] = game["computers"].copy()
    out["targets"] = game["targets"].copy()
    out["walls"] = game["walls"].copy()

    return out
    
    


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """

    player = []
    computers = set()
    targets = set()
    walls = set()

    for r in range(len(level_description)):
        for c in range(len(level_description[0])):
            for w in level_description[r][c]:
                if w == "computer":
                    computers.add((r, c))
                elif w == "target":
                    targets.add((r, c))
                elif w == "player":
                    player.append((r, c))
                elif w == "wall":
                    walls.add((r, c))
            

    return {
        "height": len(level_description),
        "width": len(level_description[0]),
        "player": player[0],
        "computers": computers,
        "targets": targets,
        "walls": walls
    }


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    if len(game["computers"]) == 0 or len(game["targets"]) == 0:
        return False

    return game["computers"] == game["targets"]


def has_visited_before(game, visited):
    key = (game["player"], frozenset(game["computers"])) # frozenset(game["targets"])
    if key in visited:
        return True
    else:
        visited.add(key)
        return False

def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a new game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    out = copy_game(game)

    vector = direction_vector[direction]
    next_coord = (out["player"][0] + vector[0], out["player"][1] + vector[1])
    next_next_coord = (out["player"][0] + vector[0] + vector[0], out["player"][1] + vector[1] + vector[1])

    if next_coord in out["walls"]:
        return out

    elif next_coord in out["computers"]:
        if next_next_coord in out["computers"] or next_next_coord in out["walls"]:
            return out

        else:
            out["player"] = next_coord
            out["computers"].remove(next_coord)
            out["computers"].add(next_next_coord)

    else:
        out["player"] = next_coord

    return out


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    out = []

    for r in range(game["height"]):
        temp = []
        for c in range(game["width"]):
            cell = []
            if game["player"] == (r, c):
                cell.append("player")
            if (r, c) in game["computers"]:
                cell.append("computer")
            if (r, c) in game["targets"]:
                cell.append("target")
            if (r, c) in game["walls"]:
                cell.append("wall")
            temp.append(cell)
        out.append(temp)

    return out


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):
        return []

    queue = [ [game, ["up"]], [game, ["down"]], [game, ["left"]], [game, ["right"]] ]
    visited = set()
    has_visited_before(game, visited)

    while queue:
        next = queue.pop(0)
        state = next[0]
        path = next[1]

        next_state = step_game(state, path[-1])
        if victory_check(next_state):
            return path

        if has_visited_before(next_state, visited):
            continue

        for direction in ["up", "down", "left", "right"]:
            queue.append([next_state, path + [direction]])

    return None


if __name__ == "__main__":
    import json

    puzzle = "m1_001"
    with open(f"puzzles/{puzzle}.json") as f:
        level = json.load(f)
        result = solve_puzzle(make_new_game(level))
        print(f"res: {result}")
