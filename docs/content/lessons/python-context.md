# understanding the zcx python evaluation context

Whenever [expressions are evaluated](/reference/template-reference#template-strings), or the [python](/reference/command-reference#python) command is used, zcx will evaluate the code in a limited Python context.

## why?

This restriction is in place to safeguard zcx users against bad actors, who might distribute 'helpful' zcx configuration files that [actually contain malicious code](https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html).
Using this attack vector, an attacker could cause a lot of damage, like wiping you entire filesystem, or reading your sensitive files.

## the solution

All user-supplied Python expressions are interpreted with the [asteval](https://lmfit.github.io/asteval/index.html) library.
asteval interprets your expressions with a limited context, which basically means that the [most dangerous Python features](https://lmfit.github.io/asteval/motivation.html#how-safe-is-asteval) are not available in this context. In particular, importing of modules is not allowed, and access to "private" attributes is prevented.

### additional restrictions

- by default, `asteval` allows access to Python's [open()](https://docs.python.org/3/library/functions.html#open) method in read-only mode. This has been disallowed in zcx.

### additional symbols

Several [additional symbols](/reference/template-reference#template-locals) are made available in template strings.
