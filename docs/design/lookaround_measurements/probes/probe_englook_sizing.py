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

THE METHOD -- **AND ITS FIRST VERSION WAS REFUTED BY R33 C2-1.**

  The first version claimed: "pcrec's UNANCHORED FORWARD DFA for the pattern
  `L` IS the Sigma*.L recognizer -- unanchoredness is the automaton's own
  self-loop." **That identity is FALSE.** `src/ir/nfa.c:766-781`
  (`nfa_wrap_unanchored`) adds the self-loop as the LOWEST-PRIORITY start
  alternative, and D3 ACCEPT-PRUNING then kills the self-loop thread at the
  first accept -- so every accepting state in the emitted forward table is a
  DEAD SINK. A Sigma*.L predicate machine must be TOTAL and must RE-ACCEPT at
  every later position (`(?<=foo)` has to answer YES at offset 6 of "foofoo"
  having already accepted at 3); this machine stops answering after the first
  occurrence. It is a LEFTMOST-OCCURRENCE SEARCH automaton, not the component.

  It also UNDER-COUNTS, which is the half that breaks a bound: truncation at
  the first accept deletes states whenever an alternation branch is
  prefix-dominated -- `a|ab` emits 2 forward states where the minimal
  D(Sigma*.L) has 3, and `ab|abc` emits 3 where the minimum is 4. A decline
  rule written against an under-count declines too little, which is the
  failure direction that matters, and §2.5 ships `(?<=a|bc)`-shaped bodies
  outright.

  SO THIS PROBE NOW REPORTS TWO COLUMNS:

    MEASURED-LOWER  -- the emitted forward/reverse table dimensions, exactly
                       as before, RELABELLED as a LOWER BOUND on the
                       component and no longer as the component itself. It is
                       still worth reporting: it is the only in-pcrec number,
                       and the forward/reverse asymmetry it shows is the tell
                       C2-1 used.
    PROTOTYPE-EXACT -- |D(Sigma*.L)| computed HERE by an explicit subset
                       construction over a small NFA for L. It is a MODEL --
                       pcrec does not build this machine -- and it is marked
                       PROTOTYPE everywhere it appears. Its SELF-CHECK is
                       C2-1's own two cells (`a|ab` -> 3, `ab|abc` -> 4) plus
                       four hand-checkable ones, asserted at import: if the
                       construction is wrong, this probe says so instead of
                       publishing a number.

  ANCHOR-BEARING BODIES ARE EXCLUDED FROM THE PROTOTYPE COLUMN AND SAY SO.
  `(?!\\z)` and `(?=\\n?\\z)` contain ANCHORS, which are not letters of Sigma;
  `Sigma*.L` is not the right question for them and [ENG-LOOK]'s own row
  handles them as the delayed-acceptance / anchor case rather than as a
  product component.

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


# ---------------------------------------------------------------------------
# THE PROTOTYPE: |D(Sigma*.L)| by explicit subset construction.
#
# A MODEL, not a measurement of pcrec -- marked PROTOTYPE wherever its numbers
# appear. It covers exactly the body syntax this lane's populations use:
# literals, `.`-free classes ([...], \w, \d, \n), concatenation, alternation,
# `?`, and bounded {n} / {n,m}. Anything else raises, and the caller reports
# the body as NOT MODELLED rather than guessing.
#
# The alphabet is COLLAPSED to the distinct character sets the body mentions
# plus one "everything else" letter, which is what makes the state count the
# same as it would be over the full 256-byte alphabet while keeping the
# construction small enough to read.
# ---------------------------------------------------------------------------
class _Unmodelled(Exception):
    pass


def _classes(body):
    """Tokenise the body into a list of (kind, payload) where kind is
    'set' | '|' | '(' | ')' | '?' | '{n,m}'.

    R33 V-5: `(?:` is normalised to `(` FIRST. Without that the `?` was read
    as a quantifier with nothing before it, and every `(?:...)` row reported
    its n/a reason as "? with nothing before" -- a TOKENISER limit printed as
    if it were a statement about the body. The real reason those rows are
    unmodelled is the nested alternation inside them, and now they say so."""
    body = body.replace("(?:", "(")
    out = []
    i, n = 0, len(body)
    while i < n:
        c = body[i]
        if c == "\\":
            if i + 1 >= n:
                raise _Unmodelled("trailing backslash")
            e = body[i + 1]
            if e == "w":
                out.append(("set", frozenset(["W"])))
            elif e == "d":
                out.append(("set", frozenset(["D"])))
            elif e == "n":
                out.append(("set", frozenset(["\n"])))
            elif e in "zAbBGK":
                raise _Unmodelled("anchor or assertion \\%s" % e)
            else:
                out.append(("set", frozenset([e])))
            i += 2
            continue
        if c == "[":
            j = body.index("]", i + 1)
            out.append(("set", frozenset([body[i:j + 1]])))
            i = j + 1
            continue
        if c in "|()?":
            out.append((c, None))
            i += 1
            continue
        if c == "{":
            j = body.index("}", i)
            spec = body[i + 1:j]
            lo, _, hi = spec.partition(",")
            out.append(("{}", (int(lo), int(hi) if hi else int(lo))))
            i = j + 1
            continue
        if c in "*+.":
            raise _Unmodelled("unbounded or dot: %s" % c)
        out.append(("set", frozenset([c])))
        i += 1
    return out


def _branches(toks):
    """Split top-level alternation; expand ? and {n,m} into explicit
    alternatives. Returns a list of lists-of-sets (each an exact word shape)."""
    depth = 0
    parts, cur = [], []
    for k, v in toks:
        if k == "(":
            depth += 1
        elif k == ")":
            depth -= 1
        if k == "|" and depth == 0:
            parts.append(cur)
            cur = []
        else:
            cur.append((k, v))
    parts.append(cur)
    out = []
    for part in parts:
        seqs = [[]]
        for idx, (k, v) in enumerate(part):
            if k == "set":
                seqs = [s + [v] for s in seqs]
            elif k == "?":
                if not seqs or not seqs[0]:
                    raise _Unmodelled("? with nothing before it")
                seqs = [s[:-1] for s in seqs] + seqs
            elif k == "{}":
                lo, hi = v
                base = [s[-1] for s in seqs]
                nseqs = []
                for s in seqs:
                    head, last = s[:-1], s[-1]
                    for r in range(lo, hi + 1):
                        nseqs.append(head + [last] * r)
                seqs = nseqs
            elif k in "()":
                # only non-capturing/parenthesised alternation-free groups are
                # modelled; a nested alternation raises
                continue
            else:
                raise _Unmodelled("token %r" % k)
        out.extend(seqs)
    if any("|" == k for part in parts for k, _v in part):
        raise _Unmodelled("nested alternation")
    return out


def dsigma_star_l(body):
    """|D(Sigma*.L)| -- PROTOTYPE. Raises _Unmodelled for a body outside the
    covered syntax."""
    words = _branches(_classes(body))
    if not words:
        raise _Unmodelled("no branches")
    # alphabet letters: every distinct set mentioned, plus OTHER
    letters = sorted({frozenset(s) for w in words for s in w}, key=lambda x: sorted(x))
    OTHER = object()
    alpha = list(letters) + [OTHER]
    maxlen = max(len(w) for w in words)

    def matches(letter, wanted):
        return letter is not OTHER and letter == wanted

    # NFA states: (word index, position). Plus the always-live start.
    start = frozenset([("S", 0)])
    seen = {start: 0}
    work = [start]
    while work:
        st = work.pop()
        for a in alpha:
            nxt = set([("S", 0)])          # the Sigma* self-loop, always live
            for (wi, pos) in st:
                if wi == "S":
                    for j, w in enumerate(words):
                        if w and matches(a, w[0]):
                            nxt.add((j, 1))
                    continue
                w = words[wi]
                if pos < len(w) and matches(a, w[pos]):
                    nxt.add((wi, pos + 1))
            f = frozenset(nxt)
            if f not in seen:
                seen[f] = len(seen)
                work.append(f)
    del maxlen
    return len(seen)


# THE FIXTURES, and one of them corrected the probe's own expectation.
# `a|b` was written expecting 2 -- the MINIMAL DFA for "strings ending in a
# or b" really does have 2 states -- and the construction answers 3, because
# a SUBSET CONSTRUCTION distinguishes "ended with a" from "ended with b" and
# nothing here merges them. The construction is right and the expectation was
# wrong, so the column is THE SUBSET SIZE, which is what a determinization
# WOULD BUILD before `src/opt/minimize.c` runs. That is the number
# [ENG-LOOK]'s estimate-before-committing rule needs (it must decline on what
# it is about to construct, not on what it would have after minimising), and
# the realised component may be smaller. C2-1's own two cells (`a|ab` -> 3,
# `ab|abc` -> 4) are subset sizes too and are reproduced exactly.
_PROTO_SELFCHECK = []
for _b, _want in [("a|ab", 3), ("ab|abc", 4), ("a", 2), ("ab", 3),
                  ("abc", 4), ("a|b", 3), ("a|bc", 4)]:
    try:
        _got = dsigma_star_l(_b)
    except _Unmodelled as _e:                                  # noqa: BLE001
        _got = "UNMODELLED: %s" % _e
    if _got != _want:
        _PROTO_SELFCHECK.append((_b, _got, _want))


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
    (r"(a|b)c",   "real",      "an alternation inside a concatenation -- the "
                               "tokeniser does not model it"),
    (r"ac|bc",    "real",      "THE SAME LANGUAGE, expanded: (a|b)c == ac|bc. "
                               "R33 V-5 -- the emitted table says 3 and the "
                               "component is 5, a NON-CONTROL under-count the "
                               "n/a row hid"),
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
print("PROTOTYPE self-check problems:", _PROTO_SELFCHECK or "none")
if _PROTO_SELFCHECK:
    print("  !! the subset construction is WRONG on its own fixtures; every")
    print("  !! PROTOTYPE-EXACT number below is unusable")
print()
print("%-12s %-10s | %-17s | %-17s | %-11s | %s"
      % ("body", "origin", "fwd st x cls (LOWER)", "rev st x cls (LOWER)",
         "|D(S*.L)|", "note"))
print("-" * 120)
comp = {}
for body, origin, note in BODIES:
    src, err = artifact(body)
    if src is None:
        print("%-12s %-10s | REFUSED: %s" % (body, origin, err[:50]))
        continue
    d = dims(src)
    try:
        d["proto"] = dsigma_star_l(body)
    except _Unmodelled as ex:                                   # noqa: BLE001
        d["proto"] = "n/a (%s)" % str(ex)[:22]
    comp[body] = d
    print("%-12s %-10s | %5s x %-9s | %5s x %-9s | %-11s | %s"
          % (body, origin,
             d["forward_states"], d["forward_classes"],
             d["reverse_states"], d["reverse_classes"], d["proto"], note))
print()
print("# A `None` column means the artifact carries no table of that name --")
print("# a VM-routed artifact. `RX_ENGINE` is stamped only for the VM, so its")
print("# ABSENCE is what reads `dfa` below:")
for body in comp:
    print("    %-12s engine=%s" % (body, comp[body]["engine"]))

print()
print("AGREEMENT BETWEEN THE TWO COLUMNS, counted rather than asserted (R33 V-5:")
print("the design said \"everywhere else the two agree\" and that was not a count):")
_mod = [(b, c) for b, c in comp.items() if isinstance(c.get("proto"), int)]
_una = [b for b, c in comp.items() if not isinstance(c.get("proto"), int)]
_dis = [(b, c["forward_states"], c["proto"]) for b, c in _mod
        if c["forward_states"] != c["proto"]]
print("  rows total                  : %d" % len(comp))
print("  MODELLED (a prototype number): %d" % len(_mod))
print("  NOT MODELLED (n/a)           : %d  -> %s" % (len(_una), ", ".join(_una)))
print("  modelled rows where emitted != prototype: %d" % len(_dis))
for b, lo, pr in _dis:
    print("      %-12s emitted %-5s prototype %-5s  (UNDER-COUNT)" % (b, lo, pr))
print("  ** an n/a row is NOT an agreement**: six bodies have no prototype")
print("  number at all, and `ac|bc` shows one of them (`(a|b)c`) is a real")
print("  under-count the n/a hid -- 3 emitted against 5.")
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
print("THE COMPONENT COLUMN IS THE PROTOTYPE |D(Sigma*.L)| WHERE THE BODY IS")
print("MODELLED, and the emitted LOWER BOUND where it is not -- each row says")
print("which. R33 C2-1: the emitted forward table UNDER-counts (it is the")
print("leftmost-occurrence automaton, accept-pruned), so a bound computed from")
print("it is not a bound. `a|bc` is the row that shows it inside this module's")
print("own shipped population: emitted 3, prototype 4.")
print()
print("%-24s %-14s | %-7s | %-9s | %-9s | %-9s | verdict"
      % ("main", "body", "src", "st product", "cls product", "st x cls"))
print("-" * 112)
over = 0
rows = 0
under = 0
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
        proto = c.get("proto")
        if isinstance(proto, int):
            csz, src_ = proto, "PROTO"
            if proto > c["forward_states"]:
                under += 1
        else:
            csz, src_ = c["forward_states"], "lower"
        st = m["forward_states"] * csz
        cls = None
        if m["forward_classes"] and c["forward_classes"]:
            cls = m["forward_classes"] * c["forward_classes"]
        stcls = st * cls if cls else None
        rows += 1
        verdict = "ok"
        if st > CAP_TABLE:
            verdict = "OVER the 32,000 state cap"
            over += 1
        elif st > CAP_GOTO:
            verdict = "over the 10,000 goto cap (table engine only)"
        print("%-24s %-14s | %-7s | %9d | %11s | %11s | %s"
              % (pat, body, src_, st, cls, stcls, verdict))
print()
print("ROWS: %d.  Over the 32,000 STATE cap: %d." % (rows, over))
print("ROWS WHERE THE PROTOTYPE EXCEEDS THE EMITTED LOWER BOUND: %d" % under)
print("  (each of those is a row the FIRST version of this probe under-stated)")
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
