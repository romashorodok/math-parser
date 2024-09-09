from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Generic, Self, TypeVar


class Lexem(StrEnum):
    DEF = "def"
    EQUALS = "="
    LAMBDA = "lambda"


class Token(ABC):
    @classmethod
    @abstractmethod
    def from_bytes(cls, values: bytes) -> tuple[Self, bytes]:
        raise NotImplementedError


Token_T = TypeVar("Token_T", bound=Token, covariant=True)


class DefStmt(Token):
    def __init__(self, values: bytes) -> None:
        print("recv", values)

    @classmethod
    def from_bytes(cls, values: bytes) -> tuple[Self, bytes]:
        # TODO: make cursor and lexem read
        for idx, byte in enumerate(values):
            print("get bytes", byte)

            if byte == int.from_bytes(b"="):
                curr = values[:idx]
                rest = values[idx + 1 :]
                return (cls(curr), rest)

        raise ValueError("Unable parse expr")


class LambdaStmt(Token):
    @classmethod
    def from_bytes(cls, values: bytes) -> tuple[Self, bytes]:
        raise NotImplementedError


class ValueStmt(Token):
    def __init__(self, value: int) -> None:
        self.value = value

    @classmethod
    def from_bytes(cls, values: bytes) -> tuple[Self, bytes]:
        values = values.replace(b"value: ", b"")

        for idx, byte in enumerate(values):
            if byte == int.from_bytes(b"\n"):
                curr = values[:idx]
                rest = values[idx:]
                curr = curr.replace(b" ", b"")
                return (cls(int(curr.decode())), rest)

        raise ValueError("Unable parse expr")


class CombinatorToken(Token):
    def __init__(self, t1: Token, t2: Token) -> None:
        raise NotImplementedError

    @classmethod
    def from_bytes(cls, values: bytes) -> tuple[Self, bytes]:
        raise NotImplementedError


Combinator_T = TypeVar(
    "Combinator_T", infer_variance=False, covariant=True, bound=CombinatorToken
)


class DefExpr(Generic[Token_T], CombinatorToken):
    def __init__(self, def_stmt: Token, content_stmt: Token_T) -> None:
        if not isinstance(def_stmt, DefStmt):
            raise ValueError("Invalid def expr statement")
        self.__def_stmt = def_stmt

        self.content_stmt = content_stmt
        print("DefExp", self.__def_stmt, self.content_stmt)


class Parser(Generic[Token_T]):
    def __init__(self, t: type[Token_T]) -> None:
        self.__type = t

    def parse(self, values: bytes) -> tuple[Token_T, bytes]:
        return self.__type.from_bytes(values)


class Combinator(Generic[Combinator_T]):
    def __init__(
        self, t: type[Combinator_T], p1: Parser[Token_T], p2: Parser[Token_T]
    ) -> None:
        self.__p1 = p1
        self.__p2 = p2
        self.__type = t

    def combine(self, values: bytes) -> tuple[Combinator_T, bytes]:
        token1, next_bytes = self.__p1.parse(values)
        print("token1", token1)

        token2, rest_bytes = self.__p2.parse(next_bytes)
        print("token2", token2)

        return (self.__type(token1, token2), rest_bytes)
