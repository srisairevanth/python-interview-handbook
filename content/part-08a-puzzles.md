@part 8 | Practice

@chapter
id: puzzles
num: 16
pkg: traps · mutability · identity · evaluation order
title: Predict the Output
summary: Short programs whose output surprises people. Predict each result before you open the answer. Every answer is produced by running the code while this page is built.
@body

Read each program, write down what you expect, and only then open **Show answer**. Interviewers use these to test whether you know the object model, not whether you have memorised trivia. The **Reveal all answers** button in the header opens every answer at once.

:::puzzle Aliasing with chained assignment
```python
a = b = []
a.append(1)
print(b, a is b)
```
`a = b = []` binds both names to one list object, so appending through `a` is visible through `b`. The `is` check confirms they are the same object.
:::

:::puzzle Floats and comparison
```python
print(0.1 + 0.2 == 0.3, round(0.1 + 0.2, 10) == 0.3)
```
Binary floats cannot represent 0.1 or 0.2 exactly, so the sum is slightly above 0.3. Rounding to ten decimal places removes the representation error before the comparison.
:::

:::puzzle Floor division and modulo with negatives
```python
print(-7 // 2, -7 % 2, 7 // -2)
```
`//` rounds toward negative infinity, and `%` takes the sign of the divisor. That keeps `a == (a // b) * b + a % b` true for every integer pair.
:::

:::puzzle A tuple holding a list
```python
t = ([1], 2)
t[0].append(3)
print(t)
```
The tuple never changes, because its slots never change. The list in slot 0 is mutable, so its contents change. Assigning `t[1] = 5` would raise `TypeError`.
:::

:::puzzle Dictionary keys that compare equal
```python
d = {1: "a", True: "b", 1.0: "c"}
print(d)
```
`True` and `1.0` hash and compare equal to `1`, so each assignment updates the one existing key. The key stays as the first object inserted, and its value becomes `"c"`.
:::

:::puzzle Identity of empty containers
```python
t, u = (), ()
print([] == [], [] is [], t is u)
```
Each `[]` builds a new list, so the two lists are equal but not identical. CPython uses one shared empty tuple, so `t is u` is true.
:::

:::puzzle Chained comparisons
```python
print(3 in [1, 2, 3] == True)
```
Comparison operators chain. This means `(3 in [1, 2, 3]) and ([1, 2, 3] == True)`. The first part is true, the second is false, so the whole expression is false.
:::

:::puzzle Late binding in a comprehension
```python
def make():
    return [lambda: i for i in range(2)]

print([f() for f in make()])
```
Each lambda captures the variable `i`, not its value at creation. By the time they are called, the loop has finished with `i == 1`, so both return 1.
:::

:::puzzle A generator used twice
```python
g = (x for x in range(3))
print(list(g), list(g))
```
The first `list()` consumes every value. The second finds the generator already exhausted and returns an empty list.
:::

:::puzzle Strings are not changed by methods
```python
s = "  hi  "
s.strip()
print(repr(s))
```
`strip()` returns a new string, and the result was thrown away. The original keeps its spaces, and `repr` shows them.
:::

:::puzzle Which operations return floats
```python
print(type(1 / 1), type(1 // 1), type(2 ** -1))
```
`/` always produces a float. `//` on two ints produces an int. A negative exponent on an int produces a float, because the result is a fraction.
:::

:::puzzle In-place addition versus rebinding
```python
x = [1, 2, 3]
y = x
x += [4]
x = x + [5]
print(x, y)
```
`+=` on a list extends the same object, so `y` sees the change. `x + [5]` builds a new list and rebinds `x`, so `y` keeps the earlier list.
:::

:::puzzle Comparing strings
```python
print("a" < "B", "a".upper() < "B")
```
String comparison uses code points, and `"a"` is 97 while `"B"` is 66. Uppercasing `"a"` gives 65, which is below 66.
:::

:::puzzle One list under two keys
```python
d = dict.fromkeys("ab", [])
d["a"].append(1)
print(d)
```
`dict.fromkeys` stores the same list object under every key. Appending through one key shows up under all of them. Use a dict comprehension to create a separate list per key.
:::

:::puzzle Truthiness of strings
```python
print(bool("False"), bool(False), bool([False]))
```
Only empty containers are false. The string `"False"` is non-empty, so it is true, and a list holding `False` is also non-empty.
:::
