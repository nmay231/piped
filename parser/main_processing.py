from grammar.PipedListener import PipedListener
from grammar.PipedParser import PipedParser
from grammar.PipedVisitor import PipedVisitor
from dataclasses import dataclass
from typing import List, Dict, Any, Union
from collections import defaultdict


# Load all enter*() and exit*() functions in grammar_registry.* modules
from grammar_registry import *
import grammar_registry

listeners = defaultdict(list)
for mod_name in dir(grammar_registry):
    if mod_name.startswith("_"):
        continue
    mod = getattr(grammar_registry, mod_name)
    for item_name in dir(mod):
        if not callable(getattr(mod, item_name)):
            continue
        if item_name.startswith("exit") or item_name.startswith("enter"):
            listeners[item_name].append(getattr(mod, item_name))
        else:
            print(f"Warning: Ignoring function {mod_name}.{item_name}")


@dataclass
class HoldPlease:
    data_map: Dict[str, Any] = None


Type = Union["SimpleType", "SuperType"]


@dataclass
class SimpleType:
    name: str


@dataclass
class SuperType:
    which: str  # 'generic' | 'intersection' | 'union' | 'tuple'
    main: Union[Type, None]
    sub: Union[List[Type], None]


@dataclass
class Value:
    name: str
    type: Type


@dataclass
class Name:
    name: str
    value: Value
    type: Type


st = SimpleType
St = SuperType
default_global_scope = {
    "int": Name(
        "int",
        # The "value" is a function that can receive an object and convert it to an int
        # e.g. `int: (val: any) -> int` which is represented as `call<(to<int>,), int>`
        Value(
            "int",
            St(
                "generic",
                st("call"),
                [St("tuple", None, [St("generic", st("to"), [st("int")]), st("int")])],
            ),
        ),
        # The type is the type itself. Much simpler
        st("int"),
    )
}


class ListenerAPI(PipedListener):
    def __init__(self, meta_data=None):
        super().__init__()
        self.listeners = defaultdict(list)
        if not meta_data:
            self.meta_data = HoldPlease()
        else:
            self.meta_data = meta_data
        for ruleMethod in dir(self):
            if (ruleMethod.startswith("enter") or ruleMethod.startswith("exit")) and (
                ruleMethod not in ("enterEveryRule", "exitEveryRule")
            ):
                setattr(self, ruleMethod, self.mockRule(ruleMethod))

    def mockRule(self, name: str):
        def func(ast):
            if name not in self.listeners:
                return
            for listener in self.listeners[name]:
                listener(ast, self.meta_data)

        return func


class VisitorAPI(PipedVisitor):
    def __init__(self, meta_data=None):
        super().__init__()
        self.visitors = defaultdict(list)
        if not meta_data:
            self.meta_data = HoldPlease()
            self.meta_data.global_scope = {}
            self.meta_data.public_scope = {}
            self.meta_data.private_scope = {}
        else:
            self.meta_data = meta_data

    def visit(self, tree, traversal_state):
        self.meta_data.state = traversal_state
        super().visit(tree)

    def register(self, node: str, visitor: Any):
        self.visitors[node].append(visitor)

    def visitModule(self, ctx: PipedParser.ModuleContext):
        for visitor in self.visitors["module"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitTopLevel(self, ctx: PipedParser.TopLevelContext):
        for visitor in self.visitors["topLevel"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitImportStatement(self, ctx: PipedParser.ImportStatementContext):
        for visitor in self.visitors["importStatement"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitImportName(self, ctx: PipedParser.ImportNameContext):
        for visitor in self.visitors["importName"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitReceiveEntry(self, ctx: PipedParser.ReceiveEntryContext):
        for visitor in self.visitors["receiveEntry"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitFunctionDefinition(self, ctx: PipedParser.FunctionDefinitionContext):
        for visitor in self.visitors["functionDefinition"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitBlockBody(self, ctx: PipedParser.BlockBodyContext):
        for visitor in self.visitors["blockBody"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitInstruction(self, ctx: PipedParser.InstructionContext):
        for visitor in self.visitors["instruction"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitAssignmentStatement(self, ctx: PipedParser.AssignmentStatementContext):
        for visitor in self.visitors["assignmentStatement"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitExpressionStatement(self, ctx: PipedParser.ExpressionStatementContext):
        for visitor in self.visitors["expressionStatement"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitBreakStatement(self, ctx: PipedParser.BreakStatementContext):
        for visitor in self.visitors["breakStatement"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitContinueStatement(self, ctx: PipedParser.ContinueStatementContext):
        for visitor in self.visitors["continueStatement"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitReturnStatement(self, ctx: PipedParser.ReturnStatementContext):
        for visitor in self.visitors["returnStatement"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitDefFunctionStatement(self, ctx: PipedParser.DefFunctionStatementContext):
        for visitor in self.visitors["functionStatement"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitForLoop(self, ctx: PipedParser.ForLoopContext):
        for visitor in self.visitors["forLoop"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitConditional(self, ctx: PipedParser.ConditionalContext):
        for visitor in self.visitors["conditional"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitAssignment(self, ctx: PipedParser.AssignmentContext):
        for visitor in self.visitors["assignment"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitOptionalAccessField(self, ctx: PipedParser.OptionalAccessFieldContext):
        for visitor in self.visitors["optionalAccessField"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitArrowFunction(self, ctx: PipedParser.ArrowFunctionContext):
        for visitor in self.visitors["arrowFunction"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitSubscript(self, ctx: PipedParser.SubscriptContext):
        for visitor in self.visitors["subscript"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitExponentiation(self, ctx: PipedParser.ExponentiationContext):
        for visitor in self.visitors["exponentiation"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitAccessField(self, ctx: PipedParser.AccessFieldContext):
        for visitor in self.visitors["accessField"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitTupleExpr(self, ctx: PipedParser.TupleExprContext):
        for visitor in self.visitors["tupleExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitUnary(self, ctx: PipedParser.UnaryContext):
        for visitor in self.visitors["unary"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitMultiplyDivide(self, ctx: PipedParser.MultiplyDivideContext):
        for visitor in self.visitors["multiplyDivide"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitBooleanAndOr(self, ctx: PipedParser.BooleanAndOrContext):
        for visitor in self.visitors["booleanAndOr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitSetExpr(self, ctx: PipedParser.SetExprContext):
        for visitor in self.visitors["setExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitBooleanCompare(self, ctx: PipedParser.BooleanCompareContext):
        for visitor in self.visitors["booleanCompare"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitIdentifierExpr(self, ctx: PipedParser.IdentifierExprContext):
        for visitor in self.visitors["identifierExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitConstString(self, ctx: PipedParser.ConstStringContext):
        for visitor in self.visitors["constString"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitListExpr(self, ctx: PipedParser.ListExprContext):
        for visitor in self.visitors["listExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitFunctionCall(self, ctx: PipedParser.FunctionCallContext):
        for visitor in self.visitors["functionCall"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitDictionaryExpr(self, ctx: PipedParser.DictionaryExprContext):
        for visitor in self.visitors["dictionaryExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitParenExpr(self, ctx: PipedParser.ParenExprContext):
        for visitor in self.visitors["parenExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitConstFloat(self, ctx: PipedParser.ConstFloatContext):
        for visitor in self.visitors["constFloat"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitConstInteger(self, ctx: PipedParser.ConstIntegerContext):
        for visitor in self.visitors["constInteger"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitRecordExpr(self, ctx: PipedParser.RecordExprContext):
        for visitor in self.visitors["recordExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitNamedTupleExpr(self, ctx: PipedParser.NamedTupleExprContext):
        for visitor in self.visitors["namedTupleExpr"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitAddSubtract(self, ctx: PipedParser.AddSubtractContext):
        for visitor in self.visitors["addSubtract"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitDictionary(self, ctx: PipedParser.DictionaryContext):
        for visitor in self.visitors["dictionary"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitTuple_(self, ctx: PipedParser.Tuple_Context):
        for visitor in self.visitors["tuple_"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitNamedItem(self, ctx: PipedParser.NamedItemContext):
        for visitor in self.visitors["namedItem"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitRecord(self, ctx: PipedParser.RecordContext):
        for visitor in self.visitors["record"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitNamedTuple(self, ctx: PipedParser.NamedTupleContext):
        for visitor in self.visitors["namedTuple"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitList_(self, ctx: PipedParser.List_Context):
        for visitor in self.visitors["list_"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitSet_(self, ctx: PipedParser.Set_Context):
        for visitor in self.visitors["set_"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitSimpleType(self, ctx: PipedParser.SimpleTypeContext):
        for visitor in self.visitors["simpleType"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitUnionType(self, ctx: PipedParser.UnionTypeContext):
        for visitor in self.visitors["unionType"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitGenericType(self, ctx: PipedParser.GenericTypeContext):
        for visitor in self.visitors["genericType"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitIntersectionType(self, ctx: PipedParser.IntersectionTypeContext):
        for visitor in self.visitors["intersectionType"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)

    def visitKeyofType(self, ctx: PipedParser.KeyofTypeContext):
        for visitor in self.visitors["keyofType"]:
            visitor(ctx, self.meta_data)
        return self.visitChildren(ctx)


@dataclass
class loadModule:
    name: str
    item: str = None


@dataclass
class Instruction:
    which: str
    data: Any


@dataclass
class defineFunction:
    name: str
    arguments: Dict[str, str]
    body: List[Instruction] = None


@dataclass
class receiveEntry:
    name: str
    arguments: Dict[str, str]
    body: List[Instruction] = None


@dataclass
class MetaData:
    public: Dict[str, Any]
    private: Dict[str, Any]
    scopes: List[Dict[str, Any]]
    whereAmI: Any = None


@dataclass
class ExplicitType:
    which: str
    children: List[Union[str, "ExplicitType"]]


@dataclass
class ValueHolder:
    v: Any
    type_: Any = None


@dataclass
class Variable:
    name: str
    type_: ExplicitType
    value: ValueHolder


# class GetModuleDefinitions(PipedVisitor):
#     def visitModule(self, ctx: PipedParser.ModuleContext):
#         self.meta = MetaData({}, {}, [])
#         self.meta.scopes = [self.meta.public, self.meta.private]
#         self.visitChildren(ctx)

#     def visitImportStatement(self, ctx: PipedParser.ImportStatementContext):
#         children = [child for child in ctx.getChildren()]
#         module_name = children[1].getText()
#         if len(children) == 2:
#             # import module_name
#             self.meta.private[module_name] = loadModule(module_name)
#         elif len(children) == 4 and str(children[0]) == "import":
#             # import module_name as alias
#             self.meta.private[str(children[3])] = loadModule(module_name)
#         else:
#             imports = " ".join(map(str, children[3:])).split(" , ")
#             for import_ in imports:
#                 import_ = import_.split(" ")
#                 if len(import_) == 1:
#                     self.meta.private[import_[0]] = loadModule(module_name, import_[0])
#                 else:
#                     self.meta.private[import_[2]] = loadModule(module_name, import_[0])

#     def visitFunctionDefinition(self, ctx: PipedParser.FunctionDefinitionContext):
#         name = str(ctx.IDENTIFIER(0))
#         args = ctx.IDENTIFIER()[1:]
#         self.meta.public[name] = defineFunction(name, list(map(str, args)))

#     def visitReceiveEntry(self, ctx: PipedParser.ReceiveEntryContext):
#         name = str(ctx.IDENTIFIER(0))
#         args = ctx.IDENTIFIER()[1:]
#         self.meta.public[name] = receiveEntry(name, list(map(str, args)))


# class TreeAnnotater(PipedVisitor):
#     def __init__(self, meta: MetaData):
#         super().__init__()
#         self.meta = meta
#         # print(meta)

#     def visitFunctionOverload(self, ctx):
#         pass  # Not implemented yet

#     def visitFunctionDefinition(self, ctx: PipedParser.FunctionDefinitionContext):
#         name = str(ctx.IDENTIFIER(0))
#         scope = {}
#         self.meta.scopes.append(scope)
#         self.meta.whereAmI = name
#         self.meta.public[name].body = []
#         self.visitChildren(ctx)
#         self.meta.whereAmI = None

#     def visitReceiveEntry(self, ctx: PipedParser.ReceiveEntryContext):
#         name = str(ctx.IDENTIFIER(0))
#         scope = {}
#         self.meta.scopes.append(scope)
#         self.meta.whereAmI = name
#         self.meta.public[name].body = []
#         self.visitChildren(ctx)
#         self.meta.whereAmI = None

#     def visitAssignmentStatement(self, ctx: PipedParser.AssignmentStatementContext):
#         assignment = self.visit(ctx.assignment())
#         self.meta.public[self.meta.whereAmI].body.append(
#             Instruction("assignment", assignment)
#         )

#     def visitAssignment(self, ctx: PipedParser.AssignmentContext):
#         name = str(ctx.IDENTIFIER())
#         value = self.visit(ctx.expr())
#         var = Variable(name, value.type_, value)
#         return (str(ctx.IDENTIFIER()), var)

#     def visitConstNumber(self, ctx: PipedParser.ConstNumberContext):
#         value = str(ctx.NUMBER())
#         if value.isdigit():
#             return ValueHolder(int(value), ExplicitType("simple", ["int"]))
#         return ValueHolder(float(value), ExplicitType("simple", ["float"]))
