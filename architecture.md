# architecture.md — Realm

One zero-dependency module, `kingdom.py` (engine + CLI + self-play harness), with
acceptance tests in `test_kingdom.py`. Splitting is deferred until a second
front-end needs the engine alone (ponytail: YAGNI).

## Modules / boundaries (all within `kingdom.py`)
- **Content generation** — `_name`, `_place`, `_make_person`; pure functions of a
  seeded `random.Random`. The only source of game content.
- **State model** — dataclasses `Person`, `Neighbor`, `Realm`, `Game`. Plain
  data; no behaviour beyond a couple of read-only properties.
- **RNG** — a single `random.Random` lives on `Game.rng`. Every stochastic call
  goes through it, so a seed fully determines a playthrough.
- **Event system** — `EVENTS` is a list of factory functions
  `f(game) -> (prompt, [(label, action), ...])`. `action()` applies an effect via
  `_apply(...)` and returns a result string. Adding an event = add one function.
- **Decree system** — `decree_options(game) -> [(label, action), ...]`, built
  from current state so only valid actions appear (war only vs a hostile
  neighbour, marriage only with an of-age child).
- **Turn engine** — `process_turn(game, choose)` orchestrates the five phases.
  `choose(prompt, options) -> index` is the only seam between engine and UI:
  the CLI passes a human prompt; the harness passes a random picker.
- **CLI** — `play()`, `_print_status`, `_ask_human`.
- **Harness** — `self_play`, `run_harness`, plus `check_invariants`.

## Game-state data structure
```
Game
 ├─ seed, rng, turn, year, next_pid, log[], over, over_reason
 ├─ realm: Realm(name, treasury:int, population, prosperity, stability,
 │                legitimacy, army, tax_rate)
 ├─ ruler: Person(pid, name, gender, age, rel='ruler', martial, stewardship,
 │                 diplomacy, intrigue, traits[], alive)
 ├─ family: [Person]   # spouse / child / sibling (heirs come from here)
 └─ neighbors: [Neighbor(name, relation:-100..100, strength, at_war)]
```

## How a turn flows end-to-end (traceable in one read)
`process_turn(g, choose)`:
1. `g.turn/year += 1`, clear `g.log`.
2. `phase_economy(g)` — income/upkeep → treasury; tax & debt → stability;
   prosperity chases stability; population drifts. Early-returns if game over.
3. Pick `EVENTS[rng]`, build options, `choose(...)`, run the chosen `action()`.
4. `decree_options(g)`, `choose(...)`, run the chosen `action()`.
5. `phase_war(g)` — invasions + resolve each `at_war` neighbour; ruler may die.
6. `phase_aging(g)` — age all; possible birth; mortality; ruler death →
   `_kill_ruler` → `_choose_heir` (child → sibling → crisis).

## Invariants (and the code that enforces them)
Checked by `check_invariants(g)`, called after every turn in the harness:
- **Treasury is an integer** — only ever changed by `+= int` in `_apply` /
  `phase_economy` / `phase_war`. Enforced: `assert isinstance(treasury, int)`.
- **army ≥ 0, population ≥ 0** — `_apply` and phase code use `max(0, …)`.
- **prosperity / stability / legitimacy / tax_rate ∈ [0,100]** — every write
  goes through `_clamp`. Enforced by the loop over `STAT_FIELDS`.
- **Exactly one living ruler, or a defined crisis** — `_kill_ruler` either sets
  a single new `g.ruler` (alive, rel='ruler') or sets `g.over` + `over_reason`.
  `_choose_heir` returns child → sibling → `None`. Enforced by the `g.over`
  branch in `check_invariants`.
- **neighbour relation ∈ [−100,100], strength ≥ 0** — all writes use `_clamp(…,
  -100, 100)` / `max(…)`. Enforced in the neighbours loop.

## Determinism
Same seed ⇒ same playthrough (harness reproducibility). The only entropy is
`Game.rng`; no wall-clock, no `os.urandom`, no global `random` in engine paths.
