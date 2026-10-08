# Course 1 learning map

Original educational implementation, not an official lab or completed course assessment.
Page references refer to the saved DeepLearning.AI Course 1 weekly PDFs. Those PDFs
and proprietary lab materials are deliberately not included in this public repository.

| Concept | Where to study in this project | Course slides |
| --- | --- | --- |
| Business value and requirements | REQUIREMENTS.md | Week 1 pp. 30–66; Week 4 pp. 8–42 |
| Generation, ingestion, storage, transformation, serving | data/, pipeline.py, queries/, report.py | Week 2 pp. 5–61 |
| Security, governance, quality | REQUIREMENTS.md; pipeline validation; synthetic inputs | Week 2 pp. 71–84 |
| Architecture, reversible choices, cost | ARCHITECTURE.md | Week 3 pp. 9–54, 83–124 |
| Batch ETL versus ELT | workflow.py implements ETL; ARCHITECTURE.md explains ELT | Week 3 pp. 55–67 |
| Streaming, replay, duplicate handling | stream.py and events.jsonl | Week 3 pp. 68–78 |
| DataOps, lineage, incident response | workflow.py run records; INCIDENTS.md | Week 2 pp. 99–109 |
| Orchestration and dependencies | workflow.py stops dependent tasks on failure | Week 2 pp. 110–128 |
| Software engineering and automated checks | tests/; GitHub Actions workflow | Week 2 pp. 129–133 |
| Architecture review | ARCHITECTURE.md six-area review | Week 3 pp. 125–131 |
| Recommendation concepts and fallback | similarity.py manually assigned vectors | Week 4 pp. 19–32, 66–76 |
| AWS and infrastructure as code | ARCHITECTURE.md conceptual mapping only | Week 2 pp. 134–157; Week 4 pp. 46–65 |

Read requirements first, then run the batch workflow, examine its records, replay
events, try similarity/fallback, and inspect tests. Architecture knowledge is not
equivalent to a deployed cloud implementation.
