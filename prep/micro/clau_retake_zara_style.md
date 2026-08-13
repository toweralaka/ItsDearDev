# micro1 Retake — Jargon-Decoding Practice + Webhook Idempotency Fix

## Part 1: The actual skill you need — decoding dense jargon on the fly

Zara isn't asking a simpler question dressed up — she's asking the *real* question, just with all the jargon left in, the way it would appear in a system design doc. The fix isn't "memorize more phrasings," it's building a **reflex for stripping jargon down to the underlying concern in real time**, because she can rephrase infinitely and you can't memorize infinitely.

### The decoding move

Almost every dense question is built from two parts:
1. **A scenario noun-phrase** (the jargon-heavy setup) — e.g. *"transactional workflows across multiple distributed microservices"*
2. **A concern verb** (what she actually wants to know) — e.g. *"ensure data consistency and integrity"*

Your job: translate the concern verb into one of a small number of underlying worries, ignoring the scenario dressing at first:

| If she says... (jargon) | She's really worried about... |
|---|---|
| "ensure consistency / integrity" | things staying correct when multiple things touch the same data |
| "handle failure / fault tolerance / resilience" | what happens when something breaks mid-process |
| "prevent duplicate effects / idempotency / exactly-once" | doing the same thing twice by accident |
| "scale / high-concurrency / high-throughput" | performance when lots of things happen at once |
| "backward compatibility / versioning / migration" | old code/data not breaking when something changes |
| "coordination / orchestration / synchronization" | multiple services agreeing on what happened |
| "observability / traceability" | how you'd know something went wrong |

Once you know *which bucket* it's in, you already know which pattern to reach for (locking, idempotency key, Saga, versioning, caching, monitoring) — even before you've fully parsed her sentence.

### A live technique: paraphrase back as your opening line

Instead of pausing silently to decode, **start speaking your paraphrase immediately** — it buys you thinking time *and* proves to the transcript-grader that you understood the question, which is exactly what tripped you up last time (asking her to repeat looks like non-comprehension; paraphrasing looks like comprehension).

Say something like: *"So essentially you're asking how I'd keep the data correct if this transaction is happening across services that don't share a database — let me walk through that."* Then answer. You've bought 5 seconds, demonstrated understanding, and set up your own answer structure — all in one sentence.

---

## Part 2: Practice questions in genuine Zara-density (no simplification)

Read each jargon-heavy version cold, try to paraphrase it in one sentence out loud, *then* check yourself against the plain-English translation and the section it maps back to in your expanded question bank.

1. *"How do you guarantee exactly-once processing semantics when an upstream producer may redeliver the same message due to at-least-once delivery guarantees?"*
   → **Translation:** "How do you stop a resent message from causing the action to happen twice?" → maps to **Section C4 / D3** (idempotency + message queue duplication).

2. *"Describe your approach to maintaining referential integrity across bounded contexts when each service owns its own persistence layer."*
   → **Translation:** "Each service has its own database — how do you keep related data from contradicting itself across them?" → maps to **Section D2** (eventual consistency via events).

3. *"What concurrency control mechanisms would you employ to prevent lost updates under high write contention on a shared resource?"*
   → **Translation:** "Two things trying to update the same row at once — how do you stop one overwriting the other?" → maps to **Section A2** (optimistic vs pessimistic locking).

4. *"How would you design your system to be resilient to partial failure in a choreographed, event-driven architecture?"*
   → **Translation:** "One step in a multi-service process fails — how do you keep the rest of the system from breaking or getting stuck?" → maps to **Section D1** (Saga + compensating actions).

5. *"Walk me through your strategy for graceful degradation when a downstream dependency breaches its SLA."*
   → **Translation:** "An API you depend on is too slow or down — what do you do instead of just failing?" → maps to **Section C1** (timeouts, retries, circuit breaker, fallback).

6. *"How do you enforce idempotent state transitions when the inbound event payload lacks a canonical unique identifier?"*
   → **Translation:** "How do you stop duplicate processing when there's no ID to check against?" → **this is your A3 follow-up — see Part 3 below.**

7. *"What's your approach to schema evolution in a polyglot persistence environment to avoid breaking existing consumers?"*
   → **Translation:** "Different services use different types of databases — how do you change a schema without breaking whoever's reading it?" → maps to **Section B4 / D4**.

8. *"How would you mitigate the thundering herd problem when a cache entry expires under high concurrent read load?"*
   → **Translation (new one for you):** "A LOT of requests hit the database all at once the second a cached value expires — how do you stop that from overwhelming the database?" → *(answer below, new topic)*

9. *"Explain how you'd achieve horizontal scalability for a stateful service without violating session affinity requirements."*
   → **Translation:** "How do you add more servers to handle load when the service needs to remember something about the user between requests?" → maps loosely to **Section E1**, plus the new concept of statelessness below.

10. *"What's your strategy for ensuring monotonicity of event ordering when consuming from a partitioned message broker?"*
    → **Translation:** "Events can arrive out of order across partitions — how do you make sure you don't process a 'cancelled' event before the 'created' event it depends on?" → *(answer below, new topic)*

---

## Part 3: Fixing A3 — idempotency when there's no unique event ID

You were right to flag this — this is a genuinely different, harder problem, and it's a great follow-up question because it tests whether you understand the *principle* behind idempotency keys, not just the "check the ID" recipe.

**The core idea:** if the provider doesn't hand you a ready-made unique ID, you have two options — **manufacture your own deduplication key from the payload**, or **make the underlying operation idempotent by design so duplicates are harmless even if you can't detect them in advance.** A solid answer uses both, but leads with the second, because it's more robust.

### Option 1 — Build a composite dedup key from the payload content
Combine several stable fields from the event into a single key you can check against — for example `order_id + event_type + amount + timestamp_rounded_to_minute` — hash that combination, and store hashes you've already processed (in Redis with a TTL roughly matching how long the provider might retry, e.g. 24 hours). If the same combination arrives again, you recognize it and skip reprocessing.

**Risk to mention:** this isn't bulletproof — two *genuinely different* legitimate events could theoretically collide if they share all those fields. That's exactly why it's a fallback, not your primary defense.

### Option 2 — Make the state transition itself idempotent (the stronger answer)
Instead of asking "have I seen this exact event before," ask "does applying this event again actually change anything?" You design the operation so replaying it is a no-op if the target state is already reached. Concretely:
- Before marking an order "paid," check `if order.status == 'paid': return` — the second delivery does nothing, because the order's already in that state.
- Use a database `UPDATE ... WHERE status != 'paid'` — an atomic conditional update where a repeat event simply updates zero rows instead of double-applying an effect.

This is stronger because it doesn't depend on detecting the duplicate at all — it makes the duplicate harmless even if you never notice it was a duplicate.

**Say this in the interview:** *"If the provider doesn't give me a unique event ID, I'd fall back to two layers. First, I'd build a composite dedup key from stable fields in the payload — like the order ID, event type, and amount — hash it, and check it against recently processed hashes in a short-lived store. But more importantly, I'd design the actual state transition to be idempotent by nature — checking the current state before applying a change, or using a conditional atomic update — so that even if a duplicate slips past my detection, replaying it has no additional effect, because the system is already in the state the event describes."*

🧒 **Like I'm 9:** If a delivery driver doesn't have a receipt number to check ("is this the same delivery as before?"), the safer trick isn't guessing whether it's a repeat — it's making sure that dropping off the same package twice doesn't matter. If your porch already has the package, setting a second identical one down next to it doesn't add anything extra — nothing bad happens even if you never noticed it was a repeat.

---

## Part 4: Two new concepts that came up in decoding above (worth knowing cold)

### Thundering herd problem (cache stampede)
🎤 *"How would you mitigate the thundering herd problem when a cache entry expires under high concurrent read load?"*

💬 **You say:** "I'd avoid every request racing to rebuild the cache the moment it expires by using a lock so only the first request that misses the cache actually recomputes the value, while the rest wait briefly and then read the freshly rebuilt cache instead of all hitting the database simultaneously. I might also stagger expiration times slightly, so many keys don't all expire at the exact same instant."

🧒 **Like I'm 9:** If a whole class runs out of pencils at the same second and all 30 kids rush the supply closet at once, that's chaos. Instead, you let one kid go get a box for everyone, while the rest wait a second — much calmer, and the closet doesn't get trampled.

### Event ordering across a partitioned message broker
🎤 *"What's your strategy for ensuring monotonicity of event ordering when consuming from a partitioned message broker?"*

💬 **You say:** "I'd make sure events for the same entity — like the same order — are always routed to the same partition, using the entity ID as the partition key, since most brokers guarantee ordering within a partition even though ordering isn't guaranteed across partitions. On top of that, I'd design consumers to be tolerant of slightly out-of-order events where possible, for example by checking the event's own timestamp or version before applying it, so an old event arriving late doesn't overwrite a newer state."

🧒 **Like I'm 9:** It's like making sure all letters about the same kid's report card go through the same mail slot in order, instead of getting split across different slots that don't talk to each other. And even then, you check the date on the letter before believing it — so an old letter that shows up late doesn't undo the newer one.

---

## Practice drill for this week

Pick 3 questions from Part 2 each day, cover the translation column, and out loud: (1) paraphrase the jargon back in your own words as your opening line, (2) name which bucket it's in (duplication / concurrency / failure / compatibility / coordination / observability), (3) give your full answer. Timing yourself matters more than getting it perfect — the goal is killing the pause between "hearing jargon" and "starting to talk."
