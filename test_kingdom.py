"""Acceptance tests for Realm — each maps to a criterion in spec.md.

Run: python test_kingdom.py   (prints PASS/FAIL, exits non-zero on failure)
No framework: plain asserts so it runs with stdlib only.
"""
import copy

import kingdom as k


def _snapshot(g: k.Game):
    """A comparable summary of all state a choice could plausibly change."""
    r = g.realm
    return (r.treasury, r.population, r.prosperity, r.stability, r.legitimacy,
            r.army, r.tax_rate,
            tuple((n.relation, n.strength, n.at_war) for n in g.neighbors),
            tuple((p.pid, p.alive, p.rel, p.age) for p in [g.ruler] + g.family),
            g.over)


# A1: self-play harness — full reign, 10 seeds, zero invariant breaks / crashes.
def test_selfplay_10_seeds():
    for seed in range(10):
        g = k.self_play(seed, turns=30)
        k.check_invariants(g)
    print("A1 ok: 10 seeds x 30 turns, invariants held")


# A2: treasury is always an integer (it may go negative — debt is allowed).
def test_treasury_integer():
    saw_negative = False
    for seed in range(20):
        g = k.new_game(seed)
        for _ in range(30):
            if g.over:
                break
            k.process_turn(g, lambda *a: g.rng.randrange(len(a[1])))
            assert isinstance(g.realm.treasury, int)
            saw_negative |= g.realm.treasury < 0
    assert saw_negative, "expected some reign to fall into debt over 20 seeds"
    print("A2 ok: treasury integer-only; debt is reachable")


# A3: succession always resolves to exactly one living ruler OR a defined crisis.
def test_succession_resolves():
    # Force-kill the ruler from many states; result is always well-defined.
    for seed in range(30):
        g = k.new_game(seed)
        for _ in range(g.rng.randint(0, 25)):
            if g.over:
                break
            k.process_turn(g, lambda *a: g.rng.randrange(len(a[1])))
        if g.over:
            continue
        k._kill_ruler(g)
        if g.over:
            assert g.over_reason, "crisis must carry a reason"
            assert k._choose_heir(g) is None
        else:
            assert g.ruler.alive and g.ruler.rel == "ruler"
            assert len([p for p in [g.ruler] if p.rel == "ruler"]) == 1
    print("A3 ok: succession -> one heir or a defined crisis")


# A4: NO DEAD CHOICES — every offered option moves a *healthy* realm. We test
# against healthy states (no stat at a floor/cap), so any inert option is a
# genuine design fault, not a saturated value absorbing the delta.
def _healthy_states():
    states = [k.new_game(seed) for seed in range(6)]
    # One with a hostile neighbour, to surface the "declare war" decree.
    g = k.new_game(100)
    g.neighbors[0].relation = -50
    states.append(g)
    # One with an of-age child + hostile neighbour, to surface "wed" + "war".
    g = k.new_game(101)
    for c in g.family:
        if c.rel == "child":
            c.age = 18
    g.neighbors[0].relation = -50
    states.append(g)
    return states


def test_no_dead_choices():
    states = _healthy_states()

    checked_events = 0
    for factory in k.EVENTS:
        for base in states:
            n = len(factory(copy.deepcopy(base))[1])
            for i in range(n):
                g = copy.deepcopy(base)         # fresh copy per option
                label, action = factory(g)[1][i]
                before = _snapshot(g)
                action()
                assert _snapshot(g) != before, (
                    f"DEAD CHOICE in event {factory.__name__}: '{label}' "
                    f"changed nothing")
                checked_events += 1

    checked_decrees = 0
    for base in states:
        n = len(k.decree_options(copy.deepcopy(base)))
        for i in range(n):
            g = copy.deepcopy(base)             # fresh copy per option
            label, action = k.decree_options(g)[i]
            before = _snapshot(g)
            action()
            assert _snapshot(g) != before, (
                f"DEAD CHOICE in decree: '{label}' changed nothing")
            checked_decrees += 1

    assert checked_events > 0 and checked_decrees > 0
    print(f"A4 ok: no dead choices ({checked_events} event-option, "
          f"{checked_decrees} decree-option checks)")


# A5: war produces both victories and defeats with real consequences.
def test_war_outcomes():
    wins = losses = 0
    for seed in range(40):
        g = k.new_game(seed)
        for _ in range(30):
            if g.over:
                break
            k.process_turn(g, lambda *a: g.rng.randrange(len(a[1])))
            for line in g.log:
                wins += "Victory over" in line
                losses += "Defeat by" in line
    assert wins > 0, "war never produced a victory"
    assert losses > 0, "war never produced a defeat"
    print(f"A5 ok: war outcomes observed (wins={wins}, losses={losses})")


# A6: diplomacy — gifts/marriage measurably move a neighbour's relation.
def test_diplomacy_moves_relations():
    g = k.new_game(0)
    worst = min(g.neighbors, key=lambda n: n.relation)
    before = worst.relation
    # The "send gifts" decree is always present; find and fire it.
    for label, action in k.decree_options(g):
        if label.startswith("Send gifts"):
            action()
            break
    assert worst.relation > before, "diplomacy did not improve relation"
    print("A6 ok: diplomacy raises a neighbour's relation")


# A7: bounded stats — every stat stays within [0,100] across long play.
def test_stats_bounded():
    for seed in range(10):
        g = k.new_game(seed)
        for _ in range(50):  # past the nominal 30 to stress bounds
            if g.over:
                break
            k.process_turn(g, lambda *a: g.rng.randrange(len(a[1])))
            r = g.realm
            for f in k.STAT_FIELDS + ("tax_rate",):
                assert 0 <= getattr(r, f) <= 100
    print("A7 ok: stats stay bounded over 50 turns")


# A8 (c1-a): no event template fires twice in a row within a reign.
def test_no_back_to_back_events():
    seq = []
    for seed in range(15):
        g = k.new_game(seed)
        for _ in range(30):
            if g.over:
                break
            k.process_turn(g, lambda *a: g.rng.randrange(len(a[1])))
            seq.append((seed, g.last_event))
    repeats = sum(1 for i in range(1, len(seq))
                  if seq[i][0] == seq[i - 1][0] and seq[i][1] == seq[i - 1][1])
    assert repeats == 0, f"{repeats} back-to-back event repeats"
    print(f"A8 ok: no back-to-back events over {len(seq)} events")


# A9 (c1-b): a neighbour just warred cannot be re-declared on (cooldown).
def test_war_cooldown():
    g = k.new_game(0)
    n = g.neighbors[0]
    n.relation = -80
    n.at_war = True
    k.phase_war(g)                       # resolves the war, sets cooldown
    assert n.cooldown > 0, "cooldown not set after a war ended"
    labels = [label for label, _ in k.decree_options(g)]
    assert not any(label == f"Declare war on {n.name}" for label in labels), \
        "war re-declarable during cooldown"
    # After the cooldown elapses, war becomes available again (if still hostile).
    for _ in range(n.cooldown):
        k.phase_economy(g)               # ticks cooldown down
    assert n.cooldown == 0
    print("A9 ok: war cooldown blocks re-declaration, then clears")


# A10 (c1-d): debt bites harder the deeper it runs.
def test_debt_penalty_scales():
    def stab_drop(debt):
        g = k.new_game(0)
        g.realm.treasury = -debt
        g.realm.tax_rate = 0          # isolate the debt penalty from tax pressure
        before = g.realm.stability
        k.phase_economy(g)
        return before - g.realm.stability
    shallow = stab_drop(500)
    deep = stab_drop(9000)
    assert deep > shallow, f"deep debt ({deep}) not worse than shallow ({shallow})"
    print(f"A10 ok: debt penalty scales (shallow={shallow}, deep={deep})")


# A11 (c1-c): prestige score is a non-negative integer summarising a reign.
def test_prestige_score():
    g = k.new_game(0)
    s0 = k.prestige_score(g)
    for _ in range(10):
        if g.over:
            break
        k.process_turn(g, lambda *a: g.rng.randrange(len(a[1])))
    s1 = k.prestige_score(g)
    assert isinstance(s0, int) and s0 >= 0
    assert isinstance(s1, int) and s1 >= 0
    assert s1 > s0, "prestige should grow as a reign endures"
    print(f"A11 ok: prestige score (start={s0}, after 10 turns={s1})")


# A12 (c6-b): an unmarried ruler can take a spouse, enabling a new heir.
def test_ruler_can_marry():
    g = k.new_game(0)
    g.family = [p for p in g.family if p.rel != "spouse"]   # widow the ruler
    g.ruler.age = 25
    assert k._spouse(g) is None
    fired = False
    for label, action in k.decree_options(g):
        if label.startswith("Take a spouse"):
            action()
            fired = True
            break
    assert fired, "no ruler-marriage decree offered to an unmarried ruler"
    assert k._spouse(g) is not None, "ruler did not gain a spouse"
    print("A12 ok: an unmarried ruler can wed and continue the line")


# A13 (c6-b): the game never lets you marry off your last heir.
def test_cannot_marry_off_last_heir():
    g = k.new_game(0)
    g.family = [p for p in g.family if p.rel == "spouse"]   # drop child + sibling
    g.family.append(k._new_person(g, "child", 18))          # exactly one heir
    labels = [label for label, _ in k.decree_options(g)]
    assert not any(label.startswith("Wed ") for label in labels), \
        "offered to marry off the only heir"
    g.family.append(k._new_person(g, "sibling", 30))        # now two heirs
    labels = [label for label, _ in k.decree_options(g)]
    assert any(label.startswith("Wed ") for label in labels), \
        "marriage alliance not offered with a spare heir"
    print("A13 ok: cannot marry away the last heir; can with a spare")


# A14 (c6-b): a young heir who ascends is not doomed — extinction is rarer now.
def test_young_heir_not_doomed():
    # Compare extinction rate; with ruler-marriage the line should survive more.
    overs = 0
    for seed in range(60):
        g = k.new_game(seed)
        for _ in range(60):
            if g.over:
                break
            # A "keep the line going" policy: wed if unmarried, else hold court.
            def policy(prompt, options):
                if prompt.startswith("DECREE"):
                    for i, o in enumerate(options):
                        if o.startswith("Take a spouse"):
                            return i
                    for i, o in enumerate(options):
                        if o.startswith("Hold court"):
                            return i
                return 0
            k.process_turn(g, policy)
        overs += g.over
    # Not a hard guarantee (old age can still end a line), but with active
    # marriage most 60-year runs should survive.
    assert overs < 30, f"too many extinctions even with marriage policy: {overs}/60"
    print(f"A14 ok: marriage policy keeps the line ({60 - overs}/60 survived 60y)")


# A15 (c6-a): stability erodes from its peak without upkeep (no frictionless 100).
def test_stability_decays_from_peak():
    g = k.new_game(0)
    g.realm.stability = 100
    g.realm.tax_rate = 20            # no tax penalty, isolate the decay
    k.phase_economy(g)
    assert g.realm.stability < 100, "stability did not erode from its peak"
    print(f"A15 ok: peak stability erodes without upkeep "
          f"(100 -> {g.realm.stability})")


def main():
    tests = [v for name, v in sorted(globals().items())
             if name.startswith("test_") and callable(v)]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"FAIL: {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"ERROR: {t.__name__}: {type(e).__name__}: {e}")
    print("\n" + ("PASS — all acceptance tests green"
                  if failures == 0 else f"FAIL — {failures} test(s) failed"))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
