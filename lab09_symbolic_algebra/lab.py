"""
6.101 Lab:
Symbolic Algebra
"""

import doctest
# import typing # optional import
# import pprint # optional import
# import string # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Expr:
    def __init__(self, precedence):
        self.precedence = precedence

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)
    
    def __rsub__(self, other):
        return Sub(other, self)
    
    def __mul__(self, other):
        return Mul(self, other)
    
    def __rmul__(self, other):
        return Mul(other, self)
    
    def __truediv__(self, other):
        return Div(self, other)
    
    def __rtruediv__(self, other):
        return Div(other, self)

class Var(Expr):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        super().__init__(99)
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"
    
    def eval(self, mapping):
        if self.name in mapping:
            return mapping[self.name]
        
        raise NameError

    def __eq__(self, other):
        if type(other) != Var:
            return False
        
        return self.name == other.name

    def deriv(self, l):
        if self.name == l:
            return Num(1)

        return Num(0)

    def simplify(self):
        return self

class Num(Expr):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        super().__init__(99)
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"
    
    def eval(self, mapping):
        return self.n

    def __eq__(self, other):
        if type(other) != Num:
            return False

        return self.n == other.n

    def deriv(self, l):
        return Num(0)
    
    def simplify(self):
        return self

class BinOp(Expr):
    def __init__(self, left, right, precedence):
        super().__init__(precedence)

        if type(left) == str:
            self.left = Var(left)
        elif type(left) == int or type(left) == float:
            self.left = Num(left)
        else:
            self.left = left
        
        if type(right) == str:
            self.right = Var(right)
        elif type(right) == int or type(right) == float:
            self.right = Num(right) 
        else:
            self.right = right

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.left) + ", " + repr(self.right) + ")"
    
    def __eq__(self, other):
        return self.left == other.left and self.right == other.right and self.__class__.__name__ == other.__class__.__name__

class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right, 1)

    def __str__(self):
        out = ""

        if self.left.precedence < self.precedence:
            out += "(" + str(self.left) + ")"
        else:
            out += str(self.left)

        out += " + "

        if (self.right.precedence < self.precedence):
            out += "(" + str(self.right) + ")"
        else:
            out += str(self.right)

        return out
    
    def eval(self, mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)
    
    def deriv(self, l):
        return Add(self.left.deriv(l), self.right.deriv(l))

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        if type(left_simplified) == Num and type(right_simplified) == Num:
            return Num(left_simplified.n + right_simplified.n)
        elif type(left_simplified) == Num and left_simplified.n == 0:
            return right_simplified
        elif type(right_simplified) == Num and right_simplified.n == 0:
            return left_simplified
        else:
            return Add(left_simplified, right_simplified)

class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right, 1)

    def __str__(self):
        out = ""

        if self.left.precedence < self.precedence:
            out += "(" + str(self.left) + ")"
        else:
            out += str(self.left)

        out += " - "

        if (self.right.precedence < self.precedence) or self.wrap_right_at_same_precedence():
            out += "(" + str(self.right) + ")"
        else:
            out += str(self.right)

        return out
    
    def wrap_right_at_same_precedence(self):
        return self.precedence == self.right.precedence

    def eval(self, mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)

    def deriv(self, l):
        return Sub(self.left.deriv(l), self.right.deriv(l))

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        if type(left_simplified) == Num and type(right_simplified) == Num:
            return Num(left_simplified.n - right_simplified.n)
        elif type(right_simplified) == Num and right_simplified.n == 0:
            return left_simplified
        else:
            return Sub(left_simplified, right_simplified)

class Mul(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right, 2)

    def __str__(self):
        out = ""

        if self.left.precedence < self.precedence:
            out += "(" + str(self.left) + ")"
        else:
            out += str(self.left)

        out += " * "

        if (self.right.precedence < self.precedence):
            out += "(" + str(self.right) + ")"
        else:
            out += str(self.right)

        return out

    def eval(self, mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)

    def deriv(self, l):
        return Add(Mul(self.left, self.right.deriv(l)), Mul(self.right, self.left.deriv(l)))

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        if type(left_simplified) == Num and type(right_simplified) == Num:
            return Num(left_simplified.n * right_simplified.n)
        elif type(left_simplified) == Num and left_simplified.n == 1:
            return right_simplified
        elif type(right_simplified) == Num and right_simplified.n == 1:
            return left_simplified
        elif (type(left_simplified) == Num and left_simplified.n == 0) or (type(right_simplified) == Num and right_simplified.n == 0):
            return Num(0)
        else:
            return Mul(left_simplified, right_simplified)

class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right, 2)

    def __str__(self):
        out = ""

        if self.left.precedence < self.precedence:
            out += "(" + str(self.left) + ")"
        else:
            out += str(self.left)

        out += " / "

        if (self.right.precedence < self.precedence) or self.wrap_right_at_same_precedence():
            out += "(" + str(self.right) + ")"
        else:
            out += str(self.right)

        return out
    
    def wrap_right_at_same_precedence(self):
        return self.precedence == self.right.precedence

    def eval(self, mapping):
        return self.left.eval(mapping) / self.right.eval(mapping)

    def deriv(self, l):
        return Div(Sub(Mul(self.right, self.left.deriv(l)), Mul(self.left, self.right.deriv(l))), Mul(self.right, self.right))

    def simplify(self):
        left_simplified = self.left.simplify()
        right_simplified = self.right.simplify()

        if type(left_simplified) == Num and type(right_simplified) == Num:
            return Num(left_simplified.n / right_simplified.n)
        elif type(right_simplified) == Num and right_simplified.n == 1:
            return left_simplified
        elif type(left_simplified) == Num and left_simplified.n == 0:
            return Num(0)
        else:
            return Div(left_simplified, right_simplified)

def tokenize(expr):
    out = []

    temp = ""
    for c in expr:
        if c == " ":
            if temp != "":
                out.append(temp)
                temp = ""
        elif c == "(" or c == ")" or c == "+" or c == "*" or c == "/":
            if temp != "":
                out.append(temp)
                temp = ""
            out.append(c)
        else:
            temp += c
    if temp != "":
        out.append(temp)

    return out

def parse(tokens):
    all_letters = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                      + ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])

    def r(index):
        # if index >= len(tokens):
        #     return None, len(tokens)
        if tokens[index] == "(":
            left, next_l_i = r(index + 1)
            op_token = tokens[next_l_i]
            right, next_r_i = r(next_l_i + 1) # 'next_r_i' should always be the ")" character

            if op_token == "+":
                return Add(left, right), next_r_i + 1
            elif op_token == "-":
                return Sub(left, right), next_r_i + 1
            elif op_token == "*":
                return Mul(left, right), next_r_i + 1
            elif op_token == "/":
                return Div(left, right), next_r_i + 1
        elif tokens[index] in all_letters:
            return Var(tokens[index]), index + 1
        else:
            return Num(float(tokens[index])), index + 1

    expr, _ = r(0)
    return expr


def make_expression(expr):
    return parse(tokenize(expr))

if __name__ == "__main__":
    doctest.testmod()
    s = "(x * (-32.3 - 3))"
    t = tokenize(s)
    print(t)
    p = parse(t)
    print(repr(p))