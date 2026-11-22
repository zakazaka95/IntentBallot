import copy
import hashlib
import importlib.util
import json
import pathlib
import unittest

from testsupport import load, UserError


A, B, C, X = ["0x" + c * 40 for c in "1234"]
SALT = "synthetic-secret-salt-for-local-tests"


class IntentBallotTests(unittest.TestCase):
    def setUp(self):
        self.m, self.c, self.rt = load()
        self.pid = self.open()
        self.start = self.rt.clock

    def open(self, options=None, voters=None, quorum=2):
        return self.c.open_poll("Technical export choice", "Choose a declared technical export implementation.",
                                json.dumps(options or ["CSV with tests", "JSON with tests", "Both formats"]),
                                json.dumps(voters or [A, B, C]), quorum, 60, 60, 60)

    def snapshot(self):
        return (dict(self.c.polls), dict(self.c.ballots), dict(self.c.voter_ballots),
                dict(self.c.attempts), self.c.poll_count, self.c.ballot_count)

    def reject(self, call, error=UserError):
        before = self.snapshot()
        with self.assertRaises(error):
            call()
        self.assertEqual(self.snapshot(), before)

    def commit(self, voter=A, statement="Prefer CSV, then JSON, then both formats.", salt=SALT, poll_id=None):
        poll_id = self.pid if poll_id is None else poll_id
        self.rt.as_sender(voter)
        poll = self.c.get_poll(poll_id)
        digest = self.m._commitment(poll["core"], poll["poll_hash"], voter, statement, salt)
        return self.c.commit_ballot(poll_id, digest), statement, salt

    def reveal(self, item):
        bid, statement, salt = item
        self.c.reveal_ballot(bid, statement, salt)
        return bid

    def ready(self, voter=A, tiers=None):
        item = self.commit(voter)
        self.rt.clock = self.start + 60
        self.reveal(item)
        self.rt.output = {"status": "RANKED", "tiers": tiers or [[0], [1], [2]]}
        self.c.assess_ballot(item[0])
        return item[0]

    def confirmed(self, rankings):
        items = []
        for voter, tiers in zip([A, B, C], rankings):
            items.append((voter, tiers, self.commit(voter)))
        self.rt.clock = self.start + 60
        for voter, tiers, item in items:
            self.rt.as_sender(voter)
            self.reveal(item)
            self.rt.output = {"status": "RANKED", "tiers": tiers}
            self.c.assess_ballot(item[0])
        self.rt.clock = self.start + 120
        for voter, tiers, item in items:
            self.rt.as_sender(voter)
            ballot = self.c.get_ballot(item[0])
            self.c.confirm_ballot(item[0], ballot["receipt_hash"])
        return [item[2][0] for item in items]

    def test_core_options_eligibility_quorum_and_exclusive_deadlines_are_fixed(self):
        poll = self.c.get_poll(self.pid)
        self.assertEqual(poll["core"]["voters"], [A, B, C])
        self.assertEqual([o["option_id"] for o in poll["core"]["options"]], [0, 1, 2])
        self.assertEqual([poll["core"][k] for k in ["commit_until", "reveal_until", "confirm_until"]],
                         [self.start + 60, self.start + 120, self.start + 180])
        self.assertEqual(poll["poll_hash"], self.m._hash(self.m._json(poll["core"])))

    def test_one_commit_per_admitted_voter_without_identity_or_weight_override(self):
        item = self.commit(A)
        self.assertEqual(self.c.get_ballot(item[0])["voter"], A)
        self.reject(lambda: self.commit(A))
        self.reject(lambda: self.commit(X))
        self.assertEqual(self.c.ballot_count, 1)

    def test_commit_is_closed_at_exact_cutoff(self):
        self.rt.clock = self.start + 60
        self.reject(lambda: self.commit())

    def test_reveal_is_not_allowed_before_commit_cutoff(self):
        item = self.commit()
        self.rt.clock += 59
        self.reject(lambda: self.reveal(item))

    def test_reveal_is_closed_at_exact_reveal_cutoff(self):
        item = self.commit()
        self.rt.clock += 120
        self.reject(lambda: self.reveal(item))

    def test_wrong_preimage_cannot_replace_or_mutate_commitment(self):
        item = self.commit()
        self.rt.clock += 60
        for statement, salt in [(item[1] + "!", item[2]), (item[1], item[2] + "!")]:
            self.reject(lambda s=statement, t=salt: self.c.reveal_ballot(item[0], s, t))
        self.reveal(item)
        self.reject(lambda: self.reveal(item))

    def test_commitment_binds_deployment_chain_poll_voter_and_exact_utf8(self):
        poll = self.c.get_poll(self.pid)
        core, poll_hash = poll["core"], poll["poll_hash"]
        baseline = self.m._commitment(core, poll_hash, A, "CSV 🦈", SALT)
        changes = []
        for key, value in [("chain_id", 1), ("contract_address", X), ("id", 1)]:
            other = dict(core)
            other[key] = value
            changes.append(self.m._commitment(other, poll_hash, A, "CSV 🦈", SALT))
        changes.extend([self.m._commitment(core, "f" * 64, A, "CSV 🦈", SALT),
                        self.m._commitment(core, poll_hash, B, "CSV 🦈", SALT),
                        self.m._commitment(core, poll_hash, A, "CSV 🦈 ", SALT),
                        self.m._commitment(core, poll_hash, A, "CSV 🦈", SALT + "x")])
        self.assertTrue(all(value != baseline for value in changes))

    def test_offline_commitment_helper_matches_contract_exactly(self):
        path = pathlib.Path(__file__).with_name("commitment.py")
        spec = importlib.util.spec_from_file_location("offline_commit", path)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        poll = self.c.get_poll(self.pid)
        actual = helper.make_commitment(poll["core"], poll["poll_hash"], A.upper().replace("0X", "0x"), "Exact\nUnicode 🦈", SALT)
        expected = self.m._commitment(poll["core"], poll["poll_hash"], A, "Exact\nUnicode 🦈", SALT)
        self.assertEqual(actual, expected)

    def test_only_committed_voter_may_reveal_assess_or_confirm(self):
        item = self.commit(A)
        self.rt.clock += 60
        self.rt.as_sender(B)
        self.reject(lambda: self.reveal(item))
        self.rt.as_sender(A)
        self.reveal(item)
        self.rt.as_sender(B)
        self.reject(lambda: self.c.assess_ballot(item[0]))
        self.rt.as_sender(A)
        self.c.assess_ballot(item[0])
        self.rt.clock = self.start + 120
        self.rt.as_sender(B)
        self.reject(lambda: self.c.confirm_ballot(item[0], self.c.get_ballot(item[0])["receipt_hash"]))

    def test_assessment_ready_never_casts_or_confirms_by_itself(self):
        bid = self.ready()
        ballot = self.c.get_ballot(bid)
        self.assertEqual(ballot["status"], "READY")
        self.assertEqual(ballot["confirmed_at"], 0)
        self.rt.clock = self.start + 180
        result = self.c.finalize_poll(self.pid)
        self.assertEqual(result["confirmed_count"], 0)
        self.assertEqual(result["status"], "NO_QUORUM")

    def test_confirmation_requires_post_reveal_window_and_exact_receipt(self):
        bid = self.ready()
        receipt_hash = self.c.get_ballot(bid)["receipt_hash"]
        self.reject(lambda: self.c.confirm_ballot(bid, receipt_hash))
        self.rt.clock = self.start + 120
        self.reject(lambda: self.c.confirm_ballot(bid, "0" * 64))
        self.c.confirm_ballot(bid, receipt_hash)
        self.assertEqual(self.c.get_ballot(bid)["status"], "CONFIRMED")
        self.reject(lambda: self.c.confirm_ballot(bid, receipt_hash))

    def test_exact_confirmation_cutoff_blocks_assessment_and_confirmation(self):
        bid = self.ready()
        self.rt.clock = self.start + 180
        self.reject(lambda: self.c.confirm_ballot(bid, self.c.get_ballot(bid)["receipt_hash"]))
        self.reject(lambda: self.c.assess_ballot(bid))

    def test_ambiguous_statement_is_terminal_and_cannot_be_rerolled(self):
        item = self.commit()
        self.rt.clock += 60
        self.reveal(item)
        self.rt.output = {"status": "AMBIGUOUS", "tiers": []}
        receipt = self.c.assess_ballot(item[0])
        self.assertEqual(receipt["decision"], "INCONCLUSIVE")
        self.assertFalse(receipt["confirmation_allowed"])
        self.rt.output = {"status": "RANKED", "tiers": [[0], [1], [2]]}
        self.reject(lambda: self.c.assess_ballot(item[0]))
        self.rt.clock = self.start + 120
        self.reject(lambda: self.c.confirm_ballot(item[0], self.c.get_ballot(item[0])["receipt_hash"]))

    def test_technical_failure_retries_exact_reveal_only_three_accepted_attempts(self):
        item = self.commit()
        self.rt.clock += 60
        self.reveal(item)
        self.rt.output = RuntimeError("temporary")
        for attempt in range(1, 4):
            receipt = self.c.assess_ballot(item[0])
            self.assertEqual(receipt["attempt"], attempt)
            self.assertEqual(receipt["decision"], "UNRESOLVED")
            self.assertEqual(self.c.get_attempt(item[0], attempt), receipt)
        self.assertEqual(self.c.get_ballot(item[0])["status"], "UNRESOLVED_FINAL")
        self.reject(lambda: self.c.assess_ballot(item[0]))
        self.reject(lambda: self.reveal(item))

    def test_every_option_must_appear_once_and_boolean_ids_are_rejected(self):
        bad = [[], [[0], [1]], [[0], [1], [1]], [[0], [1], [3]], [[False], [1], [2]],
               [[0.0], [1], [2]], [[0], [], [1, 2]], "0,1,2"]
        for tiers in bad:
            with self.subTest(tiers=tiers):
                with self.assertRaises(UserError):
                    self.m._normalize({"status": "RANKED", "tiers": tiers}, 3)
        with self.assertRaises(UserError):
            self.m._normalize({"status": "AMBIGUOUS", "tiers": [[0]]}, 3)

    def test_extra_missing_unknown_and_nonobject_model_outputs_fail_closed(self):
        item = self.commit()
        self.rt.clock += 60
        self.reveal(item)
        for raw in [{"status": "RANKED", "tiers": [[0], [1], [2]], "reason": "x"},
                    {"status": "RANKED"}, {"status": "ALLOW", "tiers": []}]:
            self.rt.output = raw
            self.assertEqual(self.c.assess_ballot(item[0])["decision"], "UNRESOLVED")
        self.assertEqual(self.c.get_ballot(item[0])["status"], "UNRESOLVED_FINAL")

    def test_independent_disagreement_is_not_an_accepted_attempt(self):
        item = self.commit()
        self.rt.clock += 60
        self.reveal(item)
        self.rt.validator_output = {"status": "RANKED", "tiers": [[1], [0], [2]]}
        self.reject(lambda: self.c.assess_ballot(item[0]), AssertionError)
        self.assertEqual(self.c.get_ballot(item[0])["attempts"], 0)
        self.assertEqual(self.rt.calls, 2)

    def test_tie_member_order_is_canonicalized_without_ranking_guess(self):
        item = self.commit()
        self.rt.clock += 60
        self.reveal(item)
        self.rt.output = {"status": "RANKED", "tiers": [[1, 0], [2]]}
        self.rt.validator_output = {"status": "RANKED", "tiers": [[0, 1], [2]]}
        self.assertEqual(self.c.assess_ballot(item[0])["tiers"], [[0, 1], [2]])

    def test_every_consequential_receipt_leaf_is_independently_bound(self):
        item = self.commit()
        self.rt.clock += 60
        self.reveal(item)
        baseline = self.m._build_receipt(self.c.get_poll(self.pid)["core"], self.c.get_poll(self.pid)["poll_hash"],
                                          self.c.get_ballot(item[0])["locked"], 1, self.rt.clock)

        def leaves(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield from leaves(child, path + (key,))
            elif isinstance(value, list):
                for key, child in enumerate(value):
                    yield from leaves(child, path + (key,))
            else:
                yield path, value

        for path, value in leaves(baseline):
            def mutate(receipt, p=path, v=value):
                cursor = receipt
                for key in p[:-1]:
                    cursor = cursor[key]
                cursor[p[-1]] = not v if isinstance(v, bool) else v + 1 if isinstance(v, int) else str(v) + "!"
                return receipt
            self.rt.mutate = mutate
            with self.subTest(path=path):
                self.reject(lambda: self.c.assess_ballot(item[0]), AssertionError)
        self.rt.mutate = lambda receipt: dict(receipt, unexpected="unbound")
        self.reject(lambda: self.c.assess_ballot(item[0]), AssertionError)

    def test_kemeny_unanimous_order_has_one_deterministic_winner(self):
        ids = self.confirmed([[[0], [1], [2]]] * 3)
        calls = self.rt.calls
        self.rt.clock = self.start + 180
        self.rt.as_sender(X)
        result = self.c.finalize_poll(self.pid)
        self.assertEqual(result["status"], "DECIDED")
        self.assertEqual(result["selected_option"], 0)
        self.assertEqual(result["optimal_score"], 9)
        self.assertEqual(result["optimal_orders"], [[0, 1, 2]])
        self.assertEqual([b["ballot_id"] for b in result["confirmed_ballots"]], ids)
        self.assertEqual(result["pairwise_matrix"], [[0, 3, 3], [0, 0, 3], [0, 0, 0]])
        self.assertEqual(calls, self.rt.calls)

    def test_condorcet_cycle_returns_all_co_winners_without_arbitrary_tiebreak(self):
        self.confirmed([[[0], [1], [2]], [[1], [2], [0]], [[2], [0], [1]]])
        self.rt.clock = self.start + 180
        result = self.c.finalize_poll(self.pid)
        self.assertEqual(result["status"], "TIED")
        self.assertEqual(result["co_winner_ids"], [0, 1, 2])
        self.assertEqual(result["selected_option"], -1)
        self.assertEqual(result["optimal_score"], 5)
        self.assertEqual(result["optimal_orders"], [[0, 1, 2], [1, 2, 0], [2, 0, 1]])

    def test_tied_ballot_options_create_no_strict_preference_between_them(self):
        self.confirmed([[[0, 1], [2]], [[1, 0], [2]]])
        self.rt.clock = self.start + 180
        result = self.c.finalize_poll(self.pid)
        self.assertEqual(result["pairwise_matrix"], [[0, 0, 2], [0, 0, 2], [0, 0, 0]])
        self.assertEqual(result["co_winner_ids"], [0, 1])

    def test_complete_indifference_meets_confirmation_quorum_but_never_selects_id_zero(self):
        self.confirmed([[[0, 1, 2]], [[2, 1, 0]]])
        self.rt.clock = self.start + 180
        result = self.c.finalize_poll(self.pid)
        self.assertEqual(result["optimal_score"], 0)
        self.assertEqual(len(result["optimal_orders"]), 6)
        self.assertEqual(result["co_winner_ids"], [0, 1, 2])
        self.assertEqual(result["status"], "TIED")

    def test_confirmed_count_below_quorum_returns_no_outcome(self):
        self.confirmed([[[0], [1], [2]]])
        self.rt.clock = self.start + 180
        result = self.c.finalize_poll(self.pid)
        self.assertEqual(result["status"], "NO_QUORUM")
        self.assertEqual(result["confirmed_count"], 1)
        self.assertEqual(result["optimal_orders"], [])
        self.assertEqual(result["co_winner_ids"], [])

    def test_finalization_cannot_run_early_or_twice(self):
        self.reject(lambda: self.c.finalize_poll(self.pid))
        self.rt.clock = self.start + 180
        result = self.c.finalize_poll(self.pid)
        self.reject(lambda: self.c.finalize_poll(self.pid))
        self.reject(lambda: self.commit(A))
        self.assertEqual(self.c.get_poll(self.pid)["result"], result)

    def test_final_result_hash_binds_complete_deterministic_tally(self):
        self.confirmed([[[0], [1], [2]], [[0], [2], [1]]])
        self.rt.clock = self.start + 180
        result = self.c.finalize_poll(self.pid)
        original = dict(result)
        digest = original.pop("result_hash")
        self.assertEqual(digest, self.m._hash(self.m._json(original)))
        for field in ["pairwise_matrix", "co_winner_ids", "confirmed_ballots", "poll_hash", "finalized_at"]:
            changed = copy.deepcopy(original)
            changed[field] = "tampered"
            self.assertNotEqual(digest, self.m._hash(self.m._json(changed)))

    def test_five_options_are_bounded_at_120_optimal_orders(self):
        core = {"id": 0, "options": [{"option_id": i, "text": str(i)} for i in range(5)], "min_confirmed": 1}
        result = self.m._tally(core, "f" * 64, [{"tiers": [[0, 1, 2, 3, 4]]}], self.rt.clock)
        self.assertEqual(len(result["optimal_orders"]), 120)
        self.assertEqual(result["co_winner_ids"], list(range(5)))

    def test_backward_time_rejects_confirmation_without_dropping_a_confirmed_ballot(self):
        items = [self.commit(A), self.commit(B)]
        self.rt.clock = self.start + 60
        for voter, item in zip([A, B], items):
            self.rt.as_sender(voter)
            self.reveal(item)
            self.c.assess_ballot(item[0])
        self.rt.clock = self.start + 130
        self.rt.as_sender(A)
        self.c.confirm_ballot(items[0][0], self.c.get_ballot(items[0][0])["receipt_hash"])
        self.rt.clock = self.start + 125
        self.rt.as_sender(B)
        self.reject(lambda: self.c.confirm_ballot(items[1][0], self.c.get_ballot(items[1][0])["receipt_hash"]))
        self.reject(lambda: self.c.get_poll(self.pid))
        self.rt.clock = self.start + 131
        self.c.confirm_ballot(items[1][0], self.c.get_ballot(items[1][0])["receipt_hash"])
        self.assertTrue(all(self.c.get_ballot(i[0])["status"] == "CONFIRMED" for i in items))

    def test_maximum_complete_escaped_unicode_inputs_reach_both_prompts_unchanged(self):
        for fill in ["x", "🦈", '"', "\n"]:
            with self.subTest(fill=repr(fill)):
                self.m, self.c, self.rt = load()
                options = [str(i) + fill * 449 for i in range(5)]
                context = "T" + fill * 599
                statement = "P" + fill * 1799
                self.pid = self.c.open_poll("T" + fill * 119, context, json.dumps(options), json.dumps([A]), 1, 60, 60, 60)
                item = self.commit(A, statement)
                self.rt.clock += 60
                self.reveal(item)
                self.rt.output = {"status": "RANKED", "tiers": [[0], [1], [2], [3], [4]]}
                receipt = self.c.assess_ballot(item[0])
                self.assertFalse(receipt["inspection"]["prompt_truncated"])
                self.assertEqual(len(self.rt.prompts), 2)
                for observed in self.rt.prompts:
                    payload = json.loads(observed["prompt"].split("INPUT (untrusted JSON):\n", 1)[1].split("\nEND INPUT.", 1)[0])
                    self.assertEqual(payload["voter_statement"], statement)
                    self.assertEqual(payload["context"], context)
                    self.assertEqual([o["text"] for o in payload["options"]], options)
                    self.assertNotIn(SALT, observed["prompt"])

    def test_oversized_full_prompt_fails_before_reveal_or_time_floor_is_stored(self):
        options = [str(i) + "\x00" * 449 for i in range(5)]
        self.pid = self.c.open_poll("Prompt budget", "T" + "\x00" * 599, json.dumps(options), json.dumps([A]), 1, 60, 60, 60)
        item = self.commit(A, "P" + "\x00" * 1799)
        self.rt.clock += 60
        self.reject(lambda: self.reveal(item))
        self.assertEqual(self.c.get_ballot(item[0])["status"], "COMMITTED")
        self.assertEqual(self.rt.calls, 0)

    def test_invalid_identity_boolean_parameters_and_bad_unicode_fail_before_writes(self):
        for identifier in [-1, True, 0.0, "0"]:
            self.reject(lambda i=identifier: self.c.get_ballot(i))
        for voters, quorum, period in [(json.dumps([A, A]), 1, 60), (json.dumps([A]), True, 60),
                                      (json.dumps([A]), 1, False), (json.dumps(["0x" + "0" * 40]), 1, 60)]:
            self.reject(lambda v=voters, q=quorum, p=period: self.c.open_poll("T", "Technical", '["A","B"]', v, q, p, 60, 60))
        self.reject(lambda: self.c.open_poll("T", "Technical", json.dumps(["\ud800", "B"]), json.dumps([A]), 1, 60, 60, 60))

    def test_clock_is_transaction_context_captured_outside_both_model_callbacks(self):
        self.ready()
        self.assertGreater(self.rt.clock_reads, 0)
        with self.assertRaisesRegex(AssertionError, "clock may not be read"):
            self.rt.run(lambda: self.m._now(), lambda result: True)


if __name__ == "__main__":
    unittest.main()
