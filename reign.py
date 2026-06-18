"""Play a full reign to its end with a fixed 'Just & Craven' policy.

Diplomacy over war, mercy to subjects, debt kept in check, dynasty kept going.
Prints a year-by-year chronicle until the dynasty's story ends.
Usage: python reign.py <seed>
"""
import sys
import kingdom as k

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
g = k.new_game(seed)


def find(labels, sub):
    for i, o in enumerate(labels):
        if sub in o.lower():
            return i
    return None


def pick_event(opts):
    L = [o.lower() for o in opts]
    joined = " ".join(L)
    r = g.realm
    if "physicians" in joined:                       # plague
        return find(L, "physicians") if r.treasury >= 60 else find(L, "course")
    if "pardon" in joined:                           # plot — Craven: avoid the axe
        return find(L, "loyalty") if r.treasury >= 50 else find(L, "pardon")
    if "people keep" in joined:                      # harvest — Just: let them keep it
        return find(L, "people keep")
    if "company" in joined:                          # sellsword
        return find(L, "company") if (r.treasury >= 80 and r.army < 700) \
            else find(L, "decline")
    if "concessions" in joined:                      # unrest — Just: concede
        return find(L, "concessions") if r.treasury >= 30 else find(L, "crush")
    if "pact" in joined:                             # envoy
        return find(L, "accept")
    return 0


def pick_decree(opts):
    L = opts
    r = g.realm
    if g.ruler.age >= 16 and k._spouse(g) is None and r.treasury >= 40:
        i = find(L, "take a spouse")                 # continuing the line is paramount
        if i is not None:
            return i
    if r.treasury < 0:                               # dig out of debt first
        i = find(L, "raise taxes")
        if i is not None:
            return i
    if any(n.relation < 0 for n in g.neighbors) and r.treasury >= 30:
        i = find(L, "send gifts")                    # defuse the worst neighbour
        if i is not None:
            return i
    # Deliberately never marry heirs OUT — this dynasty guards its succession.
    if r.stability < 70 and r.treasury >= 30:        # decay means high stability
        i = find(L, "feast")                         # now takes active upkeep
        if i is not None:
            return i
    if r.prosperity < 70 and r.treasury >= 50:
        i = find(L, "invest")
        if i is not None:
            return i
    if r.army < 400 and r.treasury >= 40:
        i = find(L, "recruit")
        if i is not None:
            return i
    if r.treasury < 60 and r.tax_rate < 35:
        i = find(L, "raise taxes")
        if i is not None:
            return i
    i = find(L, "hold court")
    return i if i is not None else 0


def chooser(prompt, options):
    return pick_event(options) if prompt.startswith("EVENT") else pick_decree(options)


NOTABLE = ("ascends", "dies", "falls in battle", "Victory over", "Defeat by",
           "child is born", "invades", "extinguished", "Plague", "riot")

print(f"THE CHRONICLE OF {g.realm.name.upper()} — beginning the reign of "
      f"{g.ruler.name} ({', '.join(g.ruler.traits)})\n")
monarchs = [g.ruler.name]
wars_won = wars_lost = births = 0

while not g.over and g.turn < 200:
    ruler_before = g.ruler.name
    k.process_turn(g, chooser)
    r = g.realm
    notes = [ln for ln in g.log
             if any(t in ln for t in NOTABLE) and not ln.startswith("===")]
    for ln in notes:
        if "Victory over" in ln:
            wars_won += 1
        if "Defeat by" in ln:
            wars_lost += 1
        if "child is born" in ln:
            births += 1
    if g.ruler.name != ruler_before and not g.over:
        monarchs.append(g.ruler.name)
    tag = ("  | " + " ".join(n.split("EVENT:")[-1].split("DECREE:")[-1].strip()
                             for n in notes)) if notes else ""
    print(f"Y{g.year} {g.ruler.name:<9} gold{r.treasury:>6} stab{r.stability:>4} "
          f"prosp{r.prosperity:>4} army{r.army:>5} pop{r.population:>6}{tag}")

print("\n" + "=" * 60)
if g.over:
    print("*** " + g.over_reason + " ***")
else:
    print("*** The chronicle reaches its 200-year horizon, dynasty enduring. ***")
print(f"Years reigned: {g.turn}  |  Monarchs: {len(monarchs)} "
      f"({' -> '.join(monarchs)})")
print(f"Wars won: {wars_won}  |  wars lost: {wars_lost}  |  royal births: {births}")
print(f"Final prestige: {k.prestige_score(g)}")
