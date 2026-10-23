@part 6 | Python for AI and Data

@chapter
id: numpy
num: 13
pkg: ndarray · broadcasting · views versus copies · pandas · seeds
title: NumPy, pandas & ML-Code Pitfalls
summary: Why arrays beat Python loops, broadcasting, views versus copies, grouped operations in pandas, and the habits that make experiments reproducible.
@body

### Why arrays are fast

A NumPy `ndarray` stores one data type in one contiguous block of memory. Operations run as compiled loops over that block instead of Python-level loops over objects, so `a * 2` on a million numbers costs far less than a `for` loop doing the same. Prefer whole-array operations to element-by-element Python code.

### Broadcasting

When shapes differ, NumPy stretches dimensions of size 1 to match. A row of three values is applied to every row of a two-by-three matrix.

```python run
import numpy as np

x = np.array([[1, 2, 3], [4, 5, 6]])
print(x * 10)
print(x + np.array([100, 200, 300]))
print(x.sum(axis=0), x.mean())
```

### Views versus copies

Basic slicing returns a view that shares memory with the original. Changing the view changes the array. Call `.copy()` when you need an independent array. Fancy indexing with a list or a boolean mask returns a copy.

```python run
import numpy as np

a = np.arange(6)
view = a[1:4]
view[0] = 99
copy = a[1:4].copy()
copy[0] = -1
print(a)
```

### Grouped operations in pandas

```python run
import pandas as pd

df = pd.DataFrame({"city": ["Pune", "Delhi", "Pune"], "temp": [31, 35, 29]})
print(df.groupby("city")["temp"].mean())
```

### Reproducible randomness

Use a generator object instead of the global random state, and pass the seed explicitly. Experiments then give the same numbers on every run in the same environment.

```python run
import numpy as np

rng = np.random.default_rng(seed=42)
print(rng.integers(0, 10, size=5))
```

### Interview questions

Q: Why is NumPy faster than a Python loop?
A: Its arrays hold one type in contiguous memory, and the operations run as compiled loops, often using vector instructions. A Python loop pays interpreter overhead and object lookups for every element.

Q: What is broadcasting?
A: The rule that lets arrays of different shapes combine. Shapes are compared from the right, and a dimension of size 1 is stretched to match the other operand. It avoids copying data just to make shapes agree.

Q: What is the difference between a view and a copy?
A: A view shares the underlying memory, so writes through it change the original. A copy has its own memory. Basic slices give views, while `.copy()`, fancy indexing and boolean masks give copies.

Q: How do you make ML experiments reproducible?
A: Fix the seeds you use and pass them explicitly. Pin library versions, record the configuration and the data version, and avoid parallel reductions when you need bit-identical results. Mention that GPU kernels can be nondeterministic unless configured otherwise.

:::pitfall Chained assignment in pandas
`df[df.temp > 30]["flag"] = 1` may write to a temporary copy and change nothing. Use a single indexer: `df.loc[df.temp > 30, "flag"] = 1`.
:::

:::pitfall Row loops in pandas
`iterrows` builds a Series for every row and is very slow on large frames. Express the logic as column operations, or use `groupby`, `where` or `np.select`.
:::
