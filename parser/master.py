from grammar.PipedLexer import PipedLexer
from grammar.PipedParser import PipedParser
from grammar.PipedListener import PipedListener
from antlr4 import InputStream, ParseTreeWalker
from antlr4.BufferedTokenStream import BufferedTokenStream

class PiedPiper(PipedListener):
    def enterImportstatement(self, ctx:PipedParser.ModuleContext):
        print(ctx.IMPORTNAME(), ctx.IDENTIFIER())
        print(list(ctx.IDENTIFIER()[0]))

stream = InputStream('import ./importname as yo')
lexer = PipedLexer(stream)
tokens = BufferedTokenStream(lexer)
parser = PipedParser(tokens)
tree = parser.toplevel()
walker = ParseTreeWalker()
walker.walk(PiedPiper(), tree)