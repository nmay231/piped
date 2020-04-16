from grammar.PipedParser import PipedParser
from collections import defaultdict
from dataclasses import dataclass
from typing import *


@dataclass
class ReceiveEntry:
    name: str
    arguments: List[int]
    return_: str


first_pass = defaultdict(list)


def define_map(ast_ctx: PipedParser.ModuleContext, meta_data):
    meta_data.map = {}
    # Private and public scopes respectively
    meta_data.scopes = [{}, {}]


def find_entries_in_module(ast_ctx: PipedParser.ReceiveEntryContext, meta_data):
    name = str(ast_ctx.IDENTIFIER(0))
    arguments = [str(iden) for iden in tuple(ast_ctx.IDENTIFIER())[1:]]
    # I'm not dealing with return right now. Get it on the next pass
    meta_data.map[ast_ctx] = ReceiveEntry(name, arguments, None)
    print(meta_data.map[ast_ctx])


def load_int(ast_ctx: PipedParser.ConstIntegerContext, meta_data):
    # Is using eval() a terrible idea? Maybe...
    meta_data.map[ast_ctx] = eval(str(ast_ctx.INTEGER()))


def load_float(ast_ctx: PipedParser.ConstFloatContext, meta_data):
    # Is using eval() a terrible idea? Maybe...
    meta_data.map[ast_ctx] = eval(str(ast_ctx.FLOAT()))


def load_string(ast_ctx: PipedParser.ConstStringContext, meta_data):
    # Is using eval() a terrible idea? Maybe...
    meta_data.map[ast_ctx] = eval(str(ast_ctx.STRING()))


def load_record(ast_ctx: PipedParser.RecordContext, meta_data):
    # Warning: doesn't handle named tuple deconstruction or spreading: (auto_inserted=), (*spread_value,)
    named_items = ((item.IDENTIFIER(), item.expr()) for item in ast_ctx.namedItem())
    meta_data.map[ast_ctx] = {
        str(iden): meta_data.map[child] for iden, child in named_items
    }
    print(meta_data.map[ast_ctx])


first_pass["enterModule"].append(define_map)
first_pass["enterReceiveEntry"].append(find_entries_in_module)
first_pass["exitConstInteger"].append(load_int)
first_pass["exitConstFloat"].append(load_float)
first_pass["exitConstString"].append(load_string)
first_pass["exitRecord"].append(load_record)
