# IntentBallot — local preparation record

Prepared **2026-11-08** for the week beginning **2026-11-16**.
**NOT PUBLISHED / NOT DEPLOYED / NOT SUBMITTED.** External release requires the
user's later explicit go. No automated or scheduled submission is configured.

| Item | Current evidence |
| --- | --- |
| Contract version / receipt schema | `1.0.0` / `intentballot-v1` |
| Exact source-file SHA-256 | `1cf8cc995608262adc0414455f276c5d7dafff1ca146c15b5932e2639617a3e2` |
| Local suite | 32 passing controlled-output deterministic tests |
| Native GenVM schema or execution | NOT RUN for IntentBallot |
| Public repository / immutable tracked source | PENDING: not published |
| Network / chain / current host runner | PENDING: verify at release |
| Deployed contract address / Explorer URL | PENDING: no deployment |
| Deployment transaction / GenVM execution | PENDING: no network transaction |
| Complete tracked/deployed source comparison | PENDING: no deployed source |
| Actual semantic compilation receipt | PENDING: no live model result |
| Voter confirmation / immutable tally transactions | PENDING: no live writes |
| Portal contribution ID / status / points | PENDING: no submission or award |

The source pins the `# v0.3.0` runner
`py-genlayer:babwp9t37jw9g4j2bccgn14g6x7x9s1f7dsmh7emvz735pz4zxa0`.
It uses deterministic `datetime.now(timezone.utc)` outside model callbacks and
reads the native `message.chain_id` and `message.contract_address` for commitment
domain separation. These fields exist in the locally inspected v0.3 SDK family;
that inspection is not execution of this new source on a future Studio host.

Independent leader/validator receipt rebuilding, state transitions and Kemeny
mechanics are tested through isolated storage/model-output doubles. This does not
authenticate preferences, measure model reliability, or establish network success.
The offline helper is self-contained; the deployed source inlines its own
commitment construction and imports no repository-local runtime modules.

At release follow [STUDIO-TEST.md](STUDIO-TEST.md), publish this exact source and
tests, then replace pending entries with actual observations only. Compare the
complete Explorer Code view with tracked source. Keep this raw byte hash and any
separately normalized rendered-text comparison hash distinct.

Require GenVM SUCCESS and actual stored compilation, explicit voter confirmation
and deterministic final result. An accepted transaction containing execution error
is not successful execution, and a leader-only output is not a consensus receipt.
Keep failed or undetermined attempts honest. A historical `READY` receipt is not
an automatically cast vote or current permission to confirm after finalization.
