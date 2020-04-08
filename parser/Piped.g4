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
	'receive' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' instruction* '}';

function_definition:
	'def' IDENTIFIER '(' (IDENTIFIER (',' IDENTIFIER)* ','?)? ')' '{' instruction* '}';

instruction: statement | for_loop | conditional_if | (NEWLINE);

statement: (
		assignment
		| expr
		// | function call thingy | 'break' | 'continue'
		| ('return' expr)
	) (NEWLINE | ';');
// Forcing all statements to end with a newline or semicolon is annoying. Mainly because of oneline
// functions.

for_loop: 'for' IDENTIFIER 'in' expr '{' instruction* '}';
conditional_if: ((('if' | 'elif') expr) | 'else') '{' instruction* '}';

// Typing is not technically correct, but whatever
assignment: IDENTIFIER (':' expr)? '=' (expr | expr);
// assignment: assignable_term (',' assignable_term)* '=' expr (',' expr)*;

expr:
	NUMBER
	| STRING
	| IDENTIFIER
	| dictionary
	| record
	| tuple_
	| named_tuple
	| list_
	| set_
	| ('(' expr ')')
	// | prefixed_encloser
	| expr '.' IDENTIFIER
	| expr '.?' IDENTIFIER
	| expr '[' expr ']' // subscripting
	| expr '(' (
		(named_item | expr) (',' (named_item | expr))* ','?
	)? ')'
	| (
		'(' (named_item (',' named_item)* ','?)? ')' '=>' '{' instruction* '}'
	)
	| expr '**' expr
	| expr ('*' | '/' | '%') expr
	| expr ('+' | '-') expr
	| expr ('==' | '!=' | '<=' | '>=') expr
	| expr ('and' | 'or') expr
	| ('not' | '+' | '-' | 'typeof') expr;

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

type: 'something_to_do_with_types' | 'keyof' expr;