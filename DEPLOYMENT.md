# IntentBallot — release record

Published **November 22, 2026**. Native source-schema and local controlled-output
checks passed. The deployment's complete source and initial persisted stats were
retrieved successfully. The semantic compilation, explicit voter confirmation and
immutable final tally below have stored results. All seven network transactions
were successful and `FINALIZED` by **09:42:35 UTC**. Portal status is recorded
separately and no award is claimed.

| Item | Current evidence |
| --- | --- |
| Contract version / receipt schema | `1.0.0` / `intentballot-v1` |
| Exact released source-file SHA-256 | `472e7be31ac2307d88bb6e168117336e4ceda4f03829568c32e0e2cdb317bd5e` |
| Public repository | https://github.com/zakazaka95/IntentBallot |
| Immutable tracked source | https://github.com/zakazaka95/IntentBallot/blob/8543d41b97d68c4ee2080cce5b06b45d282870fb/IntentBallot.py |
| Local suite on released source | 32 passing controlled-output tests |
| Native source-schema check | Passed with the pinned v0.4.0 runner during this release |
| Network / chain ID / RPC | Studio Devnet / `61997` / `https://studio-dev.genlayer.com/api` |
| Contract | [0x75F4B43af9462cd711421F8Bc96a39C2acBfE023](https://explorer-studio-dev.genlayer.com/address/0x75F4B43af9462cd711421F8Bc96a39C2acBfE023) |
| Deployment transaction | [0x65cf4ffe50dbd5da79469bb7cef6eeadd3f8123d164fb09f082757e17f312d17](https://explorer-studio-dev.genlayer.com/tx/0x65cf4ffe50dbd5da79469bb7cef6eeadd3f8123d164fb09f082757e17f312d17) |
| Full tracked/deployed source comparison | Complete source matches after CRLF-to-LF conversion and outer-whitespace trim; normalized SHA-256 `b87e9762136ba93f8965d8c5f0d35e0063c8c7fbe326a86efbdefe04c89a9455` |
| Initial persisted readback | `get_stats` retrieved successfully after deployment |
| First application write | [Synthetic poll opened successfully](https://explorer-studio-dev.genlayer.com/tx/0x8c8f589e973e6c5e8ea6157c8a8dd84479e87fa8d97118015651c7e265338187); persisted chain, deployment and transaction-clock context checked |
| Voter commitment | [Exact statement committed successfully](https://explorer-studio-dev.genlayer.com/tx/0xbe337d330a33a49693b867af4de32628134e8a1c1e235a79afe8752cd9616b17) |
| Live semantic compilation | [Assessment succeeded](https://explorer-studio-dev.genlayer.com/tx/0xc4c2cfaeef8666f5f09ab8be550c273801d34e7a056b702fcbf0d1e7401a678b), storing `READY` with exact tiers `[[0], [1], [2]]` |
| Explicit voter confirmation | [Voter confirmed the exact receipt](https://explorer-studio-dev.genlayer.com/tx/0xb10a924382f23234670b2ba87d3b93a6bcbfb17206052f6abe3f285516499548); stored ballot status `CONFIRMED` |
| Confirmed receipt SHA-256 | `b6ad72e7588c864dab7c13439ec28b248c0a13b1e94c341ccdd24c4d8c070f20` |
| Immutable final tally | [Finalization succeeded](https://explorer-studio-dev.genlayer.com/tx/0x8ff3a3a4876f0b89faa74be7c5f5c2ed1483c9d86c277846ab4426c3e26a51db) after the fixed confirmation deadline; `DECIDED`, selected option `0` |
| Deterministic tally readback | Score `3`; sole optimal order `[0, 1, 2]`; full pairwise matrix `[[0, 1, 1], [0, 0, 1], [0, 0, 0]]` |
| Immutable final result SHA-256 | `6bc535e52c438221efb677ce5092b24130240db725568a96a4410792ee6a0888` |
| Transaction finality | All seven synthetic network transactions successful and `FINALIZED`, checked November 22 at 09:42:35 UTC |
| Portal contribution ID / status | Not submitted yet |

## Minimal runner migration

The archived November 8 preparation pinned the v0.3.0 runner. The current host
rejected that runner during the native source-schema check. Only the first two
source header lines changed for compatibility:

```text
# v0.4.0
# { "Depends": "py-genlayer:kzybg95x1gn21dw72m7hyg0maaap04n4nx55j9yt6fkdqxtz6bz0" }
```

The contract body, API and consensus/state logic are unchanged. The released
source passed native source-schema validation and the complete local suite.
The archived prepared source had raw SHA-256 `1cf8cc995608262adc0414455f276c5d7dafff1ca146c15b5932e2639617a3e2`; it is historical and is
not the source identified by the current release hash above.

Raw file-byte hashes are distinct from the separately normalized complete
deployed-source comparison above. The immutable GitHub file was independently
retrieved and matches the exact released raw-file hash. Schema validation and
initial stats alone do not prove a successful application write. The poll-open
write above additionally persisted and checked the chain, deployment and clock
context. The separate semantic assessment stored the tiers above, and only the
voter's explicit confirmation moved that exact receipt into `CONFIRMED` state.
The final tally independently computes the matrix, score and optimal order above;
the model did not choose a winner. Transaction finality was separately checked
for the full seven-transaction sequence.

## Reproduce and interpret the evidence

The public [complete demonstration](evidence/demo-result.json),
[transaction list](evidence/transactions.json), [complete source comparison](evidence/source-verification.json)
and [native schema result](evidence/native-schema.json) preserve the exact observed
compilation, explicit confirmation, deterministic tally and transaction finality.

Follow [STUDIO-TEST.md](STUDIO-TEST.md) using synthetic or public material and
0 GEN transaction value. Require GenVM SUCCESS and persisted relevant state, not
consensus acceptance alone. The controlled-output suite and actual synthetic
network walkthrough are separate evidence; neither is a model-accuracy benchmark.
Keep failed or undetermined attempts in the release record.

The demonstrated poll ID is `0` and ballot ID is `0`. The complete evidence
identifies the accepted compilation receipt, exact voter-confirmation transaction
and immutable final tally. A `READY` receipt
is not a cast vote: explicit confirmation is required. Eligible wallets do not
prove unique humans. This does not execute governance or authenticate preferences.
