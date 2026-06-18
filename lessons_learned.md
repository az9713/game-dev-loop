# lessons_learned.md — Realm

The compound step. One entry per cycle: work done / evaluation / gaps / next
instruction / reusable pattern.

---

## Cycle 1 — scaffold the whole game + executable acceptance criteria
**Work done.** Built the entire game in one zero-dependency module `kingdom.py`
(state model, seeded RNG, 5-phase turn engine, treasury/succession/war/diplomacy/
event systems, interactive CLI, and a one-command self-play harness). Wrote
`test_kingdom.py` with 7 acceptance tests mapping 1:1 to spec criteria A1–A7.
Authored all six memory artifacts + README.

**Evaluation.** First harness run passed 10 seeds × 30 turns with zero invariant
violations. Acceptance tests went 6/7, then 7/7 after fixing the test (not the
game). Firing-count probe over 10 seeds: successions 3, war wins 7 / losses 6,
births 47, diplomacy moves confirmed — every system has a visible consequence.

**Gaps found.**
- Test fairness bug: "no dead choices" fed options into collapsed end-states
  (stats at the floor) where a "lose population" choice can't move a realm
  already at zero — a false positive. Fixed by testing options against *healthy*
  states only (the correct meaning of "no dead choice exists by design").
- Game bug: prosperity auto-pinned at 100 (drifted +1 forever when stable).
  Fixed by making prosperity chase stability instead.
- Cosmetic bug: a name syllable `" var"` had a leading space → "Mor var". Fixed.
- Polish (logged, non-blocking): event repetition (c1-a), re-declarable war
  (c1-b), no explicit prestige score (c1-c).

**Exit-condition status after cycle 1.**
- ✅ Harness: 10 seeds × 30 turns, zero crashes / zero invariant violations.
- ✅ Every spec acceptance test (A1–A7) passes.
- ✅ Every system has a verified visible consequence (ux_review) — no dead choices.
- ⚠️ tasks.md has open items, but they are designer-review polish (c1-a/b/c),
  not gaps in the exit criteria. The loop rule says stop only when *no new gap*
  remains; these are real, so the loop continues into cycle 2.
- ✅ README explains run + play.

**Next instruction.** Cycle 2: implement c1-a (no back-to-back repeated event)
with its done-test, then re-run harness + acceptance tests, then re-review.

**Reusable pattern → PROJECT_RULES.md.** *Make the acceptance criteria
executable as tests the simulation runs on itself* — especially "no dead
choices" as: clone a **healthy** state, apply each option, assert the state
changed. And: *when a self-check fails, first ask whether the check is fair*
(here the floor/cap absorbed the delta) before changing the system under test.

---

## Cycle 2 — c1-a: no back-to-back events
**Work.** Added `Game.last_event`; event draw excludes the previous template
(falls back to full list if only one remained). Test A8.
**Eval.** 450 events across 15 seeds, zero back-to-back repeats. Harness PASS.
**Gap.** None new from this change.
**Next.** Cycle 3: war cooldown (c1-b).

## Cycle 3 — c1-b: war cooldown
**Work.** Added `Neighbor.cooldown`; set to 2 when any war ends, decremented in
`phase_economy`; gates both player war-declaration and AI invasion. Test A9.
**Eval.** A9 passes; harness PASS; war wins/losses still both occur (A5).
**Gap.** None new.
**Next.** Cycle 4: scale the (too weak) debt penalty surfaced in the harness.

## Cycle 4 — c1-d debt scaling + c1-c prestige score
**Work.** Debt penalty now `min(10, 3 + owed//1000)` instead of flat −3.
Added `prestige_score()` shown at game over / abdication. Tests A10, A11.
**Eval.** All 11 acceptance tests pass. Harness PASS at 50 seeds × 30 and
25 × 40. Deep-debt seeds now collapse to low stability (27/19) instead of
shrugging it off. Natural game-over (dynasty extinct) reachable: 166/400 seeds
over 60 turns — the crisis path is live, not dead code.
**Gap.** None new — remaining ideas are content expansion (more events), YAGNI.
**Next.** Cycle 5: final review.

## Cycle 5 — final review + hardening: EXIT
**Advisor caught a coverage gap before exit:** invariants had only been checked
at 30/40 turns, where succession is *rare*; the succession/extinction path (the
most complex code) had never run under `check_invariants` at the rate it occurs.
Also the game-over invariant branch was near-vacuous. Fixes:
- Strengthened `check_invariants` game-over branch into a real contract:
  `over ⟹ over_reason set ∧ ruler dead ∧ no heir`.
- Ran the succession-heavy regime through invariants: **100 seeds × 60 turns,
  PASS** — many seeds hit GAME OVER and the per-turn invariant held throughout.
  This validates the subtle mid-`phase_aging` cascade (an heir who ascends while
  the captured loop list is still iterating never lands `ruler.alive=False`
  with `over=False`).

All exit conditions satisfied:
- ✅ Harness: 100 seeds × 60 turns + 50 × 30 + 25 × 40, zero crashes / zero
  invariant violations (exit asks for 10 in a row; we run 100).
- ✅ All 11 spec acceptance tests (A1–A11) pass.
- ✅ Every system (treasury, succession, war, diplomacy, events) has a verified
  visible consequence; no dead choices (167 option-checks).
- ✅ tasks.md backlog empty; review finds no new gap.
- ✅ README explains how to run and play.

**Stopping the loop.** The build is complete against the spec. New work from
here would be content/feature expansion, which the spec scopes out until a real
need appears.

**Reusable patterns promoted:** test fairness before system change; one-seed RNG;
clamp-on-write/assert-on-read; single `choose()` UI seam. (See PROJECT_RULES.md.)

---

## Cycles 6–7 — loop reopened after PLAYING A FULL REIGN
**Trigger.** Per-turn tests all passed, but actually playing a complete 72-year
reign (not just unit-testing turns) exposed two macro gaps the single-turn
checks structurally cannot see. Honest correction: the cycle-5 "exit" was
premature on the spec's own "nothing meaningful to decide" axis — because no one
had played a whole reign as a *designer* yet. **Lesson: a per-turn invariant
suite is necessary but not sufficient; you must also play the whole arc.**

**Cycle 6 — dynastic dead-end (c6-b).** A young heir who ascends childless was
unrecoverable: no ruler-marriage existed and child-marriage only *removed* heirs.
Added a "Take a spouse" decree (ruler age ≥16, unmarried), lowered the ascension
spouse-grant threshold 18→16, and gated the alliance "Wed" decree to ≥2 heirs so
the last heir can never be married away. Tests A12/A13/A14. End-to-end proof: a
marriage-aware policy took seed 7's dynasty unbroken through a 200-year horizon
(14 monarchs) where the old policy died out at year 72.

**Cycle 7 — late-game stasis (c6-a).** A peaceful realm pinned at 100/100 and
every turn became identical. Made stability above 50 decay −1/turn and cut "hold
court" to +1, so sustaining a great realm now costs active spending (feasts,
easing revolts); also rivals gain strength over time so a static army invites
trouble. Test A15; the harness confirms random play no longer sits at 100.
*Residual (logged, not fixed):* gold/population grow unbounded past ~100 turns —
outside the spec's ~30-turn envelope, so YAGNI.

**Re-verification.** All 15 acceptance tests (A1–A15) pass; deep harness
100 seeds × 60 turns still PASS (zero crashes / invariant violations).

**Reusable pattern → PROJECT_RULES.md.** *Play the whole arc, not just the
turn.* Unit/invariant tests catch local breakage; only a full playthrough
(self-play to natural end) surfaces emergent dead-ends and "solved-game" stasis.
Make "play one complete reign and review it as a designer" a required gate before
declaring a simulation done.
