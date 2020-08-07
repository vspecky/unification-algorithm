# Unification Algorithm
My Implementation of the Unification Algorithm. This was intended to be an assignment for my AI course
but I had quite a lot of fun implementing this.  

## How to Use
- Run the script in a terminal.  
- Enter an equating expression in valid Prolog syntax. eg: `p(a, X) = p(Y, b)`  
- Do not put a period at the end.  
- If unification is possible, the program will perform it and display the results, else it will tell you what went wrong.  
- Enter `quit` to exit the script.

## What is Unification?
There are different types of Unification. This program performs Syntactic Unification i.e. it will
unify the expressions as they are, without deriving any any logical inferences.  
Take the last example (`p(a, X) = p(Y, b)`). Here, `X` and `Y` are variables (since they begin with
a capital letter). The unifier asks "Are there any values for `X` and `Y` which, if substituted, will
make both sides of the equation equal?".  
In this example, there is a way. If we substitute `X = b` and `Y = a`, the expression becomes 
`p(a, b) = p(a, b)` which is true and hence unification is successful. It is the job of the unifier 
to deduce these values for the variables. More information [here](https://en.wikipedia.org/wiki/Unification_(computer_science)).  

## Examples
```
> p(f(a), g(Y)) = p(X, X)
The Expression cannot be unified

> parent(mark, Son) = parent(Father, carson)
Father = mark
Son = carson

> p(b, X, f(g(Z))) = p(Z, f(Y), f(Y))
Z = b
X = f(g(b))
Y = g(b)
```

## How does this script work?
This script has a bunch of parts. I'm going into this much detail since this is a Assignment.

### Lexer
The job of the Lexer is to take an expression in string form and produce a token stream.  
For example, the expression `f(X)` produces the following stream :-
```
[
	(type: 'ident', val: 'f'),
	(type: 'l_paren', val: '('),
	(type: 'var', val: 'X'),
	(type: 'r_paren', val: ')')
]
```

### Parser
The parser takes in the token stream and parses it into Variable Nodes, Constant Nodes and Predicate
Nodes. For example, the expression `pred(X, hello, pred2(world))` will get parsed to the following :-
```
Predicate {
	name: 'pred',
	nodes: [
		Variable {
			name: 'X'
		},
		Constant {
			name: 'hello'
		},
		Predicate {
			name: 'pred2',
			nodes: [
				Constant {
					name: 'world'
				}
			]
		}
	]
}
```
The Lexer-Parser chain gives us the inputted expression in a very convenient class format, making 
unification that much easier.

### Unifier
The Unifier takes in two expressions (Resultant ASTs from the Parser) and simply performs Unification 
on the expressions, storing the substitutions in a dictionary.
