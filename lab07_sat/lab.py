"""
6.101 Lab:
SAT Solver
"""

#!/usr/bin/env python3

import sys
import typing

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    
    all_letters = set()
    for i in range(len(formula)):
        for j in range(len(formula[i])):
            all_letters.add(formula[i][j][0])

    def simplify(formula, letter, bool):
        """
        Simplifies the CNF formula given a letter and its boolean assignment.
        """
        out = []
        for clause in formula:
            temp = clause.copy()
            flag = True
            for literal in clause:
                if literal[0] == letter:
                    # entire clause is satisfied by this literal
                    if literal[1] == bool:
                        flag = False
                        break
                    
                    # clause can't be satisfied by this literal so remove
                    else:
                        temp.remove(literal)
                        if temp == []:
                            return None
            if flag:
                out.append(temp)
        return out


    def check_for_one_liners(formula, queue, out):
        """
        Simplifies the CNF formula by removing all one literal clauses and assigning the CNF formula with that boolean assignment for that literal.
        """
        if formula == None:
            return None
        
        if formula == []:
            return []
        
        for clause in formula:
            if len(clause) == 1:
                letter = clause[0][0]
                bool = clause[0][1]

                queue.remove(letter)
                out.append((letter, bool))
                return check_for_one_liners(simplify(formula, letter, bool), queue, out)

        return formula
    

    def solve(formula, queue, out):
        """
        Solves the CNF formula.
        """
        if formula == []:
            return out

        # if queue is empty, we have no satisfying solution        
        if len(queue) == 0:
            return None

        queue_copy = queue.copy()
        out_copy = out.copy()
        
        # simplify through one liner check
        reduced_formula = check_for_one_liners(formula, queue_copy, out_copy)
        if reduced_formula == None:
            return None
        if reduced_formula == []:
            return out_copy
        
        # simplify through search
        letter = queue_copy.pop()
        formula_true = simplify(reduced_formula, letter, True)
        formula_false = simplify(reduced_formula, letter, False)

        if formula_true != None:
            res = solve(formula_true, queue_copy, out_copy + [(letter, True)])
            if res != None:
                return res

        if formula_false != None:
            res = solve(formula_false, queue_copy, out_copy + [(letter, False)])
            if res != None:
                return res
            
        return None
    

    answer = solve(formula, list(all_letters), [])
    if answer == None:
        return None

    out = {}
    for clause in answer:
        out[clause[0]] = clause[1]
    return out


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """

    def rule1(student_preferences):
        out = []
        for s in student_preferences:
            temp = []
            for r in student_preferences[s]:
                temp.append((s+"_"+r, True))
            out.append(temp)
        return out
    
    def rule2(student_preferences, room_capacities):
        out = []

        for s in student_preferences:
            temp = []
            for r in room_capacities:
                temp.append(s+"_"+r)
            
            for i in range(len(temp)):
                for j in range(i+1, len(temp)):
                    out.append([(temp[i], False), (temp[j], False)])
        
        return out

    def rule3(student_preferences, room_capacities):
        def combinations_n(students,n):
            """
            finds the combinations of size 'n' of a given list
            """
            out = []

            if n == 1:
                for student in students:
                    out.append((student,))
                return out

            for i in range(len(students)-n+1):
                combos = combinations_n(students[i+1:], n-1)
                for combo in combos:
                    out.append((students[i],) + combo)

            return out


        out = []
        students = list(student_preferences.keys())
        total_students = len(student_preferences)

        for room in room_capacities:
            if room_capacities[room] < total_students:
                combos = combinations_n(students,room_capacities[room]+1)
                for combo in combos:
                    temp = []
                    for student in combo:
                        temp.append((student+'_'+room,False))
                    out.append(temp)

        return out

    out1 = rule1(student_preferences)
    
    out2 = rule2(student_preferences,room_capacities)
    
    out3 = rule3(student_preferences,room_capacities)

    return out1 + out2 +out3



if __name__ == "__main__":
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

    l = [
    [('a', False), ('b', False)],
    [('a', True), ('d', False)],
    [('a', True)],
    [('a', False), ('e', True), ('f', False), ('g', True)],
    [('b', True), ('c', True), ('f', True)],
    [('b', False), ('f', True), ('g', False)]
    ]

    print(satisfying_assignment(l))
