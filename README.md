# IntentBallot

IntentBallot compiles a voter's own complete preference statement into ordered
tiers, requires that voter to confirm the exact accepted interpretation, then
computes a bounded Kemeny result without letting a model choose the winner.

**Prepared locally on November 8, 2026 for the week beginning November 16.
Not published, deployed or submitted. External release waits for the user's go.**

## Why the state matters

Natural-language priorities can express qualifications, ties and exceptions that
an option number cannot. Interpreting those priorities is semantic. Eligibility,
deadlines, one ballot per voter, confirmation, aggregation and finality should be
deterministic. A model interpretation must not silently cast somebody's ballot.

An owner freezes two to five complete technical options, a technical/team-choice
context, up to six eligible addresses, a confirmation quorum and three deadlines.
Each eligible voter commits the exact statement before any reveal, reveals that
statement in the next window, and requests an independent semantic compilation.
Only an explicit voter confirmation of the exact complete receipt can count.

The contract does not infer opinions from social behavior or identity, conduct
public political voting, execute governance, transfer funds or perform external
actions. It is a standalone primitive for declared technical/team preferences.
Integrations must pin the exact contract, chain, poll ID and poll hash.

## State and exclusive time windows

```text
Poll: OPEN -> DECIDED / TIED / NO_QUORUM (permissionless finalization, once)

Ballot: COMMITTED -> REVEALED -> READY -> CONFIRMED
                              -> INCONCLUSIVE (terminal, uncounted)
                              -> RETRYABLE -> UNRESOLVED_FINAL (3 accepted attempts)

Commit:   created_at <= now < commit_until
Reveal:   commit_until <= now < reveal_until
Assess:   own revealed ballot, now < confirm_until
Confirm:  reveal_until <= now < confirm_until
Finalize: confirm_until <= now
```

The owner cannot alter options, eligible voters, quorum, deadlines or another
voter's statement, and has no reset, cancellation or result-override method.
An eligible address commits once; revealing twice or replacing a failed semantic
interpretation with a different statement is forbidden. An `INCONCLUSIVE` result
cannot be rerolled. Only technical model/schema failures have bounded retries.
Network disagreement is not an accepted contract attempt or a stored certificate.

Each successful poll write advances a persisted transaction-time floor. A context
older than that floor fails before any state is stored. Mutations are staged in
decoded records and saved only after checks and consensus succeed. `get_poll`
fails closed on a backward clock while the poll is open; finalized history remains
readable. Ballot getters expose stored history, not current confirmation permission.

## Commitments and privacy boundary

The SHA-256 commitment binds canonical UTF-8 JSON containing the domain string,
chain ID, deployed contract address, poll ID, complete poll hash, voter address,
exact statement and salt. Whitespace is not stripped. A commitment from another
poll, voter, deployment or chain cannot be substituted.

Use [commitment.py](commitment.py) offline. Its `generate_salt()` uses 32 random
bytes encoded as 64 hexadecimal characters. The onchain 16-character minimum is
only a length check and does **not** prove entropy. Keep the salt and preimage
private until reveal, and save them securely: a lost salt cannot be recovered.
Do not commit with the fixed synthetic salt used in local tests.

This is not anonymous or permanently secret voting. Observers can see eligible
wallets, commitments and timing. The exact statement and salt become public in
the reveal calldata and stored revealed ballot. There is no forced disclosure.
Selective non-reveal and non-confirmation can change quorum and the result.
Eligible addresses are not proof of distinct humans; roster admission is a trust
boundary. The owner can choose a quorum below the roster size, and confirmed
complete-indifference ballots count toward that frozen quorum.

## Independent compilation and complete receipt binding

Each model execution receives the whole technical context, every complete option
and the complete voter statement. Options and statement are untrusted data; the
task asks for only expressed preferences, not invented ranks or tool instructions.
Insufficient, contradictory or nontechnical input should produce `AMBIGUOUS`.
Models can still make mistakes or disagree. The voter must inspect the exact
compiled tiers and can withhold confirmation if they do not reflect their intent.

Strict output is `RANKED` with nonempty ordered tiers containing every option ID
exactly once, or `AMBIGUOUS` with no tiers. Boolean/float IDs, duplicate or missing
options, empty tiers, unknown statuses and extra fields fail closed. Option order
within a tie is normalized numerically, without creating a preference.

Each validator independently repeats compilation, rebuilds the full receipt and
requires exact canonical JSON equality. The receipt binds the full poll and
revealed ballot, commitment, voter, statement/salt, hashes, timestamps, attempt,
tiers, decision, inspection counts/hash/truncation flag and confirmation effect.
No unvalidated model-written narrative is stored. A matching final label alone
is insufficient. Confirmation requires the exact receipt and full matching input.

There is no prompt slicing. Both the fully escaped character budget and the UTF-8
byte budget are checked before reveal storage and again before assessment.
Individual field bounds do not override combined prompt limits. Accepted maximum
ASCII, astral Unicode and quote/newline inputs are covered by tests; an aggregate
whose escaping exceeds the budget is rejected without storing a partial reveal.
Salt and address metadata are bound in the receipt but omitted from the model
prompt because they do not express preferences.

## Deterministic Kemeny aggregation

Only `CONFIRMED` ballots count, each with unit weight. For every option pair `a,b`,
the matrix records how many confirmed ballots strictly prefer `a` to `b`. A tie
contributes neither direction. The contract enumerates all at most `5! = 120`
permutations and sums the matrix support for every earlier-to-later pair.

It retains **all** maximum-score orders and the union of their first options.
One co-winner produces `DECIDED`; multiple co-winners produce `TIED` and no selected
option. A Condorcet cycle or complete indifference cannot be resolved by silently
choosing the smallest ID, the owner or a model's favorite. Below the frozen
confirmation quorum, `NO_QUORUM` has no selected option or optimal orders.

The immutable result stores the full matrix, confirmed ballot IDs/voters/receipts,
all optimal orders, score, co-winners, quorum, poll hash and a canonical result hash.
Finalization performs no model call. Old `READY` records can remain readable after
the deadline, but they do not count and cannot be confirmed into a final poll.

## API and bounds

```text
open_poll(title, context, options_json, voters_json, min_confirmed,
          commit_seconds, reveal_seconds, confirm_seconds) -> poll_id
commit_ballot(poll_id, commitment) -> ballot_id
reveal_ballot(ballot_id, statement, salt)
assess_ballot(ballot_id) -> complete_receipt
confirm_ballot(ballot_id, expected_receipt_hash)
finalize_poll(poll_id) -> complete_deterministic_result
get_poll(poll_id), get_ballot(ballot_id), get_attempt(ballot_id, attempt), get_stats()
```

| Bound | Value |
| --- | --- |
| Options / eligible voters | 2–5 / 1–6 |
| Option / context / statement characters | 450 / 600 / 1,800 |
| Each phase duration | 60–86,400 seconds |
| Salt length | 16–128 characters; use random 32-byte salt |
| Complete prompt | 20,000 characters and 30,000 UTF-8 bytes |
| Accepted technical attempts | 3 per ballot |

Run the self-contained controlled-output suite:

```text
python -m unittest -v test_intentballot
```

**32 local tests pass.** They exercise lifecycle/authority/deadline guards, domain
commitments and helper parity, explicit confirmation, complete receipt tampering,
independent disagreement, ambiguity/retry finality, full prompt coverage, strict
ranking schemas, Kemeny cycles/ties/quorum, clock regression and final result binding.
These are not GenVM execution or model-accuracy benchmarks. Network schema,
deployment, live model interpretation and actual voting transactions remain pending.
See [STUDIO-TEST.md](STUDIO-TEST.md), [DEPLOYMENT.md](DEPLOYMENT.md) and
[SUBMISSION-PACK.md](SUBMISSION-PACK.md).

Kemeny aggregation and commit/reveal are established concepts. This package's scope
is the combined voter-confirmed semantic compiler and deterministic bounded tally.
It differs from procurement qualification or bilateral term-alignment contracts;
it makes no claim to invent preference voting, privacy or fair participation.
