## Parsing of the complex math expr `(2-(2+4+(3-2)))/(2+1)*(2-1)`

Example:
```text = "x=3y=4t=(2-(2+4+(3-2)))/(2+1)*(2-1)print(t,y+4,x,x+2)c=t"```

Generated AST: </br>
[AssignmentNode(VariableNode(Token(TokenType.VARIABLE, x)), NumberNode(Token(TokenType.NUMBER, 3))), AssignmentNode(VariableNode(Token(TokenType.VARIABLE, y)), NumberNode(Token(TokenType.NUMBER, 4))), AssignmentNode(VariableNode(Token(TokenType.VARIABLE, t)), BinaryOpNode(BinaryOpNode(BinaryOpNode(NumberNode(Token(TokenType.NUMBER, 2)), Token(TokenType.MINUS, -), BinaryOpNode(BinaryOpNode(NumberNode(Token(TokenType.NUMBER, 2)), Token(TokenType.PLUS, +), NumberNode(Token(TokenType.NUMBER, 4))), Token(TokenType.PLUS, +), BinaryOpNode(NumberNode(Token(TokenType.NUMBER, 3)), Token(TokenType.MINUS, -), NumberNode(Token(TokenType.NUMBER, 2))))), Token(TokenType.DIVIDE, /), BinaryOpNode(NumberNode(Token(TokenType.NUMBER, 2)), Token(TokenType.PLUS, +), NumberNode(Token(TokenType.NUMBER, 1)))), Token(TokenType.MULTIPLY, *), BinaryOpNode(NumberNode(Token(TokenType.NUMBER, 2)), Token(TokenType.MINUS, -), NumberNode(Token(TokenType.NUMBER, 1))))), CallNode(FunctionNode(Token(TokenType.FUNCTION, print)), [VariableNode(Token(TokenType.VARIABLE, t)), BinaryOpNode(VariableNode(Token(TokenType.VARIABLE, y)), Token(TokenType.PLUS, +), NumberNode(Token(TokenType.NUMBER, 4))), VariableNode(Token(TokenType.VARIABLE, x)), BinaryOpNode(VariableNode(Token(TokenType.VARIABLE, x)), Token(TokenType.PLUS, +), NumberNode(Token(TokenType.NUMBER, 2)))]), AssignmentNode(VariableNode(Token(TokenType.VARIABLE, c)), VariableNode(Token(TokenType.VARIABLE, t)))]

Symbol Table: {'x': 3, 'y': 4, 't': -1.6666666666666667, 'c': -1.6666666666666667}
