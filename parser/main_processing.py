from grammar.PipedListener import PipedListener
from grammar.PipedParser import PipedParser
from grammar.PipedVisitor import PipedVisitor
import helper_classes as HC
import typing

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


class ListenerAPI(PipedListener):
    def __init__(self, meta_data=None):
        super().__init__()
        self.listeners = defaultdict(list)
        if not meta_data:
            self.meta_data = HC.HoldPlease()
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


# TODO: Do I need this?
class VisitorAPI(PipedVisitor):
    def __init__(self, meta_data=None):
        super().__init__()
        self.visitors = defaultdict(list)
        if not meta_data:
            self.meta_data = HC.HoldPlease()
            self.meta_data.global_scope = {}
            self.meta_data.public_scope = {}
            self.meta_data.private_scope = {}
        else:
            self.meta_data = meta_data
        for ruleMethod in dir(self):
            if ruleMethod.startswith("visit") and (
                ruleMethod[5:] not in ("Children", "Terminal", "ErrorNode", "", "ors")
            ):
                setattr(self, ruleMethod, self.mockRule(ruleMethod))

    def visit(self, tree, traversal_state):
        self.meta_data.state = traversal_state
        super().visit(tree)

    def register(self, node: str, visitor: typing.Any):
        self.visitors[node].append(visitor)

    def mockRule(self, name: str):
        def func(ast):
            if name not in self.visitors:
                return
            for visitor in self.visitors[name]:
                visitor(ast, self.meta_data)

        return func
