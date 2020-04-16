from grammar.PipedParser import PipedParser


class TypeDict:
    def __init__(self):
        self.types = {}

    def getType(self, ast: PipedParser.Type_Context):
        # Not perfect, because Records can be reordered
        if str(ast) not in self.types:
            self.types[str(ast)] = Type.getType(ast)
        return self.types[str(ast)]


class Type:
    def __init__(self, union_inter=None):
        if union_inter is None:
            self.union_inter = [[]]
        else:
            self.union_inter = union_inter

    @staticmethod
    def getType(ctx: PipedParser.Type_Context):
        if isinstance(ctx, PipedParser.UnionTypeContext):
            return Type.getType(ctx.type_(0)) | Type.getType(ctx.type_(1))
        elif isinstance(ctx, PipedParser.IntersectionTypeContext):
            return Type.getType(ctx.type_(0)) - Type.getType(ctx.type_(1))
        elif isinstance(ctx, PipedParser.KeyofTypeContext):
            return Type([[KeyofType(Type.getType(ctx.type_()))]])
        elif isinstance(ctx, PipedParser.WrappedTypeContext):
            return Type.getType(ctx.type_())
        elif isinstance(ctx, PipedParser.GenericTypeContext):
            return Type(
                [
                    [
                        GenericType(
                            Type.getType(ctx.type_(0)),
                            [
                                Type.getType(type_)
                                for i, type_ in enumerate(ctx.type_())
                                if i != 0
                            ],
                        )
                    ]
                ]
            )
        elif isinstance(ctx, PipedParser.TupleTypeContext):
            return Type([[TupleType([Type.getType(type_) for type_ in ctx.type_()],)]])
        elif isinstance(ctx, PipedParser.NamedTupleContext):
            return Type(
                [
                    [
                        NamedTupleType(
                            {
                                iden: type_
                                for iden, type_ in zip(ctx.IDENTIFIER(), ctx.type_())
                            }
                        )
                    ]
                ]
            )
        elif isinstance(ctx, PipedParser.RecordTypeContext):
            return Type(
                [
                    [
                        RecordType(
                            {
                                iden: type_
                                for iden, type_ in zip(ctx.IDENTIFIER(), ctx.type_())
                            }
                        )
                    ]
                ]
            )
        elif isinstance(ctx, PipedParser.SimpleTypeContext):
            return Type([[SimpleType(ctx.IDENTIFIER())]])

    def __or__(self, other):
        if not isinstance(other, Type):
            raise ValueError(
                f"{self!r} cannot be unioned with {other!r} of type {Type!r}"
            )
        return Type(self.union_inter + other.union_inter)

    def __sub__(self, other):
        if not isinstance(other, Type):
            raise ValueError(
                f"{self!r} cannot be intersectioned with {other!r} of type {Type!r}"
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


class KeyofType(Type):
    def __init__(self, type_):
        self.type_ = type_


class GenericType(Type):
    def __init__(self, main_type, generics):
        self.main_type = main_type
        self.generics = generics


class TupleType(Type):
    def __init__(self, items):
        self.items = items


class NamedTupleType(Type):
    def __init__(self, items):
        self.items = items


class RecordType(Type):
    def __init__(self, items):
        self.items = items


class SimpleType(Type):
    def __init__(self, name):
        self.name = name


class Value:
    def __init__(self, value, type_):
        self.actual = value
        self.type_ = type_


class Int:
    def __init__(self):
        super().__init__()


class Var:
    def __init__(self, value, type_):
        self.value = value
        self.type_ = type_


class Scope:
    def __init__(self):
        self.types = TypeDict()
        self.vars = {}  # Dict[str, Var]


class ModuleScope:
    def __init__(self):
        self.public
