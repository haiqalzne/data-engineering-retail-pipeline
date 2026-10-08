# Architecture and trade-offs

## Local components

Batch: JSON source → snapshot and fingerprint → validate/transform → SQLite star
schema → read-only SQL reports → versioned report and run records.

Activity: JSONL replay → validation and event-ID deduplication → separate activity
database → event counts. It is a finite replay demonstrating streaming mechanics,
not an unbounded stream, broker, event-time window system, or delivery guarantee.

The two paths demonstrate different workloads, not a complete Lambda or Kappa architecture.
Toy similarity uses explicit three-number feature vectors and exhaustive cosine scoring;
it is neither a trained recommender nor a production vector database. Unknown products
use sales popularity; unavailable warehouse data still produces an error, not a guarantee.

## Decisions

- SQLite and the Python standard library keep setup simple for this dataset. A managed
  warehouse may be suitable later but adds cost and operational choices.
- Full snapshot ETL is easy to reason about and safely repeat; it is unsuitable for
  large incremental sources without further work. ELT would load first and transform
  in the destination; this project does not implement that alternative.
- Separate modules and simple file/data contracts allow replacement without rewriting
  every component. This is a reversible learning choice, not a claim that migration is free.
- A sequential workflow enforces dependencies; a production orchestrator adds scheduling,
  worker coordination, retries, and centralized monitoring. Do not blindly retry invalid data.
- TCO includes maintenance, training, disk and compute. Managed services can reduce
  engineering effort; self-built systems trade that effort for control. No vendor prices assumed.

## Six-area review

| Area | Demonstration | Remaining production work |
| --- | --- | --- |
| Operations | Tests, metrics, runbook | Centralized alerts and on-call ownership |
| Security | Synthetic data, no secrets, read-only reports | Authentication, authorization, encryption, retention controls |
| Reliability | Transactions, validation, replay deduplication | Backups, disaster-recovery drills, failover |
| Performance | Small measured local run | Load tests, indexes, capacity planning |
| Cost | No required cloud resources | Usage budgets and cost monitoring |
| Sustainability | Small local workload | Resource measurement and efficient scheduling |

## Conceptual AWS mapping, not deployment instructions

Source database → RDS; object storage → S3; batch transform → Glue;
analytical querying → Athena or a warehouse; events → Kinesis or managed Kafka;
monitoring → CloudWatch; permissions → IAM. Terraform would describe cloud resources,
but no cloud resources or Terraform configuration are created by this project.
Provisioning, current service capabilities, security, and costs must be evaluated separately.
