from parser import parser

def_expr_value_parser = parser.Combinator(
    parser.DefExpr[parser.ValueStmt],
    parser.Parser(parser.DefStmt),
    parser.Parser(parser.ValueStmt),
)

# def_expr_lambda_parser = parser.Combinator(
#     parser.DefExpr[parser.LambdaStmt],
#     parser.Parser(parser.DefStmt),
#     parser.Parser(parser.LambdaStmt),
# )

test = b"def x = value: 20 \n x + 2"
# Як ці дві тєми розрізнити на рантаймі??
# 1. Робити токєни і далі чекати лівий і правий токєн в dict і юзати парсер комбінатор?
# Steps:
# Читати курсором токєни і додавати в stack,
# далі ім'я подивитись чи є в символах(Exception), і скіпнути назву
# далі має бути =, якщо нема то тоже Exception
# Далі запарсити некс нейм, і додати в стак.
# Далі подивитись комбінацію:
# {[DefStmt, LambdaStmt]: def_expr_lambda_parser}

# val = (2-(2+4+(3-2)))/(2+1)*(2-1)
# print(val)

result = eval("(2-(2+4+(3-2)))/(2+1)*(2-1)")
print("result", result)

# test_lambda = b"def y = lambda: 1 + 1"
# test_lambda = b"def y = lambda: 1 + value: 1"

# lambda: 1 + 1  == value: 20

def_expr_token, next_bytes = def_expr_value_parser.combine(test)
print(def_expr_token.content_stmt.value)
# print("next bytes", next_bytes)
# print(def_expr_token)

sum = b"x + y"
