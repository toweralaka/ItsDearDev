Good audit question — let me trace it back through all three files honestly, because the coverage isn't even between the two.

## Coordination

This bucket is reasonably covered, spread across a few files:

| Question | File | What it's really testing |
|---|---|---|
| Section D1 — "multi-step process spans several services, one step fails" | `micro1_expanded_question_bank.md` | Saga pattern / compensating actions |
| Section D2 — "two services agree on order state (paid + shipped)" | `micro1_expanded_question_bank.md` | Eventual consistency via events |
| Section D3 — "risk of message queue vs. calling directly" | `micro1_expanded_question_bank.md` | Decoupling / async coordination |
| Jargon Q2 — "referential integrity across bounded contexts" | `micro1_jargon_decoding_practice.md` | Same idea as D2, dressed in jargon |
| Jargon Q10 + Part 4 answer — "monotonicity of event ordering across a partitioned broker" | `micro1_jargon_decoding_practice.md` | Ordering guarantees across services — this is the most genuinely "coordination"-flavored one |

## Observability

This one is thin — **only one question actually covers it**, and it's not even phrased in jargon:

| Question | File | What it's testing |
|---|---|---|
| Section F1 — "How do you know something's broken before a customer tells you?" | `micro1_expanded_question_bank.md` | Monitoring/alerting/logging |

That's it. None of the 10 dense jargon-practice questions used observability-flavored jargon (things like "distributed tracing," "correlation IDs," "log aggregation," "P99 latency alerting") — I skipped that vocabulary entirely when I built that list, which is a real gap given it showed up in your bucket table.

## Want me to close the gap?

I can write a proper set for **observability specifically** — covering distributed tracing/correlation IDs across microservices, structured logging, alerting thresholds/SLOs, and how you'd debug a request that touched 4 services without a single stack trace to look at — in the same jargon-dense-question → plain translation → sayable-answer → ELI9 format as before. Want that, plus a few more genuinely jargon-heavy **coordination** questions (using words like "orchestration," "distributed consensus," "synchronization barrier") to round that bucket out too?
