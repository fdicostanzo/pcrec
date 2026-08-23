#!/usr/bin/env python3
"""[M6.6.1] §5.6 -- SIZING INPUTS FOR [ENG-LOOK], measured on pcrec itself.

[ENG-LOOK] (plan.md, chartered by Frank 2026-08-23 13:5x) is lookaround by
PRODUCT CONSTRUCTION in the DFA: `(?<=L)` at p holds iff subject[..p] is in
Sigma*.L, a property of already-consumed text, so the main automaton is
product-constructed with each body's recognizer during determinization and the
assertion becomes a predicate on the product state. `(?=L)` is the same
property in the REVERSE machine. That row says MEASUREMENT FIRST, and names
the number it needs: the size of each body's component automaton, and the
expected product growth against the caps.

THE METHOD, stated because a reader must be able to reject it:

  The component [ENG-LOOK] needs for a lookBEHIND body L is the recognizer for
  Sigma*.L. **pcrec's UNANCHORED FORWARD DFA for the pattern `L` IS that
  machine** -- unanchoredness is the automaton's own self-loop (D58's "Why"
  paragraph says so in as many words), which is exactly the Sigma* prefix. The
  component for a lookAHEAD body is reverse(L).Sigma*, and pcrec's REVERSE
  machine for the same pattern is that. So compiling the BODY ALONE and
  reading the two tables off the artifact gives both components, with no model
  in between.

  STATE COUNT is `len(rx_forward_is_accepting[])`; CLASS COUNT is
  `len(rx_forward_next_state[]) / states`, since the transition table is
  states x classes. Same for the reverse tables. These are the emitter's OWN
  array dimensions, read out of the emitted C -- not a stamp, not a count of
  anything this probe derives.

  THE CAPS are `PCREC_MAX_DFA_STATES_GOTO = 10000` (computed-goto attempt
  engine) and `PCREC_MAX_DFA_STATES_TABLE = 32000` (table engine; must fit in
  a short), src/core/limits.h:47-49.

  THE PRODUCT BOUND is |D(main)| x PRODUCT over bodies of |D(component)|, the
  worst case. It is an UPPER bound and the row already says the construction
  must ESTIMATE BEFORE COMMITTING and DECLINE past the cap ([ENG-CUT]'s
  shape), so an upper bound is the right quantity: a construction that
  declines on the bound is sound, one that declines on an optimistic guess is
  not. Reported alongside the ALPHABET product, because wave B's own precedent
  (assertions_design.md E4) is that the composed number that EXCEEDED the cap
  -- 38,009 against 32,000 -- was states x classes, not states.

POPULATION: (a) every lookaround body in the assertion-family EXPANSIONS
(probe_expansions.py's own table -- the corpus [ENG-LOOK]'s acceptance test
runs on), and (b) an enumerable real-lookaround population: the construct
table's own bodies plus the [ENG-LOOK] row's two named examples.
"""
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
PCREC = os.path.join(_ROOT, "build", "pcrec")

CAP_GOTO = 10000
CAP_TABLE = 32000


def artifact(pat, extra=()):
    r = subprocess.run(["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx",
                        "--features", "all", "-o", "-"] + list(extra)
                       + ["--", pat],
                       capture_output=True, text=True, cwd=_ROOT)
    if r.returncode != 0:
        return None, r.stderr.strip()
    return r.stdout, None


_ARR = re.compile(r"static const \w+(?: \w+)* (rx_\w+)\[(\d+)\]")


def dims(src):
    """{array-name: length} for every emitted table, plus the derived
    state/class counts for each machine."""
    out = {}
    for m in _ARR.finditer(src):
        out[m.group(1)] = int(m.group(2))
    res = {}
    for way in ("forward", "reverse"):
        acc = out.get("rx_%s_is_accepting" % way)
        nxt = out.get("rx_%s_next_state" % way)
        if acc:
            res[way + "_states"] = acc
            res[way + "_classes"] = (nxt // acc) if nxt else None
        else:
            res[way + "_states"] = None
            res[way + "_classes"] = None
    # `RX_ENGINE` is stamped only when the VM is selected; a DFA artifact
    # carries no such define, so ABSENCE means DFA. Stated rather than left
    # as a "?" column, which a reader would take for a failed measurement.
    res["engine"] = "vm" if '#define RX_ENGINE "vm"' in src else "dfa"
    return res


# (label, body-as-a-pattern, where it comes from)
BODIES = [
    # (a) the assertion-family expansions' bodies
    (r"\w",       "expansion", "\\b, \\B  (four bodies, all \\w)"),
    (r"\n",       "expansion", "(?m)^, (?m)$  ((?<=\\n), (?=\\n))"),
    (r"\n?\z",    "expansion", "\\Z and default-flags $   ((?=\\n?\\z))"),
    # \A and \z are anchors, not bodies; (?!\z)'s body is the anchor itself
    # (b) an enumerable real-lookaround population
    (r"foo",      "real",      "[ENG-LOOK]'s own example (?<=foo)bar"),
    (r"\d",       "real",      "[ENG-LOOK]'s own example (?<!\\d)\\d{4}(?!\\d)"),
    (r"\d{4}",    "real",      "the same example's MAIN pattern"),
    (r",",        "real",      "the construct table's (?<=,)\\w+"),
    (r"ab",       "real",      "a two-byte fixed body"),
    (r"abc",      "real",      "a three-byte fixed body"),
    (r"a|bc",     "real",      "two branches, different fixed lengths (§2.5)"),
    (r"[a-z]",    "real",      "a range class"),
    (r"[^\"']",   "real",      "a negated class (the backrefs lane's own idiom)"),
    (r"\w+",      "real",      "an UNBOUNDED body -- a lookAHEAD only (§2.5)"),
    (r"\d{3}",    "real",      "a counted body"),
    (r"(a|b)c",   "real",      "an alternation inside a concatenation"),
    (r"https?",   "real",      "a realistic literal-ish body"),
    # --- THE VACUITY CONTROLS. Without a body whose component is LARGE, a
    # table reading "0 over the cap" is unfalsifiable -- the population would
    # contain no cell that COULD be over. These are deliberately big.
    (r"\d{4}-\d{2}-\d{2}", "control", "a date shape -- a longer counted body"),
    (r"[a-z]{12}",         "control", "a 12-long class run"),
    (r"(?:ab|cd){8}",      "control", "a repeated two-way alternation"),
    (r"(?:a|b|c|d){10}",   "control", "a repeated four-way alternation"),
    (r"[01]*1[01]{12}",    "control", "bench case (f)'s shape -- the known "
                                      "state-explosion idiom"),
]

# The main patterns the components would be multiplied INTO.
MAINS = [
    (r"bar",       "the [ENG-LOOK] example's main"),
    (r"\d{4}",     "the second example's main"),
    (r"\w+",       "the construct table's main"),
    (r"[a-z]+@[a-z]+\.[a-z]+", "a realistic main"),
    (r"[01]*1[01]{12}", "CONTROL: a large main (bench case (f)'s shape)"),
    (r"(?:a|b|c|d){10}", "CONTROL: a second large main"),
]

print("pcrec  :", PCREC, "(present)" if os.path.exists(PCREC) else "(ABSENT)")
print("python3:", sys.version.split()[0])
print("caps   : PCREC_MAX_DFA_STATES_GOTO=%d  PCREC_MAX_DFA_STATES_TABLE=%d"
      % (CAP_GOTO, CAP_TABLE), "(src/core/limits.h:47-49)")
print()

if not os.path.exists(PCREC):
    print("SKIPPED -- no build/pcrec. This line is the skip, not silence.")
    sys.exit(0)

print("=" * 78)
print("COMPONENT AUTOMATA -- each BODY compiled ALONE")
print("=" * 78)
print("The forward machine is the Sigma*.L recognizer a LOOKBEHIND needs; the")
print("reverse machine is the reverse(L).Sigma* one a LOOKAHEAD needs.")
print()
print("%-12s %-10s | %-19s | %-19s | %s"
      % ("body", "origin", "forward st x cls", "reverse st x cls", "note"))
print("-" * 110)
comp = {}
for body, origin, note in BODIES:
    src, err = artifact(body)
    if src is None:
        print("%-12s %-10s | REFUSED: %s" % (body, origin, err[:50]))
        continue
    d = dims(src)
    comp[body] = d
    print("%-12s %-10s | %5s x %-11s | %5s x %-11s | %s"
          % (body, origin,
             d["forward_states"], d["forward_classes"],
             d["reverse_states"], d["reverse_classes"], note))
print()
print("# A `None` column means the artifact carries no table of that name --")
print("# a VM-routed artifact. `RX_ENGINE` is stamped only for the VM, so its")
print("# ABSENCE is what reads `dfa` below:")
for body in comp:
    print("    %-12s engine=%s" % (body, comp[body]["engine"]))

print()
print("=" * 78)
print("MAIN AUTOMATA")
print("=" * 78)
print("%-28s | %-19s | %-19s | %s"
      % ("main pattern", "forward st x cls", "reverse st x cls", "note"))
print("-" * 100)
mains = {}
for pat, note in MAINS:
    src, err = artifact(pat)
    if src is None:
        print("%-28s | REFUSED: %s" % (pat, err[:50]))
        continue
    d = dims(src)
    mains[pat] = d
    print("%-28s | %5s x %-11s | %5s x %-11s | %s"
          % (pat, d["forward_states"], d["forward_classes"],
             d["reverse_states"], d["reverse_classes"], note))

print()
print("=" * 78)
print("THE PRODUCT BOUND, against the caps")
print("=" * 78)
print("worst-case |D(main)| x |D(component)|, and the STATES x CLASSES figure")
print("beside it, because wave B's own over-cap number (38,009 vs 32,000) was")
print("the second quantity and not the first.")
print()
print("%-24s %-12s | %-9s | %-11s | %-11s | verdict"
      % ("main", "body", "st product", "cls product", "st x cls"))
print("-" * 100)
over = 0
rows = 0
for pat, _n in MAINS:
    if pat not in mains:
        continue
    m = mains[pat]
    for body, origin, _note in BODIES:
        if body not in comp:
            continue
        c = comp[body]
        if not (m["forward_states"] and c["forward_states"]):
            continue
        st = m["forward_states"] * c["forward_states"]
        cls = None
        if m["forward_classes"] and c["forward_classes"]:
            # the product alphabet is at most the product of the two
            # refinements, and at least the coarser -- the UPPER bound is what
            # a decline rule must use
            cls = m["forward_classes"] * c["forward_classes"]
        stcls = st * cls if cls else None
        rows += 1
        verdict = "ok"
        if st > CAP_TABLE:
            verdict = "OVER the 32,000 state cap"
            over += 1
        elif st > CAP_GOTO:
            verdict = "over the 10,000 goto cap (table engine only)"
        print("%-24s %-12s | %9d | %11s | %11s | %s"
              % (pat, body, st, cls, stcls, verdict))
print()
print("ROWS: %d.  Over the 32,000 STATE cap: %d." % (rows, over))
print()
print("VACUITY GUARD: the population must contain at least one row that COULD")
print("be over the cap, or a count measures nothing.")
biggest = max((m["forward_states"] * c["forward_states"]
               for pt, m in mains.items() for b, c in comp.items()
               if m["forward_states"] and c["forward_states"]), default=0)
print("  largest state product in the population: %d  (cap %d)"
      % (biggest, CAP_TABLE))
if biggest < CAP_TABLE:
    print("  !! NO ROW IN THIS POPULATION CAN EXCEED THE CAP, so `over` above")
    print("  !! is unfalsifiable and measures nothing.")
else:
    print("  ok: the population reaches %.0fx the cap, so the split below is a"
          % (float(biggest) / CAP_TABLE))
    print("      real result rather than an artefact of a small population")
print()
print("THE SPLIT THAT MATTERS, because the controls are deliberately extreme:")
ctl_names = set(b for b, o, _n in BODIES if o == "control") | \
            set(p for p, n in MAINS if n.startswith("CONTROL"))
nc = nco = cc = cco = 0
for pat, _n in MAINS:
    if pat not in mains:
        continue
    m = mains[pat]
    for body, origin, _note in BODIES:
        if body not in comp:
            continue
        c = comp[body]
        if not (m["forward_states"] and c["forward_states"]):
            continue
        st = m["forward_states"] * c["forward_states"]
        isctl = (pat in ctl_names) or (body in ctl_names)
        if isctl:
            cc += 1
            cco += 1 if st > CAP_TABLE else 0
        else:
            nc += 1
            nco += 1 if st > CAP_TABLE else 0
print("  CONTROL rows      (a deliberately huge body or main): %3d, %d over cap"
      % (cc, cco))
print("  NON-CONTROL rows  (the assertion expansions + the enumerable real")
print("                     lookaround population)          : %3d, %d over cap"
      % (nc, nco))
print()
print("# THE HONEST READING, and it is the input [ENG-LOOK] asked for rather")
print("# than a verdict this lane is entitled to give:")
print("#  * every component measured here is SMALL -- the bodies the assertion")
print("#    family expands to are one class or one literal, and the real")
print("#    lookaround bodies in an enumerable population are short literals")
print("#    and classes. The product's STATE growth on this population is")
print("#    therefore multiplicative by a small constant, not exponential.")
print("#  * the quantity that bit wave B is STATES x CLASSES, and the ALPHABET")
print("#    product is where a body with its own refinement costs most. That")
print("#    column is the one [ENG-LOOK] should carry into its design gate.")
print("#  * NOTHING HERE MEASURES A PRODUCT. pcrec cannot build one, so every")
print("#    number above is a bound computed from two separately-measured")
print("#    machines. A real product is smaller than the bound whenever the")
print("#    components share structure, and [ENG-LOOK]'s decline rule has to")
print("#    be written against the bound anyway.")
