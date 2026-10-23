@part 5 | Advanced Python

@chapter
id: advanced
num: 10
pkg: closures · functools.wraps · yield · iterator protocol · with
title: Decorators, Generators & Context Managers
summary: Wrapping functions with decorators, lazy generators and the iterator protocol behind them, and the with statement that guarantees cleanup.
@body

### Decorators

`@logged` above a `def` means `add = logged(add)`. The wrapper runs before and after the original. `functools.wraps` copies the name and docstring across, so introspection still shows the original function.

```python run
import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}{args}")
        return func(*args, **kwargs)
    return wrapper

@logged
def add(a, b):
    """Add two numbers."""
    return a + b

print(add(2, 3), add.__name__, add.__doc__)
```

### Generators

A function containing `yield` returns a generator. Each `next()` runs the function up to the next `yield`. Values are produced on demand, so memory use stays constant however long the sequence is.

```python run
def countdown(n):
    while n > 0:
        yield n
        n -= 1

gen = countdown(3)
print(next(gen), list(gen))
print(sum(i * i for i in range(1_000_000)))
```

### The iterator protocol

A `for` loop calls `iter()` on the object, then `next()` until `StopIteration` is raised. A class that implements `__iter__` and `__next__` works everywhere a built-in iterable does.

```python run
class Evens:
    def __init__(self, limit):
        self.limit, self.current = limit, 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.limit:
            raise StopIteration
        value = self.current
        self.current += 2
        return value

print(list(Evens(5)))
```

### Context managers

`with` calls `__enter__` on entry and `__exit__` on exit, including when an exception is raised. `contextlib.contextmanager` builds one from a generator; the code after `yield` is the cleanup.

```python run
from contextlib import contextmanager

@contextmanager
def opened(name):
    print("open", name)
    try:
        yield name.upper()
    finally:
        print("close", name)

with opened("db") as handle:
    print("using", handle)
```

### Interview questions

Q: What is a decorator?
A: A callable that takes a function and returns a replacement, usually a wrapper that adds behaviour. `@d` above `def f` is the same as `f = d(f)`. Use `functools.wraps` so the wrapper keeps the original name, docstring and metadata.

Q: How is a generator different from a list?
A: A generator produces values one at a time, in constant memory, and can be consumed only once. A list stores every value, supports indexing and can be iterated many times. Use a generator for large or unbounded sequences and a list when you need random access.

Q: What is the difference between `yield` and `return`?
A: `return` ends the function and gives back one value. `yield` suspends the function, hands a value to the caller, and resumes at the same point on the next `next()`. Calling a generator function returns a generator object without running its body.

Q: What does the `with` statement guarantee?
A: It calls `__enter__` on entry and `__exit__` on exit, even if the block raises. Files, locks and database connections use it so that cleanup cannot be forgotten.

Q: How do you write a decorator that takes arguments?
A: Add one more layer. A factory takes the arguments and returns the decorator, which takes the function and returns the wrapper. `@retry(times=3)` first calls `retry(times=3)`, and that call's result decorates the function.

:::pitfall Forgetting functools.wraps
Without `functools.wraps`, the decorated function reports the wrapper's name and loses its docstring. That breaks `help()`, logging and some frameworks that read the name.
:::

:::remember Generators are single-use
Once a generator is exhausted, `list(gen)` returns an empty list. Create a new generator, or store the values in a list, when you need to iterate twice.
:::

@chapter
id: errors
num: 11
pkg: try · except · else · finally · EAFP · custom exceptions · modules · venv
title: Exceptions, Modules & Packaging
summary: The try statement and its four clauses, EAFP versus LBYL, custom exceptions and exception chaining, the __main__ guard, and why projects get virtual environments.
@body

### try, except, else and finally

`else` runs only when the try block raised nothing. `finally` runs on every path, including `return` inside `try`.

```python run
def parse(value):
    try:
        number = int(value)
    except ValueError:
        return "not a number"
    else:
        return f"ok {number}"
    finally:
        print("checked", repr(value))

print(parse("42"))
print(parse("x"))
```

### Custom exceptions

```python run
class InsufficientFunds(Exception):
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFunds(f"need {amount - balance} more")
    return balance - amount

try:
    withdraw(10, 25)
except InsufficientFunds as err:
    print(type(err).__name__, err)
```

### Modules and the __main__ guard

```python run
import math

print(math.isqrt(50), __name__)
```

### Virtual environments

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy
```

A virtual environment gives each project its own installed packages, so two projects can pin different versions of the same library.

### Interview questions

Q: What is the difference between EAFP and LBYL?
A: EAFP, "easier to ask forgiveness than permission", attempts the operation and handles the exception. LBYL, "look before you leap", checks conditions first. Python favours EAFP, but exceptions are not a substitute for ordinary control flow when a failure is common.

Q: What does `raise ... from err` do?
A: It sets `__cause__`, so the traceback reads "The above exception was the direct cause of the following exception". Use it to translate a low-level error into a domain error without losing the original.

Q: Should you catch `Exception` broadly?
A: Catch the most specific exception you can handle. A bare `except:` also catches `KeyboardInterrupt` and `SystemExit`, which should stop the program. Broad catches belong at boundaries that must not crash, and they should log the traceback.

Q: What is the difference between a module and a package?
A: A module is one `.py` file. A package is a directory of modules, traditionally with an `__init__.py`. Namespace packages can omit that file.

Q: Why use a virtual environment?
A: It isolates each project's dependencies, which avoids version conflicts between projects and keeps the system Python clean. Create one with `python -m venv` and install into it.

:::pitfall Bare except hides bugs
`except:` followed by `pass` swallows everything, including typos inside the try block. Name the exception, and keep the try block as small as possible.
:::

:::remember finally always runs
`finally` runs after a `return` in `try` and after an exception that is not caught. Use it for cleanup you cannot skip, though `with` is usually cleaner.
:::

@chapter
id: concurrency
num: 12
pkg: reference counting · cyclic GC · GIL · threads · processes · asyncio
title: Memory, the GIL & Concurrency
summary: How CPython frees memory, what the Global Interpreter Lock means for threads, when to choose threads, processes or asyncio, and how a race condition appears.
@body

### Memory: reference counts and the cyclic collector

CPython keeps a count of references to every object. When the count reaches zero, the object is freed at once. Reference cycles never reach zero, so a separate cyclic garbage collector finds and frees them.

```python run
import gc
import sys

a = []
print(sys.getrefcount(a))
b = a
print(sys.getrefcount(a))
del b
print(sys.getrefcount(a))
print(gc.isenabled())
```

The count is one higher than you might expect, because passing `a` to `getrefcount` creates a temporary reference.

### The GIL

The Global Interpreter Lock lets only one thread run Python bytecode at a time in CPython. The lock is released while a thread waits on I/O, so threads still help with network and disk waits. CPU-bound threads gain nothing. Python 3.13 ships an experimental free-threaded build (PEP 703) that removes the GIL, but the standard build still has it.

### Threads for I/O-bound work

```python run
from concurrent.futures import ThreadPoolExecutor

def fetch(n):
    return n * n  # stands in for a call that waits on the network

with ThreadPoolExecutor(max_workers=4) as pool:
    print(list(pool.map(fetch, range(5))))
```

### asyncio for many waits in one thread

```python run
import asyncio

async def job(name, delay):
    await asyncio.sleep(delay)
    return f"{name} done"

async def main():
    results = await asyncio.gather(job("a", 0.2), job("b", 0.1))
    print(results)

asyncio.run(main())
```

### A race condition

`counter += 1` is several bytecode steps: load, add, store. A thread switch between them loses an update. A lock makes the read-modify-write block indivisible.

```python
import threading

counter = 0
lock = threading.Lock()

def work():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1
```

### Interview questions

Q: What is the GIL, and why does it exist?
A: The Global Interpreter Lock allows one thread at a time to execute Python bytecode. It keeps reference counts and interpreter state consistent without a lock on every object, and it keeps single-threaded code fast. Threads still overlap I/O waits, because the lock is released while they wait.

Q: Threads or processes?
A: Threads for I/O-bound work. Processes for CPU-bound work, through `multiprocessing` or `ProcessPoolExecutor`, because each process has its own interpreter and GIL. Processes cost more memory, and their arguments and results must be picklable.

Q: When is asyncio the right choice?
A: For many concurrent network or file waits inside one thread, with explicit `await` points. It does not speed up CPU-bound code, and a blocking call inside a coroutine stalls every other task.

Q: How does Python free memory?
A: Reference counting frees an object as soon as its count reaches zero. The cyclic garbage collector finds unreachable reference cycles. Do not rely on `__del__` for timing; use `with` for resources.

Q: What is a race condition, and how do you prevent one?
A: Two threads touch shared mutable state, and the result depends on timing. Protect the state with a lock, or avoid sharing: pass messages through a `queue.Queue`, or give each worker its own data.

:::pitfall Blocking calls inside async code
`time.sleep` inside an `async def` blocks the whole event loop. Use `await asyncio.sleep`, and move blocking library calls into a thread with `asyncio.to_thread`.
:::

:::say Explaining the GIL
"CPython runs one thread of Python bytecode at a time. Threads still help for I/O, but CPU-heavy work needs processes. That is why I would use a process pool for the numeric part and asyncio for the network part."
:::
