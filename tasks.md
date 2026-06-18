# tasks.md — Realm backlog

Ordered. Each task is small enough for one cycle and carries a done-test.
Mark `[ ]` / `[x]`.

## Cycle 1 — DONE
- [x] Engine skeleton: state model, RNG, 5-phase turn. Done-test: `import
  kingdom` and run one turn without error.
- [x] Economy, war, diplomacy, events, succession systems. Done-test: A2/A3/A5/A6.
- [x] Self-play harness, one command, PASS/FAIL. Done-test: `python kingdom.py
  --selfplay 10 30` prints PASS.
- [x] Acceptance tests A1–A7. Done-test: `python test_kingdom.py` prints PASS.
- [x] Interactive CLI. Done-test: `python kingdom.py --seed 3` plays a turn.
- [x] Fix name leading-space bug. Done-test: no generated name starts with " ".
- [x] Fix prosperity auto-pinning at 100. Done-test: prosperity not always 100
  across seeds (ux_review c1 evidence).
- [x] README. Done-test: `README.md` explains run + play.

## Cycles 2–4 — DONE
- [x] **c1-a** Avoid immediately repeating the previous event (cycle 2).
  Done-test: A8 — 450 events, zero back-to-back repeats.
- [x] **c1-b** War cooldown per neighbour, 2 turns after a war ends (cycle 3).
  Done-test: A9 — warred neighbour not re-declarable until cooldown clears.
- [x] **c1-d** Debt penalty scales with depth (cycle 4). Done-test: A10 — 9000g
  debt costs more stability than 500g debt.
- [x] **c1-c** Prestige score at game over / abdication (cycle 4). Done-test:
  A11 — non-negative integer that grows over a reign.

## Cycles 6–7 — DONE (found by playing a full reign)
- [x] **c6-b** Dynastic dead-end fixed (cycle 6): "Take a spouse" decree for an
  unmarried ruler; ascension spouse threshold 18→16; never marry away the last
  heir. Done-tests: A12, A13, A14.
- [x] **c6-a** Late-game stasis fixed (cycle 7): stability decays from its peak
  without upkeep; rivals strengthen over time. Done-test: A15 + harness spread.

## Known limitation (logged, out of scope)
- Over very long reigns (>100 turns) gold/population grow unbounded. This is
  beyond the spec's ~30-turn design envelope where numbers stay sane; not fixed
  (YAGNI). Revisit only if long-game play becomes a goal.

## Open
_None._

## Review note (cycle 5 — final)
All exit conditions met: harness PASSes 50 seeds × 30 turns and 25 × 40 turns
(zero crashes / invariant violations); all 11 acceptance tests (A1–A11) pass;
every system has a verified visible consequence with no dead choices
(`ux_review.md`); the natural game-over path is reachable (166/400 seeds over 60
turns); README explains run + play. The designer review finds no new mechanical
gap — remaining ideas would be content expansion (more events), which is YAGNI
absent a player need. **Backlog empty; loop exit conditions satisfied.**
