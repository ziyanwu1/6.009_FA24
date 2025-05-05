"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys
sys.setrecursionlimit(20_000)

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


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
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
        if tokens[0] == "(" or tokens[0] == ")":
            raise SchemeSyntaxError

        return number_or_symbol(tokens[0])

    # s-expression
    if tokens[0] != "(":
        raise SchemeSyntaxError

    left_paren_count = [1]
    right_paren_count = [0]
    def r(index):
        """
        index is the index of the character RIGHT AFTER the '(' character
        """

        out = []
        while index < len(tokens):
            if tokens[index] == "(":
                left_paren_count[0] += 1
                next_element, next_i = r(index+1)
                out.append(next_element)
                index = next_i
            elif tokens[index] == ")":
                right_paren_count[0] += 1
                return out, index + 1
            else:
                out.append(number_or_symbol(tokens[index]))
                index += 1

        raise SchemeSyntaxError

    res, end_index = r(1)
    if (end_index != len(tokens)) or (left_paren_count[0] != right_paren_count[0]):
        raise SchemeSyntaxError
    return res

######################
# Classes #
######################

class Function:
    def __init__(self, args, body, parent):
        self.args = args
        self.body = body
        self.parent = parent

    def __call__(self, *params):
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

class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def copy(self):
        # deepcopy
        if self.cdr == None:
            return Pair(self.car, self.cdr)

        if type(self.cdr) != Pair:
            raise SchemeEvaluationError

        return Pair(self.car, self.cdr.copy())

    def get_last_node(self):
        if self.cdr == None:
            return self
        
        return self.cdr.get_last_node()


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
    
def equal(*args):
    base = evaluate(args[0])
    for arg in args[1:]:
        if evaluate(arg) != base:
            return False
    return True

def greater(*args):
    current = evaluate(args[0])
    for arg in args[1:]:
        next_arg = evaluate(arg)
        if next_arg >= current:
            return False
        current = next_arg
    return True

def greater_equal(*args):
    current = evaluate(args[0])
    for arg in args[1:]:
        next_arg = evaluate(arg)
        if next_arg > current:
            return False
        current = next_arg
    return True

def less(*args):
    current = evaluate(args[0])
    for arg in args[1:]:
        next_arg = evaluate(arg)
        if next_arg <= current:
            return False
        current = next_arg
    return True

def less_equal(*args):
    current = evaluate(args[0])
    for arg in args[1:]:
        next_arg = evaluate(arg)
        if next_arg < current:
            return False
        current = next_arg
    return True

def not_func(*args):
    if len(args) != 1:
        raise SchemeEvaluationError

    ans = evaluate(args[0])
    return not ans

def is_list(*args):
    # must check if all .cdr values are Pair types AND the last Pair's .cdr value is None
    if len(args) != 1:
        raise SchemeEvaluationError

    if args[0] is None:
        return True

    if type(args[0]) != Pair:
        return False

    return is_list(*[args[0].cdr])

def length(*args):
    if len(args) != 1:
        raise SchemeEvaluationError("length 1")

    if not is_list(*[args[0]]):
        raise SchemeEvaluationError("length 2")

    if args[0] is None:
        return 0
    
    return 1 + length(*[args[0].cdr])

def list_ref(*args):
    if len(args) != 2:
        raise SchemeEvaluationError("list-ref 1")
    
    if type(args[0]) != Pair:
        raise SchemeEvaluationError("list-ref 2")

    if type(args[1]) != int:
        raise SchemeEvaluationError("list-ref 3")

    if args[1] == 0:
        return args[0].car
    
    return list_ref(*[args[0].cdr, args[1]-1])

def append(*args):
    if len(args) == 0:
        return None

    if not is_list(*[args[0]]):
        raise SchemeEvaluationError

    first = None
    current = None
    for arg in args:
        if not is_list(*[arg]):
            raise SchemeEvaluationError

        # can skip if empty list
        if arg == None:
            continue

        if current == None:
            current = arg.copy()
            first = current
        else:
            arg_copy = arg.copy()
            current.get_last_node().cdr = arg_copy
            current = arg_copy

    return first

def begin(*args):
    # all args passed in are already evaluated, so we only need to return the last item
    return args[-1]

## the below functions aren't needed, as in test_files/map_filter_reduce.scm, the test cases define the map, filter, and reduce functions for us

# def map(*args):
#     f = args[0]
#     l = args[1]

#     first = None
#     current = None
#     while l != None:
#         temp = Pair(f(l.car), None)
#         if current is None:
#             first = temp
#         else:
#             current.cdr = temp
#         current = temp
#         l = l.cdr
#     return first

# def filter(*args):
#     f = args[0]
#     l = args[1]

#     first = None
#     current = None
#     while l != None:
#         if f(l.car):
#             temp = Pair(l.car, None)
#             if current is None:
#                 first = temp
#             else:
#                 current.cdr = temp
#             current = temp

#         l = l.cdr
#     return first

# def reduce(*args):
#     f = args[0]
#     l = args[1]
#     out = args[2]

#     while l != None:
#         out = f(out, l.car)
#         l = l.cdr

#     return out

def cons(*args):
    if len(args) != 2:
        raise SchemeEvaluationError("cons")
    return Pair(args[0], args[1])

scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mul,
    "/": calc_div,
    "#t": True,
    "#f": False,
    "equal?": equal,
    ">": greater,
    ">=": greater_equal,
    "<": less,
    "<=": less_equal,
    "not": not_func,
    "list?": is_list,
    "length": length,
    "list-ref": list_ref,
    "append": append,
    "begin": begin,
    "cons": cons
}

def evaluate_file(filename, frame=None):
    if frame is None:
        frame = make_initial_frame()

    with open(filename, "r") as f:
        return evaluate(parse(tokenize(f.read())), frame)

def make_initial_frame():
    builtins = Frame(None)
    builtins.values = scheme_builtins
    frame = Frame(builtins)

    return frame

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

    if type(tree) == int or type(tree) == float or type(tree) == bool or type(tree) == Pair or tree is None:
        return tree
    elif type(tree) == str:
        return find_value(tree, frame)
    elif len(tree) == 0:
        # empty lists will be represented through None in our compiler
        return None

    # the tree is an s-expression
    op_token = tree[0]
    if op_token == "define":
        if len(tree) != 3:
            raise SchemeSyntaxError

        # easier function definitions
        if type(tree[1]) == list:
            if len(tree[1]) == 0:
                raise SchemeSyntaxError

            name, *args = tree[1]
            body = tree[2]
            value = Function(args, body, frame)
            frame.set_var(name, value)

            return value
        else:
            name = tree[1]
            value = evaluate(tree[2], frame)
            frame.set_var(name, value)

            return value
    elif op_token == "lambda":
        if len(tree) != 3:
            raise SchemeSyntaxError

        args = tree[1]
        body = tree[2]
        return Function(args, body, frame)
    elif op_token == "and":
        for token in tree[1:]:
            if evaluate(token, frame) != True:
                return False
        return True
    elif op_token == "or":
        for token in tree[1:]:
            if evaluate(token, frame) == True:
                return True
        return False
    elif op_token == "if":
        pred = tree[1]
        true_exp = tree[2]
        false_exp = tree[3]
        if evaluate(pred, frame):
            return evaluate(true_exp, frame)
        else:
            return evaluate(false_exp, frame)
    # elif op_token == "cons":
    #     if len(tree) != 3:
    #         raise SchemeEvaluationError("cons")
    #     return Pair(evaluate(tree[1], frame), evaluate(tree[2], frame))
    elif op_token == "car":
        if len(tree) != 2:
            raise SchemeEvaluationError

        token = evaluate(tree[1], frame)
        if type(token) != Pair:
            raise SchemeEvaluationError 

        return token.car
    elif op_token == "cdr":
        if len(tree) != 2: 
            raise SchemeEvaluationError

        token = evaluate(tree[1], frame)
        if type(token) != Pair:
            raise SchemeEvaluationError

        return token.cdr
    elif op_token == "list":
        # special case of empty list
        if len(tree) == 1:
            return None

        def r(tree):
            if len(tree) == 0:
                return None
            
            return Pair(evaluate(tree[0], frame), r(tree[1:]))

        return r(tree[1:])
    elif op_token == "del":
        var = tree[1]

        if frame.values.get(var) is None:
            raise SchemeNameError
        
        value = frame.values[var]
        del frame.values[var]
        return value
    elif op_token == "let":
        vars = tree[1]
        body = tree[2]
        new_frame = Frame(frame)

        for var in vars:
            new_frame.values[var[0]] = evaluate(var[1], new_frame)

        return evaluate(body, new_frame)
    elif op_token == "set!":
        var = tree[1]
        expr = tree[2]
        value = evaluate(expr, frame)

        # fixed bug:
        # i had a setbang! bug but it turns out the bug was in list
        # when resolving list, the arguments should be resolved in order, and shouldn't be backwards reversed

        def parents_r(current_frame, var, val):
            if current_frame is None:
                raise SchemeNameError
            if var in current_frame.values:
                current_frame.values[var] = val
            else:
                parents_r(current_frame.parent, var, val)
        parents_r(frame, var, value)
        return value
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
    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    repl_frame = make_initial_frame()
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            evaluate_file(filename, repl_frame)
    schemerepl.SchemeREPL(sys.modules[__name__], use_frames=True, verbose=True, repl_frame=repl_frame).cmdloop()

    # source = "(list-ref (cons 1 2) 0)"
    # print(evaluate(parse(tokenize(source))))

    # bug 1:
    # for the "test_map_filter_reduce_defined_externally_in_scheme" test case, our code currently fails
    # the reasoning for this is because it expects map, filter, and reduce to not be a class of function, lambda, or method
    # the problem is the way our Function works is that it calls its .eval() method
    # the fix here is to replace using the .eval() method with the __call__ dunder
    # and then you'd also replace every time you return a .eval