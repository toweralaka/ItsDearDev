# micro1 Retake — Expanded Question Bank (Zara-style phrasing)

Format for each question:
- 🎤 **How Zara might actually ask it** (conversational, sometimes vague on purpose)
- 💬 **What you say** (the polished, interview-ready answer)
- 🧒 **Explain it like I'm 9** (the dead-simple version — if you can say this part confidently, you can handle any follow-up)

---

## Section A: Concurrency & Duplicate Actions

### A1
🎤 *"Let's say two customers try to buy the last item in stock at the exact same second. Walk me through how your system handles that."*

💬 **You say:** "That's a race condition. I'd handle it at the database level rather than in application code, since two servers could be running this at once. I'd use a database-level lock or an atomic decrement — something like 'decrease stock by 1 where stock is greater than 0' as a single atomic query — so the database itself guarantees only one of the two requests succeeds, and the second one gets told the item is out of stock."

🧒 **Like I'm 9:** Imagine one cookie left and two kids grab for it at the same time. If you let them "check first, then take it," they might both see one cookie and both think they got it. Instead, you make a rule: only one hand is allowed to touch the cookie jar at a time. Whoever's hand gets there, the jar says "taken" instantly, so the second kid is told "sorry, gone" before they even try.

---

### A2
🎤 *"What's the difference between optimistic and pessimistic locking, and when would you use each?"*

💬 **You say:** "Pessimistic locking assumes conflicts are likely, so it locks the row the moment you read it, and everyone else has to wait until you're done — safe, but it can hurt throughput under high concurrency. Optimistic locking assumes conflicts are rare — you read the data along with a version number, and when you go to save, you check that the version hasn't changed. If someone else updated it in the meantime, your save fails and you retry. I'd use pessimistic locking for something like a bank transfer where correctness is critical and contention is expected, and optimistic locking for something like editing a shared document where conflicts are rare."

🧒 **Like I'm 9:** Pessimistic locking is like putting a "do not disturb, I'm using this" sign on the door the second you walk in — nobody else can come in until you leave. Optimistic locking is like walking in without a sign, but when you leave you check "hey, is the room still exactly how I left it?" If someone rearranged it while you were inside, you redo your work. You only lock the door when you actually expect trouble.

---

### A3
🎤 *"If a webhook or callback from a payment provider gets sent twice — maybe their server retried — how do you make sure you don't process the payment twice?"*

💬 **You say:** "Every webhook event from a reliable provider includes a unique event ID. I store the IDs I've already processed — usually in a table with a unique constraint or in Redis with a TTL — and before doing any work, I check if that ID has been seen. If it has, I return a success response immediately without redoing the side effects, since the provider will keep retrying until it gets an acknowledgment anyway."

🧒 **Like I'm 9:** It's like getting the same birthday card mailed to you twice because the post office wasn't sure the first one arrived. You don't celebrate your birthday twice — you just check "wait, didn't I already open this exact card?" and if yes, you just say "got it, thanks" and move on.

---

### A4
🎤 *"Two microservices both try to update the same order at nearly the same time — one marking it shipped, one marking it cancelled. How do you avoid a mess?"*

💬 **You say:** "This is a data ownership and ordering problem. Ideally, only one service should own the authoritative state of 'order status,' and other services request state changes through it rather than writing directly. I'd also add a version number or timestamp to the order, and reject an update if it's based on stale data — so 'cancelled' and 'shipped' can't both silently apply out of order."

🧒 **Like I'm 9:** Imagine two people trying to write different things on the same whiteboard at once, and neither one looks at what the other just wrote. You avoid the mess by having one whiteboard monitor — only they're allowed to actually change what's on the board, and everyone else has to ask the monitor first.

---

## Section B: Data Modeling & Django Specifics

### B1
🎤 *"How would you design the database so that a user can't accidentally be charged twice for the same order?"*

💬 **You say:** "I'd add a unique constraint on the combination of order ID and idempotency key in the payments table, so the database itself physically refuses a second insert for the same order-key pair — it's not just an application check, it's enforced structurally, so even a bug in my code can't create a duplicate charge."

🧒 **Like I'm 9:** It's like a rule at a movie theater: one ticket, one seat number — the computer just won't let two tickets print the same seat, no matter how many times someone clicks 'buy.' The rule isn't "please don't do that," it's "physically impossible to do that."

---

### B2
🎤 *"Tell me how you'd structure a Django app so business rules don't leak into random places."*

💬 **You say:** "I keep a clear separation: models hold data and simple validation, views/serializers handle request and response shaping, and a services layer holds the actual business rules — like 'what happens when an order is placed.' That way, if the business rule changes, I know exactly one place to update it, and I can unit test that logic without needing an HTTP request or database at all."

🧒 **Like I'm 9:** It's like a kitchen. The fridge (model) just stores ingredients. The waiter (view) just takes your order and brings your food. The chef (service layer) is the one who actually decides how the meal gets made. If you let the waiter start cooking randomly, the kitchen turns to chaos.

---

### B3
🎤 *"How do you make sure that when you save something to the database, either everything saves or nothing does — no half-finished state?"*

💬 **You say:** "I wrap the related writes in a database transaction — in Django that's `transaction.atomic()`. If any step inside that block throws an error, every write in that block is rolled back automatically, so I never end up with, say, an order recorded but the customer's loyalty points not updated."

🧒 **Like I'm 9:** It's like buying a toy with a gift card. Either both things happen — you get the toy AND the money leaves the card — or neither happens. You'd never want the toy gone but the card still full, or the money gone but no toy.

---

### B4
🎤 *"If you needed to change what a field is called in the database, but old code elsewhere is still using the old name, how would you approach that without breaking anything?"*

💬 **You say:** "I do it in phases rather than all at once. First, I make the code read either the old or new field name, preferring the new one but falling back to the old one if it's missing. Then all new writes use the new name. Once I've backfilled all the old records with a migration script, I remove the fallback logic. That way nothing breaks during the transition."

🧒 **Like I'm 9:** Imagine your school starts calling "recess" by a new name, "free time." You wouldn't just change the announcement one day and confuse everyone — you'd say "recess, now called free time" for a while, so everyone understands both, and only later drop the old name.

---

## Section C: APIs & Communication Between Services

### C1
🎤 *"Say your service calls another team's API, and it's slow or hanging. What do you do?"*

💬 **You say:** "I set a timeout so my request doesn't hang indefinitely and tie up my own resources. I'd pair that with retries using exponential backoff for transient issues, and a circuit breaker so that if the dependency keeps failing, I stop calling it for a short period and fail fast instead of queuing up requests against something that's clearly struggling."

🧒 **Like I'm 9:** If you call a friend and they don't pick up, you don't stand there holding the phone forever — you hang up after a bit, try again a little later, and if they never answer after a few tries, you stop calling for a while.

---

### C2
🎤 *"How do you prevent an API from accidentally exposing data it shouldn't — like internal fields or another user's info?"*

💬 **You say:** "I use serializers as an explicit contract that names exactly which fields go out — never just returning the raw database row. On top of that, I enforce authorization at the query level, filtering results to only what that specific user is allowed to see, rather than fetching everything and hoping the frontend hides it."

🧒 **Like I'm 9:** It's like handing someone a printed report instead of your whole notebook. You decide exactly what goes on that printed page — you don't hand over the entire notebook and trust them not to flip to the private pages.

---

### C3
🎤 *"What happens on your end if a client sends you a request but you never get a chance to send back a response — maybe the connection dropped?"*

💬 **You say:** "From the server's side, the work may have already completed even though the client never saw confirmation — so the client will likely retry. That's exactly why the operation needs to be idempotent: designed so that processing the same request twice has the same effect as processing it once, typically through an idempotency key the client sends, checked against previously handled requests before doing any work."

🧒 **Like I'm 9:** Imagine you mail a letter, but you never get a reply saying "got it," so you mail it again just in case. If the person already read your first letter, they shouldn't act on it twice — they should just recognize "this is the same letter as before."

---

### C4
🎤 *"How would you design an API so that if a request is retried, it doesn't cause the same action to happen multiple times?"*

💬 **You say:** "The client generates a unique idempotency key at the moment the action is triggered and sends it on every attempt, including retries. The server checks that key against a store of already-processed requests before doing anything — if it's seen the key before, it just returns the original result instead of repeating the work."

🧒 **Like I'm 9:** It's like a wristband at a fair — once you're stamped, you show the same stamp to get back in, and the gatekeeper doesn't stamp you a second time just because you asked twice.

---

## Section D: Microservices & Distributed Systems

### D1
🎤 *"If a multi-step process spans several services and one step fails halfway through, how do you undo what already happened?"*

💬 **You say:** "Since each service owns its own database, there's no single rollback across all of them. I use the Saga pattern — if a later step fails, I trigger compensating actions on the earlier steps, which are their own separate operations that reverse the business effect, like refunding a charge or releasing reserved stock, rather than a true database rollback."

🧒 **Like I'm 9:** If you're building a Lego tower with three friends, each building one section, and the last friend messes up, you don't magically un-build the first two sections. You tell those friends "take your piece back apart" — it's a new action to undo it, not a rewind button.

---

### D2
🎤 *"How do you make sure two services agree on the state of something, like an order being both 'paid' and 'shipped' correctly, without one getting out of sync?"*

💬 **You say:** "I favor eventual consistency with events over trying to force immediate agreement across services. Each service reacts to events — 'payment confirmed' triggers the shipping service to act — and I make sure each event handler is idempotent, so if an event is delivered more than once, state doesn't drift. For anything that truly needs strong, immediate consistency, I'd keep that data in a single service rather than splitting it."

🧒 **Like I'm 9:** It's like a relay race — each runner just needs to know "when I get the baton, do my part, then pass it on." As long as each handoff is done correctly, the whole race works out, even though nobody's in sync every single second.

---

### D3
🎤 *"What's the risk of using a message queue for communication instead of just calling the other service directly?"*

💬 **You say:** "The main tradeoff is that you gain resilience and decoupling — if the downstream service is briefly down, the message just waits in the queue — but you lose immediate feedback and get eventual rather than instant consistency. There's also a risk of message duplication depending on the queue's delivery guarantee, so consumers need to be idempotent regardless."

🧒 **Like I'm 9:** A message queue is like a mailbox instead of a phone call. If your friend isn't home, the letter just waits in the mailbox until they check it. But you don't get an instant answer, and the mail carrier might accidentally deliver the same letter twice.

---

### D4
🎤 *"How would you handle it if one service's database schema changes in a way that could break another service depending on it?"*

💬 **You say:** "Services shouldn't directly read each other's databases in the first place — they should communicate through a defined API or event contract. That contract should be versioned, so a breaking change is introduced as a new version while the old one continues to work, giving consumers time to migrate."

🧒 **Like I'm 9:** It's like changing the rules of a game you're playing with a friend over text messages. You agree on "okay, from now on we're playing version 2 of the rules," and you can both keep playing version 1 for a while until everyone's ready to switch.

---

## Section E: Performance & Scale

### E1
🎤 *"Your API is getting really slow as more users hit it — where do you even start looking?"*

💬 **You say:** "I start by measuring, not guessing — checking slow query logs and API response time metrics to find the actual bottleneck. Common culprits are missing database indexes, the N+1 query problem where a loop makes one database call per item instead of one call for all of them, and a lack of caching for data that's read far more than it changes. I'd fix in that order, since indexing and query fixes usually give the biggest win for the least risk."

🧒 **Like I'm 9:** If it's taking forever to find your shoes every morning, you don't just buy more shoe racks — you first figure out why it's slow. Maybe you're searching one shoe at a time instead of looking at all of them at once, or you just need a system, like always putting shoes in the same spot.

---

### E2
🎤 *"What's the N+1 query problem, and how do you spot it?"*

💬 **You say:** "It happens when you fetch a list of items with one query, then loop through them and run a separate query for each item's related data — so 100 items means 101 queries instead of 2. I spot it by looking at query logs or using Django Debug Toolbar, and I fix it with `select_related` or `prefetch_related` to fetch the related data in one or two queries up front."

🧒 **Like I'm 9:** It's like if you had a list of 30 friends' birthdays, and instead of asking one teacher for the whole list, you ran to ask each friend individually, 30 separate trips. Way faster to just get the whole list in one trip.

---

### E3
🎤 *"If a piece of data is cached, how do you make sure users don't see stale, outdated information?"*

💬 **You say:** "I set an appropriate expiration time based on how often the data actually changes, and for anything that changes on a known event, I explicitly invalidate or update the cache at that moment — like clearing a product's cached price the instant it's updated — rather than waiting for it to expire naturally."

🧒 **Like I'm 9:** A cache is like writing today's weather on a sticky note so you don't have to check the window every five minutes. But if it suddenly starts raining, you don't wait for the sticky note to become useless — you rip it off and write a new one right away.

---

### E4
🎤 *"How would you handle pagination for an endpoint that returns thousands of records?"*

💬 **You say:** "I'd avoid offset-based pagination at large scale, since 'skip 50,000 rows' gets slower the deeper you page. Instead I'd use cursor-based pagination — returning results after a specific record's ID or timestamp — which stays fast regardless of how deep into the dataset you are."

🧒 **Like I'm 9:** Offset pagination is like being told "skip the first 5,000 pages of this book every time you want the next page" — it gets slower the further in you go. Cursor pagination is like using a bookmark — "give me what comes right after my bookmark" is fast no matter how far in you are.

---

## Section F: Reliability, Testing & Operations

### F1
🎤 *"How do you know something's actually broken in production before a customer tells you?"*

💬 **You say:** "Through monitoring and alerting — tracking error rates, response times, and key business metrics, with alerts configured to fire when something crosses a threshold, paired with structured logging so that once alerted, I can actually trace what happened. I'd rather find out from a dashboard at 2am than from an angry customer email the next morning."

🧒 **Like I'm 9:** It's like a smoke alarm in your house. You don't want to find out there's a fire because you smell smoke — you want something that beeps the second there's a problem, way before it gets that bad.

---

### F2
🎤 *"Explain how you'd test a function that calls a third-party payment API, without actually charging a real card every time you run your tests."*

💬 **You say:** "I'd mock the third-party client in my unit tests — replacing the real API call with a fake object that returns a controlled, predictable response — so I can test my own logic's handling of success and failure cases without hitting the real service or causing real charges. Separately, I'd have a smaller set of integration tests that run against the provider's actual sandbox environment to confirm the real integration still works."

🧒 **Like I'm 9:** It's like practicing a play with a fake microphone before performing with the real one — you're testing your lines and timing, not the actual sound equipment. Later, you do one real run-through with the actual mic.

---

### F3
🎤 *"If a background job — like sending an email or processing a payment — fails partway through, what happens?"*

💬 **You say:** "I make sure the job is retried automatically, usually with a limited number of attempts and backoff between them, and after exhausting retries, it goes to a dead-letter queue so a human can investigate rather than silently disappearing. The job itself needs to be idempotent so a retry doesn't, say, send the same email twice."

🧒 **Like I'm 9:** If your alarm doesn't go off correctly, you don't just give up — you have a backup alarm, and if that fails too, you put it on a special 'needs attention' list so someone actually checks why, instead of it quietly never happening.

---

### F4
🎤 *"What would you do differently in your API design if you knew from day one that it needed to support multiple versions over time?"*

💬 **You say:** "I'd version the API explicitly from the start — either through the URL path or a header — rather than trying to retrofit versioning later. I'd treat any change that removes a field, renames a field, or changes a field's type as a breaking change requiring a new version, while purely additive changes, like adding an optional field, can go into the existing version safely."

🧒 **Like I'm 9:** It's like giving each new edition of a rulebook a number on the cover. If you change the rules but keep calling it the same edition, people get confused about which rules they're actually following.

---

## Quick Concept Glossary (say these terms naturally, don't just list them)

| Term | One-line meaning |
|---|---|
| Idempotency | Doing it twice has the same effect as doing it once |
| Race condition | Two things happening at once step on each other's toes |
| Atomicity | All the steps succeed together, or none of them do |
| Eventual consistency | Things will match up soon, just not instantly |
| Circuit breaker | Stop calling something that's clearly broken, for a while |
| Compensating action | An "undo" that's its own new action, not a true rollback |
| Backward compatibility | Old code/data still works after you change something new |

---

## One habit that will help more than any single answer

When Zara asks something you don't fully know, don't freeze. Say out loud: *"I haven't hit that exact scenario, but here's how I'd reason through it — the core risk is usually duplication, lost data, or inconsistent state, so I'd approach it by..."* — then pick whichever pattern above fits closest (idempotency key, locking, Saga/compensating action, versioning). Almost every one of these questions is a costume worn by the same handful of underlying ideas.
