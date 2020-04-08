grammar Piped;

module: (toplevel | '\n')* EOF;
toplevel: (
		importstatement
		// | deliver_entry
		| receive_entry
		| function_definition
		// | class_definition
	);

WS: [ \t]+ -> channel(HIDDEN);
NEWLINE: '\n';

NUMBER: [0-9]+;
// Don't forget escaped quotes
STRING: ('\'' ('\\\'' | ~['\n])* '\'')
	| ('"' ('\\"' | ~["\n])* '"');

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
importstatement:
	('import' import_name ('as' IDENTIFIER)?)
	| (
		'from' import_name 'import' IDENTIFIER ('as' IDENTIFIER)? (
			',' IDENTIFIER ('as' IDENTIFIER)?
		)*
	);
import_name: ('./' | '/' | '../'+)? IDENTIFIER ('/' IDENTIFIER)*;

COMMENT: (('###' .*? '###') | ('#' ~[\n]*)) -> channel(HIDDEN);
CONTINUED_LINE: '\\\n' -> channel(HIDDEN);

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
		// | function call thingy | 'break' | 'continue'
		| ('return' term)
	) (('\r'? '\n') | ';');
// Forcing all statements to end with a newline or semicolon is annoying. Mainly because of oneline
// functions.

for_loop: 'for' IDENTIFIER 'in' term '{' instruction* '}';
conditional_if: ((('if' | 'elif') term) | 'else') '{' instruction* '}';

// Typing is not technically correct, but whatever
assignment: IDENTIFIER (':' single_term)? '=' term;
// assignment: assignable_term (',' assignable_term)* '=' term (',' term)*;

single_term:
	NUMBER
	| STRING
	| IDENTIFIER
	| dictionary
	| record
	| tuple_
	| named_tuple
	| list_
	| set_
	// | prefixed_encloser | multiset
	| single_term '.' IDENTIFIER
	| single_term '.?' IDENTIFIER
	| single_term '(' ')'
	| ('(' term ')')
	| ('(' ')' '=>' '{' instruction* '}');
expression:
	<assoc = right>expression '**' expression
	| expression ('*' | '/' | '%') expression
	| expression ('+' | '-') expression
	| expression ('==' | '!=' | '<=' | '>=') expression
	| expression ('and' | 'or') expression
	// keyof might not need to be here since it is for types
	| ('not' | '+' | '-' | 'typeof' | 'keyof') expression;
term: single_term | expression;

dictionary: ('{' ':' '}') (
		'{' term ':' term (',' term ':' term)* ','? '}'
	);

tuple_: ('(' term ',' ')') | ('(' term (',' term)+ ','? ')');

named_item:
	('*' IDENTIFIER)
	| (IDENTIFIER '=')
	| (IDENTIFIER '=' term);

// I'm having the empty dictionary "{}" be a record because We can always downgrade records to
// dictionaries, but not vice versa
record: ('{' '='? '}')
	| ( '{' named_item ( ',' named_item)* ','? '}');

// I'm having the empty tuple_ "(,)" be a named tuple_ because We can always downgrade named_tuples
// to tuples, but not vice versa
named_tuple: ('(' ',' ')')
	| ( '(' named_item ( ',' named_item)* ','? ')');

// Sidenote: consider adding some sort of thing like list_/dictionary comprehensions
list_: ('[' ']') | ('[' term (',' term)* ','? ']');

set_: ('{' ',' '}') | ('{' term (',' term)+ ','? '}');

// Allowing future language developments and others to modify it themselves prefixed_encloser:
// LOWER_CHAR ( ('"' stuff '"') | ('\'' stuff '\'') | ('(' stuff ')') | ('{' stuff '}') );

// access_field: single_term '.' IDENTIFIER; access_optional_field: single_term '.?' IDENTIFIER;

// Do I need this for "and" and "or" of types (e.g.: `hash-list_<int>|hash-dict<int, str>`)
/*
 lexer;
 
 mode TYPE;
 
 TYPE_GENERIC: IDENTIFIER '<' -> pushMode(TYPE); END_GENERIC: '>' -> popMode;
 */