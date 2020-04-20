from grammar.PipedParser import PipedParser
from dataclasses import dataclass
import typing


class TypeMaster:
    def __init__(self):
        self.type_def_map = {}

    def getType(self, ctx: PipedParser.Type_Context):
        if isinstance(ctx, PipedParser.UnionTypeContext):
            return self.getType(ctx.type_(0)) | self.getType(ctx.type_(1))
        elif isinstance(ctx, PipedParser.IntersectionTypeContext):
            return self.getType(ctx.type_(0)) - self.getType(ctx.type_(1))
        elif isinstance(ctx, PipedParser.KeyofTypeContext):
            return KeyofType(self.getType(ctx.type_()))
        elif isinstance(ctx, PipedParser.WrappedTypeContext):
            return self.getType(ctx.type_())
        elif isinstance(ctx, PipedParser.GenericTypeContext):
            return GenericType(
                self.getType(ctx.type_(0)),
                [self.getType(type_) for i, type_ in enumerate(ctx.type_()) if i != 0],
            )
        elif isinstance(ctx, PipedParser.TupleTypeContext):
            type_ = TupleType([self.getType(type_) for type_ in ctx.type_()])
            self.type_def_map[type_] = type_.type_def()
            return type_
        elif isinstance(ctx, PipedParser.NamedTupleTypeContext):
            type_ = NamedTupleType(
                [
                    (str(iden), self.getType(type_))
                    for iden, type_ in zip(ctx.IDENTIFIER(), ctx.type_())
                ]
            )
            self.type_def_map[type_] = type_.type_def()
            return type_
        elif isinstance(ctx, PipedParser.RecordTypeContext):
            type_ = RecordType(
                [
                    (str(iden), self.getType(type_))
                    for iden, type_ in zip(ctx.IDENTIFIER(), ctx.type_())
                ]
            )
            self.type_def_map[type_] = type_.type_def()
            return type_
        elif isinstance(ctx, PipedParser.SimpleTypeContext):
            return SimpleType(str(ctx.IDENTIFIER()))

    def generate(self):
        return "\n".join(type_.generate() for type_ in self.type_def_map.keys())


class Type:
    id_ = 1

    def __init__(self, union_inter=None):
        if union_inter is None:
            self.union_inter = [[]]
        else:
            self.union_inter = union_inter
        self.id_ = Type.id_
        Type.id_ += 1

    def generate(self):
        return "\n".join(gen.generate() for gen in sum(self.union_inter, []))

    def type_def(self):
        if len(self.union_inter) == len(self.union_inter[0]) == 1:
            return self.union_inter[0][0].type_def()
        raise Exception("Not implemented yet!")

    def __or__(self, other):
        if not isinstance(other, Type):
            raise ValueError(
                f"{self!r} cannot be unioned with {other!r} of type {Type!r}"
            )
        return Type(self.union_inter + other.union_inter)

    def __sub__(self, other):
        if not isinstance(other, Type):
            raise ValueError(
                f"{self!r} cannot be intersectioned with {other!r} of type {other.__class__!r}"
            )
        return Type(
            sum(
                (
                    [inter1 + inter2 for inter1 in self.union_inter]
                    for inter2 in other.union_inter
                ),
                [],
            )
        )

    def __repr__(self):
        return (
            "T("
            + "|".join("-".join(str(c) for c in alt) for alt in self.union_inter)
            + ")"
        )

    def __hash__(self):
        return self.id_


class KeyofType(Type):
    def __init__(self, type_):
        self.type_ = type_
        super().__init__([[self]])

    def __str__(self):
        return f"keyof {self.type_}"


class GenericType(Type):
    def __init__(self, main_type, generics):
        self.main_type = main_type
        self.generics = generics
        super().__init__([[self]])

    def __str__(self):
        return f'{self.main_type}<{self.generics.join(", ")}>'


class TupleType(Type):
    def __init__(self, items):
        self.items = items
        super().__init__([[self]])

    def __str__(self):
        if not self.items:
            return "(,)"
        elif len(self.items) == 1:
            return f"({self.items[0]},)"
        return f'({self.items.join(", ")})'


class NamedTupleType(Type):
    def __init__(self, items):
        self.items = items
        super().__init__([[self]])

    def __str__(self):
        if not self.items:
            return "(=)"
        repr_ = ", ".join([f"{name}={val}" for name, val in self.items])
        return f"({repr_})"

    def generate(self):
        return (
            f"struct named_tuple_type{self.id_}"
            + " {\n  "
            + "\n  ".join(f"{type_.type_def()} {name};" for name, type_ in self.items)
            + "\n};"
        )

    def type_def(self):
        return f"struct named_tuple_type{self.id_}"


class RecordType(Type):
    def __init__(self, items):
        self.items = items
        super().__init__([[self]])

    def __str__(self):
        if not self.items:
            return "{=}"
        repr_ = ", ".join([f"{name}={val}" for name, val in self.items])
        return "{" + repr_ + "}"

    def generate(self):
        return (
            f"struct record_type{self.id_}"
            + " {\n  "
            + "\n  ".join(f"{type_.type_def()} {name};" for name, type_ in self.items)
            + "\n};"
        )

    def type_def(self):
        return f"struct record_type{self.id_}"


class SimpleType(Type):
    def __init__(self, name):
        self.name = name
        super().__init__([[self]])

    def __str__(self):
        return str(self.name)

    def generate(self):
        return ""

    def type_def(self):
        if self.name in ("int", "float"):
            return self.name
        elif self.name == "string":
            return "char*"
        else:
            raise ValueError(
                f'generated type of "{self.__class__}" is unknown "{self.name}"'
            )


class Statement:
    pass


class AssignmentStatement(Statement):
    def __init__(self, var: "Variable"):
        super().__init__()
        self.variable = var

    def generate(self):
        return f"{self.variable.type.type_def()} {self.variable.name} = {self.variable.value.generate()};"


# simple class as a dynamic data store
class HoldPlease:
    pass


@dataclass
class ReceiveEntry:
    name: str
    arguments: typing.List[int]
    return_: str
    body: typing.Any

    def generate(self):
        return (
            f"void receive_entry_{self.name}(void)"
            "{\n  " + "\n  ".join(stm.generate() for stm in self.body) + "\n}"
        )


@dataclass
class Record:
    repr: typing.Dict[str, typing.Any]
    # type: in the future

    def generate(self):
        # This needs to be based off of its type in the future so that
        # the items are not out of order or something like that
        return "{" f'{", ".join(val.generate() for val in self.repr.values())}' "}"


@dataclass
class NamedTuple:
    repr: typing.List[typing.Tuple[str, typing.Any]]
    # type: in the future

    def generate(self):
        # This needs to be based off of its type in the future so that
        # the items are not out of order or something like that
        return "{" f'{", ".join(x[1].generate() for x in self.repr)}' "}"


@dataclass
class Tuple:
    repr: typing.List[typing.Any]
    # type: in the future


@dataclass
class List:
    repr: typing.List[typing.Any]
    # type: in the future


@dataclass
class Integer:
    repr: str

    def generate(self):
        return self.repr


@dataclass
class Float:
    repr: str

    def generate(self):
        return self.repr


@dataclass
class String:
    repr: str

    def generate(self):
        # Force strings to use double quotes
        return f'"{eval(self.repr)}"'


@dataclass
class Variable:
    name: str
    value: typing.Any
    type: typing.Any
