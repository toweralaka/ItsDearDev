# micro1 Retake — Coding Practice: Efficient Python Toolbox

Each problem is built around ONE specific Python feature that's easy to forget under interview pressure but signals real fluency when you reach for it naturally. For each: the problem as it might be posed, why it matters, the naive approach (what most people default to), and the efficient approach with the actual code.

**Interview habit to practice:** say the tradeoff out loud before coding — *"I could do this with a list comprehension, but since we don't need all results in memory at once, I'll use a generator instead."* That sentence alone signals seniority.

---

## 1. Generators (`yield`) — processing data too large to hold in memory

**Problem:** "You have a log file with millions of lines. Write a function that returns every line containing the word 'ERROR', but assume the file is too large to load into memory at once."

**Why it matters:** This directly tests whether you reach for lazy evaluation instead of `readlines()` + a list. It's the same principle behind streaming a large API response or paginating a huge database query — don't materialize what you don't need yet.

**Naive approach** (loads everything into memory):
```python
def find_errors_naive(filepath):
    with open(filepath) as f:
        lines = f.readlines()          # entire file in memory at once
    return [line for line in lines if "ERROR" in line]
```

**Efficient approach** (constant memory, regardless of file size):
```python
def find_errors(filepath):
    with open(filepath) as f:
        for line in f:                  # file objects are already iterators — one line at a time
            if "ERROR" in line:
                yield line.rstrip("\n")

# Usage — nothing is read until you actually iterate:
for error_line in find_errors("app.log"):
    print(error_line)
    # could `break` early here and never read the rest of the file at all
```

**Say this:** *"I'm using a generator here instead of returning a list, because the caller might only need the first few matches, or might want to process them one at a time without ever holding the full result set in memory — this scales the same whether the file is 10 lines or 10 million."*

---

## 2. Decorators — caching, timing, and retry logic without duplicating code

**Problem A (caching):** "You have an expensive function that computes a user's lifetime value from their order history. It's called repeatedly with the same user ID during a request. Avoid recomputing it."

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def compute_lifetime_value(user_id):
    print(f"Computing for {user_id}...")   # only prints once per unique user_id
    # imagine an expensive DB aggregation here
    return sum(order.total for order in get_orders(user_id))
```

**Say this:** *"Rather than manually maintaining a dictionary cache, `functools.lru_cache` gives me memoization in one line — and it's thread-safe and has an eviction policy built in, which a hand-rolled dict cache usually doesn't."*

**Problem B (retry with backoff):** "Write a decorator that retries a flaky function up to 3 times with exponential backoff, without modifying the function itself." *(This is the exact pattern from the "external API is down" discussion — now implemented.)*

```python
import time
import functools

def retry_with_backoff(max_attempts=3, base_delay=1):
    def decorator(func):
        @functools.wraps(func)               # preserves func's name/docstring — easy to forget, worth mentioning
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    print(f"Attempt {attempt} failed ({e}), retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_attempts=3, base_delay=1)
def call_flaky_payment_api():
    ...  # real network call here
```

**Say this:** *"Wrapping this as a decorator means any function that calls an external service can opt into retry-with-backoff behavior with one line, instead of duplicating try/except-and-sleep logic across every call site — and `functools.wraps` keeps introspection and debugging working correctly on the wrapped function."*

---

## 3. `itertools.groupby` — grouping without a manual dictionary loop

**Problem:** "Given a list of orders sorted by status, group them by status and count each group."

**Naive approach:**
```python
def group_naive(orders):
    groups = {}
    for order in orders:
        groups.setdefault(order["status"], []).append(order)
    return {status: len(items) for status, items in groups.items()}
```
*(This one isn't wrong, just worth knowing the alternative — and `groupby` becomes the better tool when you're streaming and don't want to build a full dict of lists.)*

**Efficient approach for pre-sorted/streaming data:**
```python
from itertools import groupby
from operator import itemgetter

def group_counts(orders):
    # orders MUST already be sorted by "status" for groupby to work correctly —
    # this is the #1 gotcha with groupby, worth saying out loud in the interview
    orders_sorted = sorted(orders, key=itemgetter("status"))
    return {status: len(list(items)) for status, items in groupby(orders_sorted, key=itemgetter("status"))}
```

**Say this:** *"`itertools.groupby` only groups consecutive matching items, so the input has to be sorted by the grouping key first — that's the classic gotcha. It's most valuable when processing a stream where you don't want to hold the entire dataset in a dictionary at once."*

---

## 4. `collections.Counter` and `defaultdict` — frequency and grouping, cleanly

**Problem:** "Given a list of API request logs, find the top 3 IP addresses making the most requests — this is basically 'detect who I should rate-limit.'"

**Naive approach:**
```python
def top_ips_naive(logs):
    counts = {}
    for log in logs:
        ip = log["ip"]
        counts[ip] = counts.get(ip, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
```

**Efficient approach:**
```python
from collections import Counter

def top_ips(logs):
    counts = Counter(log["ip"] for log in logs)
    return counts.most_common(3)     # built-in, does the sort-and-slice for you
```

**Say this:** *"`Counter` is purpose-built for exactly this — frequency counting and 'give me the top N' in one call — rather than hand-rolling a dictionary and manually sorting it. It reads clearly as intent: 'I am counting things,' not just 'I am using a dict.'"*

---

## 5. `heapq` — top-K problems without sorting everything

**Problem:** *(This is close to the "maximize purchases under constraint" style problem from your feedback.)* "You're given a list of products with prices, and a budget. You want to buy as many products as possible without exceeding the budget. Which do you buy?"

**Why heapq/greedy matters:** If the goal is *maximize count* under a budget (not maximize value), the optimal strategy is provably greedy: always buy the cheapest items first. You don't need full DP for this variant — recognizing *which* variant you're facing is the actual skill being tested.

```python
import heapq

def max_items_under_budget(prices, budget):
    heapq.heapify(prices)          # O(n) heap build, cheaper than a full sort for this use case
    bought = 0
    spent = 0
    while prices and spent + prices[0] <= budget:
        price = heapq.heappop(prices)
        spent += price
        bought += 1
    return bought, spent
```

**Say this:** *"Since the goal is maximizing the count of items rather than the total value, buying cheapest-first is provably optimal — no need for dynamic programming here. I use a heap rather than a full sort because I only ever need the current minimum, and a heap gives me that in log-n each time versus re-sorting."*

**Follow-up variant to prepare for — maximize *value* under a weight/budget constraint (the real knapsack):**
```python
from functools import lru_cache

def max_value_knapsack(items, capacity):
    # items: list of (weight, value)
    @lru_cache(maxsize=None)
    def solve(index, remaining_capacity):
        if index == len(items):
            return 0
        weight, value = items[index]
        # option 1: skip this item
        best = solve(index + 1, remaining_capacity)
        # option 2: take this item, if it fits
        if weight <= remaining_capacity:
            best = max(best, value + solve(index + 1, remaining_capacity - weight))
        return best
    return solve(0, capacity)
```

**Say this:** *"This variant isn't greedy-safe, because a cheaper item isn't necessarily a worse choice if it has disproportionately high value — so I use dynamic programming with memoization. Rather than hand-writing a 2D array, I use `lru_cache` on a recursive function, which gets me memoization with much less bookkeeping code, at the cost of some recursion depth to watch for on very large inputs."*

---

## 6. `bisect` — keeping something sorted without re-sorting every time

**Problem:** "You're maintaining a live leaderboard that needs to stay sorted as new scores come in, and you need to find a player's rank quickly."

**Naive approach:**
```python
def insert_naive(scores, new_score):
    scores.append(new_score)
    scores.sort()          # O(n log n) every single insert
```

**Efficient approach:**
```python
import bisect

def insert_score(scores, new_score):
    bisect.insort(scores, new_score)   # O(n) insert into an already-sorted list, no re-sort needed
    return bisect.bisect_left(scores, new_score)   # O(log n) to find its rank/position
```

**Say this:** *"Since the list is already sorted, re-sorting from scratch on every insert is wasteful — `bisect` finds the correct insertion point in log-n time and keeps the list sorted incrementally, which matters a lot once you're doing this on every new score in a live leaderboard rather than once in a while."*

---

## 7. `contextlib.contextmanager` — your own version of `transaction.atomic()`

**Problem:** "Write a context manager that times a block of code and logs a warning if it exceeds 200ms — useful for catching slow database calls in review."

```python
import time
from contextlib import contextmanager
import logging

@contextmanager
def timed_block(label, threshold_ms=200):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > threshold_ms:
            logging.warning(f"{label} took {elapsed_ms:.1f}ms (threshold: {threshold_ms}ms)")

# Usage:
with timed_block("order_lookup_query"):
    fetch_order_from_db(order_id)
```

**Say this:** *"This is the same underlying pattern as Django's `transaction.atomic()` — setup before, guaranteed cleanup after, even if an exception is raised, because it's inside the `finally` block. I use `contextlib.contextmanager` rather than writing a full class with `__enter__`/`__exit__` because it's far less boilerplate for a simple case like this."*

---

## 8. `concurrent.futures` — calling multiple external APIs without waiting sequentially

**Problem:** "You need to call three independent third-party APIs to build one response — say, inventory, pricing, and reviews for a product page. Sequentially they'd take 300ms each, 900ms total. Speed this up."

**Naive approach (sequential):**
```python
def get_product_data_naive(product_id):
    inventory = fetch_inventory(product_id)   # 300ms
    pricing = fetch_pricing(product_id)       # 300ms
    reviews = fetch_reviews(product_id)       # 300ms
    return inventory, pricing, reviews        # ~900ms total
```

**Efficient approach (concurrent, since these are independent I/O-bound calls):**
```python
from concurrent.futures import ThreadPoolExecutor

def get_product_data(product_id):
    with ThreadPoolExecutor(max_workers=3) as executor:
        inventory_future = executor.submit(fetch_inventory, product_id)
        pricing_future = executor.submit(fetch_pricing, product_id)
        reviews_future = executor.submit(fetch_reviews, product_id)
        return inventory_future.result(), pricing_future.result(), reviews_future.result()
        # all three run concurrently — total time is ~max(300,300,300) ≈ 300ms, not the sum
```

**Say this:** *"Since these three calls are independent and I/O-bound — waiting on network, not CPU — I run them concurrently with a thread pool rather than sequentially. Python's GIL means threads don't help CPU-bound work, but for I/O-bound calls like HTTP requests, this cuts total latency from the sum of all calls down to roughly the slowest single call."*

---

## 9. `dataclasses` with `slots` — lightweight, efficient value objects

**Problem:** "You're creating thousands of small objects to represent line items in an order during a bulk import. A regular class with `__init__` works but is verbose and memory-heavy at scale."

```python
from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class LineItem:
    sku: str
    quantity: int
    unit_price: float

    @property
    def total(self):
        return self.quantity * self.unit_price
```

**Say this:** *"`@dataclass` removes the boilerplate of writing `__init__`, `__repr__`, and `__eq__` by hand. `slots=True` avoids giving every instance a full `__dict__`, which matters when you're creating a large number of these — it reduces memory per instance. `frozen=True` makes them immutable, which is a good default for something like a line item that shouldn't change after creation."*

---

Good catch, and yes — you had it backwards on categorization, but you're not wrong that there's more here. Let me first fix the terminology confusion, then give you the actual answer.

## Quick reality check on what you've already used

Not everything is a module or a function. Here's the actual breakdown of tools from earlier files:

| Thing | What it actually is |
|---|---|
| `collections` | module |
| `defaultdict`, `Counter`, `deque` | **classes**, live inside `collections` |
| `namedtuple` | a function that *builds* a class for you |
| `functools.partial` | **class** |
| `functools.lru_cache`, `reduce`, `wraps` | functions |
| `itertools.chain`, `groupby`, `islice` | technically **classes** (Python's docs even write them as `class itertools.chain`) |
| `heapq`, `bisect` | modules of plain functions — no class involved, they just operate on ordinary lists |
| `contextlib.suppress` | **class** |
| `contextlib.contextmanager` | function (a decorator) |
| `ThreadPoolExecutor`, `ProcessPoolExecutor` | **classes** |
| `threading.Lock` | **class**-like object |

So you already used several classes without realizing it — you just didn't have the label for it. Fair enough, that's a vocabulary gap, not a knowledge gap.

## Now — actual classes for real speed/memory efficiency, not yet covered

These aren't about cleaner code. Each one exists specifically because the "obvious" way is measurably slower or uses more memory.

### 1. `functools.cached_property` — stop recomputing an expensive attribute

**Problem:** you have an object where some attribute is expensive to compute but never changes once set — like a user's `total_lifetime_spend`, computed from hundreds of order rows.

```python
from functools import cached_property

class User:
    def __init__(self, user_id):
        self.user_id = user_id

    @cached_property
    def total_lifetime_spend(self):
        print("Computing...")   # only ever prints ONCE per instance
        return sum(order.total for order in fetch_all_orders(self.user_id))

u = User(42)
u.total_lifetime_spend   # computes, stores result on the instance
u.total_lifetime_spend   # returns the stored value, no recompute at all
```

Different from `lru_cache`: `lru_cache` caches by *arguments*, shared across all calls. `cached_property` caches *per instance*, and stores the result directly on that object — no arguments needed since it's just `self`.

### 2. `re.Pattern` (via `re.compile`) — stop re-parsing the same regex

**Problem:** validating thousands of emails in a loop with `re.match(pattern, text)`.

```python
import re

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")   # parsed ONCE

def is_valid_email(email):
    return bool(EMAIL_RE.match(email))         # reuses the compiled pattern every time
```

If you call `re.match(r"...", text)` inside a loop instead, Python re-parses that pattern string from scratch on every single call. `re.compile` gives you back a `Pattern` object that's already parsed — a real, measurable speedup in any hot loop doing repeated matching.

### 3. `io.StringIO` — stop doing repeated string concatenation

**Problem:** building a large CSV or log string piece by piece.

```python
# BAD — each += creates a whole new string, copying everything so far, every time
result = ""
for row in rows:
    result += format_row(row)   # O(n²) total cost as it grows

# GOOD — appends into a mutable buffer, no repeated copying
from io import StringIO
buffer = StringIO()
for row in rows:
    buffer.write(format_row(row))
result = buffer.getvalue()
```

Strings in Python are immutable — every `+=` silently creates a brand-new string and copies the old content into it. Do that in a loop over thousands of rows and it turns quadratic. `StringIO` gives you a writable, in-memory buffer, so writes are cheap and you only pay for one final read.

### 4. `array.array` — stop wasting memory on large numeric collections

**Problem:** storing a million integers (say, timestamps or product IDs) for numeric processing.

```python
import array

# a regular list stores a POINTER to each Python int object (extra overhead per element)
big_list = [i for i in range(1_000_000)]

# array.array stores raw C-level integers directly, no per-item object overhead
big_array = array.array('l', range(1_000_000))   # 'l' = signed long
```

A Python `list` of a million ints stores a million *pointers* to separately-allocated int objects. `array.array` stores the raw values packed together like a C array — for large, uniform numeric data, this is a genuine, significant memory reduction (often 3-4x less memory).

### 5. `queue.Queue` — thread-safe hand-off without managing locks yourself

**Problem:** one thread produces work (say, incoming webhook events), another thread processes them — you need this to be safe without manually juggling a `Lock`.

```python
import queue
import threading

work_queue = queue.Queue()

def producer():
    for event in incoming_events():
        work_queue.put(event)

def consumer():
    while True:
        event = work_queue.get()   # blocks efficiently until something's available — no manual locking, no busy-waiting
        process(event)
        work_queue.task_done()

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
```

You *could* build this yourself with a list + a `Lock` + manual "wait until non-empty" logic — but you'd likely end up either busy-waiting (wasting CPU checking "is it empty yet?" in a loop) or writing bug-prone synchronization by hand. `queue.Queue` has efficient blocking built in at the C level.

### 6. `threading.local` — skip the lock entirely by not sharing the data

**Problem:** each thread needs its own scratch data (e.g., its own DB connection, or its own request context), and you keep reaching for a `Lock` to protect a shared dict — but the data doesn't actually need to be shared at all.

```python
import threading

_thread_data = threading.local()

def get_db_connection():
    if not hasattr(_thread_data, "conn"):
        _thread_data.conn = create_new_connection()   # each thread gets its OWN conn, automatically
    return _thread_data.conn
```

This is a genuine efficiency win specifically because it **avoids locking altogether** — if data genuinely doesn't need to cross threads, giving each thread its own private copy is faster than making every thread take turns through a lock to access one shared copy.

---

## The pattern across all of these

Every one of these exists to avoid one of three costs: **recomputation** (`cached_property`, `re.compile`), **repeated copying/reallocation** (`StringIO`, `array.array`), or **synchronization overhead** (`Queue`, `threading.local`). If you can name *which* of those three a tool is solving in the interview, that's a much stronger signal than just knowing the tool exists.

---


## DEFAULTDICT

## Small correction: it's a class, not a module

`collections` is the **module**. `defaultdict` is a **class** that lives inside that module — same relationship as `datetime` (module) and `datetime.datetime` (class inside it). You import it like:

```python
from collections import defaultdict
```

## Your understanding is correct — here's why it works

A normal `dict` throws a `KeyError` the moment you try to touch a key that doesn't exist yet:

```python
d = {}
d["fruits"].append("apple")   # KeyError! "fruits" doesn't exist yet
```

So normally you're forced to check first:

```python
d = {}
if "fruits" not in d:
    d["fruits"] = []
d["fruits"].append("apple")
```

or the slightly shorter `setdefault` version:

```python
d = {}
d.setdefault("fruits", []).append("apple")
```

`defaultdict` removes that check entirely. When you create it, you give it a **factory function** — something that produces a "default" value whenever a missing key is accessed. Whenever you touch a key that isn't there yet, instead of throwing an error, it silently calls that factory, stores the result under that key, and gives it to you:

```python
from collections import defaultdict

d = defaultdict(list)          # factory = list, so missing keys get []
d["fruits"].append("apple")    # "fruits" didn't exist → defaultdict calls list() → gets [] → THEN appends
d["fruits"].append("banana")
print(d["fruits"])             # ['apple', 'banana']
print(d)                       # defaultdict(<class 'list'>, {'fruits': ['apple', 'banana']})
```

🧒 **Like I'm 9:** A normal dict is like a row of labeled boxes, but if you try to put a toy in a box that doesn't exist yet, someone yells at you for having no box. A `defaultdict` is like having a robot standing by that, the moment you reach for a box that isn't there, instantly builds you an empty one on the spot — so you can just drop your toy in without ever having to check first.

## One nuance worth knowing

The "factory" can be *any callable that takes no arguments and returns a value* — not just `list`:

```python
defaultdict(int)      # missing key → int() → 0            (great for counting)
defaultdict(list)     # missing key → list() → []           (great for grouping)
defaultdict(set)      # missing key → set() → set()         (great for grouping, no dupes)
defaultdict(lambda: "unknown")   # you can even give it a custom default
```

Example — this is your log-grouping problem from earlier, now trivially easy:

```python
logs_by_user = defaultdict(list)
for log in logs:
    logs_by_user[log["user_id"]].append(log)   # no setdefault, no if-check, ever
```

## On "efficiency" — worth being precise here

It's not really a *speed* optimization (a `setdefault` call and a `defaultdict` access cost about the same under the hood) — it's a **correctness and readability** win: you eliminate a whole class of bugs where someone forgets the existence check, and the code reads as "I'm building groups" instead of "I'm doing key-existence bookkeeping." If you say this distinction out loud in the interview — "it's not primarily about raw speed, it's about removing boilerplate and a source of bugs" — that's a more senior-sounding answer than just "it's faster."

---

## Quick reference: which tool, when

| Situation | Reach for |
|---|---|
| Processing something too big for memory, or might stop early | generator (`yield`) |
| Same expensive call repeated with same inputs | `functools.lru_cache` |
| Wrapping retry/timing/logging around many functions | custom decorator + `functools.wraps` |
| Grouping consecutive sorted items without a full dict | `itertools.groupby` |
| Counting things / "top N most common" | `collections.Counter` |
| Maximize count under a simple budget | greedy + `heapq` |
| Maximize value under a weight constraint | DP, often via `lru_cache` on recursion |
| Keeping a list sorted as items arrive | `bisect.insort` |
| Guaranteed setup/cleanup around a block | `contextlib.contextmanager` |
| Multiple independent slow I/O calls | `concurrent.futures.ThreadPoolExecutor` |
| Many small, simple data objects | `dataclasses` (+ `slots=True` for memory) |

---

## How to use this in practice

Don't just read the solutions — for each one, **cover the code and try to write it from the problem statement alone first**, then compare. The value isn't memorizing these exact snippets; it's building the reflex of asking *"is there a standard library tool that already does this better than a hand-rolled loop?"* before you start typing — because that question, asked out loud, is exactly what your feedback was pointing at.
