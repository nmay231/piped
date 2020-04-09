from grammar.PipedLexer import PipedLexer
from grammar.PipedParser import PipedParser
from grammar.PipedListener import PipedListener
from antlr4 import InputStream, ParseTreeWalker
from antlr4 import InputStream, CommonTokenStream
import os


class PiedPiper(PipedListener):
    def enterImportstatement(self, ctx: PipedParser.ImportstatementContext):
        print(tuple(child.getText() for child in ctx.getChildren()))

    def enterFunction_definition(self, ctx: PipedParser.Function_definitionContext):
        print(tuple(child.getText() for child in ctx.getChildren()))

    def enterArrowFunction(self, ctx: PipedParser.ArrowFunctionContext):
        print("arrow", tuple(child.getText() for child in ctx.getChildren()))


if not os.path.exists("test.piped"):
    print("Error: Expected to find `test.piped`")
    exit(1)

with open("test.piped") as f:
    input_ = f.read()

stream = InputStream(input_)
lexer = PipedLexer(stream)
tokens = CommonTokenStream(lexer)
tokens.fill()
parser = PipedParser(tokens)
tree = parser.module()
walker = ParseTreeWalker()
walker.walk(PiedPiper(), tree)
