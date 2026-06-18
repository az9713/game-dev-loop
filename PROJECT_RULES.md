# PROJECT_RULES.md — reusable patterns (promoted from lessons_learned)

Patterns proven on this project that should carry to future ones.

## 1. Make acceptance criteria executable, run by the system on itself
Phrase each spec criterion as an automated pass/fail test with no human
judgment. The headline test is a self-play harness (drive the system with a
random/scripted agent and assert invariants after every step). One command,
prints PASS/FAIL, exits non-zero on failure.

## 2. "No dead choices" = clone a *healthy* state, apply each option, assert delta
For any decision system, the test that every option matters is: snapshot a
non-degenerate state, apply one option, assert the snapshot changed. Test
against healthy states, not collapsed ones — a value already at its floor/cap
legitimately absorbs a delta and would cause a false positive.

## 3. When a self-check fails, first ask whether the check is fair
Before changing the system under test, confirm the test isn't measuring the
wrong thing. (Cycle 1: the "dead choice" failure was the test feeding options
into rock-bottom states, not a real dead choice.)

## 4. One seeded RNG, threaded through the whole engine
All entropy goes through a single `random.Random` on the state object — no
wall-clock, no global `random`, no `os.urandom` in engine paths. Same seed ⇒
same playthrough ⇒ reproducible harness and bug repro.

## 5. Clamp on write, assert on read
Every bounded value is clamped at the point of mutation (`_clamp`/`max(0,…)`)
*and* re-asserted by a central invariant checker called after each step. Belt
and braces catches both new code paths and bad inputs.

## 6. One front-end seam: `choose(prompt, options) -> index`
The engine never knows if it's talking to a human or a harness. The CLI passes
an input prompter; the harness passes a random picker. Same turn code, fully
testable.

## 7. Play the whole arc, not just the turn
Per-turn invariant/unit tests are necessary but not sufficient for a simulation.
They catch local breakage; they structurally cannot see emergent dead-ends
(unrecoverable states) or "solved-game" stasis (a stable attractor where no
decision matters). Before declaring a simulation done, **play one complete run
to its natural end and review it as a designer.** On this project that gate
caught a dynastic dead-end and late-game stasis that 11 green per-turn tests had
missed — and reopened a prematurely-closed loop.
