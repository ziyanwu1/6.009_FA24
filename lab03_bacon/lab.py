"""
6.101 Lab:
Bacon Number
"""

#!/usr/bin/env python3

import pickle
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    """
    returns a list containing the "acted", "films", and "films_reversed" dictionary
    """

    acted = {} # actors to list of other actors they acted with
    films = {} # films to list of actors
    films_reversed = {} # actors to list of films

    for tup in raw_data:
        actor1 = tup[0]
        actor2 = tup[1]
        film = tup[2]

        # add the actors
        if actor1 not in acted:
            acted[actor1] = set()
            films_reversed[actor1] = set()

        if actor2 not in acted:
            acted[actor2] = set()
            films_reversed[actor2] = set()
            
        acted[actor1].add(actor2)
        acted[actor2].add(actor1)

        # add the actors to the films
        if film not in films:
            films[film] = set()

        films[film].add(actor1)
        films[film].add(actor2)

        # add the films to the actors
        films_reversed[actor1].add(film)
        films_reversed[actor2].add(film)
    
    # add themselves
    for actor in acted:
        acted[actor].add(actor)

    return [acted, films, films_reversed]


def acted_together(transformed_data, actor_id_1, actor_id_2):
    acted = transformed_data[0]

    if acted.get(actor_id_2, None) != None:
        if actor_id_1 in acted[actor_id_2]:
            return True

    if acted.get(actor_id_1, None) != None:
        if actor_id_2 in acted[actor_id_1]:
            return True

    return False


def actors_with_bacon_number(transformed_data, n):
    acted = transformed_data[0]
    bacon = 4724

    past = {}

    def bfs(people, i, n):
        """
        'people' is a set of actor ids
        """

        past[i] = people.copy()

        # gets the ppl in the next level (subtract the ppl that already has been seen)
        next_level = set()
        for id in people:
            next_level = next_level.union(acted[id])
        for k in past:
            next_level = next_level - past[k]

        if i + 1 == n:
            return next_level
        elif next_level == set():
            return set()
        else:
            return bfs(next_level.copy(), i + 1, n)

    return bfs({bacon}, 0, n)


def bacon_path(transformed_data, actor_id):
    acted = transformed_data[0]
    bacon = 4724

    seen = set()
    seen.add(bacon)
    def bfs(peoples, goal):
        """
        'peoples' is a list of (id, (path...))
        'id' is the id of the actor
        'path' is the path to get their from the bacon id number
        """

        if len(peoples) == 0:
            return None

        next_level = []

        for id, path in peoples:
            neighbors = acted[id]
            for neighbor in neighbors:
                if neighbor in seen:
                    continue
                elif neighbor == goal:
                    return (path + (neighbor,))
                else:
                    next_level.append((neighbor, path + (neighbor,)))
                    seen.add(neighbor)

        return bfs(next_level, goal)
    
    return bfs([(bacon, (bacon,))], actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    acted = transformed_data[0]

    if actor_id_1 == actor_id_2:
        return (actor_id_1,)

    seen = set()
    seen.add(actor_id_1)
    def bfs(peoples, goal):
        """
        'peoples' is a list of (id, (path...))
        'id' is the id of the actor
        'path' is the path to get their from the bacon id number
        """

        if len(peoples) == 0:
            return None

        next_level = []

        for id, path in peoples:
            neighbors = acted[id]
            for neighbor in neighbors:
                if neighbor in seen:
                    continue
                elif neighbor == goal:
                    return (path + (neighbor,))
                else:
                    next_level.append((neighbor, path + (neighbor,)))
                    seen.add(neighbor)

        return bfs(next_level, goal)
    
    return bfs([(actor_id_1, (actor_id_1,))], actor_id_2)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    acted = transformed_data[0]

    if goal_test_function(actor_id_1):
        return [actor_id_1]

    seen = set()
    seen.add(actor_id_1)
    def bfs(peoples):

        if len(peoples) == 0:
            return None

        next_level = []

        for id, path in peoples:
            neighbors = acted[id]
            for neighbor in neighbors:
                if neighbor in seen:
                    continue
                elif goal_test_function(neighbor):
                    return (path + (neighbor,))
                else:
                    next_level.append((neighbor, path + (neighbor,)))
                    seen.add(neighbor)

        return bfs(next_level)
    
    return bfs([(actor_id_1, (actor_id_1,))])


def actors_connecting_films(transformed_data, film1, film2):
    films = transformed_data[1]

    if (film1 not in films) or (film2 not in films):
        return None

    list_actors_1 = films[film1]
    list_actors_2 = films[film2]

    min_length = float("inf")
    min_path = None

    for act1 in list_actors_1:
        for act2 in list_actors_2:
            path = actor_to_actor_path(transformed_data, act1, act2)
            if path != None:
                if len(path) < min_length:
                    min_length = len(path)
                    min_path = path
    
    if min_path == None:
        return None
    else:
        return list(min_path)

if __name__ == "__main__":
    with open("resources/large.pickle", "rb") as lf:
        db = pickle.load(lf)
    
    with open("resources/names.pickle", "rb") as nf:
        namesdb = pickle.load(nf)

    with open("resources/movies.pickle", "rb") as mf:
        moviedb = pickle.load(mf)

    reverse_moviedb = {}
    for k in moviedb:
        reverse_moviedb[moviedb[k]] = k

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    data = transform_data(db)
    
    print(namesdb["Helen Mirren"])
    print(namesdb["Vjeran Tin Turk"])
    print()

    l = actor_to_actor_path(data, 15735, 1367972)

    pairs = []
    for i in range(len(l) - 1):
        pairs.append((l[i], l[i+1]))

    out = []

    for pair in pairs:
        f1 = data[2][pair[0]]
        f2 = data[2][pair[1]]

        for m in f1:
            if m in f2:
                out.append(m)
                break

    out2 = []
    for mo in out:
       out2.append(reverse_moviedb[mo])

    print(out2)
    