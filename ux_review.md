# ux_review.md — Realm

What playing it actually feels like. Every entry names a concrete mechanical
fix, not a vibe. Evidence comes from `python kingdom.py --selfplay` and verbose
single-seed runs.

## System consequence verification (exit condition: no dead choices)
Measured across 10–40 seeds (see `test_kingdom.py` A4/A5/A6 and the firing-count
probe in `lessons_learned.md`):
- **Economy** — treasury swings visibly each turn; debt is reachable and bites
  stability. ✅ visible.
- **Succession** — observed in 3/10 base seeds; an heir ascends with −10
  stability / −5 legitimacy. ✅ visible (rare but real; A3 forces & verifies it).
- **War** — 63 wins / 14 losses over 40 seeds; plunder, troop losses, indemnity,
  occasional battlefield death of the ruler. ✅ visible.
- **Diplomacy** — gifts +25, marriage +40, refusals/war lower relation; very
  hostile + stronger neighbours invade. ✅ visible (A6).
- **Events** — all 6 templates' options move state (A4, 104 event-option checks).
  ✅ visible. No dead choices remain.

## Cycle 1 observations & fixes

### [FIXED c1] Name generator emitted a leading space ("Mor var")
A syllable in `_MALE` was `" var"`. → removed the space. Mechanical, done.

### [FIXED c1] Prosperity auto-pinned at 100 mid-reign (6/10 seeds)
Prosperity drifted +1 every turn while stable, so it always maxed and stopped
being a meaningful variable. → prosperity now *chases stability* (max +2/turn up,
−1/turn down toward the stability value), so 100 prosperity demands sustained
~100 stability. Post-fix spread: prosperity ranged 44–100 across seeds.

### [FIXED c2] Event repetition within a short window
In one 8-turn sample, "peasants riot" fired 3×. → the event draw now excludes
the previous turn's template (`EVENTS` minus last factory). Verified by A8 (zero
back-to-back repeats over 450 events).

### [FIXED c3] You could re-declare war on the same neighbour every turn
Victory drops relation by 20, keeping the target "hostile", so the bot warred
the same neighbour repeatedly. → added a 2-turn `Neighbor.cooldown` after any
war ends; gates both player declaration and AI invasion. Verified by A9.

### [FIXED c4] Debt was nearly toothless
5/10 seeds ended deep in debt (−1991…−2883g) while stability stayed high (96,
82) — a flat −3/turn penalty was easily offset. → debt penalty now scales:
−3 minus 1 per 1000g owed, capped at −10. Post-fix, the same deep-debt seeds
fall to stability 27/19. Verified by A10.

### [FIXED c4] No reign summary at game over
Added an explicit prestige score (years reigned, legitimacy, stability,
prosperity, surplus, population) shown at game over and abdication. Verified by
A11. This is the soft "how well did you do" signal the spec lacked.

## Cycle 5 — final designer review
No new mechanical gap. Every system fires with a visible consequence and no dead
choices remain (167 option-checks). Further work would be *content* (more event
templates) — deliberately deferred (YAGNI) until a player asks for variety.

## Cycle 6 candidates — found by playing a FULL reign (seed 7, 72 years)
Per-turn tests passed but a complete played-through reign exposed two macro gaps
the single-turn "no dead choices" check cannot see. (Honest note: this means the
cycle-5 "exit" was premature on the "nothing meaningful to decide" axis.)

### [FIXED c7] Late-game stasis — the realm becomes frictionless at 100/100
For ~56 of 72 years every turn was identical: stability & prosperity pinned at
100, treasury ballooning (200g → 3000g+) with nothing worth buying, zero
external threat. No decision mattered. **Fix (mechanical):** introduce
late-game pressure so a peaceful optimum decays without active management — e.g.
(a) prosperity/stability gently decay toward a baseline each turn so upkeep of
"perfect" requires spending; (b) army upkeep or court expectations scale with
population/treasury so idle gold isn't free; (c) neighbours grow stronger over
time, so a static army eventually invites invasion. Done-test: assert that over a
60-turn hands-off reign, stability is NOT pinned at 100 for >N consecutive turns.
**Done (cycle 7):** stability above 50 decays −1/turn and "hold court" cut to +1,
so a high-stability realm needs active spending to sustain (passive equilibrium
settles ~50); rival realms gain strength over time so a static army invites
trouble. Verified by A15 + harness (random play no longer sits at 100).
*Residual:* over a 200-year run gold/population still grow unbounded — outside
the spec's ~30-turn envelope, left as-is (YAGNI).

### [FIXED c6] Dynastic dead-end — a young heir cannot continue the line
`_kill_ruler` only grants a spouse if `heir.age >= 18`; there is no decree to
marry/remarry the *ruler*; marriage only marries children OUT (removing heirs).
So an heir who ascends young and childless dooms the dynasty with no recourse
(seed 7: Torgar ascended at 14, reigned 44 years, died heirless → extinct). The
engine also allows marrying off your ONLY heir. **Fix:** (1) add an "Arrange your
marriage" decree when the ruler is unmarried; (2) on ascension, grant/queue a
spouse regardless of age (marry at coming-of-age); (3) forbid marrying out a
child if it would leave zero heirs. **Done (cycle 6):** added a "Take a spouse"
decree for an unmarried ruler aged ≥16; lowered the ascension spouse-grant
threshold 18→16; the alliance "Wed" decree now appears only when ≥2 heirs remain
(never marries away the last). Verified by A12/A13/A14. End-to-end proof: a
marriage-aware policy carried the seed-7 dynasty unbroken through the full
200-year horizon (14 monarchs), where the old policy went extinct at year 72.
