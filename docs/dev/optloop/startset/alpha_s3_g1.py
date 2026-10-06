#!/usr/bin/env python3
# [START-SET] stage 3 -- the alpha's Q3 and Q4 EXTENSION (lane alphas3, D148
# addendum 4), run beside alpha_s3.sh on the SAME work dir ($S2A: the base/ and
# new/ builds and subj/ that alpha_s3.sh's `build` step made, plus keep/).
#
# WHAT IT ADDS. alpha_s3.sh times 19 named cells. D148 addendum 4 asks for
# more: Q3 -- each of the 28 stage-3 movers whose DFA-hat set T is one byte
# equal to the required byte (G1 `emitted -> dominated`: the pre-check is
# elided) timed WITH and WITHOUT the pre-check; Q4 -- the T ⊊ E admission's
# null cells (every mover whose hat narrows E by one or two bytes).
#
# THE ARMS, per cell (every arm is one compiler + flags on the same pattern):
#   base   main before the hat (abi 63): no hat, the pre-check emitted
#   new    stage 3 (abi 64): the hat, the pre-check ELIDED on a G1 mover
#   deny   new -fno-start-set: == base program (the floor's reference)
#   noreq  new -fno-req-byte: the ruling's arm -- no pre-check at all; on a G1
#          mover the elided form already has none, so noreq must be the same
#          program as new (checked: .text byte-identical) and is a direct
#          program-identical null sample against new
#   keep   a scratch build of stage 3 with ONE line patched
#          (`req_dominated_applies` returns false): the hat AND the pre-check.
#          This is the form the ruling's "with the pre-check" means; no flag
#          produces it (the `dominated` row is undeniable), so it is a twin.
#   (G1 movers get all five arms; every other mover base/new/deny.)
# Q3's ruling: if `new` (elided) is slower than `keep` on ANY cell beyond the
# program-identical null band, G1 keeps the pre-check for that shape.
#
# STEPS: classify | build | check | time | all.   Env: S2A (work dir), BENCH,
# CPU (2), LAUNCHES (5), PASSES (5), CC (gcc).
import os, sys, re, shlex, subprocess, statistics, time, json
from concurrent.futures import ThreadPoolExecutor

S2A = os.environ.get("S2A", "/tmp/s3alpha_startset")
BENCH = os.environ.get("BENCH", "/home/duxevents/pcrec-bench")
CPU = os.environ.get("CPU", "2")
LAUNCHES = int(os.environ.get("LAUNCHES", "5"))
PASSES = int(os.environ.get("PASSES", "5"))
CC = os.environ.get("CC", "gcc")
HAT = ("first-memchr-bounded", "first-class-bounded")
SUBJ = {  # set -> subject ids (the same subjects alpha_s3.sh generates and sha-checks)
    "cap": ["cap:t-64k", "cap:t-1m"],
    "log": ["log:t-064k-syslog", "log:t-1024k-syslog"],
    "bnd": ["bnd:t-letters-064k"],
    "alt": ["alt:t-128k-sparse", "alt:t-128k-dense"],
}
SETOF = {"capability": "cap", "loglines": "log", "bounded": "bnd", "altwide": "alt"}
os.chdir(S2A)
G1 = os.path.join(S2A, "g1")
os.makedirs(G1, exist_ok=True)
STAMP = re.compile(r'^#define RX_(\w+) +(.*)$', re.M)


def stamps(t):
    return {m.group(1): m.group(2).strip().strip('"') for m in STAMP.finditer(t)}


def table_count(t, name):
    m = re.search(r'static const unsigned char rx_%s\[256\] = \{\n((?:.*\n)*?)\s*\};' % name, t)
    if not m:
        return None
    v = [int(x) for x in re.findall(r"\d+", m.group(1))]
    return sum(1 for x in v if x) if len(v) == 256 else None


def hat_T(t):
    n = table_count(t, "start_bytes")
    if n is not None:
        return n
    return 1 if re.search(r'memchr\(subject \+ scan_position, \d+, ', t) else None


def rows():
    out = []
    for ln in open("new/tests/startset/manifests/manifest_s3_dfa.tsv", encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        f = ln.rstrip("\n").split("\t")
        out.append((f[0], shlex.split(f[1]), bytes.fromhex(f[2])))
    return out


def pcrec(side):
    return {"base": "base", "new": "new", "deny": "new", "noreq": "new", "keep": "keep"}[side] + "/build/pcrec"


def extra(side):
    return {"deny": ["-fno-start-set"], "noreq": ["-fno-req-byte"]}.get(side, [])


def emit(side, opts, pat, d):
    os.makedirs(d, exist_ok=True)
    o = os.path.join(d, "art.c")
    # the pattern travels as argv bytes (some carry non-UTF-8 bytes): bytes argv
    r = subprocess.run([pcrec(side), "-p", "rx", *opts, *extra(side), "-o", o, "--pattern", pat],
                       capture_output=True, timeout=300)
    return o if r.returncode == 0 else None


def classify():
    def one(r):
        id_, opts, pat = r
        k = re.sub(r"[^A-Za-z0-9]+", "_", id_)
        o1 = emit("new", opts, pat, "g1/cls/%s/new" % k)
        o0 = emit("deny", opts, pat, "g1/cls/%s/deny" % k)
        if not o1 or not o0:
            return (id_, "REFUSED", "", "", "", "", "")
        t1, t0 = open(o1, encoding="latin-1").read(), open(o0, encoding="latin-1").read()
        s1, s0 = stamps(t1), stamps(t0)
        pf = s1.get("DFA_PREFILTER", "")
        nT = hat_T(t1) if pf in HAT else ""
        nE = table_count(t0, "can_begin_match")
        return (id_, "mover" if pf in HAT else "non", pf, s0.get("REQ_WHY", ""), s1.get("REQ_WHY", ""),
                nT, "" if nE is None else nE)
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(one, rows()))
    with open("g1/movers.tsv", "w") as f:
        f.write("id\tstatus\tprefilter\twhy_deny\twhy_new\tnT\tnE\n")
        for r in res:
            f.write("\t".join(str(x) for x in r) + "\n")
    g1 = sum(1 for r in res if r[1] == "mover" and r[3] == "emitted" and r[4] == "dominated")
    mv = sum(1 for r in res if r[1] == "mover")
    print("classify: %d rows, %d movers, %d G1 emitted->dominated" % (len(res), mv, g1))


def cells():
    out = []
    byid = {r[0]: r for r in rows()}
    for ln in list(open("g1/movers.tsv"))[1:]:
        f = ln.rstrip("\n").split("\t")
        if f[1] != "mover":
            continue
        id_ = f[0]
        g1 = f[3] == "emitted" and f[4] == "dominated"
        nT = int(f[5]) if f[5] else None
        nE = int(f[6]) if f[6] else None
        m = re.match(r"bench/([^/]+)/", id_)
        st = SETOF.get(m.group(1), "cap") if m else "cap"
        kind = "G1" if g1 else ("Q4n" if (nT is not None and nE is not None and 1 <= nE - nT <= 2) else "mover")
        out.append(dict(id=id_, key=re.sub(r"[^A-Za-z0-9]+", "_", id_), kind=kind, nT=nT, nE=nE,
                        subjects=SUBJ[st], arms=["base", "new", "deny"] + (["noreq", "keep"] if g1 else []),
                        opts=byid[id_][1], pat=byid[id_][2]))
    return out


def build():
    cs = cells()

    def one(c):
        for a in c["arms"]:
            d = "g1/art/%s/%s" % (c["key"], a)
            o = emit(a, c["opts"], c["pat"], d)
            if not o:
                return "EMIT FAILED %s %s" % (c["id"], a)
            r = subprocess.run([CC, "-O2", "-I" + d, "-o", d + "/run", "drv.c", o], capture_output=True)
            if r.returncode:
                return "CC FAILED %s %s: %s" % (c["id"], a, r.stderr.decode()[:300])
            if a in ("new", "noreq"):
                subprocess.run([CC, "-O2", "-I" + d, "-c", "-o", d + "/art.o", o], check=True)
                subprocess.run(["objcopy", "-O", "binary", "-j", ".text", d + "/art.o", d + "/text.bin"], check=True)
        return None
    with ThreadPoolExecutor(3) as ex:
        bad = [x for x in ex.map(one, cs) if x]
    for b in bad:
        print(b)
    print("build: %d cells, %d failed" % (len(cs), len(bad)))
    return 1 if bad else 0


def subj_path(s):
    return "subj/%s/%s.bin" % (s.split(":")[0], s.split(":")[1])


def run1(c, a, s, mode="t", passes=1, pin=False):
    cmd = ["g1/art/%s/%s/run" % (c["key"], a), mode, subj_path(s), str(passes)]
    if pin:
        cmd = ["taskset", "-c", CPU] + cmd
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600).stdout


def check():
    rc = 0
    for c in cells():
        for s in c["subjects"]:
            ans = {a: run1(c, a, s).split(" ")[0] for a in c["arms"]}
            for a in c["arms"][1:]:
                if ans[a] != ans["base"]:
                    print("ANSWER DIFF %s %s %s: %s vs %s" % (c["id"], a, s, ans["base"], ans[a]))
                    rc = 1
    print("g1 check: rc=%d" % rc)
    return rc


def load1():
    return float(open("/proc/loadavg").read().split()[0])


def timecells():
    print("# alpha_s3_g1 %s %s load1=%.2f CPU=%s LAUNCHES=%d PASSES=%d" % (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), os.uname().nodename, load1(), CPU, LAUNCHES, PASSES))
    hdr = "id kind nT nE subject base new deny noreq keep new-base new-keep floor nullband textsame verdict".split()
    print("\t".join(hdr))
    for c in cells():
        ident = None
        if "noreq" in c["arms"]:
            ident = open("g1/art/%s/new/text.bin" % c["key"], "rb").read() == \
                open("g1/art/%s/noreq/text.bin" % c["key"], "rb").read()
        for s in c["subjects"]:
            while load1() >= 0.5:
                time.sleep(20)
            M = {a: [] for a in c["arms"]}
            for _ in range(LAUNCHES):
                for a in c["arms"]:
                    m = re.search(r"median=([0-9.]+)", run1(c, a, s, "t", PASSES, True))
                    if m:
                        M[a].append(float(m.group(1)))
            med = {a: statistics.median_low(v) if v else float("nan") for a, v in M.items()}
            fl = abs(med["deny"] - med["base"])
            d_nb = med["new"] - med["base"]
            if "noreq" in med:
                d_nk = med["new"] - med["keep"]
                nb = abs(med["new"] - med["noreq"]) if ident else float("nan")
                band = max(fl, nb if nb == nb else 0.0)
                q3 = "ELIDE-SLOWER" if d_nk > band else ("ELIDE-FASTER" if -d_nk > band else "NULL")
            else:
                d_nk, nb, band, q3 = float("nan"), float("nan"), fl, ""
            v = "NULL" if abs(d_nb) <= fl else ("WIN" if d_nb < 0 else "REGRESSION")
            f = lambda x: "%.5f" % x
            print("\t".join([c["id"], c["kind"], str(c["nT"]), str(c["nE"]), s,
                             f(med["base"]), f(med["new"]), f(med["deny"]),
                             f(med["noreq"]) if "noreq" in med else "-", f(med["keep"]) if "keep" in med else "-",
                             "%+.5f" % d_nb, "%+.5f" % d_nk if d_nk == d_nk else "-", f(fl),
                             f(nb) if nb == nb else "-", "" if ident is None else ("Y" if ident else "N"),
                             (v + (" Q3:" + q3 if q3 else ""))]))
            sys.stdout.flush()


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step == "classify":
        classify()
    elif step == "build":
        sys.exit(build())
    elif step == "check":
        sys.exit(check())
    elif step == "time":
        timecells()
    elif step == "all":
        classify()
        if build() == 0 and check() == 0:
            timecells()
    else:
        print("usage: alpha_s3_g1.py [classify|build|check|time|all]")
        sys.exit(2)
