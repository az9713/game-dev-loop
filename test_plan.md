# test_plan.md — Realm

## Headline test: self-play harness (one command)
```
python kingdom.py --selfplay 10 30
```
Plays 10 reigns (seeds 0–9) of up to 30 turns each with a random decision-maker,
asserts `check_invariants` after every turn, and prints per-seed status plus a
final **PASS / FAIL**. Exits 0 on PASS, 1 on FAIL.

Exit-condition form (10 in a row, different seeds): the harness *is* 10 distinct
seeds; PASS means all 10 reigns completed with zero crashes / zero invariant
violations.

## Acceptance tests (one command)
```
python test_kingdom.py
```
Plain-stdlib asserts, no framework. Each `test_*` maps to a spec acceptance
criterion (A1–A7) and prints `Ax ok: …`; the runner prints **PASS / FAIL** and
exits non-zero on any failure.

| Test | Spec | Exercises |
|------|------|-----------|
| `test_selfplay_10_seeds`      | A1 | full reigns, invariants |
| `test_treasury_integer`       | A2 | treasury type + debt reachable |
| `test_succession_resolves`    | A3 | one heir or defined crisis |
| `test_no_dead_choices`        | A4 | every event/decree option moves state |
| `test_war_outcomes`           | A5 | wins and losses both occur |
| `test_diplomacy_moves_relations` | A6 | gifts raise relation |
| `test_stats_bounded`          | A7 | stats ∈ [0,100] over 50 turns |
| `test_no_back_to_back_events` | A8 | no immediate event repeats |
| `test_war_cooldown`           | A9 | cooldown blocks re-declaration |
| `test_debt_penalty_scales`    | A10 | deeper debt costs more stability |
| `test_prestige_score`         | A11 | score grows over a reign |
| `test_ruler_can_marry`        | A12 | unmarried ruler can wed |
| `test_cannot_marry_off_last_heir` | A13 | last heir is protected |
| `test_young_heir_not_doomed`  | A14 | marriage keeps most lines alive |
| `test_stability_decays_from_peak` | A15 | peak stability needs upkeep |

## How each system is exercised
- **Treasury / economy** — A2 (20 seeds, asserts integer + debt) and every
  harness turn.
- **Succession** — A3 force-kills the ruler from 30 randomly-advanced states.
- **War** — A5 counts victories and defeats over 40 seeds.
- **Diplomacy** — A6 fires the gifts decree and checks the relation rose.
- **Events** — A4 runs all 6 templates' options against 8 healthy states.
- **Invariants/bounds** — A1 + A7, plus `check_invariants` after each turn.

## How to read harness output as a designer
Beyond PASS/FAIL, scan the per-seed line for: reigns ending early (too lethal),
stats stuck at a cap (dead variable), or every seed looking identical (shallow
decisions). Findings go to `ux_review.md` with a mechanical fix.

## Manual smoke test
```
python kingdom.py            # random seed, play interactively
python kingdom.py --seed 3   # fixed seed
```
