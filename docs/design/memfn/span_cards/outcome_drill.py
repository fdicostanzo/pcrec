# span_cards rev 1.2 drill (lane s2rev12): §3.5's OUTCOME table (review 2026-11-06 r6 MEAS-2, MEAS-3, MEAS-7),
# implemented as the first-match table the text writes, over §3.7's jobs and §2.5's keys, on constructed run
# outcomes (the r6 critic's scenarios S3, S5, S6, S7, S8 among them). Prints each scenario's inputs, the
# first matching row, the outcome, its causes and `partial`; then HELD over pairs of runs.
# The table (first match wins; §3.5):
#   1 UNIT     the unit row fails its half gate or its bimodal test          -> REFUSED, cause class `unit`
#   2 FLOOR    an ACTIVE floor clause has no priced key                      -> REFUSED, cause `floor:<clause>`
#              with each of the clause's keys' reason: `text` (a cost row over its gate, a delta row NULL),
#              `drift:J<j>` (its job drift-refused) or `never-ran:J<j>`
#   3 PARTIAL  some planned key is absent (never ran, drift-refused job, cost row over its gate) -> exit 4
#   4 FULL     otherwise                                                       -> exit 0
# A clause is ACTIVE unless the run record's J1 verdict is (b) and the clause is a pair clause. A cost row
# passes or fails ALONE (MEAS-3); a job's drift refusal removes every row of the job. HELD: two REFUSED runs
# sharing a cause of a TEXT class (`unit`, or one `floor:<clause>` whose keys are unpriced by `text` in both
# runs); a `drift` or `never-ran` cause is box state or a job failure and is never HELD.
# INPUTS (§3.7, tree_drill.py's): 8 census verify pairs over 2 cls, 3 consumer kinds; J1's verdict per scenario.
# python3 -I outcome_drill.py
PAIRS = [("settest", "c0"), ("settest", "c1"), ("rc-words", "c0"), ("rc-words", "c1"),
         ("rc-overlap", "c0"), ("rc-bytes", "c1"), ("rc-memcmp", "c0"), ("rc-memcmp", "c1")]   # 8 stand-ins, 2 cls
KINDS = ["k1", "k2", "k3"]

plan = {}                                   # key -> (job, group, cost?)
def add(key, job, group, cost):
    plan["kit." + key] = (job, group, cost)
add("find_byte.walk", "J2", "J2.unit", True)
for f in ("libc", "walk-set"):
    add("find_byte." + f, "J2", "J2.byte", True)
add("find_byte.pair", "J2p", "J2p.byte", True)
for land in ("periodic", "random"):
    for g in (256, 1024):
        for f, sp in (("libc", "one"), ("walk", "one"), ("walk-set", "alt")):
            add("find_hit.%s.%s.%s.%d" % (f, land, sp, g), "J3", "J3.hit.%s.%d" % (land, g), False)
        for sp in ("one", "alt"):
            add("find_hit.pair.%s.%s.%d" % (land, sp, g), "J2p", "J2p.hit.%s.%d" % (land, g), False)
for f, cls in PAIRS:
    for p in ("p0", "p50"):
        add("verify_cmp.%s.%s.%s" % (f, cls, p), "J4", "J4.verify.%s" % cls, False)
for k in KINDS:
    for e in ("NONE", "PARKED", "RESEED"):
        add("enter.%s.%s" % (k, e), "J5", "J5.enter.%s" % k, False)

floor = {}                                  # the run record's floor section: clause -> its keys
for f in ("walk", "libc", "walk-set", "pair"):
    floor["byte." + f] = ["kit.find_byte." + f]
    floor["hit." + f] = [k for k in plan if k.startswith("kit.find_hit.%s." % f) and ".random." in k]
for f, cls in PAIRS:
    floor["verify.%s.%s" % (f, cls)] = ["kit.verify_cmp.%s.%s.%s" % (f, cls, p) for p in ("p0", "p50")]
for k in KINDS:
    floor["enter." + k] = ["kit.enter.%s.NONE" % k]
PAIR_CLAUSES = {"byte.pair", "hit.pair"}

def outcome(sc):
    """sc: unit ('pass'|'gate'|'bimodal'), j1 ('a'|'b'|'c'), never (jobs), drift (jobs), over (cost keys over
    their gate), null (delta keys NULL). Returns (row, outcome, causes, partial, unpriced reasons)."""
    never = set(sc.get("never", ()))
    if sc.get("j1") == "b":
        never.add("J2p")
    drift, over, null = set(sc.get("drift", ())), set(sc.get("over", ())), set(sc.get("null", ()))
    reason = {}
    for key, (job, group, cost) in plan.items():
        if job in never:
            reason[key] = "never-ran:" + job
        elif job in drift:
            reason[key] = "drift:" + job
        elif key in over or key in null:
            reason[key] = "text"
    absent = [k for k, r in reason.items() if r != "text" or plan[k][2]]   # a NULL delta row is present, null
    if sc.get("unit", "pass") != "pass":
        return 1, "REFUSED", ["unit"], None, reason
    active = [c for c in floor if not (sc.get("j1") == "b" and c in PAIR_CLAUSES)]
    failed = [c for c in active if all(k in reason for k in floor[c])]
    if failed:
        causes = ["floor:%s(%s)" % (c, ",".join(sorted({reason[k] for k in floor[c]}))) for c in failed]
        return 2, "REFUSED", causes, None, reason
    if absent:
        return 3, "PARTIAL", ["%d keys absent" % len(absent)], 1, reason
    return 4, "FULL", [], 0, reason

def text_causes(sc):
    row, out, causes, _, reason = outcome(sc)
    if out != "REFUSED":
        return set()
    if row == 1:
        return {"unit"}
    return {c.split("(")[0] for c in causes if c.endswith("(text)")}

hit = lambda f, land: [k for k in plan if k.startswith("kit.find_hit.%s." % f) and (".%s." % land) in k]
S = [
    ("S1 clean", {"j1": "a"}),
    ("S2 J1 (b): J2p held out", {"j1": "b"}),
    ("S3 J3 drift-refused (r6 S3)", {"j1": "c", "drift": ["J3"]}),
    ("S4 unit bimodal", {"j1": "a", "unit": "bimodal"}),
    ("S4g unit over its half gate", {"j1": "a", "unit": "gate"}),
    ("S5 every non-unit group refused", {"j1": "a", "drift": ["J2p", "J3", "J4", "J5"],
                                         "over": ["kit.find_byte.libc", "kit.find_byte.walk-set"]}),
    ("S6 all non-unit refused but J3 (r5 GOAL2)", {"j1": "a", "drift": ["J2p", "J4", "J5"],
                                                   "over": ["kit.find_byte.libc", "kit.find_byte.walk-set"]}),
    ("S7 walk-set byte over its gate (MEAS-3)", {"j1": "a", "over": ["kit.find_byte.walk-set"]}),
    ("S8 J4 and J5 drift-refused", {"j1": "a", "drift": ["J4", "J5"]}),
    ("S9 every periodic hit row NULL", {"j1": "a", "null": [k for f in ("libc", "walk", "walk-set", "pair")
                                                            for k in hit(f, "periodic")]}),
    ("S10 every random walk hit row NULL", {"j1": "a", "null": hit("walk", "random")}),
    ("S11 J2p failed, J1 (c)", {"j1": "c", "never": ["J2p"]}),
    ("S12 J1 (b) and J3 drift-refused", {"j1": "b", "drift": ["J3"]}),
    ("S13 one random walk hit row NULL", {"j1": "a", "null": hit("walk", "random")[:1]}),
]
print("plan: %d keys over %d jobs; floor: %d clauses (%d pair clauses)" % (
    len(plan), len({v[0] for v in plan.values()}), len(floor), len(PAIR_CLAUSES)))
reach = {}
for name, sc in S:
    row, out, causes, partial, _ = outcome(sc)
    reach.setdefault(row, []).append(name.split()[0])
    print("%-44s inputs %s\n    -> row %d %s causes %s partial %s" % (name, {k: (v if len(v) < 6 else "%d keys" % len(v))
          if isinstance(v, list) else v for k, v in sc.items()}, row, out, causes, partial))
print("rows reached: " + "; ".join("row %d by %s" % (r, ", ".join(v)) for r, v in sorted(reach.items())))
print("\nHELD over two REFUSED runs (a shared TEXT-class cause):")
named = dict(S)
for a, b in (("S4 unit bimodal", "S4g unit over its half gate"), ("S3 J3 drift-refused (r6 S3)", "S3 J3 drift-refused (r6 S3)"),
             ("S10 every random walk hit row NULL", "S10 every random walk hit row NULL"),
             ("S7 walk-set byte over its gate (MEAS-3)", "S10 every random walk hit row NULL"),
             ("S11 J2p failed, J1 (c)", "S11 J2p failed, J1 (c)")):
    shared = text_causes(named[a]) & text_causes(named[b])
    print("  %-40s then %-40s -> %s" % (a.split(" ")[0], b.split(" ")[0], "HELD on %s" % sorted(shared) if shared
                                        else "re-run (no shared text cause)"))
