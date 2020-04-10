grammar Piped;

NUMBER: ([0-9]+ ('.' [0-9]*)? | '.' [0-9]+) ([eE]'-'? [0-9]+)?;
STRING: ('\'' ('\\\'' | ~['\r\n])* '\'')
	| ('"' ('\\"' | ~["\r\n])* '"');

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;

WS: [ \t]+ -> channel(HIDDEN);
NEWLINE: '\r'? '\n';

COMMENT: (('###' .*? '###') | ('#' ~[\r\n]*)) -> channel(HIDDEN);
CONTINUED_LINE: '\\' '\r'? '\n' -> channel(HIDDEN);

module: (topLevel | NEWLINE)* EOF;
topLevel: (
		importStatement
		// | deliver_entry
		| receiveEntry
		| functionDefinition
		// | class_definition
	);

importStatement:
	('import' importName ('as' IDENTIFIER)?)
	| (
		'from' importName 'import' IDENTIFIER ('as' IDENTIFIER)? (
			',' IDENTIFIER ('as' IDENTIFIER)?
		)*
	);
importName: ('./' | '/' | '../'+)? IDENTIFIER ('/' IDENTIFIER)*;

// deliver_entry: // Entries are able to be replaced or can be setup to be replaced ('repeatable' |
// 'repeat')? // Can this entry be run in parallel or sequencially with other entries of the same
// name? Or is // it unique, like the `main` entry? If sequential, is it before or after the
// original // sequential ( 'unique' | 'sequential' // This is only for entry data definitions (not
// user entry definitions) | 'parallel' | (('after' | 'before') BRACKETTAG)

// )? // Every entry has a name 'entry' IDENTIFIER // Entries can be optionally tagged with a string
// BRACKETTAG? // Parameters '(' commalisttrailing? ')' // Of course, the content '{' instruction*
// '}' ;

receiveEntry:
	'receive' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' block_body '}';

functionDefinition:
	'def' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' block_body '}';

// `statement?` allows ending statements to not require terminator
block_body: instruction* statement?;

instruction: (statement (NEWLINE | ';'))
	| forLoop
	| conditional
	| (NEWLINE);

statement:
	assignment				# assignmentStatement
	| expr					# expressionStatement
	| 'break'				# breakStatement
	| 'continue'			# continueStatement
	| 'return' expr			# returnStatement
	| functionDefinition	# defFunctionStatement;

forLoop: 'for' IDENTIFIER 'in' expr '{' block_body '}';
conditional: ((('if' | 'elif') expr) | 'else') '{' block_body '}';

// Typing is not technically correct, but whatever
assignment: IDENTIFIER (':' expr)? '=' (expr | expr);
// assignment: assignable_term (',' assignable_term)* '=' expr (',' expr)*;

// TODO: prefixed_encloser, e.g. `m{1,2,3}`
expr:
	NUMBER					# ConstNumber
	| STRING				# ConstString
	| IDENTIFIER			# IdentifierExpr
	| dictionary			# DictionaryExpr
	| record				# RecordExpr
	| tuple_				# TupleExpr
	| namedTuple			# NamedTupleExpr
	| list_					# ListExpr
	| set_					# SetExpr
	| ('(' expr ')')		# ParenExpr
	| expr '.' IDENTIFIER	# AccessField
	| expr '.?' IDENTIFIER	# OptionalAccessField
	| expr '[' expr ']'		# Subscript
	| expr '(' (
		(namedItem | expr) (',' (namedItem | expr))* ','?
	)? ')' # FunctionCall
	| (
		'(' (namedItem (',' namedItem)* ','?)? ')' '=>' '{' block_body '}'
	)										# ArrowFunction
	| expr '**' expr						# Exponentiation
	| expr ('*' | '/' | '%') expr			# MultiplyDivide
	| expr ('+' | '-') expr					# AddSubtract
	| expr ('==' | '!=' | '<=' | '>=') expr	# BooleanCompare
	| expr ('and' | 'or') expr				# BooleanAndOr
	| ('not' | '+' | '-' | 'typeof') expr	# Unary;

dictionary: ('{' ':' '}') (
		'{' expr ':' expr (',' expr ':' expr)* ','? '}'
	);

tuple_: ('(' ',' ')') | ('(' expr (',' expr)* ','? ')');

namedItem:
	('*' IDENTIFIER)
	| (IDENTIFIER '=')
	| (IDENTIFIER '=' expr);

record: ('{' '=' '}')
	| ( '{' namedItem ( ',' namedItem)* ','? '}');

namedTuple: ('(' '=' ')')
	| ( '(' namedItem ( ',' namedItem)* ','? ')');

// Sidenote: consider adding some sort of thing like list_/dictionary comprehensions
list_: ('[' ']') | ('[' expr (',' expr)* ','? ']');

set_: ('{' ',' '}') | ('{' expr (',' expr)+ ','? '}');

type_: 'something_to_do_with_types' | 'keyof' expr;