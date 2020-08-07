'''
Name: Shashank *******
Roll No: 015

Implementation of the Unification Function
'''
import re

class Token(object):
    def __init__(self, tok_type, value):
        self.tok_type = tok_type
        self.value = value

    def __str__(self):
        return f"Token({self.tok_type}, {self.value})"

    def __repr__(self):
        return self.__str__()

class Lexer(object):
    def __init__(self, expr):
        self.expr = expr
        self.idx = 0

    def peek(self):
        if self.idx < len(self.expr):
            return self.expr[self.idx]

        return None

    def consume(self):
        val = self.peek()
        self.idx += 1
        return val

    def take_while(self, pat):
        res = ''

        while self.peek() != None and re.match(pat, self.peek()):
            res += self.consume()

        return res

    def parse_var(self):
        return Token('var', self.take_while('\w'))

    def parse_ident(self):
        return Token('ident', self.take_while('\w'))

    def get_token(self):
        self.take_while('\s')
        ch = self.peek()
        
        if ch == None:
            return None

        if ch == ',':
            self.consume()
            return Token('comma', ',')
        elif ch == '(':
            self.consume()
            return Token('l_paren', '(')
        elif ch == ')':
            self.consume()
            return Token('r_paren', ')')
        elif ch.isupper():
            return self.parse_var()
        elif ch.islower():
            return self.parse_ident()
        else:
            return False

    def tokenize(self):
        tokens = []

        while self.peek() != None:
            tok = self.get_token()
            if tok == False:
                return False
            if tok == None:
                break
            tokens.append(tok)

        tokens.append(Token('EOF', 'EOF'))

        return tokens


class AtomNode(object):
    def __init__(self, val):
        self.val = val

    def contains(self, other):
        return self.__eq__(other)

    def copy(self):
        return AtomNode(self.val)

    def __str__(self):
        return self.val

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, AtomNode):
            return self.val == other.val

        return False

class VarNode(object):
    def __init__(self, val):
        self.val = val

    def contains(self, other):
        return self.__eq__(other)

    def copy(self):
        return VarNode(self.val)

    def __str__(self):
        return self.val

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, VarNode):
            return self.val == other.val

        return False


class PredicateNode(object):
    def __init__(self, name, nodes):
        self.name = name
        self.nodes = nodes

    def contains(self, node):
        for n in self.nodes:
            if n.contains(node):
                return True

        return False

    def substitute(self, node, sub_node):
        for i, n in enumerate(self.nodes):
            if isinstance(n, PredicateNode):
                n.substitute(node, sub_node)

            if n == node:
                self.nodes[i] = sub_node.copy()

    def contains(self, node):
        for n in self.nodes:
            if n.contains(node):
                return True

        return False


    def copy(self):
        return PredicateNode(self.name, [n.copy() for n in self.nodes])

    def __str__(self):
        return f"{self.name}({', '.join([str(n) for n in self.nodes])})" 

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, PredicateNode):
            return self.name == other.name and len(self.nodes) == len(other.nodes)

        return False


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0

    def peek(self):
        if self.idx < len(self.tokens):
            return self.tokens[self.idx]

        return None

    def consume(self):
        res = self.peek()
        self.idx += 1
        return res

    def skip(self, punc):
        if self.peek().value == punc:
            self.consume()
            return
        
        return False

    def maybe_pred(self):
        tok = self.consume()

        if self.peek().value != '(':
            return AtomNode(tok.value)

        self.consume()
        nodes = []
        while self.peek().tok_type != 'r_paren':
            nodes.append(self.parse_node())
            if self.peek().tok_type == 'r_paren':
                break
            if self.skip(',') == False:
                return False

        self.consume()

        return PredicateNode(tok.value, nodes)

    def parse_node(self):
        res = self.peek()

        if res.tok_type == 'var':
            self.consume()
            return VarNode(res.value)
        elif res.tok_type == 'ident':
            return self.maybe_pred()
        else:
            return False
    
    def parse(self):
        nodes = self.parse_node()

        if self.peek().value != 'EOF':
            nodes = False

        return nodes

class Unifier(object):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2
        self.subs = {}
        self.failed = False

        self.unify(self.expr1, self.expr2)
    
    def substitute(self, node, sub_node):
        self.subs[node.val] = sub_node.copy()

        for n in self.subs.values():
            if isinstance(n, PredicateNode):
                n.substitute(node, sub_node)

        if isinstance(self.expr1, PredicateNode):
            self.expr1.substitute(node, sub_node)

        if isinstance(self.expr2, PredicateNode):
            self.expr2.substitute(node, sub_node)

    def fail(self):
        self.failed = True

    def is_var(self, node):
        return isinstance(node, VarNode)

    def is_atom(self, node):
        return isinstance(node, AtomNode)

    def unify(self, psi1, psi2):
        if self.is_var(psi1) or self.is_var(psi2) or self.is_atom(psi1) or self.is_atom(psi2):
            if psi1 == psi2:
                return
            elif isinstance(psi1, VarNode):
                if psi2.contains(psi1):
                    self.fail()
                    return

                self.substitute(psi1, psi2)
                return
            elif isinstance(psi2, VarNode):
                if psi1.contains(psi2):
                    self.fail()
                    return

                self.substitute(psi2, psi1)
                return
            else:
                self.fail()
                return

        if psi1 != psi2:
            self.fail()
            return

        for psi1_, psi2_ in zip(psi1.nodes, psi2.nodes):
            self.unify(psi1_, psi2_)
            if self.failed:
                return

    def __str__(self):
        if self.failed:
            return "The Expression cannot be unified\n"

        res = ""

        for var, val in self.subs.items():
            res += f"{var} = {val}\n"

        return res

    def __repr__(self):
        return self.__str__()

def main():
    while True:
        expr = input('> ')
        if expr == 'quit':
            print("Bye\n")
            break

        sides = expr.split('=')

        if len(sides) != 2:
            print("Expression should have two sides\n")
            continue

        tokens1 = Lexer(sides[0]).tokenize()
        tokens2 = Lexer(sides[1]).tokenize()

        if False in [tokens1, tokens2]:
            print("There was a problem lexing the input\n")
            continue

        parsed1 = Parser(tokens1).parse()
        parsed2 = Parser(tokens2).parse()

        if False in [parsed1, parsed2]:
            print("There was a problem parsing the input\n")
            continue

        expr1 = Parser(Lexer(sides[0]).tokenize()).parse()
        expr2 = Parser(Lexer(sides[1]).tokenize()).parse()

        print(Unifier(expr1, expr2))


if __name__ == '__main__':
    main()
