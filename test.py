from enum import Enum
import re


class TokenType(Enum):
    NUMBER = "NUMBER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    VARIABLE = "VARIABLE"
    ASSIGN = "ASSIGN"
    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, value: str | None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Tokenizer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def variable(self):
        result = ""
        while self.current_char is not None and re.match(
            r"[a-zA-Z_]", self.current_char
        ):
            result += self.current_char
            self.advance()
        return Token(TokenType.VARIABLE, result)

    def number(self):
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token(TokenType.NUMBER, result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha() or self.current_char == "_":
                return self.variable()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MULTIPLY, "*")

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIVIDE, "/")

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")")

            if self.current_char == "=":
                self.advance()
                return Token(TokenType.ASSIGN, "=")

            raise Exception(f"Unexpected character: {self.current_char}")

        return Token(TokenType.EOF, None)


class Node:
    def evaluate(self, symbol_table):
        raise NotImplementedError("Subclass must implement evaluate method")


class NumberNode(Node):
    def __init__(self, token: Token):
        self.token = token

    def __repr__(self):
        return f"NumberNode({self.token})"

    def evaluate(self, symbol_table):
        return int(self.token.value)


class VariableNode(Node):
    def __init__(self, token: Token):
        self.token = token

    def __repr__(self):
        return f"VariableNode({self.token})"

    def evaluate(self, symbol_table):
        var_name = self.token.value
        # Like a reference
        if var_name in symbol_table:
            return symbol_table[var_name]
        else:
            raise Exception(f"Undefined variable: {var_name}")


class BinaryOpNode(Node):
    def __init__(self, left: Node, op: Token, right: Node):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOpNode({self.left}, {self.op}, {self.right})"

    def evaluate(self, symbol_table):
        left_value = self.left.evaluate(symbol_table)
        right_value = self.right.evaluate(symbol_table)

        if self.op.type == TokenType.PLUS:
            return left_value + right_value
        elif self.op.type == TokenType.MINUS:
            return left_value - right_value
        elif self.op.type == TokenType.MULTIPLY:
            return left_value * right_value
        elif self.op.type == TokenType.DIVIDE:
            if right_value == 0:
                raise ZeroDivisionError("Division by zero")
            return left_value / right_value


class AssignmentNode(Node):
    def __init__(self, var_node: VariableNode, expr_node: Node):
        self.var_node = var_node
        self.expr_node = expr_node

    def __repr__(self):
        return f"AssignmentNode({self.var_node}, {self.expr_node})"

    def evaluate(self, symbol_table):
        value = self.expr_node.evaluate(symbol_table)
        symbol_table[self.var_node.token.value] = value
        return value


class Parser:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
        self.current_token = self.tokenizer.get_next_token()

    def error(self):
        raise Exception(f"Parsing error: Unexpected token {self.current_token}")

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.tokenizer.get_next_token()
        else:
            self.error()

    def factor(self):
        if self.current_token.type == TokenType.NUMBER:
            token = self.current_token
            self.eat(TokenType.NUMBER)
            return NumberNode(token)
        elif self.current_token.type == TokenType.VARIABLE:
            token = self.current_token
            self.eat(TokenType.VARIABLE)
            return VariableNode(token)
        elif self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

        self.error()

    def term(self):
        node = self.factor()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOpNode(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOpNode(left=node, op=token, right=self.term())

        return node

    def assignment(self):
        var_node = self.factor()

        if not isinstance(var_node, VariableNode):
            self.error()

        self.eat(TokenType.ASSIGN)
        expr_node = self.expr()
        return AssignmentNode(var_node, expr_node)

    def parse(self):
        nodes = []
        while self.current_token.type != TokenType.EOF:
            if (
                self.current_token.type == TokenType.VARIABLE
                and self.peek_next_token().type == TokenType.ASSIGN
            ):
                nodes.append(self.assignment())
            else:
                nodes.append(self.expr())
                if self.current_token.type == TokenType.EOF:
                    break
        return nodes

    def peek_next_token(self):
        pos = self.tokenizer.pos
        current_char = self.tokenizer.current_char
        tokenizer = Tokenizer(self.tokenizer.text)
        tokenizer.pos = pos
        tokenizer.current_char = current_char
        return tokenizer.get_next_token()


text = "x=(2-(2+4+(3-2)))/(2+1)*(2-1)y=x"
tokenizer = Tokenizer(text)
parser = Parser(tokenizer)
ast_nodes = parser.parse()

symbol_table = {}

for ast in ast_nodes:
    result = ast.evaluate(symbol_table)

print(f"AST: {ast_nodes}")
print(f"Result: {result}")
print(f"Symbol Table: {symbol_table}")
