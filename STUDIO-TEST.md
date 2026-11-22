# IntentBallot reproducible Studio walkthrough

This is the reproducible procedure. Actual execution evidence is recorded
separately in [DEPLOYMENT.md](DEPLOYMENT.md). Use synthetic technical preferences,
Normal / Full Consensus, simulation off and transaction value 0 GEN. Network fees
are separate. The release pins the v0.4.0 runner; recheck your actual chain and
host schema before reproducing it.

Do not switch the selected Studio source while a transaction displays Sending or
a deployment displays Deploying. Wait for the intended hash/address first.
Require GenVM SUCCESS and persisted state reads, not consensus acceptance alone.

## 1. Deploy exact source and open a synthetic one-voter poll

The constructor has no arguments. Confirm `get_stats()` reports version `1.0.0`,
schema `intentballot-v1`, max options `5`, max voters `6` and counters `0`.

Copy the actual current Studio account address. Call `open_poll`:

```text
title: Synthetic export preference
context: Choose a declared serialization format for an internal demo export tool. Descriptions are supplied assumptions, not verified product claims.
options_json: ["CSV export with tests.","JSON export with tests.","Parquet export with tests."]
voters_json: ["<actual copied Studio address>"]
min_confirmed: 1
commit_seconds: 60
reveal_seconds: 120
confirm_seconds: 300
```

Use the actual returned poll ID; on a fresh deployment it is `0`. Read `get_poll`
and save its complete `core` and `poll_hash`, including actual chain/deployment
domain and the three absolute deadlines. This first write exercises the real
transaction clock and message context. Choose longer periods if manual tooling
cannot reliably complete commitment within 60 seconds; periods are then fixed.

## 2. Produce the exact salted commitment offline

Use the published self-contained helper in the repository directory. Supply the
actual poll read as `poll.json`; never substitute a guessed hash or deployment.

```python
import json
from pathlib import Path
from commitment import make_commitment, generate_salt

poll = json.loads(Path("poll.json").read_text(encoding="utf-8"))
voter = "<actual current Studio address>"
statement = "I strictly prefer CSV export to JSON export, and JSON export to Parquet export."
salt = generate_salt()
commitment = make_commitment(poll["core"], poll["poll_hash"], voter, statement, salt)
# Save statement and salt privately until reveal. Only paste commitment now.
print(commitment)
```

Do not use angle-bracket placeholders in a call. Save the actual random salt
outside the public repository. Salt length is not a guarantee of entropy. Both
statement and salt become public at reveal; this is not an anonymous voting system.

From that eligible account call `commit_ballot(actual_poll_id, commitment)` before
`commit_until`. Record the ballot ID. Its stored state must be `COMMITTED`; it
must not contain the statement/salt yet. A second commitment by that voter fails.

## 3. Reveal the exact statement

At `commit_until <= now < reveal_until`, from the same account call:

```text
reveal_ballot(actual_ballot_id, exact_statement, exact_saved_salt)
```

Read `get_ballot`: state must be `REVEALED`, with exact bytes and the original
commitment. Wrong salts, whitespace changes, another voter and late reveals must
not replace it. These are optional live negative checks until actually executed.

## 4. Independently compile and inspect

Before `confirm_until`, call `assess_ballot(actual_ballot_id)`. For the clear
synthetic statement above, a faithful complete interpretation is:

```json
{"status":"RANKED","tiers":[[0],[1],[2]]}
```

Inspect the accepted stored receipt. Require `decision: READY`, complete semantic
inspection, no truncation, all three exact options and the complete statement,
and the same domain/poll/voter/commitment. Copy the actual `receipt_hash`.
The ballot is still **not cast**. An incorrect or ambiguous model interpretation
must not be automatically confirmed. Model disagreement is possible; capture its
actual transaction and result honestly, without claiming an expected ranking passed.

## 5. Voter confirmation and deterministic finalization

At `reveal_until <= now < confirm_until`, inspect the full ranking and, only if it
matches the synthetic voter's intended order, call:

```text
confirm_ballot(actual_ballot_id, exact_stored_receipt_hash)
```

Read back `CONFIRMED` and the exact confirmation time. At `now >= confirm_until`,
any account can call `finalize_poll(actual_poll_id)`. For one confirmed clear ballot
and quorum one, expect `DECIDED`, selected option `0`, optimal score `3`, the one
optimal order `[0,1,2]`, and matrix:

```json
[[0,1,1],[0,0,1],[0,0,0]]
```

Read the immutable stored result and its hash. A second finalization or later
confirmation must fail. This final step must use no new model calls.

## Optional multi-voter and adversarial checks

- Three confirmed rankings `0>1>2`, `1>2>0`, `2>0>1` create a Condorcet cycle:
  `TIED`, score `5`, co-winners `[0,1,2]`, selected option `-1`.
- Explicit ties contribute no pairwise direction. Complete indifference can meet
  confirmation quorum while all choices remain co-winners.
- A `READY` ballot never confirmed, unrevealed commitments and ambiguous ballots
  are excluded. Below quorum, `NO_QUORUM` has no selected option or optimal order.
- Another voter cannot operate a ballot. Changing chain/deployment/poll/voter or
  exact preimage invalidates a commitment.
- At exact phase boundaries, use the exclusive timing rules. A backwards
  transaction context must fail without overwriting the successful time floor.

The local suite covers these cases with controlled outputs. They are not live
evidence until actually executed. Save actual IDs, transactions, GenVM results,
complete receipts, confirmation and final tally reads in [DEPLOYMENT.md](DEPLOYMENT.md).
Compare the complete tracked source with the Explorer Code view, stating any
text normalization separately from raw file hashes.
