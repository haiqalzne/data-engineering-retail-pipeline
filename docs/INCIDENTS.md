# Incident response and recovery exercise

1. Find the newest run record under output/; check status, task history, and error_type.
2. If the run failed, do not interpret an older report as fresh. Reports are named by
   run ID; only the successful run record identifies its valid report.
3. Check source availability and schema. Validation issues require correcting the
   input contract, not suppressing checks or repeatedly retrying.
4. Notify the fictional source owner/analyst in an exercise; this program sends no messages.
5. Rerun after correcting the source, verify totals and tests, then record the cause.

Safe failure demonstration (does not damage the source):

```bash
python workflow.py --source data/does-not-exist.json --output output/failure-exercise
```

Expect exit code 1 and a failed run record, with no warehouse or report produced there.
Then run the normal workflow. Automated tests also exercise malformed input and
prove that the prior warehouse survives batch validation failure.

Replay exercise: run stream.py twice. The second pass accepts zero new events;
previously accepted IDs count as duplicates. Event IDs must uniquely identify immutable
events: corrections need a new ID. This is not distributed exactly-once processing.
