# micro1 Retake Prep — Production & Database Deep-Dive Questions

Your first round tested "can you talk about your career." This round tests **"have you actually operated a system in production and thought about what breaks it."** These questions all orbit three themes: **not doing the same thing twice by accident (idempotency)**, **not corrupting data when two things happen at once (concurrency)**, and **not breaking old code when the data model changes (compatibility)**. Once you see that pattern, the answers start rhyming with each other.

Each answer below has: a **plain-English explanation** first, then a **line you can actually say out loud** in the interview.

---

## 1. Primary key vs unique constraint (and nulls in Django)

**Plain English:** A primary key is the ID that officially identifies a row — every table gets exactly one, it can never be empty, and it never changes. A unique constraint is a separate promise you put on *other* columns, like "no two users can have the same email." You can have several unique constraints, and — this is the twist — most databases (Postgres included) treat `NULL` as "unknown," so multiple rows with a `NULL` in a unique column are allowed to coexist. Two rows can both have `email = NULL` and that doesn't violate the unique constraint, because NULL is never considered equal to NULL.

**Say this:** *"A primary key uniquely identifies the row itself and can never be null — it's the table's backbone. A unique constraint enforces uniqueness on a business field, like email or SKU, but in Django and Postgres, NULL isn't treated as a value that equals another NULL, so you can actually have multiple NULLs in a unique column unless you add extra application-level validation for that case."*

---

## 2. How do you handle API calls (to external services)?

**Plain English:** Never call an external API and just hope for the best. You wrap it in: a **timeout** (don't wait forever), **retries with backoff** (try again, but wait a bit longer each time so you don't hammer a struggling service), and ideally a **circuit breaker** (after enough failures, stop calling it for a while and fail fast, instead of piling up requests against a service that's clearly down).

**Say this:** *"I wrap external calls with a timeout so a slow dependency can't hang my request thread, retries with exponential backoff for transient failures, and a circuit breaker so that if the external service is consistently failing, I stop hammering it and fail fast instead — protecting my own system's resources."*

---

## 3. How do you keep business logic out of models and views in Django?

**Plain English:** Django tempts you to either cram logic into the model (fat models) or into the view (fat views). The cleaner pattern is a **service layer** — a plain Python module/function (often in a `services.py`) that contains the actual business rules ("what does it mean to place an order"), while the model stays focused on *data shape and simple data rules* (like "this field can't be negative"), and the view stays focused on *HTTP concerns* (parsing the request, calling the service, returning a response).

**Say this:** *"I use a service layer — models stay responsible for data integrity and simple invariants, views stay responsible for HTTP request/response handling, and the actual business logic — the steps involved in 'placing an order' or 'issuing a refund' — lives in a services module that both can call into. That keeps each layer testable independently."*

---

## 4. How do you prevent errors when an external service is down?

**Plain English:** Same toolbox as #2, plus a **fallback**: what should happen instead? Maybe you serve cached/stale data, maybe you queue the request to retry later, maybe you degrade gracefully (show "price unavailable" instead of crashing the whole page).

**Say this:** *"Beyond timeouts and circuit breakers, I design a fallback path — serving cached data, queuing the action for later processing, or degrading that one feature gracefully — so one dependency's outage doesn't cascade into a full outage of my own service."*

---

## 5. What logic do you store in utils vs models in Django?

**Plain English:** `models.py` should hold logic that is *intrinsically about the data itself* — a method like `order.total_price()` that only needs the order's own fields. `utils.py` (or a services module) should hold logic that's *generic, reusable, or has no natural home on one model* — a currency formatter, a date-range calculator, a slug generator — things that don't depend on a specific model instance's state.

**Say this:** *"If the logic only needs data that already lives on that one model instance, it belongs on the model. If it's a reusable helper that doesn't care which model called it — formatting, calculations, string manipulation — it goes in utils, so it isn't duplicated across models."*

---

## 6. Order number vs UUID as primary key

**Plain English:** A UUID is great as a primary key because it's globally unique and can be generated before the row even hits the database (useful in distributed systems) — but it's random, so it's bad for a human-facing "order number" and can hurt database index performance a little because it's not sequential. An auto-incrementing order number is easy to read and sort, but it leaks information (competitors can guess your order volume) and doesn't work well if you have multiple services generating orders independently. Common solution: use a UUID as the actual primary key internally, and generate a separate, human-friendly, sequential "order number" field just for display to customers.

**Say this:** *"I'd typically use a UUID as the primary key for uniqueness across distributed services and to avoid leaking business volume, but expose a separate, sequential, human-readable order number field for customer-facing use — so I get both database-level robustness and a friendly number for support and receipts."*

---

## 7. Unit test vs integration test, and mocking

**Plain English:** A **unit test** checks one small piece of logic in total isolation — no database, no network. An **integration test** checks that multiple pieces actually work together — like your view, your service, and a real (test) database. **Mocking** means replacing a real dependency (an external API, the database, the clock) with a fake stand-in that you control, so your unit test doesn't need the real thing to be running and doesn't produce real side effects (like actually charging a credit card).

**Say this:** *"Unit tests isolate a single function or method and mock out its dependencies so the test is fast and deterministic. Integration tests exercise multiple components together — often against a real test database — to confirm the pieces actually cooperate correctly. I mock external services in unit tests specifically so I'm not dependent on their uptime or causing real side effects during testing."*

---

## 8. Two-Phase Commit (2PC) in microservices

**Plain English:** 2PC is a way to make multiple services agree on a transaction together. Phase 1 ("prepare"): a coordinator asks every service "can you do this?" and each says yes/no without committing yet. Phase 2 ("commit"): if everyone said yes, the coordinator tells them all to actually commit; if anyone said no, everyone rolls back. The catch: it's slow (everyone has to wait), and if the coordinator crashes mid-process, services can get stuck holding locks. That's why most microservice architectures avoid 2PC and use the **Saga pattern** instead — each service commits its own local transaction and publishes an event, and if a later step fails, you run **compensating actions** (reverse operations) on the earlier steps instead of a true rollback.

**Say this:** *"2PC has a coordinator ask every participating service to 'prepare' a transaction, then only commits it everywhere once all services confirm they're ready — giving strong consistency, but at the cost of blocking and a single point of failure if the coordinator dies. In practice, for microservices I favor the Saga pattern: each service commits locally and emits an event, and if a downstream step fails, I run compensating actions — like issuing a refund instead of a true rollback — to undo the earlier steps."*

---

## 9. How do you ensure atomicity in Django?

**Plain English:** Wrap the operations in `transaction.atomic()`. That tells Django "either every database write inside this block succeeds, or none of them do." If an exception is raised partway through, everything already done inside that block gets rolled back.

**Say this:** *"I wrap multi-step database operations in Django's `transaction.atomic()` block, often as a decorator on the service function. If any exception is raised anywhere inside that block, Django rolls back every write that happened within it, so I never end up with half-applied state — like an order created but its inventory not decremented."*

---

## 10. How does the frontend/API ensure it only receives the values it wants?

**Plain English:** You don't just return the raw database row. You define a **serializer** (in Django REST Framework) that acts as an explicit allow-list — it names exactly which fields go out, and it validates and shapes exactly which fields are allowed in on write. This prevents both accidentally leaking internal fields (like a password hash) and accidentally accepting fields the client shouldn't be allowed to set (like `is_admin`).

**Say this:** *"I use a serializer as an explicit contract — it defines exactly which fields are exposed on read and exactly which fields are accepted on write, so the API never accidentally leaks internal fields or accepts a field a client shouldn't be able to set, like a role or permission flag."*

---

## 11. How do you ensure an API response doesn't duplicate effects if the response is resent?

*(This is "idempotency" — the exact gap called out in your feedback.)*

**Plain English:** If a client's request times out, it often retries — but the first request may have actually succeeded on the server even though the client never saw the response. If "place order" isn't idempotent, the customer gets charged twice. The fix: make the *operation*, not just the response, safe to repeat. Two concrete techniques:
- **Client-provided idempotency key**: the client generates a unique key (often a UUID) and sends it with the request. The server stores "I've already processed this key" and, if it sees the same key again, returns the original result instead of redoing the action.
- **Upserts / unique constraints**: instead of "insert a new payment row," you do "insert or update where this key already exists" — the database itself refuses a second insert with the same unique value.

**Say this:** *"I make the operation idempotent rather than just relying on the response — typically via a client-provided idempotency key sent in the request header, which the server checks against a store of already-processed keys before doing any work. Combined with a unique constraint or upsert on that key at the database level, this means even if the client retries after a timeout, the action only ever actually happens once."*

---

## 12. What value do you check for idempotency, and where does it come from?

**Plain English:** The value is the **idempotency key** — and critically, it's **generated by the client**, not the server (because if the server generated it, a retry would just get a new key and defeat the whole purpose). The client typically generates a UUID once, right when the user initiates the action (e.g., clicks "Pay Now"), and sends that same UUID on every retry of that same request. The server stores a mapping of key → result (often in Redis or a dedicated database table with a unique constraint on the key) so a repeated key returns the cached result instead of re-running the logic.

**Say this:** *"The idempotency key has to be generated client-side, at the moment the action is triggered, and reused on every retry — if the server generated it, retries wouldn't be recognizable as duplicates. The server persists that key alongside the result, usually in Redis or a table with a unique constraint on the key column, and checks for it before doing any work."*

---

## 13. How do you communicate a commit/rollback across microservices?

**Plain English:** You can't roll back another service's already-committed transaction directly — it owns its own database. Instead, in the Saga pattern, if a later step fails, the earlier services are told (usually via an event on a message queue) to run a **compensating action** — a business-level "undo," like refunding a payment or releasing reserved inventory — rather than a database-level rollback.

**Say this:** *"Since each microservice owns its own database, there's no cross-service rollback in the traditional sense. Instead I use the Saga pattern's compensating actions — if step three fails, I publish an event that tells step one and two's services to reverse their own already-committed changes, like releasing reserved stock or refunding a charge, rather than attempting an actual transactional rollback."*

---

## 14. How do you handle a column name change in NoSQL while keeping old code working?

**Plain English:** NoSQL has no rigid schema, so old documents in the database still have the old field name even after your code starts writing the new one. If you just rename it in code, old records "lose" that data as far as the new code is concerned. The safe pattern: **read both, write one** — read code checks for the new field name first and falls back to the old name if it's missing; write code always writes the new name (and optionally both, temporarily). Once a background migration script has rewritten all old documents, you remove the fallback.

**Say this:** *"I do a phased migration — the application is updated first to read either the old or new field name, falling back to the old one if the new one is absent, while all new writes use the new name going forward. I then run a background migration to backfill existing documents to the new field name, and only once that's complete and verified do I remove the fallback read logic — so nothing breaks mid-migration."*

---

## 15. Duplicate columns or duplicate calls — why does this happen and why does it matter?

**Plain English:** Duplicate calls usually happen from network retries, double-clicks, or race conditions — the same logical action getting executed more than once. Duplicate columns/data usually happen from a lack of a unique constraint, or from a migration/merge that didn't dedupe first. Both matter because they silently corrupt your data's meaning — double-charging a customer, double-counting revenue, or having two "sources of truth" for the same field that can drift out of sync.

**Say this:** *"Duplicate calls typically come from client retries, double form submissions, or race conditions where a request is processed twice concurrently — which is exactly why idempotency keys matter. Duplicate columns usually stem from a missing unique constraint or an incomplete migration, and the risk is that you end up with two fields representing 'the same' data that can silently drift apart, which is much harder to detect than an outright crash."*

---

## On the coding challenge (maximizing purchases under constraints)

Your feedback specifically flagged "optimal algorithmic strategy" and code cleanliness. A few things worth brushing up regardless of the exact problem phrasing:

- **Recognize the pattern.** "Maximize X under a constraint (budget/capacity/time)" is almost always a variant of the **knapsack problem** or a **greedy algorithm** problem. Ask yourself: is a greedy choice (always pick the cheapest / highest-value-per-cost item) provably optimal here, or do I need dynamic programming because greedy could miss a better combination? If items are divisible (like fractional stock), greedy on value/cost ratio usually works. If items are indivisible (like whole units you either buy or don't), you often need DP.
- **State your approach out loud before coding.** Say "I'll sort by X, then greedily take Y, because Z" — interviewers (and Zara's transcript-based grading) score the *reasoning*, not just working code.
- **Match the required input/output format exactly.** A correct algorithm that returns the wrong shape (e.g., a list instead of a dict, or off-by-one in bounds) reads as an incomplete solution.
- **Delete anything you don't use.** Leftover print statements, commented-out attempts, or unused variables read as sloppiness even when the core logic is right — clean up in your last minute or two.

---

## Delivery reminders for the retake (same as before, still true)

- Use the words "idempotency key," "upsert," "unique constraint," "compensating action," and "Saga pattern" explicitly where relevant — the feedback specifically wants to hear this vocabulary, not just the underlying idea.
- Structure every answer with a spoken shape: *"The problem is X. My approach is Y. The tradeoff is Z."*
- For scenario/production questions, it's fine to say *"I haven't personally hit this exact failure, but here's how I'd reason through it"* — then walk through the framework. Zara scores structured reasoning, not just war stories.
