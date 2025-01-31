"""
6.101 Lab:
Recipes
"""

import pickle
import sys
# import typing # optional import
# import pprint # optional import

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    out = {}

    for tup in recipes:
        if tup[0] == "atomic":
            out[tup[1]] = tup[2]

    return out


def compound_ingredient_possibilities(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    out = {}

    for tup in recipes:
        if tup[0] == "compound":
            if tup[1] not in out:
                out[tup[1]] = []
            out[tup[1]].append(tup[2])

    return out


def lowest_cost(recipes, food_item, restrictions=None):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """

    atomics = atomic_ingredient_costs(recipes)
    compounds = compound_ingredient_possibilities(recipes)

    if restrictions != None:
        for r in restrictions:
            if r in atomics:
                del atomics[r]
            if r in compounds:
                del compounds[r]

    def r(food_item):
        if food_item in atomics:
            return atomics[food_item]
        elif food_item in compounds:
            out = float("inf")
            # go through each potential recipe in the compound recipes
            for l in compounds[food_item]:
                temp = 0 # keep track of total cost for this recipe
                valid_recipe = True # flag for whether or not this recipe can even be made or not

                # go through each ingredient in the recipe
                for ingredient in l:
                    cost = r(ingredient[0])
                    if cost == None:
                        valid_recipe = False
                        break

                    temp += ingredient[1] * cost

                if valid_recipe:
                    out = min(out, temp)

            if out < float("inf"):
                return out
            else:
                return None
        else:
            return None

    return r(food_item)

def scaled_flat_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    out = {}
    for k in flat_recipe:
        out[k] = flat_recipe[k] * n

    return out


def add_flat_recipes(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        add_flat_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    out = {}

    all_keys = set()
    for r in flat_recipes:
        all_keys = all_keys.union(set(r.keys()))

    for k in all_keys:
        for r in flat_recipes:
            if k in r:
                out[k] = out.get(k, 0) + r[k]
    
    return out


def cheapest_flat_recipe(recipes, food_item, restrictions=None):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """

    atomics = atomic_ingredient_costs(recipes)
    compounds = compound_ingredient_possibilities(recipes)
    out = {}

    if restrictions != None:
        for r in restrictions:
            if r in atomics:
                del atomics[r]
            if r in compounds:
                del compounds[r]

    def r(food_item):
        if food_item in atomics:
            return atomics[food_item], [food_item]
        elif food_item in compounds:
            best = float("inf")
            best_l = None
            
            # go through each potential recipe in the compound recipes
            for l in compounds[food_item]:
                temp = 0 # keep track of total cost for this recipe
                temp_l = [] # keep track of the atomics for this recipe
                valid_recipe = True # flag for whether or not this recipe can even be made or not

                # go through each ingredient in the recipe
                for ingredient in l:
                    cost, cost_l = r(ingredient[0])
                    if cost == None:
                        valid_recipe = False
                        break

                    temp += ingredient[1] * cost
                    temp_l.extend(ingredient[1] * cost_l)

                if valid_recipe and temp < best:
                    best = temp
                    best_l = temp_l

            if best < float("inf"):
                return best, best_l
            else:
                return None, None
        else:
            return None, None

    _, best_atomics = r(food_item)
    if best_atomics == None:
        return None

    out = {}
    for food in best_atomics:
        out[food] = out.get(food, 0) + 1
    return out


def combined_flat_recipes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    if len(flat_recipes) == 0:
        return []

    out = [{}]
    for ingredient in flat_recipes:
        temp = []
        for recipe in ingredient:    
            for o in out:
                temp.append(add_flat_recipes([recipe, o]))
        out = temp

    return out


def all_flat_recipes(recipes, food_item, restrictions=None):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """

    atomics = atomic_ingredient_costs(recipes)
    compounds = compound_ingredient_possibilities(recipes)

    if restrictions != None:
        for r in restrictions:
            if r in atomics:
                del atomics[r]
            if r in compounds:
                del compounds[r]

    def r(food_item):
        if food_item in atomics:
            return [{food_item: 1}]
        elif food_item in compounds:
            out = []

            for recipe in compounds[food_item]:
                recipe_combos = [{}]
                valid_recipe = True

                for ingredient in recipe:
                    food, num = ingredient[0], ingredient[1]
                    ingredient_recipes = r(food)
                    if ingredient_recipes == None:
                        valid_recipe = False
                        break
                    
                    # scale by number of ingredient we need
                    for i in range(len(ingredient_recipes)):
                        ingredient_recipes[i] = scaled_flat_recipe(ingredient_recipes[i], num)
                    
                    temp = [] # collects the cross product combinations of the current recipes and the new ones for this ingredient
                    for first in recipe_combos:
                        for second in ingredient_recipes:
                            temp.append(add_flat_recipes([first, second]))

                    recipe_combos = temp

                if valid_recipe:
                    out.extend(recipe_combos)

            return out
        else:
            return None

    all_flat = r(food_item)
    if all_flat == None:
        return []
    return all_flat



if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
