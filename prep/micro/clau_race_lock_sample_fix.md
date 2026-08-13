This is the **cache stampede / dogpile prevention** pattern. The tools involved:

- **`threading.Lock`** (or `asyncio.Lock` if you're in async code) — to make sure only one thread actually does the expensive recompute
- **A dict of locks, one per cache key** — so locking on key A doesn't block requests for unrelated key B
- **Double-checked locking** — check the cache, acquire lock, check the cache *again* (because another thread might've just filled it while you were waiting for the lock), only then recompute

### Single-process version (in-memory cache)

```python
import threading
import time
from collections import defaultdict

cache = {}
cache_locks = defaultdict(threading.Lock)   # one lock per key, not one global lock

def get_cached_value(key, compute_fn, ttl_seconds=60):
    entry = cache.get(key)

    # fast path — cache hit and still fresh, no locking needed at all
    if entry and (time.time() - entry["cached_at"]) < ttl_seconds:
        return entry["value"]

    # cache miss or expired — only now do we bother with a lock
    with cache_locks[key]:
        # re-check inside the lock: another thread may have already rebuilt it
        # while we were waiting our turn — this is the "double-checked" part
        entry = cache.get(key)
        if entry and (time.time() - entry["cached_at"]) < ttl_seconds:
            return entry["value"]

        # we're genuinely the first one here — do the expensive work
        value = compute_fn()
        cache[key] = {"value": value, "cached_at": time.time()}
        return value
```

**What actually happens when 50 requests hit an expired key at once:**
1. All 50 see the cache is stale and try to acquire `cache_locks[key]`.
2. Only 1 gets the lock immediately; the other 49 block, waiting.
3. That 1 request recomputes the value and stores it in the cache — this is the only DB hit.
4. As each of the other 49 finally gets the lock, the *second* check inside the lock finds the cache is now fresh, so they just read it and return — no recompute, no DB hit.

Without the lock, all 50 would see "expired" simultaneously and all 50 would hit the database at once — that's the stampede.

### If you're running multiple processes/servers (in-memory `threading.Lock` won't coordinate across them)

You need a **distributed lock**, typically via Redis:

```python
import redis
import time

r = redis.Redis()

def get_cached_value_distributed(key, compute_fn, ttl_seconds=60):
    value = r.get(key)
    if value is not None:
        return value

    lock_key = f"lock:{key}"
    # SET ... NX = only set if it doesn't already exist (this IS the lock)
    # PX = auto-expire the lock so a crashed process can't hold it forever
    got_lock = r.set(lock_key, "1", nx=True, px=5000)

    if got_lock:
        try:
            value = compute_fn()
            r.set(key, value, ex=ttl_seconds)
            return value
        finally:
            r.delete(lock_key)
    else:
        # someone else is rebuilding it — wait briefly, then read what they produced
        time.sleep(0.05)
        return r.get(key) or get_cached_value_distributed(key, compute_fn, ttl_seconds)
```

The `SET key value NX PX 5000` is the whole trick — it's Redis's atomic "only I get to do this" primitive, and the `PX` expiry means if your process dies mid-recompute, the lock self-releases instead of jamming forever.

**Say this in the interview:** *"I prevent the stampede with double-checked locking — check the cache, and only if it's actually stale do I acquire a lock scoped to that specific key. Inside the lock I check the cache one more time, because another thread may have just rebuilt it while I was waiting. Only the genuinely first request recomputes; everyone else either reads the fresh result after the lock releases, or in a distributed setup, waits briefly and re-reads from a shared cache like Redis, using `SET NX PX` as the atomic distributed lock."*

🧒 **Like I'm 9:** It's like 50 kids all noticing the classroom snack jar is empty at once. Instead of all 50 running to the kitchen, only the first kid to grab the "I'm getting more" sign is allowed to go. Everyone else just waits by the jar — and when the sign-holder comes back and refills it, everyone else just takes a snack from the now-full jar instead of also running to the kitchen.



## ELABORATION

## `threading.Lock` — what it actually is

In Python, when you write normal code, only one thing happens at a time, in order. But when you use **threads**, you can have multiple pieces of code running *at the same time*, and they can interleave in ways you don't control — one thread might pause halfway through a task while another thread jumps in.

A `Lock` is a simple object with exactly two states: **locked** or **unlocked**. It gives you two operations:
- `lock.acquire()` — "I want to go in. If someone else is already in, make me wait until they leave."
- `lock.release()` — "I'm done, next person can go in."

The `with lock:` syntax does both automatically — acquire at the start, release at the end (even if an error happens inside).

```python
import threading

lock = threading.Lock()

def do_something():
    with lock:
        # only ONE thread can be inside this block at a time
        # everyone else calling do_something() at the same moment
        # just waits here until the lock is free
        print("doing the important part")
```

🧒 **Like I'm 9:** Imagine a single bathroom with one key hanging outside. If you have the key, you can go in. If someone else has the key, you just wait outside the door until they come out and hang the key back up. The lock IS the key — only one person can hold it at a time.

**Why we needed it in the cache example:** without a lock, when the cache expires, every single thread just barrels straight into "recompute the value" at the same time — like 50 people all trying to walk through the same door with no rule about who goes first. The lock forces them to line up, so only the first one actually does the work.

---

## `NX` and `PX` — these are Redis command options, not Python

Redis has one basic command: `SET key value`. It just sets a value. But Redis lets you add extra flags to that same command to change its behavior:

### `NX` = "only set if it does NOt eXist yet"

Normally, `SET` will happily overwrite a key even if it's already there. `NX` changes that: it says "only actually set this if the key is currently empty/missing. If it already has a value, do nothing, and tell me you failed."

This is exactly what a lock needs: *"only let ONE person succeed at creating this key — everyone else who tries gets told no."* That's the whole lock mechanism — it's really just a race to see who can `SET` a key first, and Redis guarantees only one winner even if a thousand people try at the exact same instant.

```python
r.set("lock:my_key", "1", nx=True)
# Returns True  → you got the lock (key didn't exist before, now it does)
# Returns None/False → someone else already has the lock (key already existed)
```

🧒 **Like I'm 9:** Imagine a sign-up sheet with one blank line at the top. `NX` means "only write your name on that line if it's still blank." The first kid to reach it writes their name and the line is no longer blank. Every kid after that tries to write on the same line, sees it's already got a name on it, and just walks away — they know someone beat them to it.

### `PX` = "auto-delete this key after X milliseconds"

`PX 5000` means "this key should automatically disappear after 5000 milliseconds (5 seconds), even if nobody explicitly deletes it."

Why you need this for a lock: if the process holding the lock crashes, or the server dies, before it gets to `r.delete(lock_key)` — normally that lock would stay "held" forever, and nobody could ever get it again. `PX` acts as a safety net: even if nobody explicitly frees the lock, Redis will free it automatically after the timer runs out.

🧒 **Like I'm 9:** It's like a parking meter. Even if the driver forgets to move their car, the meter runs out on its own after a while, and the spot becomes available again for someone else — instead of being stuck "taken" forever just because one person forgot to leave properly.

---

## Putting it together, one line at a time

```python
got_lock = r.set(lock_key, "1", nx=True, px=5000)
```

Reading it out loud: *"Try to set this lock key to '1', but only if it doesn't already exist (`nx=True`), and if you do set it, make it automatically expire after 5000 milliseconds (`px=5000`) so it can't get stuck forever."*

- If **you're the first one** to run this line → Redis creates the key, returns `True` → you now hold the lock, go do the expensive work.
- If **someone already holds the lock** → the key already exists → Redis refuses to overwrite it (because of `nx`) → returns `None` → you know you *didn't* get the lock, so you go wait and read the cache instead of doing the work yourself.

That's genuinely the entire trick — one atomic command that answers "am I the first one here or not," with a built-in expiration so a crash can't leave everyone locked out forever.
