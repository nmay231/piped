/*
 * This is just an idea for maintaining integrity between different library versions
 */

grammar Changelog;
NEWLINE: '\r'? '\n';
IDENTIFIER: [a-zA-Z][a-zA-Z0-9_]*;
IGNORE_NEWLINE: '\\' NEWLINE -> channel(HIDDEN);
/*
 This is semver, but don't forget about calver ^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)
 (?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?
 (?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
 */
VERSION:
	([0-9]+ '.' [0-9]+ '.' [0-9]+) ('-' (ANH+ ('.' ANH+)*))? (
		'+' (ANH+ ('.' ANH+)*)
	)?;
fragment ANH: [0-9a-zA-Z\-]; // Alphanumeric and hyphens
LIST_BULLET: [\-*>];
WS: [ \t] -> channel(HIDDEN);

file: header? (version | NEWLINE)*;

header: headerLine* NEWLINE '---' NEWLINE;
headerLine: IDENTIFIER .*? NEWLINE;

version: VERSION ':' NEWLINE versionChanges*;
versionChanges:
	LIST_BULLET '[' versionChangeType ('-' versionChangeType)+ ']' .*? NEWLINE;

// A single change can include one or more of the following types
versionChangeType:
	'SIMPLE' // Change is simple enough to be ignored/automatically updated
	| 'SECURITY' // Code that uses the old version might be at risk
	| 'BUGFIX' // Unintended behaviour/side-effect changed/removed
	| 'RENAME' // Simple rename of an API
	| 'TYPING' // Simple type change of an API
	| 'API' // More complex/general changes to API than RENAME or TYPING
	| 'DEPRECATION' // An API is marked as deprecated and might be removed in the future
	| 'REVERT'
	// Some change was reverted partially, completely, or never actually changed in the first place
	| 'BEHAVIOUR' // (It may be) the same API but has different behaviour
	| 'INTERNAL' // Internal refactoring
	| 'OPTIMIZE_S' // Optimizations in speed performance
	| 'OPTIMIZE_M' // Optimizations in memory performance
	| 'DEPENDENCY' // Dependenc(ies) updated/added/removed/pinned
	| 'OTHER'; // Doesn't fit into any previous categories