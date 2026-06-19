# From Text to Browser Game — a Development Journey

This is the story of turning **Realm** from a text game you run in a terminal
(`kingdom.py`) into a **graphical game anyone can play in a browser**
([`realm.html`](realm.html)) — told as the sequence of *forks* in the road, the
choice made at each, and **how** that choice was reached.

It is a companion to [`DEVELOPMENT.md`](DEVELOPMENT.md) (which covers the 7 cycles
that built the original game). The throughline here is the same as the rest of
this repo: *the journey is the point, warts included.*

---

## The request

> *"the game is text based. to make it fun to play, we need game graphics. can
> you explore if it is doable to turn this text based game into something like a
> video game? i have no game design/development experience."*

Two things shaped everything after: the goal was **"feels like a video game,"**
and the person asking **doesn't speak game-developer** — so every fork had to be
decided with plain-language tradeoffs and, where possible, *things to look at*
rather than things to read.

The one piece of luck: the original engine was already built with a clean seam.
`process_turn(g, choose)` never prints or reads input itself — it just calls a
`choose(prompt, options)` function handed to it. That meant a graphical version
could **reuse the whole game** and only swap *how a choice is made* (a click
instead of a typed number). A graphical front-end was additive, not a rewrite.

---

## Fork 1 — How will players actually run it?

The first instinct ("a desktop app with windows and buttons") collided with the
brief the moment we asked *how a non-technical player launches it.*

| Option | What the player must do | Cross-platform? |
|--------|-------------------------|-----------------|
| **tkinter desktop** (Python stdlib GUI) | Install Python, run a terminal command — or download a per-OS binary that antivirus flags and macOS refuses to run unsigned. **No phones at all.** | For the *developer*, yes; for the *player*, painful |
| **Browser, single HTML file** | **Nothing.** Double-click, or click a link. | Windows, Mac, Linux, **and phones** |
| **pygame / a real engine** | Install Python *and* dependencies | Breaks the zero-install goal |

**Decision: a browser game.** *How it was made:* by reframing "cross-platform"
from the developer's side ("the same code runs everywhere") to the **player's**
side ("the same *file* runs everywhere with nothing installed"). Once put that
way, the browser was the only option that fit "no setup burden + cross-platform."

> **Wart:** "tkinter is cross-platform" is technically true and practically
> misleading. The honest blocker isn't the toolkit — it's that **Python itself is
> the dependency**, and it's the heaviest one for a player.

---

## Fork 2 — One self-contained file, or a Python backend?

A browser game can keep the game logic in Python (served to the browser by a
local web server) **or** move the logic into the page itself as JavaScript.

**Decision: a single self-contained `realm.html`**, engine ported to JavaScript.
*How it was made:* the Python-backend option still requires the player to install
Python and run a command — it only makes sense if *you* are the only player. A
single HTML file needs no runtime at all, which is actually *more* faithful to the
project's "self-contained, zero-dependency" spirit than the Python version was.

The cost, stated honestly: **two codebases** (the Python reference + the JS port)
instead of one. For a game meant to be *played by others*, easy-to-deliver beats
single-codebase — a game nobody can launch isn't fun regardless of its internals.

---

## Fork 3 — What should it *look* like?

Describing a visual style in words is nearly useless to someone who doesn't speak
design. So instead of asking, we **built three real, openable mockups** of the
same game moment and let the eye decide:

1. **Illuminated Chronicle** — warm parchment, red & gold ink, the reign told as
   an old storybook.
2. **Throne Hall** — dark candle-lit stone, gold accents, a house banner.
3. **War Table / Map** — a parchment map of the realm and its neighbours with a
   council panel (most strategy-game-like).

All three were drawn **entirely in code** (CSS gradients + inline SVG, including a
procedurally generated coat of arms), so the mockups were honest previews of the
real ceiling, not faked comps. They're preserved in [`mockups/`](mockups/).

**Decision: Illuminated Chronicle.** *How it was made:* the user opened all three
and picked by eye. It also happened to be the best fit — the game already produces
a year-by-year *chronicle*, so the look matches what the game actually is, and
pure CSS renders parchment-and-gold reliably well.

---

## Fork 4 — The lettering felt too modern

First pass used the computer's built-in serif fonts. The feedback: *"the fonts
used are too modern."* True — a system serif reads as "nice book," not "medieval
scribe."

**Decision: embed real medieval fonts**, with a craft rule:

- **Blackletter** (UnifrakturMaguntia) for the *title, drop-cap, and ornaments*.
- A **readable period serif** for the body — never blackletter for whole
  paragraphs, which is authentic but exhausting to read (the most common mistake
  in "medieval" UIs).

*How it was made:* the fonts are **embedded inside the HTML as base64**, so the
single file still works offline on any machine with nothing to install. This very
slightly bends the project's "no external data" purity (a font is a bundled
asset), but it's the only way to get true medieval lettering — and it was an
explicit ask. The fonts are OFL-licensed, which permits embedding.

> **Wart:** fetching the fonts failed twice first — the machine's network closed
> the connection until TLS 1.2 was forced, and the font files turned out to have
> non-obvious filenames (`UnifrakturMaguntia-Book.ttf`, `IMFeENrm28P.ttf`) that a
> first guess got wrong (404s). Then `.woff2` subsets were chosen over `.ttf` to
> keep the file small.

---

## Fork 5 — "More ornate, please" → a font-comparison tab

The body still felt too plain: *"I still would like the body more
ornate/calligraphic."* Three candidates were in play (MedievalSharp, Uncial
Antiqua, Grenze Gotisch) and, again, words wouldn't settle it.

*How it was made:* rather than ship one and ask, we built **one page with three
buttons that swap the body font live** ([`mockups/1_chronicle_fonts.html`](mockups/1_chronicle_fonts.html)) —
flip between all three on the identical page, with the blackletter title held
constant so only the body changed. The whole switch is three lines of JavaScript
rewriting a single CSS variable.

**Decision: Grenze Gotisch** — the most overtly Gothic of the three, a tall narrow
text face. Chosen by clicking back and forth until one won.

---

## Engineering the port so it's *faithful*, not just a lookalike

A port's real risk isn't the UI — it's that the rewritten rules quietly behave
differently. "Faithful" is unverifiable by playing a few turns, so the safety net
came across with the game:

- **The invariants and the self-play harness were ported too**, not just the
  game. `check_invariants` (which the Python version runs after every turn)
  became `checkInvariants` throwing on violation; the random-playthrough harness
  came across as well.
- **Verified headless under Node**: the engine block is extracted from the HTML
  and run **300 seeds × 60 turns with invariants checked every single turn → PASS**,
  with a believable spread of surviving vs. extinct dynasties (matching the Python
  balance).
- **RNG semantics matched on purpose**: `randint` inclusive, `randrange`
  exclusive, `sample` returns distinct items — so the *logic* behaves identically,
  even though the JS uses its own PRNG and so **seeds are not byte-identical** to
  Python's (a deliberate choice; CPython's RNG isn't worth reproducing). The saved
  Python chronicles stay Python-only artifacts.
- **The `choose` seam carried over**: `processTurn` is `async` so a button-click
  resolves a promise, while the harness passes a synchronous random picker through
  the *same* seam. One code path, two drivers — exactly the original design.

> **Warts worth keeping:**
> - The parent folder had a `package.json` with `"type":"module"`, so the Node
>   test had to be a `.cjs` file (CommonJS) to use `require`.
> - Once fonts are injected, `realm.html` is too large to safely hand-edit (an
>   early edit attempt failed for exactly this reason). The fix: keep
>   [`realm.src.html`](realm.src.html) (with font *tokens*) as the editable source
>   of truth, and treat `realm.html` as a **build output** — change the source,
>   then re-inject the fonts, never hand-edit the giant file.

---

## The "play it in the README" problem

The natural finish — *embed the playable game right in the README* — isn't
possible: **GitHub sanitizes README markdown and strips `<script>`/`<iframe>`**,
so a game can't execute on the repo page. The real "click and play" experience is
**GitHub Pages** (free static hosting from this same repo), which serves
`realm.html` at a live URL. The README links straight to it with a banner.

---

## The result

A single **~90 KB** file — engine, UI, and both medieval fonts inside it — that
opens by double-click or a link, on any OS or phone, with nothing installed.

- **Play in your browser:** see the link at the top of the [README](README.md).
- **Run the self-test yourself:** open `realm.html?selftest` (optionally
  `?selftest&seeds=300&turns=60`).

### Artifacts this journey produced
| File / folder | What it is |
|---------------|------------|
| `realm.html` | **The game.** Self-contained build output — fonts injected, ready to play or share. |
| `realm.src.html` | The **editable source of truth** (font tokens instead of base64). All changes go here, then re-inject fonts. |
| `.realm_runtest.cjs` | Dev harness — extracts the engine from the HTML and runs the self-play test under Node. |
| `mockups/` | The three style explorations + the live font-comparison page — the forks above, preserved. |
| `docs/img/` | Screenshots of the finished game (title + a reign in progress). |
| `VIDEO_GAME_JOURNEY.md` | This document. |
