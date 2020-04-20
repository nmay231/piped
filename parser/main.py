from grammar.PipedLexer import PipedLexer
from grammar.PipedParser import PipedParser
from main_processing import VisitorAPI, ListenerAPI, listeners
from antlr4 import *
import os


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

# Walk the tree
listener = ListenerAPI()
listener.listeners = listeners
take_a_walk = ParseTreeWalker()
take_a_walk.walk(listener, tree)

# Write extra useful comments :)
print(listener.meta_data.TypeMaster.generate())
print(listener.meta_data.generated)
print(
    """
int main () {
    receive_entry_main();
    return 0;
}"""
)
