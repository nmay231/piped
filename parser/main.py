from grammar.PipedLexer import PipedLexer
from grammar.PipedParser import PipedParser
from main_processing import VisitorAPI
from generate_c import generate
from antlr4 import *
import os

from visitor_registors import first_pass


if not os.path.exists("test.piped"):
    print("Error: Expected to find `test.piped`")
    exit(1)

with open("test.piped") as f:
    input_ = f.read()

# Parse
stream = InputStream(input_)
lexer = PipedLexer(stream)
tokens = CommonTokenStream(lexer)
tokens.fill()
parser = PipedParser(tokens)
tree = parser.module()

# collect global variables
first_visitor = VisitorAPI()
first_visitor.visitors = first_pass
first_visitor.visit(tree, "first_pass")

# print(generate(first_visitor.meta_data))
