@part 4 | Object-Oriented Python

@chapter
id: classes
num: 08
pkg: __init__ · instance versus class attributes · dunder methods · properties
title: Classes, Dunder Methods & Properties
summary: How instances and class attributes resolve, what __repr__, __eq__ and __hash__ are for, computed attributes with @property, and the difference between classmethod and staticmethod.
@body

### Instance attributes and class attributes

Attributes written on `self` belong to one instance. Attributes written in the class body belong to the class and are shared until an instance shadows them.

```python run
class Counter:
    count = 0

    def __init__(self, name):
        self.name = name
        Counter.count += 1

a, b = Counter("a"), Counter("b")
print(a.count, b.count, Counter.count)
a.count = 99
print(a.count, b.count, Counter.count)
```

### Dunder methods: repr, eq and hash

`__repr__` is the developer-facing text. `__eq__` defines `==`. If you define `__eq__` and want instances in sets or dict keys, you must also define a `__hash__` consistent with it.

```python run
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

p = Point(1, 2)
print(p, [p], p == Point(1, 2), {p, Point(1, 2)})
```

### Properties

A property looks like an attribute but runs code on access. It is the usual way to derive a value from stored state.

```python run raises
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

t = Temperature(100)
print(t.fahrenheit)
t.fahrenheit = 50
```

The last line fails on purpose: the property has a getter but no setter.

### classmethod and staticmethod

A classmethod receives the class, so it can build alternative constructors that work for subclasses too. A staticmethod receives neither the class nor the instance; it is a function that lives in the class namespace.

```python run
class Pizza:
    def __init__(self, toppings):
        self.toppings = toppings

    @classmethod
    def margherita(cls):
        return cls(["tomato", "mozzarella"])

    @staticmethod
    def is_vegetarian(toppings):
        return "ham" not in toppings

print(Pizza.margherita().toppings, Pizza.is_vegetarian(["tomato"]))
```

### Name mangling

Names that begin with two underscores inside a class body are rewritten to `_ClassName__name`. This avoids accidental clashes with subclasses. It is not access control.

```python run
class Account:
    def __init__(self):
        self.__balance = 10

print(Account()._Account__balance)
```

### Interview questions

Q: What is `self`?
A: The instance the method was called on. Python passes it automatically, so `obj.method(x)` is the same as `Class.method(obj, x)`. The name is a strong convention, not a keyword.

Q: What is the difference between `__repr__` and `__str__`?
A: `__repr__` is the unambiguous developer representation, used by `repr()`, the debugger and containers. `__str__` is the friendly text used by `print` and `str()`. If `__str__` is missing, Python falls back to `__repr__`.

Q: Why define `__hash__` when you define `__eq__`?
A: If a class defines `__eq__` without `__hash__`, Python sets `__hash__` to `None`, so instances become unhashable. Define both, and make sure equal objects have equal hashes. Hashing an object whose state can change is risky.

Q: What is the difference between `@classmethod` and `@staticmethod`?
A: A classmethod receives the class as `cls` and suits alternative constructors. A staticmethod receives no implicit argument and is simply a function grouped under the class name.

Q: What is name mangling?
A: A name written as `__x` inside a class body is stored as `_ClassName__x`. It prevents accidental overrides in subclasses. It is not privacy, and `obj._ClassName__x` still works.

:::pitfall Mutable class attributes are shared
A list or dict defined in the class body is shared by every instance. `self.items.append(x)` changes the class-level list for everyone. Create mutable state in `__init__`.
:::

:::remember Computed attributes
Use `@property` for values derived from other state. Callers keep the same attribute syntax if you change how the value is stored later.
:::

@chapter
id: inheritance
num: 09
pkg: super() · MRO · abstract base classes · dataclasses · __slots__
title: Inheritance, MRO & Dataclasses
summary: How super() follows the method resolution order, abstract base classes, dataclasses with frozen and ordered options, and what __slots__ trades away.
@body

### super() and the method resolution order

Python searches a class hierarchy in the order given by the C3 linearisation, stored in `__mro__`. `super()` continues along that order, which is what makes cooperative multiple inheritance work.

```python run
class A:
    def hello(self):
        return "A"

class B(A):
    def hello(self):
        return "B>" + super().hello()

class C(A):
    def hello(self):
        return "C>" + super().hello()

class D(B, C):
    def hello(self):
        return "D>" + super().hello()

print(D().hello())
print([k.__name__ for k in D.__mro__])
```

### Abstract base classes

```python run
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        ...

class Square(Shape):
    def __init__(self, s):
        self.s = s

    def area(self):
        return self.s ** 2

print(Square(3).area())
try:
    Shape()
except TypeError as err:
    print(err)
```

### Dataclasses

`@dataclass` writes `__init__`, `__repr__` and `__eq__` from the field annotations. `frozen=True` makes instances immutable and hashable. `order=True` adds comparison methods based on the fields in order.

```python run
from dataclasses import dataclass, field

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    tags: tuple = field(default=(), compare=False)

v1, v2 = Version(1, 4), Version(2, 0)
print(v1, v1 < v2)
try:
    v1.major = 9
except Exception as err:
    print(type(err).__name__)
```

### __slots__

```python run
class Slotted:
    __slots__ = ("x",)

s = Slotted()
s.x = 1
try:
    s.y = 2
except AttributeError:
    print("AttributeError")
```

### Interview questions

Q: What is the MRO, and how is it computed?
A: The method resolution order is the list of classes Python searches for an attribute, stored in `Class.__mro__`. It comes from C3 linearisation, which keeps each class before its bases, keeps the left-to-right order of the bases, and fails if no consistent order exists.

Q: Why use `super()` instead of naming the base class directly?
A: `super()` follows the MRO of the instance's actual class. Naming a parent directly can call a shared ancestor twice or skip a class in a diamond hierarchy. Cooperative classes all call `super()`.

Q: Is an abstract base class the same as an interface?
A: It plays that role. An ABC refuses to instantiate a subclass that leaves an abstract method unimplemented, and it supports `isinstance` checks. Pythonic code often relies on duck typing instead, so use ABCs for public contracts.

Q: How does a dataclass differ from a NamedTuple or a plain class?
A: A dataclass generates the boilerplate methods and can be frozen. A NamedTuple is an immutable tuple with named fields, so it unpacks like a tuple. A plain class suits objects with a lot of custom behaviour.

Q: What does `__slots__` buy you, and what does it cost?
A: Instances drop their per-object `__dict__`, which saves memory and makes attribute access a little faster. The cost is that you cannot add arbitrary attributes, and a subclass without its own `__slots__` gets a `__dict__` back.

:::remember Dataclass defaults
Dataclass instances are mutable unless you pass `frozen=True`, which suits value objects. A bare `[]` default raises `ValueError` when the class is defined, so write `field(default_factory=list)` instead.
:::

:::pitfall Diamond hierarchies need super()
If two bases share an ancestor, a base that calls the ancestor by name can run its code twice. Calling `super()` everywhere keeps each method running once.
:::
