"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    out = []
    
    comment = False
    temp = ""
    for c in source:
        if not comment:
            if c == " " or c == "\n":
                if temp != "":
                    out.append(temp)
                    temp = ""
            elif c == "(" or c == ")":
                if temp != "":
                    out.append(temp)
                    temp = ""
                out.append(c)
            elif c == ";":
                if temp != "":
                    out.append(temp)
                    temp = ""
                comment = True
            else:
                temp += c
        else:
            if c == "\n":
                comment = False
    
    if temp != "":
        out.append(temp)

    return out

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if len(tokens) == 1:
        return number_or_symbol(tokens[0])

    # s-expression
    def r(index):
        """
        index is the index of the character RIGHT AFTER the '(' character
        """
        
        out = []
        while index < len(tokens):
            if tokens[index] == "(":
                next_element, next_i = r(index+1)
                out.append(next_element)
                index = next_i
            elif tokens[index] == ")":
                return out, index + 1
            else:
                out.append(number_or_symbol(tokens[index]))
                index += 1
        return out, len(tokens)

    res, _ = r(1)
    return res

######################
# Classes #
######################

class Function:
    def __init__(self, args, body, parent):
        self.args = args
        self.body = body
        self.parent = parent

    def eval(self, *params):
        frame = Frame(self.parent)

        if len(params) != len(self.args):
            raise SchemeEvaluationError
    
        for i in range(len(self.args)):
            frame.set_var(self.args[i], params[i])

        return evaluate(self.body, frame)

class Frame:
    def __init__(self, parent):
        self.parent = parent
        self.values = {}

    def set_var(self, name, value):
        self.values[name] = value

def make_initial_frame():
    builtins = Frame(None)
    builtins.values = scheme_builtins

    return Frame(builtins)

def find_value(name, frame):
    if name in frame.values:
        return frame.values[name]

    if frame.parent is None:
        raise SchemeNameError
    
    return find_value(name, frame.parent)

######################
# Built-in Functions #
######################

def calc_sub(*args):
    if len(args) == 1:
        return -args[0]
    else:
        first_num, *rest_nums = args
        return first_num - scheme_builtins['+'](*rest_nums)

def calc_mul(*args):    
    total = 1
    for num in args:
        total *= num

    return total

def calc_div(*args):
    if type(args[0]) != int and type(args[0]) != float:
        raise SchemeEvaluationError

    if len(args) == 1:
        return args[0]

    total = args[0]
    for num in args[1:]:
        total /= num
    
    return total
    

scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mul,
    "/": calc_div,
}




##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if frame is None:
        frame = make_initial_frame()

    if type(tree) == int or type(tree) == float:
        return tree
    elif type(tree) == str:
        return find_value(tree, frame)

    # the tree is an s-expression
    op_token = tree[0]
    if op_token == "define":
        # easier function definitions
        if type(tree[1]) == list:
            name, *args = tree[1]
            body = tree[2]
            value = Function(args, body, frame).eval
            frame.set_var(name, value)

            return value
        else:
            name = tree[1]
            value = evaluate(tree[2], frame)
            frame.set_var(name, value)

            return value
    elif op_token == "lambda":
        args = tree[1]
        body = tree[2]
        return Function(args, body, frame).eval
    else:
        op = evaluate(op_token, frame)
        
        if not callable(op):
            raise SchemeEvaluationError
        operands = []
        for token in tree[1:]:
            simplified = evaluate(token, frame)
            operands.append(simplified)

        return op(*operands)


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    
    import schemerepl
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=True, verbose=True).cmdloop()
    
    # inp = ['o', 9, 4, ['-', ['+', 3, 2]]]
    # print(evaluate(inp))