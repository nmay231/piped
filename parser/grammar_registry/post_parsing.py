import grammar.PipedParser as P
import helper_classes as HC
import itertools as IT
import internal_objects as Internal


def enterModule(ast_ctx: P.PipedParser.ModuleContext, meta_data):
    meta_data.map = {}
    # Private and public scopes respectively
    meta_data.scopes = [{}, {}]
    meta_data.generated = ""  # This DEFINITELY needs to change from a string
    meta_data.TypeMaster = HC.TypeMaster()
    meta_data.current_focus = HC.HoldPlease()
    meta_data.current_focus.now = "toplevel"

    # Temporary method of adding a print function to global scope
    meta_data.scopes[0]["print"] = Internal.printFunc


def exitModule(ast_ctx: P.PipedParser.ModuleContext, meta_data):
    # Misusing asserts, but ah well
    assert (
        len(meta_data.scopes) == 2
    ), f"Module scopes were not cleaned up {meta_data.scopes}"


def enterReceiveEntry(ast_ctx: P.PipedParser.ReceiveEntryContext, meta_data):
    name = str(ast_ctx.IDENTIFIER(0))
    arguments = [str(iden) for iden in tuple(ast_ctx.IDENTIFIER())[1:]]
    # I'm not dealing with return types right now
    return_ = None
    body = []
    meta_data.map[ast_ctx] = HC.ReceiveEntry(name, arguments, return_, body)
    meta_data.scopes.append({})

    new_focus = HC.HoldPlease()
    new_focus.now = ast_ctx
    new_focus.parent = meta_data.current_focus.now
    meta_data.current_focus = new_focus


def exitReceiveEntry(ast_ctx: P.PipedParser.ReceiveEntryContext, meta_data):
    meta_data.generated += meta_data.map[meta_data.current_focus.now].generate()
    meta_data.scopes.pop()
    meta_data.current_focus = meta_data.current_focus.parent


def exitConstInteger(ast_ctx: P.PipedParser.ConstIntegerContext, meta_data):
    meta_data.map[ast_ctx] = HC.Integer(str(ast_ctx.INTEGER()))


def exitConstFloat(ast_ctx: P.PipedParser.ConstFloatContext, meta_data):
    meta_data.map[ast_ctx] = HC.Float(str(ast_ctx.FLOAT()))


def exitConstString(ast_ctx: P.PipedParser.ConstStringContext, meta_data):
    meta_data.map[ast_ctx] = HC.String(str(ast_ctx.STRING()))


def exitRecord(ast_ctx: P.PipedParser.RecordContext, meta_data):
    # Warning: doesn't handle named tuple deconstruction or spreading: (auto_inserted=), (*spread_value,)
    named_items = ((item.IDENTIFIER(), item.expr()) for item in ast_ctx.namedItem())
    dict_repr = {str(iden): meta_data.map[child] for iden, child in named_items}
    meta_data.map[ast_ctx] = HC.Record(dict_repr)


def exitRecordExpr(ast_ctx: P.PipedParser.RecordExprContext, meta_data):
    meta_data.map[ast_ctx] = meta_data.map[ast_ctx.record()]


def exitNamedTuple(ast_ctx: P.PipedParser.NamedTupleContext, meta_data):
    # Warning: doesn't handle named tuple deconstruction or spreading: (auto_inserted=), (*spread_value,)
    named_items = [
        (str(item.IDENTIFIER()), meta_data.map[item.expr()])
        for item in ast_ctx.namedItem()
    ]
    meta_data.map[ast_ctx] = HC.NamedTuple(named_items)


def exitNamedTupleExpr(ast_ctx: P.PipedParser.NamedTupleExprContext, meta_data):
    meta_data.map[ast_ctx] = meta_data.map[ast_ctx.namedTuple()]


def exitTuple_(ast_ctx: P.PipedParser.Tuple_Context, meta_data):
    data = [meta_data.map[expr] for expr in ast_ctx.expr()]
    meta_data.map[ast_ctx] = HC.Tuple(data)


def exitTupleExpr(ast_ctx: P.PipedParser.TupleExprContext, meta_data):
    meta_data.map[ast_ctx] = meta_data.map[ast_ctx.tuple_()]


def exitList_(ast_ctx: P.PipedParser.List_Context, meta_data):
    data = [meta_data.map[expr] for expr in ast_ctx.expr()]
    meta_data.map[ast_ctx] = HC.List(data)


def exitListExpr(ast_ctx: P.PipedParser.ListExprContext, meta_data):
    meta_data.map[ast_ctx] = meta_data.map[ast_ctx.list_()]


def exitAssignment(ast_ctx: P.PipedParser.AssignmentContext, meta_data):
    name = str(ast_ctx.IDENTIFIER())
    type_ = meta_data.map.get(ast_ctx.type_(), None)
    expr = meta_data.map[ast_ctx.expr()]
    meta_data.map[ast_ctx] = HC.Variable(name, expr, type_)
    meta_data.scopes[-1][name] = meta_data.map[ast_ctx]


def exitAssignmentStatement(
    ast_ctx: P.PipedParser.AssignmentStatementContext, meta_data
):
    assignment = ast_ctx.assignment()
    current_function = meta_data.map[meta_data.current_focus.now]
    current_function.body.append(HC.AssignmentStatement(meta_data.map[assignment]))


def exitSimpleType(ast_ctx: P.PipedParser.SimpleTypeContext, meta_data):
    meta_data.map[ast_ctx] = meta_data.TypeMaster.getType(ast_ctx)


def exitRecordType(ast_ctx: P.PipedParser.RecordTypeContext, meta_data):
    meta_data.map[ast_ctx] = meta_data.TypeMaster.getType(ast_ctx)


def exitNamedTupleType(ast_ctx: P.PipedParser.NamedTupleTypeContext, meta_data):
    meta_data.map[ast_ctx] = meta_data.TypeMaster.getType(ast_ctx)


def exitExpressionStatement(
    ast_ctx: P.PipedParser.ExpressionStatementContext, meta_data
):
    if not isinstance(ast_ctx.expr(), P.PipedParser.FunctionCallContext):
        print(
            f"Warning: non-function-call expressions result in no-op (line: {ast_ctx.start.line})"
        )
        return
    current_function = meta_data.map[meta_data.current_focus.now]
    current_function.body.append(meta_data.map[ast_ctx.expr()])


def exitFunctionCall(ast_ctx: P.PipedParser.FunctionCallContext, meta_data):
    children = list(
        filter(
            lambda x: isinstance(
                x, (P.PipedParser.ExprContext, P.PipedParser.NamedItemContext)
            ),
            ast_ctx.getChildren(),
        )
    )
    caller, *children = children
    caller = meta_data.map[caller]
    args = [meta_data.map[arg] for arg in children]
    meta_data.map[ast_ctx] = HC.FunctionCallStatement(caller, args)


def exitAccessField(ast_ctx: P.PipedParser.AccessFieldContext, meta_data):
    meta_data.map[ast_ctx] = HC.AccessField(
        meta_data.map[ast_ctx.expr()], str(ast_ctx.IDENTIFIER())
    )


def exitIdentifierExpr(ast_ctx: P.PipedParser.IdentifierExprContext, meta_data):
    id_ = str(ast_ctx.IDENTIFIER())
    for scope in reversed(meta_data.scopes):
        if id_ in scope:
            meta_data.map[ast_ctx] = scope[id_]
            break
    else:
        print(f"Error: {id_} not defined")
