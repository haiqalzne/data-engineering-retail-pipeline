# Stakeholders, requirements, and governance

## Business goal and owners

A fictional retail manager wants to compare product lines and countries. An analyst
needs reconciled sales records. The source owner supplies a JSON snapshot. The pipeline
maintainer owns validation, failure investigation, and the learning warehouse.
Success means reports agree with completed order lines, excluding cancellations.

## Functional acceptance criteria

- Load customer, product, date, and order-line facts from the synthetic snapshot.
- Reject missing references, duplicate IDs, invalid quantities, prices, and dates.
- Compute country and product-line revenue; expected fixture total is 16,500 cents.
- Rerunning a snapshot must not duplicate facts.
- Replay activity one event at a time and ignore previously accepted event IDs.
- Provide a toy similarity demonstration with a popularity fallback for unknown products.

## Nonfunctional requirements and limits

- Reliability: invalid batch input must leave previous sales intact; failed runs must
  not publish a new report. Automated tests verify these expectations.
- Observability: every batch invocation produces a status, duration, task history,
  UTC timestamps, source fingerprint, and schema version. Timings are measurements,
  not guarantees of data freshness or an end-to-end latency SLA.
- Security: synthetic records only; no keys, network services, or real customer data.
  SQLite has no application-level authorization here. Local OS permissions protect files.
  Generated artifacts stay out of Git, but this does not encrypt them or restrict access.
- Maintainability: processing, reporting, event consumption, and requirements are separated.
- Capacity: small single-machine demonstration only, not a production benchmark.
- Cost: no paid service is required; local compute and disk still have a cost.
- Recovery objective for this demo: regenerate from the retained source. No tested
  numerical RTO/RPO commitment; production targets need stakeholder agreement.

## Data contract and retention

Identifiers are nonblank strings; dates are ISO calendar dates; quantities are positive
integers; money is nonnegative integer cents in one fictional currency. Order status
is completed or cancelled. Source owner must communicate schema changes; validation
fails rather than guessing how to interpret a breaking change.
The fact grain is one completed order line. Historical snapshots and run records
accumulate locally under output/; the maintainer should review retention and remove
only confirmed disposable artifacts. This demo does not implement privacy-law compliance.
