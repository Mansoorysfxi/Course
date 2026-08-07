# Lesson 05 — Object-Oriented Python: Classes, Dunders, Inheritance, and Composition

## What you'll learn

- How to define a class, create instances, and understand what `self` actually is.
- Dunder ("double underscore") methods — `__init__`, `__str__`, `__repr__`, `__eq__`, `__len__`, and how to make your own class iterable using `__iter__`/`__next__` from Lesson 04.
- Inheritance in Python: syntax, `super()`, method overriding — and exactly how it compares to and differs from C++ inheritance.
- Composition as an alternative to inheritance, and a concrete rule for choosing between them.
- Class attributes vs. instance attributes, and a mutable-class-attribute trap analogous to Lesson 02's mutable default argument trap.

## Why this matters

You already know OOP from C++ and Unreal's Actor/Component model — this lesson isn't teaching the *concept* of objects from zero, it's translating what you already know into Python's specific syntax and rules, several of which differ from C++ in ways that matter (no access modifiers enforced by the language, everything is effectively virtual, multiple inheritance works differently, and "duck typing" replaces strict interface contracts). Your capstone's core data model — a `Quest` and a `QuestManager`/`QuestLog` class — is built directly on everything in this lesson.

## Prerequisites

Lessons 01–04. Dunder methods specifically build on the `iter()`/`next()` mechanism from Lesson 04.

## The concept, explained simply

A **class** is a blueprint; an **instance** is one concrete thing built from that blueprint — exactly the same relationship as a C++ class and an object of that class, or an Unreal Blueprint class and an actor placed in the level from it. Where Python differs immediately: there's no separate header/declaration step, no `public`/`private`/`protected` enforced by the compiler (Python uses naming *conventions* instead — covered below), and every method implicitly takes the instance itself as its first parameter, spelled `self`, which you write explicitly in every method signature (C++'s `this` is implicit and hidden; Python's `self` is explicit and visible, by design — "explicit is better than implicit" is a genuine, often-quoted piece of Python philosophy).

## The details

### Defining a class and creating instances

```python
class Quest:
    def __init__(self, name, difficulty):
        self.name = name
        self.difficulty = difficulty
        self.is_complete = False

    def complete(self):
        self.is_complete = True

q1 = Quest("Slay the Dragon", "Hard")
q2 = Quest("Water the Plants", "Trivial")

print(q1.name, q1.difficulty, q1.is_complete)
q1.complete()
print(q1.is_complete)
print(q2.is_complete)   # unaffected — separate instance
```
**Run:** `python lesson05.py` → **Expected output:**
```
Slay the Dragon Hard False
True
False
```

**Line by line:**
- `class Quest:` — defines the blueprint. By convention, class names use `CapitalizedWords` ("PascalCase"), while everything else in Python (variables, functions, methods) uses `snake_case` — this convention matters for readability and is followed throughout this course and virtually all Python code you'll ever read.
- `def __init__(self, name, difficulty):` — the **constructor**, called automatically exactly once, right when you write `Quest("Slay the Dragon", "Hard")`. `__init__` is itself a dunder method (more below) — Python doesn't have a separate keyword like C++'s constructor-named-after-the-class syntax; it recognizes `__init__` specifically by name and calls it for you.
- `self` — the instance being created/operated on, always the first parameter of every regular method, always passed automatically by Python when you call `q1.complete()` (you never type `self` at the *call* site — only in the method's own `def` line). If you forget `self` in a method definition, calling it produces a confusing `TypeError` about too many/too few arguments — a very common early mistake, listed below.
- `self.name = name` — attaches `name` as an **attribute** on *this specific instance*. Each `Quest` instance gets its own independent `name`, `difficulty`, `is_complete` — exactly like each C++ object having its own copy of its non-static member variables.
- `q1.complete()` — Python automatically passes `q1` itself as `self` here; you're calling the method *on* `q1`.

### Dunder methods — Python's version of operator overloading

**"Dunder"** is short for "double underscore" — methods named `__like_this__`. Python's classes use them specifically as hooks the language itself calls automatically in response to built-in operations: printing, comparing with `==`, calling `len()`, looping with `for`, and more. This is Python's answer to C++ operator overloading, but far more pervasive — nearly everything you do to a built-in type (printing it, comparing it, adding it) is, underneath, a dunder method call.

```python
class Quest:
    def __init__(self, name, difficulty, reward_gold):
        self.name = name
        self.difficulty = difficulty
        self.reward_gold = reward_gold

    def __str__(self):
        return f"Quest: {self.name} ({self.difficulty})"

    def __repr__(self):
        return f"Quest(name={self.name!r}, difficulty={self.difficulty!r}, reward_gold={self.reward_gold})"

    def __eq__(self, other):
        return self.name == other.name and self.difficulty == other.difficulty

q = Quest("Slay the Dragon", "Hard", 500)
print(q)                        # calls __str__
print(repr(q))                  # calls __repr__ explicitly
print([q])                      # a list of one quest — printing a list calls repr() on each item, not str()
print(q == Quest("Slay the Dragon", "Hard", 999))   # __eq__, ignoring reward_gold entirely
```
**Expected output:**
```
Quest: Slay the Dragon (Hard)
Quest(name='Slay the Dragon', difficulty='Hard', reward_gold=500)
[Quest(name='Slay the Dragon', difficulty='Hard', reward_gold=500)]
True
```

**Line by line:**
- `__str__` — controls what `str(q)` and `print(q)` show: a **human-readable** description.
- `__repr__` — controls `repr(q)`: an **unambiguous, developer-facing** description, ideally one that looks like the code you'd type to recreate the object (`!r` inside an f-string is shorthand for calling `repr()` on that value instead of `str()`, which is why the strings show their quotes). If a class defines `__repr__` but not `__str__`, Python falls back to using `__repr__` for `print()` too — which is why defining at least `__repr__` on every class you write is a strong, widespread convention: it makes debugging (printing objects while tracking down a bug) dramatically easier than the default `<__main__.Quest object at 0x000001A2B3C4D5E6>` you'd get with neither defined.
- `__eq__` — controls what `==` does between two instances. Without it, `==` on two separate instances checks *identity* (are these literally the same object in memory — like comparing two pointers), which is almost never what you want when comparing two `Quest`s that merely have the same data.

**Without any dunders**, printing a plain object shows something genuinely unhelpful:
```python
class Bare:
    pass

print(Bare())
```
**Expected output:** something like `<__main__.Bare object at 0x000001A2B3C4D5E6>` — a memory address, telling you almost nothing. This is exactly the "magic behavior, opened up" moment: that ugly default *is* what `__str__`/`__repr__` return when you don't define them yourself — there's no deeper magic, just a default implementation you're free to override.

### Making your own class iterable — connecting back to Lesson 04

```python
class QuestLine:
    def __init__(self, quests):
        self._quests = quests

    def __len__(self):
        return len(self._quests)

    def __iter__(self):
        return iter(self._quests)

line = QuestLine([Quest("A", "Easy", 10), Quest("B", "Medium", 20)])
print(len(line))
for quest in line:
    print(quest)
```
**Expected output:**
```
2
Quest: A (Easy)
Quest: B (Medium)
```

`__len__` makes `len(line)` work. `__iter__` makes `for quest in line:` work — and here it's implemented by simply delegating to the *already-iterable* internal list's own `iter()`, exactly the mechanism from Lesson 04. You could instead write a fully custom `__iter__`/`__next__` pair by hand for more control, but delegating to an internal collection like this is extremely common and perfectly idiomatic.

### Class attributes vs. instance attributes — and a familiar-looking trap

```python
class Quest:
    total_quests_created = 0    # class attribute — shared by ALL instances

    def __init__(self, name):
        self.name = name        # instance attribute — unique per instance
        Quest.total_quests_created += 1

q1 = Quest("A")
q2 = Quest("B")
print(Quest.total_quests_created)
print(q1.name, q2.name)
```
**Expected output:**
```
2
A B
```

A **class attribute** (defined directly in the class body, not inside `__init__`) is shared across every instance — genuinely one single value, not a per-instance copy — closer to a C++ `static` member variable. An **instance attribute** (assigned via `self.x = ...`, almost always inside `__init__`) belongs to that one specific object.

**The trap — recognize this immediately, it's Lesson 02's mutable default argument bug wearing a different costume:**

```python
class QuestLog:
    entries = []   # DANGER: a mutable class attribute, shared by every instance

    def add(self, quest_name):
        self.entries.append(quest_name)

log1 = QuestLog()
log2 = QuestLog()
log1.add("Slay the Dragon")
print(log2.entries)   # you'd expect [], but...
```
**Expected output:** `['Slay the Dragon']` — `log2` sees `log1`'s entry, because `entries = []` at class level created exactly **one** list, shared by every instance, exactly like the shared default-argument list from Lesson 02. **The fix is the same shape as Lesson 02's fix:** create mutable state inside `__init__` instead, as an instance attribute:

```python
class QuestLog:
    def __init__(self):
        self.entries = []   # a fresh, independent list per instance

    def add(self, quest_name):
        self.entries.append(quest_name)
```

### Inheritance — syntax, `super()`, and overriding

```python
class Quest:
    def __init__(self, name, reward_gold):
        self.name = name
        self.reward_gold = reward_gold

    def describe(self):
        return f"{self.name} — rewards {self.reward_gold} gold"

class TimedQuest(Quest):
    def __init__(self, name, reward_gold, time_limit_minutes):
        super().__init__(name, reward_gold)
        self.time_limit_minutes = time_limit_minutes

    def describe(self):
        base = super().describe()
        return f"{base}, must finish within {self.time_limit_minutes} minutes"

tq = TimedQuest("Defuse the Trap", 300, 5)
print(tq.describe())
print(isinstance(tq, Quest))
print(isinstance(tq, TimedQuest))
```
**Expected output:**
```
Defuse the Trap — rewards 300 gold, must finish within 5 minutes
True
True
```

**Line by line:**
- `class TimedQuest(Quest):` — `TimedQuest` **inherits** from `Quest`; every `TimedQuest` *is a* `Quest` and automatically has everything `Quest` defines, unless overridden. Same core idea as C++ `class TimedQuest : public Quest`.
- `super().__init__(name, reward_gold)` — explicitly calls the parent class's `__init__`, so `TimedQuest` doesn't have to re-implement setting `self.name`/`self.reward_gold` itself. `super()` gives you a reference to the parent class specifically for this purpose. **A genuine difference from C++:** Python does **not** call the parent's `__init__` automatically when a subclass defines its own — if `TimedQuest.__init__` exists at all, it completely replaces `Quest.__init__` unless you explicitly call `super().__init__(...)` yourself. Forgetting this line is a common bug: `self.name` would simply never get set.
- `describe` in `TimedQuest` **overrides** `describe` in `Quest` — same method name, different behavior, called automatically based on the actual instance's real type. Notice `TimedQuest.describe` calls `super().describe()` to reuse the parent's version and extend it, rather than duplicating that logic — a common, good pattern.
- `isinstance(tq, Quest)` is `True` — `tq` is a `TimedQuest`, and every `TimedQuest` is *also* a `Quest`.

**The biggest conceptual difference from C++:** in C++, a method is only polymorphic (callable-via-base-pointer-and-resolved-to-the-derived-version) if you mark it `virtual`. **In Python, every method is effectively virtual, always** — there's no `virtual` keyword, no separate concept of "non-virtual method calls," because Python resolves *every* method call by looking at the object's *actual* runtime type first, always. This removes an entire category of C++ bugs (forgetting `virtual` and silently getting base-class behavior) at the cost of removing a tool C++ gives you for deliberately preventing overriding (though Python does have a narrower, less commonly used way to discourage subclassing certain things — outside this lesson's scope).

**Also different: no enforced access modifiers.** Python has no `private`/`protected`/`public` keywords the *language* enforces. Instead, convention marks intent: a single leading underscore (`self._entries`) means "internal, please don't touch this from outside the class, but nothing stops you" — this course used exactly this convention in `QuestLine._quests` above. A double leading underscore (`self.__entries`) triggers a Python-specific mechanism called **name mangling** that makes accidental external access *harder* (not impossible) — genuinely rare in everyday code, worth recognizing if you see it, not something you need to reach for yourself in this course.

### Composition — an alternative to inheritance

**Inheritance** answers "is this fundamentally a more specific version of that?" (a `TimedQuest` *is a* `Quest`). **Composition** answers a different question: "does this *have* / *use* one of those?" — building a class by holding instances of other classes as attributes, rather than inheriting from them.

```python
class Reward:
    def __init__(self, gold, item=None):
        self.gold = gold
        self.item = item

    def describe(self):
        text = f"{self.gold} gold"
        if self.item:
            text += f" and {self.item}"
        return text

class Quest:
    def __init__(self, name, reward: Reward):
        self.name = name
        self.reward = reward   # composition: a Quest HAS a Reward, it isn't one

    def describe(self):
        return f"{self.name} — rewards {self.reward.describe()}"

q = Quest("Slay the Dragon", Reward(500, "Dragon Scale"))
print(q.describe())
```
**Expected output:** `Slay the Dragon — rewards 500 gold and Dragon Scale`

**The decision rule this course uses, and that translates directly to your Unreal experience (Actor/Component):** default to composition. Reach for inheritance specifically when the relationship is genuinely "is-a" *and* you want the subtype to be usable anywhere the base type is expected (`isinstance(tq, Quest)` being `True` and meaningful, like passing a `TimedQuest` into a function that expects any `Quest`). If you're inheriting purely to reuse some code, with no real "is-a" relationship, that's a sign composition (holding an instance, calling its methods) is the better fit — it's more flexible, easier to change later, and avoids deep, fragile inheritance chains. This is exactly the reasoning behind Unreal's own long-term shift toward Actor Components over deep Actor subclass hierarchies — the same trade-off, different language.

## Common mistakes & gotchas

- **Forgetting `self` as a method's first parameter.** Produces a `TypeError: method() takes 0 positional arguments but 1 was given` (or similar) — Python is trying to pass the instance automatically and your method signature has nowhere for it to go.
- **Defining a mutable class attribute (`entries = []`) expecting each instance to get its own.** It's shared by every instance — exactly Lesson 02's mutable-default-argument bug, same fix: initialize it inside `__init__` as an instance attribute instead.
- **Forgetting to call `super().__init__(...)` in a subclass that defines its own `__init__`.** The parent's setup code silently never runs; attributes you expected to exist (from the parent) simply aren't there, producing an `AttributeError` later, often far from the actual cause.
- **Relying on `==` before defining `__eq__` and being surprised it's `False` for "equal-looking" objects.** Without `__eq__`, `==` compares identity (same object in memory), not the values inside — define `__eq__` explicitly whenever "same data" should count as equal.
- **Overusing inheritance for code reuse when there's no real "is-a" relationship.** Leads to deep, fragile class hierarchies where changing a base class breaks distant, seemingly unrelated subclasses. Default to composition; reach for inheritance deliberately.

## How this connects

This lesson gives you the exact building blocks the capstone's core data model needs: a `Quest` class (attributes, dunders for readable printing/equality) and a `QuestManager`/`QuestLog` class that likely holds a collection of `Quest`s internally (composition, plus possibly `__iter__`/`__len__` from Lesson 04's mechanism). Lesson 06 (Error Handling) shows how to define **custom exception classes**, which are themselves classes — usually inheriting from Python's built-in `Exception` — so everything about class syntax and inheritance here applies directly there too.

## Quick self-check

1. What is `self`, and why do you write it explicitly in every method definition when C++'s equivalent (`this`) is implicit?
2. Why does Python not have a `virtual` keyword, and what does that imply about every method call on an object?
3. What's the practical difference between a class attribute and an instance attribute, and what's the specific trap with *mutable* class attributes?
4. If `TimedQuest` defines its own `__init__` and never calls `super().__init__(...)`, what happens to the attributes `Quest.__init__` would normally set?
5. Give a concrete example (not from this lesson) of when you'd choose composition over inheritance, and explain why.
