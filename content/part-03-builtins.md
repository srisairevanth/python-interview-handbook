@part 3 | Built-in Data Structures

@chapter
id: builtins
num: 06
pkg: dynamic arrays · hash tables · complexity · copying · sorting
title: Lists, Tuples, Sets & Dicts
summary: Lists are dynamic arrays, sets and dicts are hash tables. Covers complexity, hashability, shallow versus deep copies, insertion order, and sorting with a key.
@body

### What the containers are built on

A `list` is a dynamic array of references: indexing is O(1), appending is amortised O(1), and inserting or deleting in the middle shifts every later element. A `dict` and a `set` are hash tables: a key's hash chooses where it lives, so lookup, insertion and deletion are O(1) on average. Dicts keep insertion order. Sets do not promise any order.

| Operation | list | set | dict |
|---|---|---|---|
| index or key access | `x[i]` O(1) | not applicable | `d[k]` O(1) average |
| membership `x in c` | O(n) | O(1) average | `k in d` O(1) average |
| add or append | `append` O(1) amortised | `add` O(1) average | `d[k] = v` O(1) average |
| remove | `remove` O(n) | `discard` O(1) average | `del d[k]` O(1) average |
| insert or pop at the front | `insert(0, x)` O(n) | not applicable | not applicable |

### Dicts and sets in action

```python run
d = {"b": 2, "a": 1}
d["c"] = 3
print(d, list(d.keys()))
print(d.get("z", 0), "a" in d)
s = {3, 1, 2, 3}
print(s, len(s))
```

### Hashability

Only hashable objects can be dictionary keys or set members. A hashable object has a hash that never changes during its lifetime, and it compares equal to other objects with the same hash when they are equal.

```python run
try:
    {[1, 2]: "x"}
except TypeError as err:
    print(err)
print(hash((1, 2)) == hash((1, 2)))
```

### Aliasing and copies

`grid[:]` and `list(grid)` copy only the outer list. The inner lists are still shared, which the output below makes visible.

```python run
import copy

grid = [[0, 0], [0, 0]]
shallow = grid[:]
deep = copy.deepcopy(grid)
grid[0][0] = 9
print(shallow[0][0], deep[0][0])
```

### Sorting with a key

`sorted` returns a new list and accepts any iterable. `list.sort` sorts in place and returns `None`. Both are stable, so items with equal keys keep their original order.

```python run
people = [("ana", 31), ("bo", 25), ("cy", 31)]
print(sorted(people, key=lambda p: p[1], reverse=True))
print(sorted(["b", "A", "c"], key=str.lower))
```

### Changing a list while looping over it

Removing items from a list during a `for` loop skips the element that slides into the removed slot.

```python run
items = [2, 4, 6, 7]
for x in items:
    if x % 2 == 0:
        items.remove(x)
print(items)
```

### Interview questions

Q: How does a dictionary lookup work?
A: The key's hash picks a starting slot in the table. CPython probes from there and compares keys with `==` when the hashes match. The average cost is O(1). Keys must be hashable, and their hash must not change while they are stored in the dict.

Q: Why are tuples hashable but lists are not?
A: A tuple of hashable items cannot change, so its hash can stay fixed. A list can change, and a hash that changed after insertion would make lookups fail. That is why `{[1, 2]: "x"}` raises `TypeError: unhashable type: 'list'`.

Q: When would you use a list, a tuple, a set or a dict?
A: A list for an ordered, mutable sequence. A tuple for a fixed record, or as a dict key because it is immutable. A set for uniqueness and fast membership tests. A dict to map keys to values.

Q: What is the difference between `list.sort()` and `sorted()`?
A: `list.sort()` sorts in place and returns `None`. `sorted()` returns a new list and works on any iterable. Both use Timsort, which is stable and fast on partly sorted data.

Q: Are dicts ordered?
A: Yes. Since Python 3.7, a dict keeps insertion order and the language guarantees it. Sets make no ordering promise and cannot be indexed.

Q: Why is `x in some_list` slow for large lists?
A: It scans element by element, so it is O(n). If you test membership many times, build a set once. Each test then averages O(1).

:::pitfall Shallow copies share nested objects
`grid[:]` copies one level. Nested lists and dicts are shared between the copies. Use `copy.deepcopy` for nested data that must stay independent.
:::

:::remember dict.get and setdefault
`d.get(k, default)` reads without raising `KeyError` and leaves the dict unchanged. `d.setdefault(k, default)` also stores the default when the key is missing.
:::

@chapter
id: collections
num: 07
pkg: Counter · defaultdict · deque · heapq · bisect
title: collections, heapq & bisect
summary: The standard-library containers and algorithms that show up in interview code: counting, grouping, queues, priority queues and binary search on sorted lists.
@body

### Counter and defaultdict

```python run
from collections import Counter, defaultdict

words = "the cat and the hat and the bat".split()
print(Counter(words).most_common(2))
groups = defaultdict(list)
for w in words:
    groups[len(w)].append(w)
print(dict(groups))
```

### deque for queues

`deque` gives O(1) appends and pops at both ends. Read the output carefully: `print` renders its arguments only after every argument has been evaluated, so the queue is already smaller when it prints.

```python run
from collections import deque

q = deque([1, 2, 3])
q.append(4)
q.appendleft(0)
print(q, q.popleft(), q.pop())
```

### heapq: a min-heap

```python run
import heapq

nums = [5, 1, 8, 3]
heapq.heapify(nums)
print(heapq.heappop(nums), nums[0])
print(heapq.nlargest(2, [5, 1, 8, 3]))
```

### bisect on a sorted list

```python run
import bisect

sorted_nums = [1, 3, 3, 7]
print(bisect.bisect_left(sorted_nums, 3), bisect.bisect_right(sorted_nums, 3))
bisect.insort(sorted_nums, 5)
print(sorted_nums)
```

### Interview questions

Q: Why use `deque` for a queue instead of a list?
A: `append` and `popleft` are O(1) on a deque. Removing from the front of a list with `pop(0)` shifts every remaining element, which is O(n). A breadth-first search on a large graph slows badly with a list.

Q: How do you build a max-heap in Python?
A: `heapq` provides only a min-heap. For numbers, push negated values. For anything else, push `(-priority, item)` tuples, or `(priority, counter, item)` so that equal priorities never compare the items themselves.

Q: What does `defaultdict` do that a plain dict does not?
A: It creates a default value the first time a missing key is read or written, using a factory such as `list` or `int`. That removes the `if key not in d` branch from grouping and counting loops.

Q: When would you reach for `Counter`?
A: To count hashable items. `most_common(k)` returns the top k. Counters also support addition, subtraction and intersection, which makes frequency and anagram problems short.

:::pitfall Heap ties compare the next field
A heap of tuples compares the second field whenever the first fields are equal. If the second field is not orderable, such as a dict, the comparison raises `TypeError`. Add a unique counter as a tie-breaker.
:::

:::remember bisect and insort
`bisect` finds a position in O(log n). `insort` also inserts, but the shift makes the insertion O(n) in the worst case, so it is best for modest sizes.
:::
