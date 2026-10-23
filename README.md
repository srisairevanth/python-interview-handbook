# Python Interview Handbook

A single-page revision guide for Python interviews, built like the C++ and Java handbooks: quiz mode, revision progress, search, a must-do problem tracker and predict-the-output puzzles.

**Live page:** https://srisairevanth.github.io/python-interview-handbook/

Open `index.html` in any browser or use the live link. Revision progress, quiz mode and solved problems are saved in your browser.

## What is inside

19 sections in eight parts:

- **Start:** how to use the page, and what Python interviews test
- **Foundations:** syntax and names, types and identity, strings, control flow, functions and scope
- **Built-in data structures:** lists, tuples, sets and dicts; collections, heapq and bisect
- **Object-oriented Python:** classes and dunder methods, inheritance, MRO and dataclasses
- **Advanced Python:** decorators, generators and context managers; exceptions and packaging; memory, the GIL and concurrency
- **Python for AI and data:** NumPy, pandas and reproducibility
- **DSA in Python:** the toolkit and templates, with a 61-problem tracker grouped by pattern
- **Practice:** 15 predict-the-output puzzles, practice sets and a 21-day plan with a cheat sheet

## Building

`index.html` is generated from the Markdown files in `content/`:

    pip install pygments
    python3 build.py

Every snippet marked `run` is executed by the build with the interpreter that runs it, and the real output is embedded under the code. Puzzle answers are produced the same way. Add `--report` to print each output.

`template/` holds the stylesheet and scripts. They were copied from the C++ handbook. `python3 build.py --save-template` re-extracts them from `../cpp-interview-handbook/index.html`.

## Companion handbooks

- [C++ Interview Handbook](https://srisairevanth.github.io/cpp-interview-handbook/)
- [Java Interview Handbook](https://srisairevanth.github.io/java-interview-handbook/)
