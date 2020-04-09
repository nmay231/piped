grammar Piped;

NUMBER: ([0-9]+ ('.' [0-9]*)? | '.' [0-9]+) ([eE]'-'? [0-9]+)?;
STRING: ('\'' ('\\\'' | ~['\r\n])* '\'')
	| ('"' ('\\"' | ~["\r\n])* '"');

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;

WS: [ \t]+ -> channel(HIDDEN);
NEWLINE: '\r'? '\n';

COMMENT: (('###' .*? '###') | ('#' ~[\r\n]*)) -> channel(HIDDEN);
CONTINUED_LINE: '\\' '\r'? '\n' -> channel(HIDDEN);

module: (toplevel | NEWLINE)* EOF;
toplevel: (
		importstatement
		// | deliver_entry
		| receive_entry
		| function_definition
		// | class_definition
	);

importstatement:
	('import' import_name ('as' IDENTIFIER)?)
	| (
		'from' import_name 'import' IDENTIFIER ('as' IDENTIFIER)? (
			',' IDENTIFIER ('as' IDENTIFIER)?
		)*
	);
import_name: ('./' | '/' | '../'+)? IDENTIFIER ('/' IDENTIFIER)*;

// deliver_entry: // Entries are able to be replaced or can be setup to be replaced ('repeatable' |
// 'repeat')? // Can this entry be run in parallel or sequencially with other entries of the same
// name? Or is // it unique, like the `main` entry? If sequential, is it before or after the
// original // sequential ( 'unique' | 'sequential' // This is only for entry data definitions (not
// user entry definitions) | 'parallel' | (('after' | 'before') BRACKETTAG)

// )? // Every entry has a name 'entry' IDENTIFIER // Entries can be optionally tagged with a string
// BRACKETTAG? // Parameters '(' commalisttrailing? ')' // Of course, the content '{' instruction*
// '}' ;

receive_entry:
	'receive' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' block_body '}';

function_definition:
	'def' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' block_body '}';

// `statement?` allows ending statements to not require terminator
block_body: instruction* statement?;

instruction: (statement (NEWLINE | ';'))
	| for_loop
	| conditional_if
	| (NEWLINE);

statement:
	assignment				# assignmentStatement
	| expr					# expressionStatement
	| 'break'				# breakStatement
	| 'continue'			# continueStatement
	| 'return' expr			# returnStatement
	| function_definition	# defFunctionStatement;

for_loop: 'for' IDENTIFIER 'in' expr '{' block_body '}';
conditional_if: ((('if' | 'elif') expr) | 'else') '{' block_body '}';

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
	| named_tuple			# NamedTupleExpr
	| list_					# ListExpr
	| set_					# SetExpr
	| ('(' expr ')')		# ParenExpr
	| expr '.' IDENTIFIER	# AccessField
	| expr '.?' IDENTIFIER	# OptionalAccessField
	| expr '[' expr ']'		# Subscript
	| expr '(' (
		(named_item | expr) (',' (named_item | expr))* ','?
	)? ')' # FunctionCall
	| (
		'(' (named_item (',' named_item)* ','?)? ')' '=>' '{' block_body '}'
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

named_item:
	('*' IDENTIFIER)
	| (IDENTIFIER '=')
	| (IDENTIFIER '=' expr);

record: ('{' '=' '}')
	| ( '{' named_item ( ',' named_item)* ','? '}');

named_tuple: ('(' '=' ')')
	| ( '(' named_item ( ',' named_item)* ','? ')');

// Sidenote: consider adding some sort of thing like list_/dictionary comprehensions
list_: ('[' ']') | ('[' expr (',' expr)* ','? ']');

set_: ('{' ',' '}') | ('{' expr (',' expr)+ ','? '}');

type_: 'something_to_do_with_types' | 'keyof' expr;