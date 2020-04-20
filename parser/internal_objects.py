import helper_classes as HC
import typing

printFunc = HC.Variable("print", "Internal.print", None)
printFunc.generate = lambda: "printf"
