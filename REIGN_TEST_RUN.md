# Full-Reign Play-Test — Documentation

This documents the **designer play-test**: playing a complete reign from the
first year to its natural end, as opposed to the per-turn automated tests. It is
the exercise that surfaced two emergent flaws and reopened the loop for cycles
6–7 (see `lessons_learned.md`, `ux_review.md`).

## Why this exists
Per-turn tests (A1–A15 in `test_kingdom.py`) catch *local* breakage but cannot
see *emergent* problems — unrecoverable dynastic states, or a "solved-game"
late phase where no decision matters. Those only appear when you play the whole
arc. This file captures that playthrough as a durable artifact (the raw
transcript regenerates deterministically from a seed, but is saved here so a
fresh session can read it without running anything).

## Method
- **Tool:** `reign.py` — plays a full reign with a fixed "Just & Craven" policy
  (diplomacy over war, mercy to subjects, debt kept in check, the line kept
  going) until the dynasty ends or a 200-year horizon is reached. It prints a
  year-by-year chronicle plus a final tally.
- **Reproduce:** `python reign.py 7` (deterministic — same seed, same reign).
- **Raw transcript:** [`reign_seed7.txt`](reign_seed7.txt) — the full 200-year
  chronicle of House Corgar of Lorhelm under the current (post-fix) engine.

## Result with the current (post-fix) engine — dynasty endures
Seed 7, marriage-aware policy: **the bloodline survives the full 200-year
horizon — 14 monarchs in unbroken succession, 26 royal births, prestige
24,352.** Stability oscillates (≈70–100) rather than locking at 100, because the
cycle-7 decay means holding it high costs active spending (feasts, easing
revolts). Opening years (from `reign_seed7.txt`):

```
THE CHRONICLE OF LORHELM — beginning the reign of Corgar (Craven, Just)
Y1023 Corgar    gold   251 stab  62 prosp  60 army  300 pop  4900
Y1024 Corgar    gold   262 stab  61 prosp  62 army  380 pop  4998  | A child is born to the royal house: Draulf.
...
*** The chronicle reaches its 200-year horizon, dynasty enduring. ***
Years reigned: 200 | Monarchs: 14 (Corgar -> Wildric -> ... -> Garmund)
Wars won: 0 | wars lost: 0 | royal births: 26 | Final prestige: 24352
```

## What the play-test originally found (pre-fix) — the motivation for cycles 6–7
The *first* full reign played (before cycles 6–7, with the then-current engine
and a policy that married heirs out for alliances) ended very differently. These
runs are not byte-reproducible now because the engine has since changed, but the
observed outcomes were:

| Run | Outcome | Cause |
|-----|---------|-------|
| Seed 7, original policy | **Extinct at year 72** (2 monarchs: Corgar → Torgar) | Torgar ascended at 14; the engine granted no spouse under 18 and had no ruler-marriage decree, so he reigned 44 years childless → no heir. |
| Seed 7, re-run after the c7 engine work but old policy | **Extinct at year 47** (Corgar → Lorana) | Same root cause — Lorana ascended at 14, policy never used the new "Take a spouse" decree. |

Both expose the **two flaws**:
1. **Dynastic dead-end** — a young, childless heir was unrecoverable.
2. **Late-game stasis** — before cycle 7, a peaceful realm pinned at 100/100 and
   every year was identical (≈56 of 72 years in the original run).

## Findings → fixes (cross-references)
- Full findings with concrete fixes: `ux_review.md` (entries `[FIXED c6]` and
  `[FIXED c7]`).
- The cycle write-ups: `lessons_learned.md` (Cycles 6–7).
- The acceptance tests that now lock the fixes in: **A12–A15** in
  `test_kingdom.py` (ruler can marry; last heir protected; marriage keeps most
  lines alive; peak stability erodes without upkeep).
- The end-to-end proof: the same seed-7 dynasty that died at year 72 now endures
  200 years once its rulers marry (this file's transcript).

## Known limitation (logged, out of scope)
Over very long reigns (>~100 turns) gold and population grow without bound — see
the late years of `reign_seed7.txt` (gold into the hundreds of thousands). This
is outside the spec's ~30-turn design envelope and is deliberately not fixed
(YAGNI); recorded in `tasks.md` and `ux_review.md`.
