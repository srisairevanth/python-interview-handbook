@chapter
id: sets
num: 17
pkg: timed drills · mock rounds · where to practise
title: Practice Sets & Where to Practise
summary: Timed drills and mock rounds that match an interview, and the places to practise Python, with links to the official references you should trust over any summary.
@body

### Practice sets

| Set | What to do | Time |
|---|---|---|
| Pattern drill | Two problems from one group of the tracker, the same day you read its templates | 60 min |
| Mock DSA round | One random problem from the tracker, no hints, explaining aloud as you go | 25 min |
| Output round | Ten puzzles from the previous chapter, answers hidden until you commit | 15 min |
| Explain-aloud drill | Five interview questions answered aloud in quiz mode, recorded on your phone | 15 min |
| Full mock | A DSA problem followed by a Python Q&A round, back to back, no breaks | 45 min |

### Where to practise

- [LeetCode](https://leetcode.com/): set the editor language to Python3 and work through the tracker. Read the editorial only after a real attempt.
- [NeetCode](https://neetcode.io/): a pattern-based roadmap with walkthrough videos, useful when a pattern in the tracker is unfamiliar.
- [Exercism Python track](https://exercism.org/tracks/python): short exercises with feedback from mentors, good for writing idiomatic code.
- [Python Tutor](https://pythontutor.com/): step through a program one line at a time and watch references, closures and mutation. Use it for every trap in chapter 16 you got wrong.
- [Python documentation](https://docs.python.org/3/): the standard library reference is the final authority. When a summary and the docs disagree, trust the docs.

:::tip Mock rounds beat reading
Reading a solution gives a feeling of progress. Writing one from a blank file, out loud and against a timer, is what an interview tests. Use the timer, and record one session a week to hear where your explanations stall.
:::

@chapter
id: plan
num: 18
pkg: 21 days · cheat sheet · last-night checklist
title: 21-Day Plan & Final Cheat Sheet
summary: A three-week revision plan that mixes reading, quiz mode and timed problems, followed by a one-page cheat sheet and a checklist for the night before the interview.
@body

### The 21-day plan

| Days | Focus | What to do |
|---|---|---|
| 1 to 3 | Foundations (01 to 05) | Quiz mode on. Retype every snippet from memory, then compare with the page. |
| 4 to 6 | Containers and collections (06, 07) | Write the complexity table from memory. Solve two Counter or heap problems. |
| 7 to 9 | OOP and advanced Python (08 to 10) | Build a small class hierarchy with a dataclass, a property and a decorator. |
| 10 to 11 | Errors, memory and concurrency (11, 12) | Explain the GIL and the choice between threads, processes and asyncio in two minutes. |
| 12 | NumPy and pandas (13) | Rewrite one Python loop as a vectorised expression, and explain the speed-up. |
| 13 to 17 | DSA templates and the tracker (14, 15) | Five problems a day, timed. Re-solve yesterday's failures before anything new. |
| 18 | Predict the Output (16) | Predict every answer on paper before opening it. Count your misses. |
| 19 | Practice sets (17) | Two timed mock rounds with recording. |
| 20 | Weak spots | Reopen every section you could not answer aloud, and answer its questions again. |
| 21 | Light review | Skim the cheat sheet below. Stop studying early and sleep. |

### Cheat sheet

- **Costs:** list append O(1) amortised, `in` on a list O(n), dict and set operations O(1) average, `deque` at either end O(1), heap push and pop O(log n), `sorted` O(n log n).
- **Idioms:** `enumerate`, `zip`, `dict.get`, `setdefault`, `defaultdict(list)`, `Counter.most_common`, `sorted(key=...)`, `f"{x=}"`, `with`, `try/except/else/finally`.
- **Traps:** mutable default arguments, shallow copies of nested lists, late binding in lambdas, `is` versus `==`, float rounding, `+=` on a list shared by two names, generators that are exhausted after one pass.
- **Concurrency:** threads for I/O, processes for CPU, asyncio for many waits in one thread, and a lock around any read-modify-write on shared state.

### The night before

- Sleep at a normal time. A rested mind recalls patterns better than a late cram session.
- Re-run the templates from chapter 14 once, by hand, and say the complexity of each.
- Check the interview setup: the editor you will use, the Python version, and a quiet room with a working camera and microphone.
- Pick two stories from your projects, each with the problem, your choice and the result, ready to tell in under two minutes.

:::say Closing a solution
"The approach is a sliding window with a dictionary of last-seen indices. It runs in O(n) time because each index enters and leaves the window once, and O(k) space for the characters in the window. I can also write the brute-force version first if that helps."
:::
