@chapter
id: strings
num: 03
pkg: immutable str · slicing · f-strings · join · encode
title: Strings & Formatting
summary: Immutability and what it costs, slicing, joining versus concatenating, f-strings and their format specifiers, and the boundary between str and bytes.
@body

### Strings are immutable

Methods such as `upper`, `replace` and `strip` return a new string. The original is untouched. Item assignment is not allowed at all.

```python run
s = "python"
t = s.upper()
print(s, t)
try:
    s[0] = "P"
except TypeError as err:
    print("TypeError:", err)
```

### Slicing

`s[start:stop:step]` builds a new string. Negative indices count from the end, and a missing bound means the edge of the string.

```python run
word = "interview"
print(word[0], word[-1], word[2:6], word[::-1], word[::2])
```

### Joining instead of concatenating

Joining a list of pieces is linear in the total length. Repeated `+=` on an immutable string can copy the whole prefix at every step.

```python run
parts = ["a", "b", "c"]
print("-".join(parts))
```

### f-strings and format specifiers

```python run
name, score = "Ravi", 91.456
print(f"{name:>8} | {score:.1f}")
print(f"{score=}")
print("{} scored {:.0f}".format(name, score))
```

The `=` specifier, added in Python 3.8, prints both the expression and its value, which is handy for quick debugging.

### Bytes and encoding

```python run
text = "héllo"
data = text.encode("utf-8")
print(len(text), len(data), data)
print(data.decode("utf-8") == text)
```

### Interview questions

Q: Why are strings immutable?
A: Immutability makes a string safe to share between names and threads, lets it be used as a dictionary key, and gives it a hash that never changes. Operations return new strings, so a value cannot change under a reference that holds it.

Q: Why is `"".join(items)` preferred to `+=` in a loop?
A: Each `+=` on a string can allocate a new string and copy everything built so far, so the total work grows quadratically. `join` computes the final length once and copies each piece once. CPython has an optimisation for some `+=` cases, but do not rely on it in an interview answer.

Q: How do you check whether a string is a palindrome?
A: `s == s[::-1]` is the idiomatic answer. It runs in O(n) time and uses O(n) extra space for the reversed copy. A two-pointer loop from both ends does the same work in O(1) extra space, which is worth mentioning.

Q: What is the difference between `str` and `bytes`?
A: `str` is text, a sequence of Unicode code points. `bytes` is a sequence of raw eight-bit values. `encode` turns text into bytes with a chosen codec, and `decode` reverses it. Mixing the two raises `TypeError`.

:::pitfall Methods return new strings
`s.strip()`, `s.replace(...)` and `s.upper()` do not change `s`. Writing them without assigning the result is a silent no-op. Assign the result, or return it.
:::

:::remember Formatting choices
f-strings are the default for Python 3.6 and later, because they are fast and readable. Use `str.format` only when the template comes from outside the code.
:::

@chapter
id: control
num: 04
pkg: if · for · while · else on loops · range · enumerate · zip · comprehensions
title: Control Flow & Comprehensions
summary: Loops with else, range, enumerate and zip, list, set, dict and generator comprehensions, and structural pattern matching with match.
@body

### Loops with else

The `else` block of a loop runs only when the loop ends without `break`. It is the clean way to write "search, and handle not found".

```python run
for n in [3, 5, 8, 9]:
    if n % 2 == 0:
        print("first even:", n)
        break
else:
    print("no even number")
```

### range, enumerate and zip

```python run
names = ["ana", "ben", "cy"]
scores = [88, 92, 79]
for i, name in enumerate(names, start=1):
    print(i, name)
print(list(zip(names, scores)))
print(list(range(10, 0, -3)))
```

### Comprehensions

```python run
squares = [x * x for x in range(6) if x % 2 == 0]
print(squares)
print({c: len(c) for c in ["go", "java", "python"]})
print({n % 3 for n in range(10)})
print(sum(x for x in range(5)))
```

The last line uses a generator expression. Parentheses build a lazy generator, so nothing is stored in memory.

### Pattern matching

```python run
def describe(status):
    match status:
        case 200 | 201:
            return "ok"
        case 404:
            return "not found"
        case _:
            return "other"

print(describe(201), describe(404), describe(500))
```

### Interview questions

Q: What does `else` on a loop do?
A: It runs when the loop finishes without hitting `break`. It is useful for search loops, where the `else` branch means nothing matched. It does not run after `break`, and `continue` has no effect on it.

Q: Do comprehension variables leak into the enclosing scope?
A: Not in Python 3. A comprehension has its own scope, so its loop variable is gone after the expression. Python 2 leaked list-comprehension variables, which is a known trap in old code.

Q: Why is `x in range(...)` fast?
A: For integers, `range` tests membership arithmetically in constant time instead of scanning. `range` also uses constant memory however large it is, so prefer it to `list(range(...))`.

Q: How does a list comprehension differ from a generator expression?
A: Brackets build the whole list immediately. Parentheses build a generator that yields one value at a time, so memory stays constant and values are computed on demand. The generator can be consumed only once.

Q: What is `match` for?
A: Structural pattern matching, added in Python 3.10. It is more than a switch: cases can unpack sequences and mappings, bind names and check classes. It does not fall through, so there are no `break` statements.

:::pitfall Indexing when you only need the values
`for i in range(len(items))` followed by `items[i]` is slower and harder to read than iterating directly. Use `for item in items`, or `enumerate` when the index is needed.
:::

@chapter
id: functions
num: 05
pkg: def · defaults · *args · **kwargs · closures · LEGB
title: Functions, Scope & Arguments
summary: Default arguments are evaluated once, *args and **kwargs, name lookup with LEGB, closures and late binding, and positional-only and keyword-only parameters.
@body

### Default arguments are evaluated once

The default value is created when the `def` statement runs, not on each call. A mutable default is therefore shared between calls.

```python run
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item(1))
print(add_item(2))
```

The fix is a sentinel: use `bucket=None` and create the list inside the function.

### *args and **kwargs

```python run
def report(title, *values, sep=", ", **meta):
    print(title, sep.join(map(str, values)), meta)

report("sizes", 1, 2, 3, unit="cm", source="survey")
```

### Scope: LEGB, global and nonlocal

Name lookup checks Local, then Enclosing functions, then Global, then Built-in names. Assignment creates a local name unless you declare otherwise.

```python run
x = "global"

def outer():
    x = "enclosing"
    def inner():
        nonlocal x
        x = "changed"
    inner()
    return x

print(outer(), x)
```

### Closures and late binding

A closure remembers variables from the scope where it was created. Lambdas created in a loop all share the same loop variable, so they see its final value.

```python run
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])

funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])
```

### Positional-only and keyword-only parameters

```python run
def f(a, /, b, *, c):
    return a + b + c

print(f(1, 2, c=3))
```

Parameters before `/` must be passed by position. Parameters after `*` must be passed by keyword.

### Interview questions

Q: What is the mutable default argument trap?
A: Default values are evaluated once, when `def` runs, so a default list or dict is shared by every call that relies on it. Use `None` as the default and create the object inside the function.

Q: Is Python pass-by-value or pass-by-reference?
A: Neither exactly. It is call by object reference, sometimes called pass-by-sharing. The function receives a reference to the same object, so mutating it is visible to the caller. Rebinding the parameter to a new object is not visible outside the function.

Q: Explain LEGB.
A: Lookup searches Local, then Enclosing function scopes, then Global, then Built-in names, and stops at the first match. `nonlocal` and `global` let an inner function rebind a name from a wider scope. Without them, assignment creates a new local name.

Q: What is the difference between `*args` and `**kwargs`?
A: `*args` collects extra positional arguments into a tuple, and `**kwargs` collects extra keyword arguments into a dict. At a call site, `*` and `**` do the reverse: they unpack an iterable or a mapping into separate arguments.

Q: What does `global` do?
A: It makes assignment inside the function rebind the module-level name. Reading a global needs no declaration. Heavy use of `global` makes code hard to reason about, so pass values in and return results instead.

Q: When should you avoid a lambda?
A: A lambda holds exactly one expression and no statements. Use a named `def` when the function needs a name in tracebacks, a docstring, more than one line, or reuse in several places.

:::pitfall Late binding in loops
Closures capture variables, not values. Creating lambdas in a loop without binding the current value as a default argument gives every function the final value.
:::

:::remember Parameter order
Positional-only parameters come first, before `/`. Ordinary parameters come next. Keyword-only parameters come after `*`. `*args` and `**kwargs` come last.
:::
