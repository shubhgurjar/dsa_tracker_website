# Default Data Structures and Algorithms seed data for the 3-month DSA sprint

DATA_STRUCTURES = [
    {
        "name": "Arrays & Dynamic Arrays",
        "category": "Linear Data Structures",
        "description": "Contiguous memory blocks, O(1) random access, amortized O(1) append. Foundation for two pointers, prefix sums, and sliding window.",
        "cheat_sheet": "• Direct Indexing: O(1)\n• Insertion/Deletion at end: O(1) amortized\n• Insertion/Deletion at arbitrary pos: O(N)\n• Common Techniques: Two Pointers, Prefix Sum, Kadane's, Binary Search"
    },
    {
        "name": "Strings",
        "category": "Linear Data Structures",
        "description": "Character sequences, immutable in Python/Java. Involves palindrome checks, anagram matching, Rabin-Karp, and sliding window frequency maps.",
        "cheat_sheet": "• ASCII array (128/256 size) or Hash Map for frequency\n• Palindrome validation with left/right pointers\n• Substring problems usually pair with Sliding Window or KMP"
    },
    {
        "name": "Linked Lists (Singly & Doubly)",
        "category": "Linear Data Structures",
        "description": "Nodes with pointer references. Critical for pointer manipulation, cycle detection (Floyd's algorithm), and reversing in-place.",
        "cheat_sheet": "• Use Dummy Head node to simplify edge cases (head deletion/insertion)\n• Fast & Slow pointer (Tortoise & Hare) for middle node or cycle detection\n• In-place reversal: prev, curr, next pattern"
    },
    {
        "name": "Stacks & Monotonic Stacks",
        "category": "Linear Data Structures",
        "description": "LIFO order. Monotonic stacks maintain increasing/decreasing order for Next Greater Element, Histogram areas, and parentheses validation.",
        "cheat_sheet": "• Valid Parentheses, Call Stack simulation, Expression evaluation\n• Monotonic Stack: Find Next Greater / Previous Smaller in O(N)\n• Maintain elements strictly increasing or decreasing"
    },
    {
        "name": "Queues & Monotonic Deques",
        "category": "Linear Data Structures",
        "description": "FIFO order. Essential for Breadth-First Search (BFS) level-order traversals and sliding window maximum/minimum queries.",
        "cheat_sheet": "• Queue for BFS tree/graph traversal\n• Deque (Double-ended queue) for O(1) push/pop on both ends\n• Monotonic Deque for Sliding Window Maximum in O(N)"
    },
    {
        "name": "Hash Tables & Hash Sets",
        "category": "Hashing & Fast Lookups",
        "description": "Key-value and unique element sets offering average O(1) lookup, insertion, and deletion. Core for two-sum lookups, counting, and deduplication.",
        "cheat_sheet": "• Average O(1) get/set/delete, worst-case O(N) on hash collisions\n• Use for frequency maps, seen sets, Two Sum complement lookups\n• Beware of non-hashable types (e.g. lists in Python - use tuples)"
    },
    {
        "name": "Binary Trees",
        "category": "Trees & Hierarchical",
        "description": "Hierarchical nodes with up to 2 children. Fundamental recursive structures: DFS (Pre/In/Postorder), BFS (Level-order), Depth, Diameter, LCA.",
        "cheat_sheet": "• Preorder: Root -> Left -> Right\n• Inorder: Left -> Root -> Right\n• Postorder: Left -> Right -> Root\n• Lowest Common Ancestor (LCA) recursive pattern"
    },
    {
        "name": "Binary Search Trees (BST)",
        "category": "Trees & Hierarchical",
        "description": "Ordered binary trees where left < root < right. Inorder traversal yields sorted order. O(log N) average search, insert, and delete.",
        "cheat_sheet": "• Inorder traversal is strictly increasing\n• Search / Insert: O(h) where h is height (O(log N) balanced, O(N) skewed)\n• Validate BST: pass min_val and max_val bounds recursively"
    },
    {
        "name": "Heaps & Priority Queues",
        "category": "Trees & Hierarchical",
        "description": "Complete binary trees satisfying heap invariant (min-heap or max-heap). Fundamental for Top-K elements, Dijkstra, and median finding.",
        "cheat_sheet": "• Peek min/max: O(1), Insert/Extract: O(log N)\n• Python heapq is min-heap by default (negate values for max-heap)\n• Top-K Frequent: Keep min-heap of size K -> O(N log K)"
    },
    {
        "name": "Graphs (Representation & Properties)",
        "category": "Graph Theory",
        "description": "Vertices and edges. Adjacency lists vs matrix, directed/undirected, cyclic/acyclic (DAG), weighted/unweighted, bipartite graphs.",
        "cheat_sheet": "• Adjacency List: Space O(V + E), best for sparse graphs\n• Visited Set to avoid infinite loops in cyclic graphs\n• Indegree array for topological sorting"
    },
    {
        "name": "Trie (Prefix Tree)",
        "category": "Advanced Data Structures",
        "description": "Tree structure for storing dynamic strings/characters. Super fast prefix lookups, autocomplete, dictionary search, and XOR maximums.",
        "cheat_sheet": "• Search / Insert word of length L: O(L) time\n• Each node has children dictionary/array (26 lowercase) & is_end_of_word flag\n• Prefix matching is O(prefix length)"
    },
    {
        "name": "Disjoint Set Union (Union-Find)",
        "category": "Advanced Data Structures",
        "description": "Data structure tracking partitioned disjoint sets. Near O(1) find and union with Path Compression and Union by Rank.",
        "cheat_sheet": "• Path compression: parent[x] = find(parent[x])\n• Union by rank/size avoids skewed trees\n• Find connected components, cycle detection in undirected graphs, Kruskal's MST"
    }
]

ALGORITHMS = [
    {
        "name": "Binary Search",
        "category": "Searching & Partitioning",
        "description": "O(log N) search on sorted arrays, monotonic answer spaces (Binary Search on Answer), finding boundaries (first/last position).",
        "cheat_sheet": "• Template: low, high = 0, len(nums) - 1\n• mid = low + (high - low) // 2\n• Binary search on answer: check feasibility function is monotonic (True...True...False)"
    },
    {
        "name": "Two Pointers Technique",
        "category": "Array & String Patterns",
        "description": "Left/right pointers moving towards each other (sorted pair sums, palindrome, container with most water) or same-direction fast/slow pointers.",
        "cheat_sheet": "• Opposite ends: sorted arrays (Two Sum II, 3Sum, trapping rain water)\n• Same direction: fast runner and slow runner for in-place removal or cycle detection\n• Time: O(N), Space: O(1)"
    },
    {
        "name": "Sliding Window (Fixed & Variable)",
        "category": "Array & String Patterns",
        "description": "Subarray / substring window with expand right pointer and contract left pointer. Longest/shortest substring with constraints.",
        "cheat_sheet": "• Expand window: add right element to state\n• While invalid condition: remove left element from state and advance left\n• Record max/min window size at valid states"
    },
    {
        "name": "Prefix Sums & Frequency Arrays",
        "category": "Array & String Patterns",
        "description": "Precomputed cumulative sums for O(1) range sum queries. Combined with Hash Maps for Subarray Sum Equals K.",
        "cheat_sheet": "• prefix[i] = prefix[i-1] + nums[i]\n• Range sum [L, R] = prefix[R] - prefix[L-1]\n• Subarray sum == k: use hash map tracking seen prefix sums and their frequencies"
    },
    {
        "name": "Sorting Algorithms (Merge, Quick, Count)",
        "category": "Searching & Partitioning",
        "description": "Divide and conquer (Merge Sort O(N log N) stable, Quick Sort O(N log N) avg), Heap Sort, Counting / Bucket Sort for bounded integers.",
        "cheat_sheet": "• Merge Sort: stable, O(N log N) time, O(N) space, great for linked lists\n• Quick Sort: in-place partition, O(N log N) avg, O(N^2) worst\n• Custom comparator: sort by primary key asc, secondary key desc"
    },
    {
        "name": "Breadth-First Search (BFS)",
        "category": "Graph & Tree Traversals",
        "description": "Level-order queue traversal. Guarantees shortest path in unweighted graphs. Level by level tree processing.",
        "cheat_sheet": "• Queue initialized with start node, visited set\n• Loop while queue: for _ in range(len(queue)) processes full level\n• Shortest path step count = level count"
    },
    {
        "name": "Depth-First Search (DFS) & Backtracking",
        "category": "Graph & Tree Traversals",
        "description": "Explore paths to leaf/dead-end before backtracking. Generating permutations, combinations, subsets, word search, N-Queens.",
        "cheat_sheet": "• Base case (leaf reached or solution found)\n• Loop through candidates: choose -> recurse -> unchoose (backtrack)\n• Pruning early saves exponential runtime"
    },
    {
        "name": "Dynamic Programming (1D & 2D)",
        "category": "Optimization & DP",
        "description": "Breaking problem into overlapping subproblems with optimal substructure. Memoization (Top-down) or Tabulation (Bottom-up).",
        "cheat_sheet": "• State definition: dp[i] or dp[i][j]\n• Recurrence relation: how dp[i] transitions from previous states\n• Base cases & iteration order (0 to N or backwards for space optimization)\n• Common: Climbing Stairs, House Robber, 0/1 Knapsack, LCS, LIS, Edit Distance"
    },
    {
        "name": "Dijkstra & Shortest Path",
        "category": "Graph Theory",
        "description": "Greedy priority-queue based shortest path in directed/undirected graphs with non-negative edge weights. Time O((V + E) log V).",
        "cheat_sheet": "• Min-heap of (dist, node), distances table initialized to inf\n• If popped dist > distances[node], skip (already found better path)\n• Relax edges: new_dist = dist + weight; if new_dist < distances[nbr], push"
    },
    {
        "name": "Topological Sort (Kahn's & DFS)",
        "category": "Graph Theory",
        "description": "Linear ordering of vertices in Directed Acyclic Graph (DAG). Course schedule prerequisites, build dependency resolutions.",
        "cheat_sheet": "• Kahn's Algorithm: calculate in-degrees, queue nodes with in-degree 0\n• Pop node, decrement neighbor in-degrees, push when neighbor in-degree hits 0\n• If processed count != total nodes, graph contains a cycle!"
    },
    {
        "name": "Greedy Algorithms & Intervals",
        "category": "Optimization & DP",
        "description": "Making locally optimal choices at each stage. Meeting rooms, interval merging, non-overlapping intervals, gas station.",
        "cheat_sheet": "• Usually requires sorting first (by start time or end time)\n• Merge Intervals: sort by start time, compare curr.start with prev.end\n• Non-overlapping Intervals: sort by end time, pick earliest finishing interval"
    },
    {
        "name": "Bit Manipulation",
        "category": "Math & Low-Level",
        "description": "Bitwise AND, OR, XOR, shifts. Single number, counting 1 bits, power of two, bitmask dynamic programming.",
        "cheat_sheet": "• x ^ x = 0, x ^ 0 = x (XOR cancels duplicates)\n• x & (x - 1) removes lowest set bit (Brian Kernighan)\n• x & -x isolates lowest set bit\n• 1 << k sets bit k, (x >> k) & 1 checks bit k"
    }
]

SAMPLE_PROBLEMS = [
    {
        "title": "Two Sum",
        "leetcode_number": 1,
        "problem_url": "https://leetcode.com/problems/two-sum/",
        "difficulty": "Easy",
        "data_structure": "Hash Tables & Hash Sets",
        "algorithm": "Prefix Sums & Frequency Arrays",
        "pattern": "Hash Map Complement Lookup",
        "status": "Solved",
        "solved_date": "2026-10-25",
        "last_revised_date": "2026-10-25",
        "revision_count": 1,
        "time_complexity": "O(N)",
        "space_complexity": "O(N)",
        "approach_notes": "Single pass hash map. For each number, check if target - num exists in map. If so return pair, else store num -> index.",
        "code_snippet": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        seen = {}\n        for i, num in enumerate(nums):\n            comp = target - num\n            if comp in seen:\n                return [seen[comp], i]\n            seen[num] = i\n        return []",
        "starred": 1
    },
    {
        "title": "Valid Anagram",
        "leetcode_number": 242,
        "problem_url": "https://leetcode.com/problems/valid-anagram/",
        "difficulty": "Easy",
        "data_structure": "Strings",
        "algorithm": "Prefix Sums & Frequency Arrays",
        "pattern": "Character Frequency Counting",
        "status": "Solved",
        "solved_date": "2026-10-26",
        "last_revised_date": "2026-10-28",
        "revision_count": 2,
        "time_complexity": "O(N)",
        "space_complexity": "O(1) [26 lowercase letters]",
        "approach_notes": "Compare string lengths first. Use fixed-size array of 26 integers or collections.Counter.",
        "code_snippet": "class Solution:\n    def isAnagram(self, s: str, t: str) -> bool:\n        if len(s) != len(t): return False\n        counts = [0] * 26\n        for c1, c2 in zip(s, t):\n            counts[ord(c1) - 97] += 1\n            counts[ord(c2) - 97] -= 1\n        return all(x == 0 for x in counts)",
        "starred": 0
    },
    {
        "title": "3Sum",
        "leetcode_number": 15,
        "problem_url": "https://leetcode.com/problems/3sum/",
        "difficulty": "Medium",
        "data_structure": "Arrays & Dynamic Arrays",
        "algorithm": "Two Pointers Technique",
        "pattern": "Sort + Two Pointers with Deduplication",
        "status": "Solved",
        "solved_date": "2026-10-18",
        "last_revised_date": "2026-10-18",
        "revision_count": 0,
        "time_complexity": "O(N^2)",
        "space_complexity": "O(1) excluding output",
        "approach_notes": "Sort array first. Fix first element with index i. Run two pointers (left = i+1, right = n-1). Skip duplicates for i, left, and right.",
        "code_snippet": "class Solution:\n    def threeSum(self, nums: List[int]) -> List[List[int]]:\n        nums.sort()\n        res = []\n        for i in range(len(nums) - 2):\n            if i > 0 and nums[i] == nums[i-1]:\n                continue\n            l, r = i + 1, len(nums) - 1\n            while l < r:\n                total = nums[i] + nums[l] + nums[r]\n                if total == 0:\n                    res.append([nums[i], nums[l], nums[r]])\n                    l += 1\n                    while l < r and nums[l] == nums[l-1]: l += 1\n                elif total < 0:\n                    l += 1\n                else:\n                    r -= 1\n        return res",
        "starred": 1
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "leetcode_number": 3,
        "problem_url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        "difficulty": "Medium",
        "data_structure": "Strings",
        "algorithm": "Sliding Window (Fixed & Variable)",
        "pattern": "Variable Sliding Window with Hash Map Index",
        "status": "Solved",
        "solved_date": "2026-10-12",
        "last_revised_date": "2026-10-12",
        "revision_count": 0,
        "time_complexity": "O(N)",
        "space_complexity": "O(min(M, N))",
        "approach_notes": "Keep map of char -> last seen index. When duplicate seen inside current window, jump left pointer to last_seen + 1.",
        "code_snippet": "class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        seen = {}\n        left = 0\n        max_len = 0\n        for right, char in enumerate(s):\n            if char in seen and seen[char] >= left:\n                left = seen[char] + 1\n            seen[char] = right\n            max_len = max(max_len, right - left + 1)\n        return max_len",
        "starred": 1
    }
]

SAMPLE_FLASHCARDS = [
    {
        "concept_name": "Strings",
        "title": "Palindrome Verification & Inward Two Pointers",
        "tag": "Pattern",
        "content": """### 💡 Theory & Core Intuition
A palindrome reads identically forwards and backwards. The optimal verification technique uses **Two Pointers** moving inward from the extremities towards the center.

### 📋 Algorithmic Steps
1. Place `left = 0` and `right = len(s) - 1`.
2. Skip non-alphanumeric characters using `s[left].isalnum()` if problem requires ignoring spaces/symbols.
3. Compare `s[left].lower()` with `s[right].lower()`. If they mismatch, return `False`.
4. Increment `left += 1`, decrement `right -= 1`.
5. If pointers cross without mismatch, return `True`.

### ⚡ Complexity Analysis
- **Time Complexity:** $O(N)$ — each character inspected at most twice.
- **Space Complexity:** $O(1)$ auxiliary memory since we check in-place without copying reversed strings.

### 🐍 Python Clean Implementation
```python
def isPalindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True
```

### ⚠️ Pitfalls & Edge Cases
- Empty string or single character string is valid palindrome.
- Character casing (`'A'` vs `'a'`) requires normalization with `.lower()`.
- Palindrome substring expansion: For finding longest palindromic substring, expand **outward** from each index (odd length: `i`, even length: `i, i+1`)."""
    },
    {
        "concept_name": "Strings",
        "title": "Character Frequency Arrays vs HashMaps",
        "tag": "Cheat Sheet",
        "content": """### 💡 Technique Overview
When dealing with strings restricted to ASCII or lowercase English letters (`'a'` through `'z'`), an array of fixed size 26 or 128 is significantly faster and more cache-friendly than a general hash map (`dict`).

### 📌 Core Formula
- Index calculation for lowercase letters: `ord(char) - ord('a')`
- Index calculation for uppercase letters: `ord(char) - ord('A')`
- Full ASCII set: fixed array of size `128` or `256`.

### 🐍 Python Anagram Verification Template
```python
def isAnagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    counts = [0] * 26
    for c1, c2 in zip(s, t):
        counts[ord(c1) - ord('a')] += 1
        counts[ord(c2) - ord('a')] -= 1
    return all(count == 0 for count in counts)
```

### ⚡ Why Use Array Over Hash Map?
- **Zero Hash Collisions:** Direct array indexing is guaranteed $O(1)$ worst-case.
- **Cache Locality:** Contiguous memory block of 26 integers fits inside a single CPU cache line.
- **Space Complexity:** $O(1)$ strictly bounded memory."""
    },
    {
        "concept_name": "Strings",
        "title": "Sliding Window Substring Template",
        "tag": "Template",
        "content": """### 💡 When to Apply
Apply when asked for:
- Longest substring satisfying a condition (e.g. without repeating characters).
- Smallest substring containing all characters of pattern (Minimum Window Substring).

### 🛠️ Universal Variable Window Template
```python
def slidingWindow(s: str) -> int:
    state = {}
    left = 0
    ans = 0
    
    for right in range(len(s)):
        # 1. Add current character into window
        char = s[right]
        state[char] = state.get(char, 0) + 1
        
        # 2. While window constraint is violated, shrink from left
        while window_is_invalid(state):
            left_char = s[left]
            state[left_char] -= 1
            if state[left_char] == 0:
                del state[left_char]
            left += 1
            
        # 3. Update answer with valid window
        ans = max(ans, right - left + 1)
        
    return ans
```

### 🧠 Key Takeaway
The right pointer **expands** the window to include new information. The left pointer **contracts** the window to restore invariant. Both pointers move at most $N$ times $\\implies O(N)$ runtime!"""
    },
    {
        "concept_name": "Strings",
        "title": "String Immutability & Efficient Construction",
        "tag": "Theory",
        "content": """### ⚠️ The $O(N^2)$ String Concatenation Trap
In languages like Python and Java, strings are **immutable**.
When you write:
```python
# ANTI-PATTERN: DO NOT DO THIS IN A LOOP!
s = ""
for char in large_stream:
    s += char  # Creates a brand new copy of string each time!
```
Each concatenation copies all previous characters:
$$1 + 2 + 3 + \\dots + N = \\frac{N(N+1)}{2} = O(N^2)$$

### 🚀 The Optimal Pattern: List Accumulation
Instead of repeated string addition, accumulate elements into a dynamic array (Python `list`), then combine with `str.join()`:
```python
# OPTIMAL PATTERN: O(N) Total Time
buffer = []
for char in stream:
    buffer.append(char)
result = "".join(buffer)  # Single O(N) pass memory allocation
```

### 💡 StringBuilder Equivalent in Python
Python's `io.StringIO` or appending to a list and calling `''.join()` acts as the equivalent of Java's `StringBuilder`."""
    }
]
