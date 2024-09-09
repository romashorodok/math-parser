import re


class Parser:
    def __init__(self, parse_fn):
        self.parse_fn = parse_fn

    def parse(self, text):
        result = self.parse_fn(text)
        print(f"Parsing '{text}': {result}")
        return result

    def __or__(self, other):
        return Parser(lambda text: self.parse(text) or other.parse(text))

    def __rshift__(self, other):
        return Parser(
            lambda text: [
                (res2, text2)
                for (res1, text1) in self.parse(text)
                for (res2, text2) in other.parse(text1)
            ]
        )

    def map(self, func):
        return Parser(
            lambda text: [(func(res), text1) for (res, text1) in self.parse(text)]
        )


def literal(s):
    return Parser(lambda text: [(s, text[len(s) :])] if text.startswith(s) else [])


def regex(rgx):
    return Parser(
        lambda text: [(m.group(0), text[m.end() :]) for m in [re.match(rgx, text)] if m]
    )


def many(p):
    def parse(text):
        result = []
        while True:
            parsed = p.parse(text)
            if parsed:
                res, text = parsed[0]
                result.append(res)
            else:
                break
        return [(result, text)] if result else [([], text)]

    return Parser(parse)


def sequence(*parsers):
    def parse(text):
        results = []
        current_text = text
        for parser in parsers:
            if callable(parser):
                parser = parser()  # Call the function if it's a callable
            if not isinstance(parser, Parser):
                raise TypeError("Expected a Parser instance.")
            parsed = parser.parse(current_text)
            if not parsed:
                return []
            result, current_text = parsed[0]
            results.append(result)
        return [(results, current_text)]

    return Parser(parse)


def choice(*parsers):
    def parse(text):
        for parser in parsers:
            if callable(parser):
                parser = parser()  # Call the function if it's a callable
            if not isinstance(parser, Parser):
                raise TypeError("Expected a Parser instance.")
            result = parser.parse(text)
            if result:
                return result
        return []

    return Parser(parse)


def optional(p):
    return Parser(lambda text: p.parse(text) or [([], text)])


def one_of(chars):
    return Parser(
        lambda text: [
            (text[0], text[1:]) if text and text[0] in chars else (None, text)
        ]
    )


def parens(p):
    return sequence(literal("("), p, literal(")")).map(lambda res: res[1])


def number():
    return regex(r"\d+").map(int)


def symbol(sym):
    return literal(sym) >> optional(regex(r"\s*"))


def make_expression_parsers():
    def factor():
        return choice(
            number(),
            parens(expression),  # Use the expression parser here
        )

    def term():
        return sequence(
            factor(),
            many(
                choice(symbol("*").map(lambda _: "*"), symbol("/").map(lambda _: "/"))
                >> factor()
            ),
        ).map(lambda res: flatten_term(res))

    def expression():
        return sequence(
            term(),
            many(
                choice(symbol("+").map(lambda _: "+"), symbol("-").map(lambda _: "-"))
                >> term()
            ),
        ).map(lambda res: flatten_expression(res))

    return expression()


def flatten_term(res):
    factors, ops = res
    if not isinstance(factors, list):
        factors = [factors]

    result = factors[0] if factors else None

    for op, factor in zip(ops[::2], ops[1::2]):
        if isinstance(result, list) and len(result) == 1:
            result = result[0]

        if not isinstance(factor, list):
            factor = [factor]

        result = [op, result] + factor

    return result


def flatten_expression(res):
    terms, ops = res
    if not isinstance(terms, list):
        terms = [terms]

    result = terms[0]

    for op, term in zip(ops[::2], ops[1::2]):
        result = [op, result, term]

    return result


def eval_tokens(tokens):
    def apply_operator(op, left, right):
        if op == "+":
            return left + right
        elif op == "-":
            return left - right
        elif op == "*":
            return left * right
        elif op == "/":
            return left / right
        else:
            raise ValueError(f"Unknown operator: {op}")

    def eval_expr(expr):
        if isinstance(expr, int):
            return expr
        elif isinstance(expr, list):
            op = expr[0]
            if op in ["*", "/"]:
                left = eval_expr(expr[1])
                right = eval_expr(expr[2])
                return apply_operator(op, left, right)
            elif op in ["+", "-"]:
                left = eval_expr(expr[1])
                right = eval_expr(expr[2])
                return apply_operator(op, left, right)
        else:
            raise ValueError("Invalid expression")

    return eval_expr(tokens)


def test_custom_operation():
    expression_parser = make_expression_parsers()  # Get the parser instance
    test_input = "(2-(2+4+(3-2)))/(2+1)*(2-1)"
    parsed = expression_parser.parse(test_input)  # Parse the input
    print("Parsed tokens:", parsed)
    if parsed:
        result = eval_tokens(parsed[0][0])  # Evaluate the result
        print("Result for custom operation:", result)
    else:
        print("Parsing failed.")


test_custom_operation()
