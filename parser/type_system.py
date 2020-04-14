from typing import List, Dict

# class Constraint:
#     pass


# class Alternative:
#     pass


# class Subscripted:
#     pass


# class Type:
#     def __init__(self, repr):
#         self._repr = repr

#     def __repr__(self):
#         return self._repr


# # int
# Type("int")

# # int | string
# Type(
#     Alternative((Type("int"), Type("string")))
# )  # or Type(Alternative(('int', 'string')))

# # (float, float, string)
# Type(Subscripted({0: "float", 1: "float", 2: "string"}))

# # {name=string, age=int}   --- aka, record
# Type(Subscripted({"name": "string", "age": "int"}))

# # (name=string, age=int)   --- aka, named_tuple
# Type(Subscripted({"name": "string", "age": "int", 0: "string", 1: "int"}))

# (int, float) | (int, int) =? (int, int | float)

# def func(arg: (int, int)) -> irrelavent
# def func(arg: (float, float)) -> irrelavent
# def func(arg) {
#     arg # type (int, int) | (float, float)
#     arg[0] # type int | float
#     if typeof arg[0] == int {
#         arg[1] # type int
#     } else {
#         arg[1] # type float
#     }
# }

# What this is doing is first checking if all alternatives of `arg` allow subscript `0`
# If it does, then what it really checks is if `(typeof arg)[0]` is `int`


class Type:
    def __init__(self, repr_):
        self.x = 1
        if isinstance(repr_, list):
            self._repr = repr_
        else:
            self._repr = [[repr_ if isinstance(repr_, str) else repr(repr_)]]

    def __repr__(self):
        return "|".join("-".join(c for c in alt) for alt in self._repr)

    def __or__(self, other):
        if isinstance(other, Type):
            return Type(self._repr + other._repr)
        return Type(self._repr + [[other]])

    def __sub__(self, other):
        if isinstance(other, Type):
            return Type(
                sum(([con1 + con2 for con1 in self._repr] for con2 in other._repr), [])
            )


# def parse_type(s: str):
#     return Type([x.replace(" ", "").split("-") for x in s.split("|")])


class Subscript(Type):
    def __init__(self, key, value):
        super().__init__(f"subscript<{key}, {value}>")
        self._key = key
        self._value = value


class Add(Type):
    def __init__(self, addend, result):
        super().__init__(f"add<{addend}, {result}>")
        self._addend = addend
        self._result = result


class Record(Type):
    def __init__(self, dict_):
        super().__init__(
            "{" + ", ".join(f"{k}={v._repr}" for k, v in dict_.items()) + "}"
        )
        self._dict = dict_


class NamedTuple(Type):
    def __init__(self, dict_):
        super().__init__(
            "(" + ", ".join(f"{k}={v._repr}" for k, v in dict_.items()) + ")"
        )
        self._dict = dict_

    def __getitem__(self, attr):
        try:
            return self._dict[attr]
        except KeyError:
            raise KeyError("whoops!")


# recursiveType = Type("...")
# string = Type("string")
# int_ = Type("int")
# float_ = Type("float")
# unknown = Type("unknown")
