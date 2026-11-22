# IntentBallot Portal package

Published November 22, 2026. Category: Builder → Intelligent Contracts.
See [DEPLOYMENT.md](DEPLOYMENT.md) for the current verified release evidence.

## Title

IntentBallot: Voter-Confirmed Preference Compilation and Deterministic Kemeny Tally

## Notes / Description

IntentBallot turns a voter's own technical preference statement into a ballot they must explicitly confirm. An owner freezes complete options, eligible wallets, quorum and commit/reveal/confirmation deadlines. A salted commitment binds chain, deployment, poll, voter and exact text. Independent GenLayer validators compile complete ordered tiers and rebuild the entire canonical receipt. Ambiguity cannot count; technical retries are bounded. Only voter confirmation of the exact receipt enters the tally. Contract code then computes the full pairwise matrix and all optimal Kemeny orders over at most five options, preserving every co-winner instead of inventing a tiebreak. Finalization is permissionless and irreversible. It holds no funds, infers no opinions from behavior and executes no governance. Eligibility is not unique humanity; selective non-participation can affect outcomes. Includes adversarial tests, an offline commitment helper and a Studio walkthrough.

## Evidence

1. GitHub Repository — https://github.com/zakazaka95/IntentBallot
2. GitHub File — https://github.com/zakazaka95/IntentBallot/blob/8543d41b97d68c4ee2080cce5b06b45d282870fb/IntentBallot.py
3. GenLayer Explorer Contract — https://explorer-studio-dev.genlayer.com/address/0x75F4B43af9462cd711421F8Bc96a39C2acBfE023
4. Other — https://explorer-studio-dev.genlayer.com/tx/0xc4c2cfaeef8666f5f09ab8be550c273801d34e7a056b702fcbf0d1e7401a678b

The compilation transaction is linked above. Its exact receipt was explicitly
confirmed by the voter; the final tally and full sequence are recorded separately
in DEPLOYMENT.md as observed.
The [complete public demonstration](evidence/demo-result.json) includes the exact
confirmed receipt, immutable tally and all successful finalized transactions.

The description has 972 characters. All 32 controlled-output unit tests and the
current native source-schema check pass. Deployment, live-model and Portal
observations are separate evidence in [DEPLOYMENT.md](DEPLOYMENT.md); neither a
schema check nor a synthetic walkthrough is a model-accuracy benchmark.
