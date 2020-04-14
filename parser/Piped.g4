grammar Piped;

FLOAT: (INTEGER '.' [0-9]* | '.' [0-9]+) ([eE]'-'? [0-9]+)?;
INTEGER: [0-9]+;
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
		// | deliverEntry
		| receiveEntry
		| functionDefinition
		// | classDefinition
	);

importStatement:
	('import' importName ('as' IDENTIFIER)?)
	| (
		'from' importName 'import' IDENTIFIER ('as' IDENTIFIER)? (
			',' IDENTIFIER ('as' IDENTIFIER)?
		)*
	);
importName: ('./' | '/' | '../'+)? IDENTIFIER ('/' IDENTIFIER)*;

// deliverEntry: // Entries are able to be replaced or can be setup to be replaced ('repeatable' |
// 'repeat')? // Can this entry be run in parallel or sequencially with other entries of the same
// name? Or is // it unique, like the `main` entry? If sequential, is it before or after the
// original // sequential ( 'unique' | 'sequential' // This is only for entry data definitions (not
// user entry definitions) | 'parallel' | (('after' | 'before') BRACKETTAG)

// )? // Every entry has a name 'entry' IDENTIFIER // Entries can be optionally tagged with a string
// BRACKETTAG? // Parameters '(' commalisttrailing? ')' // Of course, the content '{' instruction*
// '}' ;

receiveEntry:
	'receive' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' blockBody '}';

functionDefinition:
	'def' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' blockBody '}';

// `statement?` allows ending statements to not require terminator
blockBody: instruction* statement?;

instruction: (statement (NEWLINE | ';'))
	| forLoop
	| conditional
	| (NEWLINE);

statement:
	assignment				# assignmentStatement
	| 'break'				# breakStatement
	| 'continue'			# continueStatement
	| 'return' expr			# returnStatement
	| functionDefinition	# defFunctionStatement
	// expr needs to be last to avoid ambiguity with keywords break, continue, etc.
	| expr # expressionStatement;

forLoop: 'for' IDENTIFIER 'in' expr '{' blockBody '}';
conditional: ((('if' | 'elif') expr) | 'else') '{' blockBody '}';

// Don't forget about tuple unpacking (can I ban the use of "()" or are they needed?)
assignment: IDENTIFIER ':' type_ '=' expr;

// TODO: prefixedEncloser, e.g. `m{1,2,3}`
expr:
	FLOAT					# ConstFloat
	| INTEGER				# ConstInteger
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
	| '~' type_ '~'			# TypeExpr
	| expr '(' (
		(namedItem | expr) (',' (namedItem | expr))* ','?
	)? ')' # FunctionCall
	| (
		'(' (namedItem (',' namedItem)* ','?)? ')' '=>' '{' blockBody '}'
	)										# ArrowFunction
	| <assoc = right>expr '**' expr			# Exponentiation
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

type_:
	IDENTIFIER # SimpleType
	| (
		('{' '=' '}')
		| (
			'{' IDENTIFIER '=' type_ (',' IDENTIFIER '=' type_)* ','? '}'
		)
	) # RecordType
	| (
		('(' '=' ')')
		| (
			'(' IDENTIFIER '=' type_ (',' IDENTIFIER '=' type_)* ','? ')'
		)
	)																# NamedTupleType
	| (('(' type_? ',' ')') | ( '(' type_ (',' type_)+ ','? ')'))	# TupleType
	| IDENTIFIER '<' type_ (',' type_)* '>'							# GenericType
	| '(' type_ ')'													# WrappedType
	| 'keyof' type_													# KeyofType
	| type_ '-' type_												# IntersectionType
	| type_ '|' type_												# UnionType;