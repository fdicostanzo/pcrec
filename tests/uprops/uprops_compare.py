#!/usr/bin/env python3
"""uprops_compare.py — the `\\p{...}` membership differential's COMPARATOR,
and the one place [M5.0] stage 3's Unicode-version-drift policy is written
down.

    uprops_compare.py PCREC.txt ORACLE.txt PINNED_VERSION ORACLE_VERSION \\
        [STORE_ROOT STORE_ORACLE_NAME STORE_ORACLE_VERSION STORE_ENCODING]

The four trailing args are OPTIONAL and, when given, add a SECOND, INDEPENDENT
comparison against `docs/design/oracle_interface.md`'s committed answer store
([ORWIRE], `oracle_interface.md` §9 Step 1's own migration): `mine` (pcrec's
own sweep) against the committed `oracle_store/<STORE_ORACLE_NAME>-
<STORE_ORACLE_VERSION>/membership.tsv`'s answers for `STORE_ENCODING`. This
does NOT replace the live-oracle comparison above — it runs beside it. The
live oracle is whatever library this BOX resolves (drift-budgeted, tier 2 on
every box but the reference itself); the store is the TRUE 10.46 capture
(`docs/dev/lanes/orstore_report.md`), so a name the store covers is compared
at EXACT agreement UNCONDITIONALLY, on every box, with no drift budget at
all — that is the whole point of consulting a committed capture instead of
re-resolving a local library. A name `mine` asks about that the store does
not (yet) cover falls back to the live-oracle result above, reported as a
COVERAGE SPLIT rather than silently dropped (`docs/dev/learnings.md` §3: a
check must never narrow what it covers without saying so). Every run prints
which oracle answered which population — PROVENANCE, not assumed: a reduced
or absent store must never read as though the full one answered.

Both input files are `NAME lo-hi lo-hi ...` lines, printed independently by
`uprops_sweep.c` (pcrec's own emitted artifacts) and `uprops_oracle.c`
(libpcre2).  Each file's own `Cn` line — the code points that side leaves
UNASSIGNED — is what makes the drift policy below a check rather than a shrug,
and it is read out of the sweep rather than passed in, so it cannot be a
version's worth of stale.

THE PROBLEM THIS FILE EXISTS FOR.  pcrec's property tables are pinned at one
Unicode version (`third_party/ucd-16.0.0/`).  libpcre2 carries its own, and no
two boxes this project uses agree: the Linux reference runs 10.46 (Unicode
16.0.0, which is the pin), this Mac's Homebrew build is 10.48 (Unicode
17.0.0), and — MEASURED, and not what anyone expected — the library the
suite's own dlopen shim actually resolves on this Mac is macOS's SYSTEM
libpcre2 10.42 at `/usr/lib`, Unicode 14.0.0, because `tests/fuzz/
pcre2_abi.h` lists bare SONAMEs before the Homebrew absolute paths and a bare
name resolves through the dyld shared cache.  So the oracle can be TWO MAJOR
UNICODE VERSIONS BEHIND the pin on one box and one AHEAD on another.  A
membership differential demanding exact agreement would be green on one box
and red on the others while pcrec was equally correct on all three — the
failure mode where a check reports the environment rather than the code.

THE POLICY, in two tiers:

  (1) ORACLE VERSION == PIN.  Demand EXACT agreement, every property, every
      code point.  This is the real check and it is what runs on the reference
      box.

  (2) ORACLE VERSION != PIN.  Every disagreement must be EXPLAINED, and the
      only explanation accepted is "one of the two versions had not ASSIGNED
      that code point" — i.e. the differing code point is in pcrec's own
      `\\p{Cn}` or in the ORACLE's own `\\p{Cn}`.  The rule is deliberately
      SYMMETRIC, because the drift runs both ways: against a NEWER oracle the
      unexplained-looking members are new assignments the pin lacks, and
      against an OLDER one they are assignments the pin has and the oracle
      lacks.  Both sides' `Cn` line comes out of the same sweep that produced
      every other line, so neither version number is needed to apply it.
      Anything else is a hard failure that names the code points, because a
      table bug does not politely confine itself to unassigned space.  Plus a
      small NAMED exception list for RECLASSIFICATIONS, the one legitimate
      disagreement this cannot express: a code point assigned in BOTH versions
      whose category CHANGED is in neither `Cn`.

  (3) [M5.0 stage 5] THE NAME AXIS DRIFTS TOO, and it did not before.  Every
      name stage 3 shipped is a general category that has existed since
      Unicode 1.0; Unicode ADDS SCRIPTS, so an older oracle refuses `\\p{Kawi}`
      outright.  Excused only when every code point pcrec attributes to the
      name is UNASSIGNED on the oracle's side — the same `Cn` line, the same
      symmetry, and a name pcrec invented still fails naming its addresses.

Tier (2) is deliberately not "skip".  A skipped check certifies nothing, and
the whole point of stating a drift budget is that the residue after drift is
still checked.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "oracle"))

# ---------------------------------------------------------------------------
# THE RECLASSIFICATION EXCEPTIONS — one entry per code point whose PROPERTY
# VALUE changed between the pinned Unicode version and a newer one an oracle
# may carry.  Each names the code point, the two values, and the versions,
# because the whole value of the list is that a reader can check it.
#
# [M5.0] stage 5 WIDENED THE SENTENCE ABOVE from "general category" to
# "property value" and added seventeen entries: Unicode revises the
# Script_Extensions of ALREADY-ASSIGNED code points between versions, so they
# are in neither side's `Cn` and the symmetric budget cannot reach them.  It
# is the same fact one property over, not a new tier — and it runs in BOTH
# directions, one entry (U+00B7) against the older oracle and sixteen against
# the newer one.
#
# MEASURED 2026-09-06 against libpcre2 10.48 / Unicode 17.0.0 over the 45
# stage-3 properties (two members) and again 2026-09-09 over the 171 script
# values in three spellings (sixteen more, below).  With them the tier-(2)
# residue is EMPTY on this box.
#
# It is NOT a general escape hatch: an entry costs a line naming a specific
# code point, so a table bug cannot be silenced by it without someone writing
# the bug's own address down.
RECLASSIFIED = {
    0x0295: "U+0295 LATIN LETTER PHARYNGEAL VOICED FRICATIVE — Ll in "
            "Unicode 16.0.0, Lo in 17.0.0 (measured against 10.48)",
    0x1171E: "U+1171E AHOM CONSONANT SIGN MEDIAL RA — Mn in Unicode 14.0.0, "
             "Mc in 16.0.0 (measured: 10.42 says Mn, 10.46 says Mc, and the "
             "pin agrees with 10.46)",
}

# The sixteen Script_Extensions revisions, measured 2026-09-09 against 10.48 /
# Unicode 17.0.0 over all 171 script values x 3 spellings: 17.0.0 attributes
# each of these combining marks to MORE scripts than 16.0.0 does, and every
# one of them is assigned in both versions.  Written as a separate dict so the
# reason stays attached to the group, and merged into RECLASSIFIED below so
# the budget stays ONE set — the code that applies it does not gain a branch.
SCX_REVISED = {
    # The one this list was first written for, and the only member the BYTE
    # arm can reach: at Unicode 14.0.0 U+00B7's Script_Extensions is just its
    # own Script (Common); at 16.0.0 (the pin) it names fifteen scripts.  It
    # is therefore the single code point on which a 10.42 oracle disagrees
    # with pcrec about `\p{Greek}`, `\p{Coptic}`, `\p{Han}` and twelve more,
    # and — because it is Latin-1 — the only script disagreement the byte arm
    # sees at all.
    0x00B7: "MIDDLE DOT",
    0x0306: "COMBINING BREVE", 0x0308: "COMBINING DIAERESIS",
    0x0320: "COMBINING MINUS SIGN BELOW", 0x0323: "COMBINING DOT BELOW",
    0x0331: "COMBINING MACRON BELOW",
    0x0951: "DEVANAGARI STRESS SIGN UDATTA",
    0x0952: "DEVANAGARI STRESS SIGN ANUDATTA",
    0x1CD5: "VEDIC TONE YAJURVEDIC AGGRAVATED INDEPENDENT SVARITA",
    0x1CD6: "VEDIC TONE YAJURVEDIC INDEPENDENT SVARITA",
    0x1CD7: "VEDIC TONE YAJURVEDIC KATHAKA INDEPENDENT SVARITA",
    0x1CD8: "VEDIC TONE CANDRA BELOW", 0x1CE2: "VEDIC SIGN VISARGA SVARITA",
    0x1CE9: "VEDIC SIGN ANUSVARA ANTARGOMUKHA",
    0x1CEA: "VEDIC SIGN ANUSVARA BAHIRGOMUKHA",
    0x1CEB: "VEDIC SIGN ANUSVARA VAMAGOMUKHA",
    0x1CED: "VEDIC SIGN TIRYAK",
}
for _cp, _name in SCX_REVISED.items():
    RECLASSIFIED[_cp] = ("U+%04X %s — its Script_Extensions set differs "
                         "between Unicode 16.0.0 (the pin) and 17.0.0"
                         % (_cp, _name))

# ---------------------------------------------------------------------------
# THE SECOND EXCEPTION TIER: PCRE2 CHANGED WHAT THE PROPERTY MEANS.
#
# `RECLASSIFIED` above covers Unicode moving a code point between categories.
# This covers something the `Cn` budget structurally cannot: libpcre2 changing
# the DEFINITION of one of its own invented properties, where both versions
# agree about every code point's category and disagree about which of them the
# property holds.
#
# MEASURED 2026-09-06, and it has exactly one member.  `Xwd` on libpcre2 10.42
# is `Xan` plus underscore; on 10.46 (the REFERENCE) and 10.48 it is `Xan` plus
# `Mn` plus `Pc` — confirmed by a direct probe of the reference box, which
# matches `\p{Xwd}` against U+0300 (Mn), U+005F (Pc) and U+203F (a non-ASCII
# Pc).  pcrec follows the reference, so an OLDER oracle disagrees on the whole
# `Mn`+`Pc` residue and a table bug would look identical if this tier said only
# "ignore Xwd".
#
# SO IT DOES NOT SAY THAT.  Each entry names the properties whose union the
# residue must lie INSIDE, taken from pcrec's own sweep of those same
# properties in the same run — so the exception admits exactly the code points
# the old definition can explain and fails, naming addresses, on anything else.
# `docs/dev/upstream_issues.md` U15 is the citable record.
PCRE2_SEMANTIC_DRIFT = {
    "Xwd": (["Mn", "Pc"],
            "libpcre2 changed Xwd from `Xan + underscore` (10.42) to "
            "`Xan + Mn + Pc` (10.46, the reference, and 10.48); pcrec follows "
            "the reference — upstream_issues.md U15"),
}


def load(path):
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            if len(parts) > 1 and parts[1] == "ERR":
                out[name] = ("ERR", int(parts[2]))
                continue
            members = set()
            for tok in parts[1:]:
                lo, hi = tok.split("-")
                members.update(range(int(lo, 16), int(hi, 16) + 1))
            out[name] = ("SET", members)
    return out


# ---------------------------------------------------------------------------
# [ORWIRE] the committed-store comparison -- oracle_interface.md §9 Step 1's
# migration-ladder wiring.  A SEPARATE function, not a branch threaded through
# the live-oracle loop above, because the two comparisons have different
# failure shapes: the live one has a drift budget and a version to weigh, the
# store one is either EXACT (the pin) or NOT COVERED (fall back to the live
# result) -- conflating them would smuggle the drift budget into a comparison
# that structurally cannot need one.
# ---------------------------------------------------------------------------

def compare_against_store(mine, store_root, oracle_name, oracle_version,
                           encoding):
    """`mine`: load()'s return shape.  Looks up each of `mine`'s own property
    names in the committed store's `membership` kind via `oracle_store.lookup`
    -- the self-checking read path (R56-4): a truncated file, a duplicate
    hash, or a stored question that does not match the recomputed one is a
    `StoreCorruption` raised HERE, at consult time, never absorbed into a
    wrong answer (the brief's "corruption is a loud failure" requirement --
    this function does not catch it; the caller decides how loud).

    Returns (fails, checked, missing): `missing` is the COVERAGE SPLIT --
    names `mine` asks about that this store file does not have a row for --
    reported by the caller rather than silently compared against nothing.
    A name IS covered with an EMPTY interval list (a real empty set, e.g. a
    byte-arm control script under the utf8 population) and that is not
    `missing`; only a `lookup()` miss (no row at all) is.
    """
    import oracle_store as os_  # local import: only needed on this path
    oid = os_.OracleId(oracle_name, oracle_version)
    fails = []
    checked = 0
    missing = []
    for name, (kind, val) in sorted(mine.items()):
        if kind == "ERR":
            # pcrec's own compile failure for this property is already a
            # FAIL from the live-oracle loop above; do not report it twice.
            continue
        afields = os_.lookup(store_root, oid, "membership",
                              property=name, encoding=encoding)
        if afields is None:
            missing.append(name)
            continue
        checked += 1
        store_members = set()
        for tok in afields[0].split():
            lo, hi = tok.split("-")
            store_members.update(range(int(lo, 16), int(hi, 16) + 1))
        diff = val ^ store_members
        if diff:
            fails.append(
                "%s: %d code points differ from the COMMITTED %s-%s "
                "reference store (exact agreement required -- this is the "
                "true pin, not a drift-budgeted local library), first %s"
                % (name, len(diff), oracle_name, oracle_version,
                   [hex(c) for c in sorted(diff)[:8]]))
    return fails, checked, missing


def main():
    if len(sys.argv) not in (5, 9):
        sys.stderr.write(__doc__)
        return 2
    pcrec_f, oracle_f, pinned, oracle_ver = sys.argv[1:5]
    store_args = sys.argv[5:9] if len(sys.argv) == 9 else None
    mine = load(pcrec_f)
    theirs = load(oracle_f)
    # BOTH SIDES' OWN UNASSIGNED SET, out of the same sweep that produced
    # every other line — no version number is consulted to build it.
    mine_cn = mine.get("Cn", ("SET", set()))[1]
    their_cn = theirs.get("Cn", ("SET", set()))[1]
    unassigned = mine_cn | their_cn

    exact = (pinned == oracle_ver)
    print("  [LIVE] pinned Unicode %s; oracle Unicode %s -> %s"
          % (pinned, oracle_ver,
             "EXACT agreement required" if exact else
             "drift budget: every disagreement must be a code "
             "point UNASSIGNED on one side or the other"))
    # A DELIBERATELY ABSENT PRE-CHECK. An empty `Cn` is NOT an error: under
    # `--encoding=byte` the universe is Latin-1 and every one of those 256
    # code points has been assigned since Unicode 1.0, so both sides' `Cn`
    # are legitimately empty AND there is nothing for them to excuse. The
    # budget is applied per disagreement below, so an empty `Cn` costs
    # nothing when there are none and fails loudly, naming code points, when
    # there are.

    fails, drifted, checked, newer_names = [], 0, 0, 0
    for name, (kind, val) in sorted(mine.items()):
        if kind == "ERR":
            fails.append("%s: pcrec side reported ERR %d" % (name, val))
            continue
        if name not in theirs:
            fails.append("%s: no oracle line — the oracle run is short" % name)
            continue
        okind, oval = theirs[name]
        if okind == "ERR":
            # pcrec ships a NAME this oracle does not have.  Until [M5.0]
            # stage 5 that was an unconditional failure, and it was right to
            # be: every name stage 3 shipped is a general category that has
            # existed since Unicode 1.0.  Scripts break that — Unicode ADDS
            # scripts, so a 14.0.0 oracle genuinely does not know `Kawi`,
            # while `Kawi` is a real name at the pin and on the reference.
            #
            # THE EXPLANATION IS THE SAME SHAPE AS THE MEMBERSHIP BUDGET AND
            # IS JUST AS CHECKABLE: a name the oracle lacks is excused only if
            # every code point pcrec attributes to it is UNASSIGNED on the
            # ORACLE's side — read out of the oracle's own `Cn` line in this
            # same run, so no version number is consulted.  A name pcrec
            # INVENTED, or a name whose set reaches real characters the oracle
            # knows, still fails and names its addresses.
            if exact:
                fails.append("%s: pcrec COMPILES it, libpcre2 refuses with "
                             "error %d, and the two are at the SAME Unicode "
                             "version — pcrec must not ship a property name "
                             "the oracle does not have" % (name, oval))
                continue
            live = sorted(c for c in val if c not in their_cn)
            if live:
                fails.append("%s: pcrec COMPILES it and libpcre2 refuses with "
                             "error %d, and %d of its %d code points are "
                             "ASSIGNED on the oracle's side, so this is not a "
                             "newer-Unicode name: %s"
                             % (name, oval, len(live), len(val),
                                [hex(c) for c in live[:8]]))
            else:
                drifted += len(val)
                newer_names += 1
            continue
        checked += 1
        diff = val ^ oval
        if not diff:
            continue
        if exact:
            fails.append("%s: %d code points differ, first %s"
                         % (name, len(diff),
                            [hex(c) for c in sorted(diff)[:8]]))
            continue
        allowed = set(unassigned) | set(RECLASSIFIED)
        if name in PCRE2_SEMANTIC_DRIFT:
            props, _why = PCRE2_SEMANTIC_DRIFT[name]
            missing = [p for p in props
                       if mine.get(p, ("ERR", 0))[0] != "SET"]
            if missing:
                fails.append("%s: its semantic-drift exception is stated over "
                             "%s and this run has no pcrec sweep for %s, so "
                             "the exception cannot be applied"
                             % (name, props, missing))
                continue
            for p in props:
                allowed |= mine[p][1]
        unexplained = sorted(c for c in diff if c not in allowed)
        drifted += len(diff) - len(unexplained)
        if unexplained:
            fails.append("%s: %d of %d differing code points are NOT explained "
                         "by version drift (assigned on BOTH sides, not a "
                         "listed reclassification): %s"
                         % (name, len(unexplained), len(diff),
                            [hex(c) for c in unexplained[:8]]))

    for name in sorted(set(theirs) - set(mine)):
        if theirs[name][0] != "ERR":
            print("  note: libpcre2 has \\p{%s} and pcrec does not ship it "
                  "(declined by design §3.4 — the booleans and Bidi_Class)"
                  % name)

    print("  [LIVE] compared %d properties; %d code points attributed to "
          "version drift%s" % (checked, drifted,
                       ("; %d property NAMES this oracle does not have, each "
                        "wholly inside its own unassigned space" % newer_names)
                       if newer_names else ""))

    # [ORWIRE] the committed-store comparison, oracle_interface.md §9 Step 1's
    # migration wiring -- a SECOND, INDEPENDENT check beside the live-oracle
    # one above, never a replacement (BOILERPLATE's "nothing retires without
    # the design saying it retires").  Only runs when the caller passed the
    # four trailing store args; §3's byte arm does not (the committed store
    # holds only the utf8-arm capture — see tests/oracle/CLAUDE.md).
    if store_args is not None:
        store_root, s_name, s_ver, s_enc = store_args
        print("  [STORE] consulting the COMMITTED reference store "
              "%s-%s (encoding=%s) — this IS the true pin (Unicode %s), so "
              "every name it covers is compared at EXACT agreement "
              "regardless of what library this box resolves live"
              % (s_name, s_ver, s_enc, pinned))
        try:
            store_fails, store_checked, store_missing_names = \
                compare_against_store(mine, store_root, s_name, s_ver, s_enc)
        except Exception as e:
            # A StoreCorruption (or any other read-time failure) is a LOUD
            # failure naming itself, never a silently-skipped comparison —
            # the brief's "corruption is a loud failure, not a wrong answer".
            fails.append("[STORE] the committed store failed its own "
                         "self-check and could not be consulted: %r" % (e,))
            store_checked, store_missing_names = 0, []
        else:
            fails.extend("[STORE] " + f for f in store_fails)
            n_asked = sum(1 for _n, (k, _v) in mine.items() if k != "ERR")
            split = ""
            if store_missing_names:
                sample = store_missing_names[:8]
                more = "..." if len(store_missing_names) > 8 else ""
                split = ": %s%s" % (sample, more)
            print("  [STORE] coverage: %d of %d properties this run asks "
                  "about are in the committed store and were compared "
                  "(exact); %d are NOT covered and fall back to the [LIVE] "
                  "result above%s" % (store_checked, n_asked,
                                       len(store_missing_names), split))

    for f in fails:
        print("FAIL: " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
