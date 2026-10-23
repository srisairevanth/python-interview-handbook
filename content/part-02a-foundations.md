@part 2 | Foundations

@chapter
id: basics
num: 01
pkg: interpreter · names · indentation · docstrings
title: Syntax, Names & the First Program
summary: How Python runs your code, indentation as syntax, names as references, input and output, docstrings, and the conventions interviewers notice.
@body

### What runs when you run a file

CPython, the reference implementation, compiles each module to **bytecode** and then a virtual machine executes that bytecode. Compiled bytecode is cached in `__pycache__` as `.pyc` files, which is why the first import of a big module is slower than later ones. You never write machine code, and the same `.py` file runs on any platform that has the interpreter.

### The first program

```python run
name = "Asha"
print("Hello,", name)
```

### Names are labels, not boxes

Assignment binds a name to an object. It never copies the object. Two names can point at the same list, so a change made through one is visible through the other.

```python run
x = [1, 2, 3]
y = x
y.append(4)
print(x, x is y)
```

### Indentation is syntax

A block is defined by its indentation, and the convention is four spaces per level. The colon at the end of `if`, `for`, `def` and `class` opens the block.

```python
def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    return "positive"
```

### Input and output

`input()` always returns a `str`, so numbers need an explicit conversion. `print` separates its arguments with a space and ends with a newline, and both can be changed.

```python
age = int(input("Age: "))
print("Next year:", age + 1, sep=" ", end="!\n")
```

### Docstrings

```python run
def area(width, height):
    """Return the area of a rectangle."""
    return width * height

print(area(3, 4), area.__doc__)
```

### Interview questions

Q: Is Python compiled or interpreted?
A: Both, in two steps. CPython compiles source to bytecode, caches it in `__pycache__`, and a virtual machine executes that bytecode. There is no separate machine-code build step for the program you write.

Q: What does `if __name__ == "__main__":` do?
A: When a file runs directly, its `__name__` is the string `"__main__"`. When another module imports it, `__name__` is that module's own name. The guard lets one file be both a script and an importable module without running its demo code on import.

Q: What is PEP 8?
A: The official style guide: four-space indentation, `snake_case` for functions and variables, `CapWords` for classes, `UPPER_CASE` for constants, and lines short enough to read side by side in a review.

Q: Is Python dynamically typed, and is it strongly typed?
A: Dynamically typed means names carry no declared type while objects do, and types are checked as the program runs. Strongly typed means the interpreter will not silently mix incompatible types: `"1" + 1` raises a `TypeError` instead of guessing what you meant.

Q: What is a docstring, and where does it live?
A: A string literal placed as the first statement of a module, class or function. It is stored in `__doc__` and shown by `help()`, so it is the right place to state what the function promises to do.

:::pitfall Mixing tabs and spaces
Python 3 refuses to guess how wide a tab is. A file that mixes them raises `TabError` or `IndentationError`. Configure the editor to insert four spaces and never mix the two.
:::

:::remember Names are references
Assignment never copies. `b = a` makes two names for one object. To get an independent copy of a list, use `a[:]`, `a.copy()` or `copy.deepcopy`, and choose deliberately.
:::

@chapter
id: types
num: 02
pkg: int · float · bool · None · is versus == · truthiness
title: Data Types, Objects & Identity
summary: Everything is an object with an identity, a type and a value. Covers unbounded integers, binary floats, bool as a subclass of int, is versus ==, and which values are falsy.
@body

### Everything is an object

Every value is an object. It has a type, a value and an identity, which `id()` reports. `type()` gives the class, and `isinstance()` also accepts subclasses, which is usually what you want.

```python run
x = 42
print(type(x))
print(isinstance(True, int))
print(type(3.14), type(True), type(None))
```

### Integers and floats

`int` has no fixed size. Arithmetic on large values just uses more memory. `float` is an IEEE 754 double, which keeps about 15 to 17 significant decimal digits, so some decimal fractions cannot be stored exactly.

```python run
print(2 ** 100)
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(7 / 2, 7 // 2, -7 // 2, -7 % 3)
```

Note the division rules: `/` always gives a float, `//` floors toward negative infinity, and `%` takes the sign of the divisor.

### is versus ==

`==` asks whether two values are equal, by calling `__eq__`. `is` asks whether they are the *same object*. Use `is` for `None` and for sentinel objects, and `==` for everything else.

```python run
a = [1, 2]
b = [1, 2]
c = a
print(a == b, a is b, a is c)
```

### Truthiness

Every object has a truth value. Zero, empty containers, empty strings and `None` are false. Almost everything else is true, including the string `"0"`.

```python run
for value in [0, 0.0, "", [], {}, None, "0", [0]]:
    print(repr(value), bool(value))
```

### Rounding

`round()` uses banker's rounding: halves go to the nearest even number.

```python run
print(round(2.5), round(3.5))
```

### Interview questions

Q: What is the difference between `is` and `==`?
A: `==` compares values by calling `__eq__`. `is` compares identity, meaning the two names refer to the same object in memory. Two equal lists are `==` but not `is`.

Q: Why is `0.1 + 0.2 != 0.3` in Python?
A: Binary floating point cannot represent 0.1 exactly, so the sum is slightly above 0.3. Compare floats with `math.isclose`, and use `decimal.Decimal` when exact decimal arithmetic matters, such as money.

Q: Are Python integers bounded?
A: No. They grow as far as memory allows. Converting a very large integer to a decimal string is limited by default to 4300 digits since Python 3.11, which protects against slow quadratic conversions; `sys.set_int_max_str_digits` changes the limit.

Q: Which values are falsy?
A: `False`, `None`, zero of any numeric type, and empty strings, lists, tuples, dicts and sets. A class is falsy when it defines `__bool__` returning `False` or `__len__` returning `0`.

Q: Is `bool` a subclass of `int`?
A: Yes. `True` equals `1`, so `True + True` is `2`. That is why `isinstance(True, int)` is `True`, and why a check for integers sometimes needs to exclude booleans explicitly.

Q: What is the small-integer cache?
A: CPython keeps shared objects for integers from -5 to 256, so `is` happens to work for them. That is an implementation detail. Never rely on identity for numbers; compare with `==`.

:::pitfall is with a literal
`x is 5` looks like a comparison by value but tests identity. Modern Python warns about it with a `SyntaxWarning`. Use `x == 5`.
:::

:::remember Numeric types at a glance
`int` is unbounded and exact. `float` is binary and approximate. `bool` is a subclass of `int`. `decimal.Decimal` is exact in base ten.
:::
