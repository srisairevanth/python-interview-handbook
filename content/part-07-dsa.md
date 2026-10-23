@part 7 | DSA in Python

@chapter
id: dsa
num: 14
pkg: complexity · sliding window · BFS · heapq · deque · recursion limit
title: The Python DSA Toolkit
summary: The costs of the built-in structures, the standard-library helpers that make interview solutions short, and the templates for sliding windows, breadth-first search and recursion limits.
@body

### The cost of the tools you will reach for

| Tool | Operation | Cost |
|---|---|---|
| `dict`, `set` | lookup, insert, delete | O(1) average |
| `deque` | append and pop at either end | O(1) |
| `list` | append | O(1) amortised |
| `list` | insert or pop at the front | O(n) |
| `heapq` | push and pop | O(log n) |
| `heapq` | smallest item | `heap[0]`, O(1) |
| `bisect` | search a sorted list | O(log n) |
| `sorted` | sort | O(n log n) |

### Sliding window

Track the last index at which each character appeared. When a repeat falls inside the current window, move the left edge past it. Each index enters and leaves the window once, so the whole pass is O(n).

```python run
def length_of_longest_substring(s):
    last_seen = {}
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best

print(length_of_longest_substring("abcabcbb"), length_of_longest_substring("pwwkew"), length_of_longest_substring(""))
```

### Breadth-first search

```python run
from collections import deque

def bfs(graph, start):
    seen, order, q = {start}, [], deque([start])
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order

g = {1: [2, 3], 2: [4], 3: [4], 4: []}
print(bfs(g, 1))
```

### Recursion depth

CPython does not eliminate tail calls, and the default recursion limit is small. Deep recursion raises `RecursionError`, so write deep traversals iteratively with an explicit stack or deque.

```python run
import sys

print(sys.getrecursionlimit())
```

### Interview questions

Q: Why can `list.pop(0)` be slow?
A: Removing the first element shifts every other element one slot left, which is O(n). Use `collections.deque` and `popleft()` whenever the list is used as a queue.

Q: How do you find the k largest elements?
A: `heapq.nlargest(k, items)` runs in O(n log k). A min-heap of size k is the streaming version: push each value, and pop whenever the heap grows past k. The heap then holds the k largest values seen so far.

Q: What is the complexity of Python's sort?
A: O(n log n) in the worst case. Timsort is stable, and it runs close to linear time on data that is already partly ordered, which is common in real inputs.

Q: Why store seen items in a set or dict?
A: A membership test on a list is O(n), while a set or dict averages O(1). Replacing a list scan with a set lookup often removes a whole loop, turning an O(n²) solution into O(n).

:::pitfall Recursion depth
A recursive DFS on a path graph with 10⁵ nodes raises `RecursionError` at the default limit. Convert it to an explicit stack, or raise the limit only when you are sure the depth is bounded.
:::

:::remember Templates to know by heart
Sliding window with a dict of last-seen indices, BFS with a deque and a seen set, and a min-heap of size k. Those three cover a large share of the must-do list.
:::

@chapter
id: problems
num: 15
pkg: arrays · windows · heaps · trees · graphs · DP · bits
title: Must-Do Problems
summary: A tracker of the LeetCode problems that cover the patterns above, grouped by pattern. Tick a problem when you can solve it cleanly in about 25 minutes without notes.
@body

Solve in order inside each group, tick the box when the solution is clean, and then re-solve it a week later from a blank file. Explaining the complexity out loud is part of solving it.

### Arrays and hashing

:::problems
1 | Two Sum | E | Dict from value to index
217 | Contains Duplicate | E | Compare set size with list length
242 | Valid Anagram | E | Counter comparison
49 | Group Anagrams | M | Key by sorted letters or letter counts
347 | Top K Frequent Elements | M | Counter plus heapq.nlargest
238 | Product of Array Except Self | M | Prefix and suffix products
128 | Longest Consecutive Sequence | M | Set; count only from the start of each run
56 | Merge Intervals | M | Sort by start, then extend
53 | Maximum Subarray | M | Kadane's algorithm
:::

### Two pointers and sliding window

:::problems
125 | Valid Palindrome | E | Two pointers that skip non-alphanumerics
167 | Two Sum II - Input Array Is Sorted | M | Opposite-end pointers
15 | 3Sum | M | Sort, fix one value, two pointers, skip duplicates
11 | Container With Most Water | M | Move the shorter side inward
42 | Trapping Rain Water | H | Two pointers with running maxima
3 | Longest Substring Without Repeating Characters | M | Window with last-seen index
424 | Longest Repeating Character Replacement | M | Window keeping the most frequent letter count
438 | Find All Anagrams in a String | M | Fixed-size window of counts
76 | Minimum Window Substring | H | Need-count window that shrinks
:::

### Binary search

:::problems
704 | Binary Search | E | Standard lo and hi loop
35 | Search Insert Position | E | bisect_left
33 | Search in Rotated Sorted Array | M | Find the sorted half, then decide
153 | Find Minimum in Rotated Sorted Array | M | Compare mid with the right end
875 | Koko Eating Bananas | M | Binary search on the answer
:::

### Stacks and heaps

:::problems
20 | Valid Parentheses | E | Stack of opening brackets
155 | Min Stack | M | Store the running minimum with each value
739 | Daily Temperatures | M | Monotonic stack of indices
84 | Largest Rectangle in Histogram | H | Monotonic stack
215 | Kth Largest Element in an Array | M | Min-heap of size k
703 | Kth Largest Element in a Stream | E | Min-heap of size k, updated per value
973 | K Closest Points to Origin | M | Heap keyed by squared distance
23 | Merge k Sorted Lists | H | Heap of current list heads
:::

### Linked lists

:::problems
206 | Reverse Linked List | E | Three pointers, iterative
21 | Merge Two Sorted Lists | E | Dummy head node
141 | Linked List Cycle | E | Fast and slow pointers
19 | Remove Nth Node From End of List | M | Two pointers with a gap of n
:::

### Trees and graphs

:::problems
104 | Maximum Depth of Binary Tree | E | Recurse into both children
226 | Invert Binary Tree | E | Swap children recursively
543 | Diameter of Binary Tree | E | Height function with a running best
102 | Binary Tree Level Order Traversal | M | BFS by level with a deque
98 | Validate Binary Search Tree | M | Pass lower and upper bounds down
230 | Kth Smallest Element in a BST | M | Inorder traversal
236 | Lowest Common Ancestor of a Binary Tree | M | Recurse into both subtrees
200 | Number of Islands | M | Flood fill from each unvisited land cell
695 | Max Area of Island | M | Flood fill that returns the area
207 | Course Schedule | M | Topological order with indegrees
994 | Rotting Oranges | M | Multi-source BFS by minute
:::

### Dynamic programming and greedy

:::problems
70 | Climbing Stairs | E | Fibonacci-style DP with two variables
198 | House Robber | M | Take or skip, two running values
322 | Coin Change | M | Bottom-up table over amounts
300 | Longest Increasing Subsequence | M | DP, or patience sorting with bisect
1143 | Longest Common Subsequence | M | Two-dimensional table
139 | Word Break | M | Prefix table over string positions
121 | Best Time to Buy and Sell Stock | E | Track the minimum price so far
455 | Assign Cookies | E | Sort both lists and match greedily
:::

### Bits, math and strings

:::problems
136 | Single Number | E | XOR cancels pairs
338 | Counting Bits | E | dp[i] = dp[i >> 1] + (i & 1)
9 | Palindrome Number | E | Reverse half of the digits
13 | Roman to Integer | E | Subtract when a smaller value precedes a larger one
14 | Longest Common Prefix | E | Compare characters column by column
387 | First Unique Character in a String | E | Counter, then scan in order
151 | Reverse Words in a String | M | split and join, no manual spacing loops
:::
