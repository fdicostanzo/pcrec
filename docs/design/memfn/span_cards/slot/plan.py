# span_cards/slot/plan.py — THE PLAN of the stage-2 window (span_cards.md §2.4-§2.5, §3.3, §3.5, §3.7): every
# row key the run plans, its group, job, arms and estimator; the delta bases; the floor's clauses. The ONE
# source the slot harness's other parts read (link.py, run.py, est.py, record.py); the recompute (S2e) reads
# the run record's copy, never this file.
#
# Populations: the find forms are §2.5's (walk the unit, libc, pair); `walk-set` is FOLDED into `walk` (§2.4: the
# hash decides): formhash.c's entry table renders the composer's FIND over `{X,x}` named by pcrec's table as
# the walk's text byte for byte, so its keys are not planned (formhash.c's entry-table comment); the verify (form, cls) pairs are
# vcls.out's (the census's sites re-classed by the text's boundaries, vcls.py); the `enter` kinds are
# census0.out's "(2) the card population" `enter kind=K` lines (RTE and DEF), entries NONE (the floor's) plus
# PARKED and RESEED where enter/fixtures.tsv names a fixture (a pair no fixture reaches is reported by
# `plan.py report`, never forced). J1's cells are j1/'s.
#   python3 -I plan.py report      the plan, the floor, the counts (§3.7's table, recounted)
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# SLOT_TREE: the tree when slot/ runs from a copy (sabotage.sh plants in scratch copies)
TREE = os.environ.get("SLOT_TREE") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
CENSUS0 = os.path.join(TREE, "docs", "design", "memfn", "span_pick", "census0.out")
VCLS = os.path.join(HERE, "vcls.out")
ENTER_FIX = os.path.join(HERE, "enter", "fixtures.tsv")

LENGTHS = (65536, 262144, 1048576)     # find_byte's slope (§2.3)
LEN = 1048576                          # every delta row's LEN
GAPS = (256, 1024)
LANDINGS = ("periodic", "random")
PASSES = ("p0", "p50")
L_LAUNCHES, R_ROUNDS = 7, 7            # the cards' launches and rounds (§2.1)
GATE_E6 = 30000                        # the cards' gate_e6 (UNMEASURED DEFAULT carried, §2.4)
CAND_STRIDE = 64                       # a verify candidate every 64 bytes (slot.h; UNMEASURED DEFAULT, D149)

def census_enter_kinds():
    kinds = set()
    for ln in open(CENSUS0):
        m = re.match(r"(RTE|DEF) enter kind=(\d+) ", ln)
        if m:
            kinds.add(int(m.group(2)))
    return sorted(kinds)

def vcls_pairs():
    pairs = set()
    for ln in open(VCLS):
        f = ln.rstrip("\n").split("\t")
        if len(f) == 5 and f[1] == "verify" and int(f[4]) > 0:
            pairs.add((f[2], f[3]))
    return sorted(pairs)

ENTER_GAP = 256                        # an `enter` candidate every 256 bytes (§2.3)
J1_WIDTHS = (32, 64, 128, 256, 512)    # §3.6; 128 carries the twin 128#b
J1_SUBJECTS = ("mixed", "qs")          # j1/subjects.py: the bench capability subjects' two shapes
J1_REGIMES = (("throughput", 1048576), ("short", 524288))   # j1/subjects.py LEN_TPUT, LEN_SHORT

def j1_pattern_ids():
    return [ln.split("\t")[0] for ln in open(os.path.join(HERE, "j1", "patterns.tsv"))
            if ln.strip() and not ln.startswith("#")]

def enter_fixtures():
    fx = {}
    for ln in open(ENTER_FIX):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        fx[(int(f[0]), f[1])] = f
    return fx

class Arm:
    """One timed arm: its name (a row key, KEY#b, base.<name> or ctl), the job group, its shape and lengths."""
    def __init__(self, name, group, kind, form, cls=None, lengths=(LEN,), landing=None, split=None, gap=None,
                 pas=None, base=None, events=None, fixture=None):
        self.name, self.group, self.kind, self.form, self.cls = name, group, kind, form, cls
        self.lengths, self.landing, self.split, self.gap = lengths, landing, split, gap
        self.pas, self.base, self.events, self.fixture = pas, base, events, fixture

    def twin(self):
        t = Arm(self.name + "#b", self.group, self.kind, self.form, self.cls, self.lengths, self.landing,
                self.split, self.gap, self.pas, self.base, self.events, self.fixture)
        return t

def find_hit_rows(form, splits):
    return [(form, ld, sp, g) for g in GAPS for ld in LANDINGS for sp in splits]

def build():
    """The plan: jobs -> groups -> arms (twins included), the rows (key, group, job, estimator, base),
    the floor's clauses (clause, key, when), and what the plan could not reach."""
    jobs, rows, floor, unreached = {}, [], [], []
    def add(job, arm):
        jobs.setdefault(job, []).append(arm)
    def row(job, arm, est, base=None, twin=True):
        rows.append((arm.name, arm.group, job, est, base))
        add(job, arm)
        if twin:
            add(job, arm.twin())
    sl = "slope " + ",".join(str(x) for x in LENGTHS)
    # J2: the unit group (walk and its twin ONLY, §2.2) and the byte group (libc, walk-set)
    row("J2", Arm("kit.find_byte.walk", "J2.unit", "find", "walk", lengths=LENGTHS), sl)
    row("J2", Arm("kit.find_byte.libc", "J2.byte", "find", "libc", lengths=LENGTHS), sl)
    # J2p: pair, its byte row and its hit rows, the base on its own job (§3.7)
    row("J2p", Arm("kit.find_byte.pair", "J2p.byte", "find", "pair", lengths=LENGTHS), sl)
    add("J2p", Arm("base.pair", "J2p.base", "find", "pair", events=0))
    for form, ld, sp, g in find_hit_rows("pair", ("one", "alt")):
        row("J2p", Arm("kit.find_hit.pair.%s.%s.%d" % (ld, sp, g), "J2p.hit.%s.%d" % (ld, g), "find", "pair",
                       landing=ld, split=sp, gap=g, base="base.pair", events=LEN // g),
            "delta %d" % LEN, "base.pair")
    # J3: libc one, walk one (walk-set alt folded into walk); bases on J3.base
    for f in ("libc", "walk"):
        add("J3", Arm("base.%s" % f, "J3.base", "find", f, events=0))
    for g in GAPS:
        for ld in LANDINGS:
            for f, sp in (("libc", "one"), ("walk", "one")):
                row("J3", Arm("kit.find_hit.%s.%s.%s.%d" % (f, ld, sp, g), "J3.hit.%s.%d" % (ld, g), "find", f,
                              landing=ld, split=sp, gap=g, base="base.%s" % f, events=LEN // g),
                    "delta %d" % LEN, "base.%s" % f)
    # J4: verify_cmp per (form, cls), each cls its own null base
    pairs = vcls_pairs()
    for cls in sorted({c for _f, c in pairs}):
        add("J4", Arm("base.null.%s" % cls, "J4.base", "verify", "null", cls=cls, events=0))
    for f, c in pairs:
        for p in PASSES:
            row("J4", Arm("kit.verify_cmp.%s.%s.%s" % (f, c, p), "J4.verify.%s" % f, "verify", f, cls=c, pas=p,
                          base="base.null.%s" % c, events=LEN // CAND_STRIDE), "delta %d" % LEN, "base.null.%s" % c)
    # J5 (art.py): enter per (kind, entry) with a fixture; the fail subject is the base. events: the pass
    # subject's candidates (one per ENTER_GAP bytes), 0 on the fail base (§3.4 step 1)
    fx = enter_fixtures()
    for k in census_enter_kinds():
        for e in ("NONE", "PARKED", "RESEED"):
            if (k, e) not in fx or fx[(k, e)][2] == "-":
                why = fx[(k, e)][-1] if (k, e) in fx else "no fixture pattern states kind %d with a %s alternative" % (k, e)
                unreached.append("enter.%d.%s: %s" % (k, e, why))
                continue
            b = "base.fail.%d.%s" % (k, e)
            add("J5", Arm(b, "J5.base", "enter", "artifact", fixture=fx[(k, e)], events=0))
            row("J5", Arm("kit.enter.%d.%s" % (k, e), "J5.enter", "enter", "artifact", fixture=fx[(k, e)], base=b,
                          events=LEN // ENTER_GAP), "delta %d" % LEN, b)
    # J1 (§3.6, art.py, j1/): per cell (pattern, subject, regime) one group, a whole-artifact arm per PAIR width
    # and the twin 128#b; no rows (J1's cells go to the run record, never the set)
    for pid in j1_pattern_ids():
        for subj in J1_SUBJECTS:
            for regime, n in J1_REGIMES:
                g = "J1.%s.%s.%s" % (pid, subj, regime)
                for w in J1_WIDTHS:
                    a = Arm("j1.%s.%s.%s.%d" % (pid, subj, regime, w), g, "j1", "artifact", lengths=(n,),
                            fixture=(pid, subj, regime, w))
                    add("J1", a)
                    if w == 128:
                        add("J1", a.twin())
    # every job's control (§3.2): three find_byte lengths, one fixed executable
    for j in jobs:
        jobs[j].insert(0, Arm("ctl", "%s.ctl" % j, "ctl", "walk", lengths=LENGTHS))
    # the floor (§3.5 "The run record"): byte.<form>, hit.<form>, verify.<form>.<cls>, enter.<kind>
    for key, _g, job, _e, _b in rows:
        q = key.split(".")
        when = "unless-j1-b" if job == "J2p" else "always"
        if q[1] == "find_byte":
            floor.append(("byte.%s" % q[2], key, when))
        elif q[1] == "find_hit" and q[3] == "random":
            floor.append(("hit.%s" % q[2], key, when))
        elif q[1] == "verify_cmp":
            floor.append(("verify.%s.%s" % (q[2], q[3]), key, when))
        elif q[1] == "enter" and q[3] == "NONE":
            floor.append(("enter.%s" % q[2], key, when))
    return jobs, rows, floor, unreached

def points(arms):
    return sum(len(a.lengths) for a in arms)

if __name__ == "__main__":
    jobs, rows, floor, unreached = build()
    print("== slot plan: %d rows, %d floor lines over %d clauses" % (len(rows), len(floor), len({c for c, _k, _w in floor})))
    for j in sorted(jobs):
        print("%s\tarms %d\tpoints %d\tgroups %s" % (j, len(jobs[j]), points(jobs[j]),
                                                   ",".join(sorted({a.group for a in jobs[j]}))))
    for r in rows:
        print("row\t%s\t%s\t%s\t%s\t%s" % (r[0], r[1], r[2], r[3], r[4] or "-"))
    for c in floor:
        print("floor\t%s\t%s\t%s" % c)
    for u in unreached:
        print("UNREACHED\t" + u)
