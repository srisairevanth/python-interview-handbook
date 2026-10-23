@part 1 | Start

@chapter
id: start
num: 00
pkg: how to use this page
title: Start Here
summary: What Python interviews actually test, which sections matter most for each kind of role, and how to revise with this handbook.
@body

### How to use this handbook

- **First pass: read in order.** Sections build on each other, from the interpreter and names up to decorators, memory and concurrency. Then the NumPy part for AI and data roles, the DSA part, the puzzles and the plan.
- **Every section has the same shape:** notes, then code, then callouts, then interview questions.
- **Revise actively.** Turn on **Quiz mode** in the contents panel. Every answer folds, so you answer aloud first and open only to check.
- **Track progress.** Tick *Mark as revised* under a section title when you can answer all of its questions. Progress is remembered in this browser.
- **Search** with the box at the top (press `/`). It finds topics, questions and puzzles.

### What Python interviews test

| Round | Service-based companies | Product-based companies | AI and data roles |
|---|---|---|---|
| Online test | Aptitude, output-prediction questions on Python, one or two basic coding problems | Two or three DSA problems in Python (LeetCode medium, sometimes hard) | Python plus a data task (NumPy, pandas) or SQL |
| Technical interview | Lists versus tuples versus sets versus dicts, OOP basics, exceptions, your project | Complexity, `heapq` and `deque`, decorators and generators, memory and the GIL | NumPy and pandas, broadcasting, reproducibility, how you would structure an ML pipeline |
| Project and HR | Your projects and internships, how you debug | Trade-offs and how you would scale a design | Your models, metrics and experiments, and what went wrong |

:::note How the code samples run
Snippets marked **verified run** were executed with the same Python version that built this page, and the output shown under them is the real output. Snippets without a badge are illustrative and are not executed. Puzzle answers are produced the same way, so they cannot drift from the real behaviour.
:::

:::say Opening the Python round
Ask for the interviewer's preference on version first. Then say: "I'll write the simplest correct version, state its complexity, and then improve it if you want." That habit covers most interview rounds.
:::
