from grammar.PipedLexer import PipedLexer
from grammar.PipedParser import PipedParser
from main_processing import GetModuleDefinitions, TreeAnnotater
from generate_c import generate
from antlr4 import InputStream, CommonTokenStream
import os


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

visitor = GetModuleDefinitions()
visitor.visit(tree)

# Should have an intermediary walk-through to type-check things

getBuildInstructions = TreeAnnotater(visitor.meta)
getBuildInstructions.visit(tree)

print(generate(getBuildInstructions.meta))
