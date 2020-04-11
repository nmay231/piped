from grammar.PipedListener import PipedListener
from grammar.PipedParser import PipedParser
from grammar.PipedVisitor import PipedVisitor
from dataclasses import dataclass
from typing import List, Dict, Any


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
class MetaData:
    public: Dict[str, Any]
    private: Dict[str, Any]
    scopes: List[Dict[str, Any]]
    whereAmI: Any = None


class GetModuleDefinitions(PipedVisitor):
    def visitModule(self, ctx: PipedParser.ModuleContext):
        self.meta = MetaData({}, {}, [])
        self.meta.scopes = [self.meta.public, self.meta.private]
        self.visitChildren(ctx)

    def visitImportStatement(self, ctx: PipedParser.ImportStatementContext):
        children = [child for child in ctx.getChildren()]
        module_name = children[1].getText()
        if len(children) == 2:
            # import module_name
            self.meta.private[module_name] = loadModule(module_name)
        elif len(children) == 4 and str(children[0]) == "import":
            # import module_name as alias
            self.meta.private[str(children[3])] = loadModule(module_name)
        else:
            imports = " ".join(map(str, children[3:])).split(" , ")
            for import_ in imports:
                import_ = import_.split(" ")
                if len(import_) == 1:
                    self.meta.private[import_[0]] = loadModule(module_name, import_[0])
                else:
                    self.meta.private[import_[2]] = loadModule(module_name, import_[0])

    def visitFunctionDefinition(self, ctx: PipedParser.FunctionDefinitionContext):
        name = str(ctx.IDENTIFIER(0))
        args = ctx.IDENTIFIER()[1:]
        self.meta.public[name] = defineFunction(name, list(map(str, args)))


class TreeAnnotater(PipedVisitor):
    def __init__(self, meta: MetaData):
        super().__init__()
        self.meta = meta
        # print(meta)

    def visitFunctionOverload(self, ctx):
        pass  # Not implemented yet

    def visitFunctionDefinition(self, ctx: PipedParser.FunctionDefinitionContext):
        name = str(ctx.IDENTIFIER(0))
        scope = {}
        self.meta.scopes.append(scope)
        self.meta.whereAmI = name
        self.meta.public[name].body = []
        self.visitChildren(ctx)
        self.meta.whereAmI = None

    def visitAssignmentStatement(self, ctx: PipedParser.AssignmentStatementContext):
        assignment = self.visit(ctx.assignment())
        self.meta.public[self.meta.whereAmI].body.append(
            Instruction("assignment", assignment)
        )

    def visitAssignment(self, ctx: PipedParser.AssignmentContext):
        return (str(ctx.IDENTIFIER()), self.visit(ctx.expr(0)))

    def visitConstNumber(self, ctx: PipedParser.ConstNumberContext):
        value = str(ctx.NUMBER())
        if value.isdigit():
            return int(value)
        return float(value)
