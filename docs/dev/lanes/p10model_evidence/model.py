#!/usr/bin/env python3
"""P10 deferred presence check: cost model (arithmetic only, stdlib).

Units are whatever the Route's rates are in (INSTR = instructions, CYC = cycles).
One 'call' = one attempt of a one-attempt route at start s of a subject of
length n: the attempt consumes L bytes then matches or dies (L==n-s means it
ran to the end); p = first required-byte position >= s (None = absent).
Run:  python3 -I model.py            (all tables)
"""
import bisect, math, random, sys
from dataclasses import dataclass

@dataclass
class Route:
    name: str
    a: float      # attempt cost per byte (generic-path table step)
    m: float      # memchr cost per byte
    C: float      # memchr fixed call cost (UNMEASURED; fits the pre twin's ~7 instr)
    F: float      # attempt fixed cost when it runs to its own end
    gpre: float   # codegen multiplier on the attempt loop, check-first placement
    gpace: float  # same, paced placement (separate term, never hidden)

# calibrated from p910_report.md P10 twin table (instructions) and its cycle ratios
INSTR_EMAIL = Route("instr/email", 8.0, 0.0945, 7, 112, 1.25, 1.375)
INSTR_ISO   = Route("instr/iso",   9.0, 0.0945, 7, 146, 1.052, 1.052)
CYC_EMAIL   = Route("cyc/email",   2.64, 0.038, 20, 40, 1.0, 1.0)   # C,F UNMEASURED
CYC_ISO     = Route("cyc/iso",     7.4,  0.038, 20, 40, 1.0, 1.0)
ROUTES = [INSTR_EMAIL, INSTR_ISO, CYC_EMAIL, CYC_ISO]

@dataclass
class Call:
    s: int; n: int; L: int; matched: bool; p: object   # p: abs pos or None

def scan_len(c):                      # bytes memchr touches from c.s
    return (c.p - c.s + 1) if c.p is not None else (c.n - c.s)

# ---- strategies: cost(route, call, state) ----------------------------------
def today(r, c, st):
    return r.F + r.a * c.L

def pre(r, c, st):
    cost = r.C + r.m * scan_len(c)
    return cost if c.p is None else cost + r.F + r.gpre * r.a * c.L

def bound_fixed(K, D0):
    return lambda r, c: max(D0, (c.n - c.s) >> K)

def bound_derived(r, c):              # pay-as-spent: attempt spend == cost of the check
    return int((r.C + r.m * (c.n - c.s)) / (r.a * r.gpace))   # floor: 0 = check at entry

def paced(bound, mem=False):
    def f(r, c, st):
        if mem:
            if st.get("abs") is not None and c.s >= st["abs"]:
                return 2.0                               # remembered: answer at once
            if st.get("fnd") is not None and st["fnd"] >= c.s:
                return r.F + r.gpace * r.a * c.L + 2.0   # remembered presence: no check
        b = bound(r, c)
        if c.L <= b and b > 0:
            return r.F + r.gpace * r.a * c.L
        cost = r.gpace * r.a * b + r.C + r.m * scan_len(c)
        if c.p is None:
            if mem: st["abs"] = c.s if st.get("abs") is None else min(st["abs"], c.s)
            return cost
        if mem: st["fnd"] = c.p
        return cost + r.F + r.gpace * r.a * (c.L - b)
    return f

def online(D0, rr=None):
    """geometric schedule keyed to bytes consumed: at c = D0*2^j the next c*r bytes are
    scanned (memchr spend <= attempt spend), each byte scanned once, frontier kept.
    Same code as the streaming 'online doubling' with the whole subject buffered."""
    def f(r, c, st):
        return stream_cost("online doubling", r, c.n - c.s, c.n - c.s + 1, None if c.p is None else c.p - c.s,
                           c.L, c.matched, D0=D0)[0]
    return f

def opt(r, c):
    t = today(r, c, {})
    if c.p is None:
        t = min(t, r.C + r.m * (c.n - c.s))
    return t

def strategies():
    S = {"today": today, "pre": pre}
    for K in (4, 5, 6, 7, 8):
        S[f"paced K{K}"] = paced(bound_fixed(K, 16))
    S["paced K6 D0=8"] = paced(bound_fixed(6, 8))
    S["paced K6 D0=32"] = paced(bound_fixed(6, 32))
    S["paced K6 D0=64"] = paced(bound_fixed(6, 64))
    S["derived"] = paced(bound_derived)
    S["paced K6 +mem"] = paced(bound_fixed(6, 16), mem=True)
    S["derived +mem"] = paced(bound_derived, mem=True)
    S["online D0=16"] = online(16)
    return S

# ---- subjects: sequences of calls -------------------------------------------
def first_ge(pos, s):
    i = bisect.bisect_left(pos, s)
    return pos[i] if i < len(pos) else None

def run(strat, r, calls):
    st, tot = {}, 0.0
    for c in calls:
        tot += strat(r, c, st)
    return tot

def total_opt(r, calls):
    return sum(opt(r, c) for c in calls)

# ---- calibration --------------------------------------------------------------
# (name, route, n, p, L, matched, meas today, pre, paced)   p None = absent
CAL = [
 ("email evil-match-60k", INSTR_EMAIL, 61440, None, 61440, False, 491626, 5905, 16491),
 ("email nearmiss-16k",   INSTR_EMAIL, 16384, None, 16384, False, 131184, 1681, 4523),
 ("email prose-1m",       INSTR_EMAIL, 1048576, None, 8, False, 176, 98449, 193),
 ("email hyb-digits-4k",  INSTR_EMAIL, 4096, None, 4096, False, 32874, 529, 1259),
 ("email wit A 30000 cls, 1MiB", INSTR_EMAIL, 1048576, None, 30000, False, 240112, 101265, 286663),
 ("email wit B 19800 ltr, 1MiB", INSTR_EMAIL, 1048576, None, 19800, False, 158512, 100310, 283959),
 ("email wit C 60000 cls + match", INSTR_EMAIL, 60100, 59990, 60000, True, 480239, 605943, 665985),
 ("iso trim-match-60k",   INSTR_ISO, 61440, None, 61440, False, 553106, 5944, 15571),
 ("iso trim-nearmiss-16k",INSTR_ISO, 16384, None, 16384, False, 147610, 1725, 4312),
 ("iso prose-1m",         INSTR_ISO, 1048576, None, 1, False, 154, 98489, 155),
 ("iso wit A 30000 ws, 1MiB (OUTLIER)", INSTR_ISO, 1048576, None, 30000, False, 270154, 101270, 269856),
 ("iso wit C 140111 + match", INSTR_ISO, 140200, 140100, 140111, True, 1260998, 1326687, 1326720),
]

def calibrate():
    print("== CALIBRATION (instructions; model vs measured, twin = p910 job 691/earlier)")
    print(f"{'subject':36s} {'strat':6s} {'model':>10s} {'meas':>10s} {'err%':>6s}  ratio(model/meas) vs today")
    worst = 0
    for name, r, n, p, L, mt, mt0, mpre, mpac in CAL:
        c = Call(0, n, L, mt, p)
        row = [("today", today(r, c, {}), mt0), ("pre", pre(r, c, {}), mpre),
               ("paced", paced(bound_fixed(6, 16))(r, c, {}), mpac)]
        for nm, mod, me in row:
            e = 100 * (mod - me) / me
            if "OUTLIER" not in name: worst = max(worst, abs(e))
            print(f"{name:36s} {nm:6s} {mod:10.0f} {me:10d} {e:+6.1f}  x{mod/mt0:7.3f} / x{me/mt0:7.3f}")
    print(f"worst |err| excluding the flagged outlier: {worst:.1f}%\n")
    # cycles-only ratios reported by p910: email 162,222 -> 5,975 (x27), iso 453,090 -> 9,226 (x49)
    for r, n, meas in ((CYC_EMAIL, 61440, 162222/5975), (CYC_ISO, 61440, 453090/9226)):
        c = Call(0, n, n, False, None)
        mod = today(r, c, {}) / paced(bound_fixed(6, 16))(r, c, {})
        print(f"cycles hazard gain {r.name}: model x{mod:.1f} vs measured x{meas:.1f}")
    print()

# ---- single-call sweep: worst ratio to hindsight-optimal per strategy ---------
def sweep(r, label):
    S = strategies()
    worst = {k: [(0.0, None), (0.0, None), (0.0, None)] for k in S}   # vs opt all n, vs opt n>=4096, vs today
    for n in (32, 64, 128, 256, 1024, 4096, 65536, 1 << 20):
        Ls = sorted({0, 1, 2, 8, 16, 17, 32, 64, 65, 129, n >> 6, (n >> 6) + 1, n >> 7, (n >> 7) + 1,
                     n >> 8, (n >> 8) + 1, n >> 5, n >> 3, n >> 1, n})
        for p in (None, 0, 4, n // 100, n // 2, n - 1):
            for L in Ls:
                if L > n: continue
                for mt in (False, True):
                    if mt and (p is None or p >= L): continue
                    c = Call(0, n, L, mt, p)
                    o, t0 = opt(r, c), today(r, c, {})
                    for k, f in S.items():
                        v = f(r, c, {})
                        for idx, x in enumerate((v / o, v / o if n >= 4096 else 0, v / t0)):
                            if x > worst[k][idx][0]:
                                worst[k][idx] = (x, (n, p, L, mt))
    print(f"== SWEEP single call, {label}: worst ratio (vs hindsight opt, all n | vs opt n>=4096 | vs TODAY) and where")
    for k, w in worst.items():
        print(f"  {k:16s} opt:x{w[0][0]:7.2f} | n>=4096:x{w[1][0]:6.2f} | today:x{w[2][0]:5.2f}  at n={w[2][1][0]} p={w[2][1][1]} L={w[2][1][2]}; opt-worst at n={w[0][1][0]} p={w[0][1][1]} L={w[0][1][2]}")
    print()
    return worst

# ---- real-text-like (line-per-call and whole-buffer) --------------------------
def text_calls(kind, rng, lines=2000):
    # (mean line length, mean attempt depth, P(byte on line), P(attempt survives whole line))
    P = {"prose":  (70, 6, 0.03, 0.02), "logs": (110, 25, 0.60, 0.15), "code": (40, 12, 0.85, 0.10)}[kind]
    calls = []
    for _ in range(lines):
        n = max(8, int(rng.expovariate(1 / P[0])))
        p = rng.randrange(n) if rng.random() < P[2] else None
        L = n if rng.random() < P[3] else min(n, int(rng.expovariate(1 / P[1])))
        mt = (p is not None and L == n and p < L)
        calls.append(Call(0, n, L, mt, p))
    return calls

def texts():
    rng = random.Random(10)
    S = strategies()
    keep = ["today", "pre", "paced K5", "paced K6", "derived", "paced K6 D0=32", "online D0=16"]
    for r in ROUTES:
        print(f"== REAL-TEXT-LIKE, line per call, {r.name}: total cost ratio to per-call hindsight optimum")
        print(f"  {'kind':6s} " + " ".join(f"{k:>14s}" for k in keep))
        for kind in ("prose", "logs", "code"):
            calls = text_calls(kind, random.Random(rng.random()))
            o = total_opt(r, calls)
            print(f"  {kind:6s} " + " ".join(f"{run(S[k], r, calls)/o:14.3f}" for k in keep))
    print()
    # one big buffer, e.g. a 1 MiB file as ONE subject, attempt dies near the start
    print("== whole-buffer subjects (n=1 MiB, one call), instr/email")
    r = INSTR_EMAIL
    for kind, L, p in (("prose, dies at 8, byte absent", 8, None), ("log, dies at 60, byte at 4000", 60, 4000),
                       ("hazard, survives all, byte absent", 1 << 20, None), ("survives 20000 then dies", 20000, None)):
        c = Call(0, 1 << 20, L, False, p)
        o = opt(r, c)
        print(f"  {kind:36s} " + " ".join(f"{k}=x{S[k](r, c, {})/o:.2f}" for k in ("today", "pre", "paced K6", "derived")))
    print()

# ---- find-all: many calls on one subject, memory ------------------------------
def findall_scenarios():
    S = strategies()
    keep = ["today", "pre", "paced K6", "paced K6 +mem", "derived", "derived +mem"]
    print("== FIND-ALL scenarios (instr/email, ratio to per-call hindsight opt; <1 = beats stateless opt)")
    print(f"  {'scenario':58s} " + " ".join(f"{k:>14s}" for k in keep))
    r = INSTR_EMAIL
    sc = {}
    # 1: retry loop (caller emulates unanchored search with the anchored attempt), byte ABSENT,
    #    attempt dies just past the bound at every start: the per-call worst case repeated
    for n in (4096, 65536):
        sc[f"retry loop, byte absent, L=bound+1, n={n}"] = [
            Call(s, n, ((n - s) >> 6) + 17, False, None) for s in range(0, n, max(1, n // 2000))]
    sc["retry loop, byte absent, L=3 (dies fast), n=65536"] = [Call(s, 65536, 3, False, None) for s in range(0, 65536, 32)]
    # 2: tokenizer: 500 matches of 20 B, each containing the byte, then 1 failing call surviving 40 B, byte gone
    n = 11000
    calls = [Call(20 * i, n, 20, True, 20 * i + 7) for i in range(500)] + [Call(10000, n, 40, False, None)]
    sc["tokenizer 500 matches (byte inside each) + final fail"] = calls
    # 3: byte far ahead, many short calls start before it and survive past D0 (found-memory case)
    n = 2000
    sc["byte at 1990, 90 calls L=40 start<1000 (found memory)"] = [Call(10 * i, n, 40, False, 1990) for i in range(90)]
    # 4: end-of-subject tail: rest small, bound = D0 floor, byte absent, many survive
    n = 1200
    sc["tail: n=1200, byte absent, 1000 calls L=30 (D0 floor)"] = [Call(s, n, 30, False, None) for s in range(0, 1000)]
    # 5: find-all few matches with byte dense in text
    n = 1 << 20
    pos = sorted(random.Random(3).sample(range(n), 20000))
    calls, s = [], 0
    rng = random.Random(4)
    while s < n - 100 and len(calls) < 400:
        L = int(rng.expovariate(1 / 12)) + 1
        calls.append(Call(s, n, L, False, first_ge(pos, s)))
        s += rng.randrange(1, 4000)
    sc["1MiB, byte every ~52 B, 400 starts, L~12"] = calls
    for name, cl in sc.items():
        o = total_opt(r, cl)
        print(f"  {name:58s} " + " ".join(f"{run(S[k], r, cl)/o:14.2f}" for k in keep))
    print()

# ---- sensitivity of the worst-case bound to the measured ratio ----------------
def sensitivity():
    print("== SENSITIVITY: worst ratio vs TODAY's cost (attempt dies just past the checkpoint, byte absent)")
    print("   closed form 1 + gp*2^-K * (a/m)^0 ... = 1 + 2^K/r' with r' = a*gp/m ; derived K = ceil(log2 r')")
    print(f"  {'r(a/m)':>8s} " + " ".join(f"K={K:<2d}" .rjust(8) for K in (4, 5, 6, 7, 8)) + "   derived K")
    for r_ in (25, 53, 69, 100, 194, 400):
        row = [1 + 2 ** K / r_ for K in (4, 5, 6, 7, 8)]
        print(f"  {r_:8d} " + " ".join(f"{x:8.2f}" for x in row) + f"   {math.ceil(math.log2(r_))}")
    print("  and the same schedule vs hindsight min(today, pre) when pre wins (r > 2^K):")
    for r_ in (53, 69, 194, 400):
        print(f"   r={r_}: K=6 -> x{1 + r_ / 64:.2f}   K=ceil(log2 r)={math.ceil(math.log2(r_))} -> x{1 + r_ / 2 ** math.ceil(math.log2(r_)):.2f}")
    print()
    print("== derived D0 and bound fraction (pay-as-spent: b = (C + m*R)/(a*g))")
    for r in (INSTR_EMAIL, INSTR_ISO, CYC_EMAIL, CYC_ISO):
        print(f"  {r.name:12s} D0=C/(a*g)={r.C/(r.a*r.gpace):5.1f} steps   fraction m/(a*g)=1/{r.a*r.gpace/r.m:5.0f}")
    print("  C is UNMEASURED: D0 for C in 20..120 cycles on cyc/email:",
          [round(c / 2.64, 1) for c in (20, 40, 80, 120)], " cyc/iso:", [round(c / 7.4, 1) for c in (20, 40, 80, 120)])
    print()
    print("== memchr slower than modelled (Zen 1 style, m x2, x4) / attempt faster (a x0.5): worst single-call ratio vs TODAY at K=6")
    for tag, fm, fa in (("as measured", 1, 1), ("m x2", 2, 1), ("m x4", 4, 1), ("a x0.5", 1, 0.5), ("m x2, a x0.5", 2, 0.5)):
        r = Route("x", CYC_EMAIL.a * fa, CYC_EMAIL.m * fm, 20, 40, 1, 1)
        w = 0
        for n in (1 << 16, 1 << 20):
            c = Call(0, n, (n >> 6) + 1, False, None)
            w = max(w, paced(bound_fixed(6, 16))(r, c, {}) / today(r, c, {}))
        print(f"  {tag:14s} x{w:.2f}")
    print()

# ---- streaming ----------------------------------------------------------------
def stream_cost(kind, r, n, B, p, L, matched, K=6, D0=16):
    """chunked subject, n unknown to the matcher; chunk size B arrives whole; the attempt
    cannot read past the buffered bytes. Returns (cost, answer_correct, rejected_early)."""
    buf = min(n, B)
    a, g = r.a, r.gpace
    truth_match = matched
    if kind == "today":
        return r.F + a * L, True, False
    if kind == "naive paced (rest=buffered)":
        b = max(D0, (buf >> K))
        if L <= b:
            return r.F + g * a * L, True, False
        pp = p if (p is not None and p < buf) else None
        cost = g * a * b + r.C + r.m * ((pp + 1) if pp is not None else buf)
        if pp is None:                              # 'absent -> no match' on the BUFFER
            return cost, (not truth_match), True    # wrong when the attempt would have matched
        return cost + r.F + g * a * (L - b), True, False
    if kind == "safe paced (reject only at EOF)":   # same check, but absence only rejects if buf==n
        b = max(D0, (buf >> K))
        if L <= b:
            return r.F + g * a * L, True, False
        pp = p if (p is not None and p < buf) else None
        cost = g * a * b + r.C + r.m * ((pp + 1) if pp is not None else buf)
        if pp is None and buf >= n:
            return cost, True, True
        return cost + r.F + g * a * (L - b), True, False
    if kind == "online doubling":                   # windows c*r keyed to bytes consumed, frontier kept
        rate = a * g / r.m
        q, cons, cost, spent = 0, D0, 0.0, 0
        avail = lambda c: min(n, ((c // B) + 1) * B)   # bytes buffered when attempt is at offset c
        while cons < L:
            cost += g * a * (cons - spent); spent = cons
            hi = min(avail(cons), max(q, int(cons * rate)))   # frontier ~ consumed*r: memchr spend <= attempt spend
            if p is not None and p < hi:
                return cost + r.C + r.m * (p + 1 - q) + r.F + g * a * (L - cons), True, False
            if hi > q:
                cost += r.C + r.m * (hi - q); q = hi
            if q >= n:
                return cost, True, True
            cons *= 2
        return cost + r.F + g * a * (L - spent), True, False

def streaming():
    r = CYC_EMAIL
    print("== STREAMING (cyc/email): chunk size B, n unknown to the matcher; only buffered bytes scannable")
    kinds = ["today", "naive paced (rest=buffered)", "safe paced (reject only at EOF)", "online doubling"]
    cases = [
      ("hazard: survives all 1MiB, byte absent", 1 << 20, None, 1 << 20, False),
      ("match: byte at 600000, attempt matches at 600001", 1 << 20, 600000, 600001, True),
      ("dies at 5000, byte absent (n 1MiB)", 1 << 20, None, 5000, False),
      ("prose: dies at 8, byte absent (n 1MiB)", 1 << 20, None, 8, False),
    ]
    for B in (4096, 65536, 1 << 20):
        print(f" -- B={B}" + ("  (whole subject buffered = the non-streaming case)" if B == 1 << 20 else ""))
        for name, n, p, L, mt in cases:
            o = opt(r, Call(0, n, L, mt, p))
            out = []
            for k in kinds:
                c, ok, rej = stream_cost(k, r, n, B, p, L, mt)
                out.append(f"{k.split(' (')[0][:14]}=x{c/o:.2f}{'' if ok else ' WRONG'}{'*' if rej else ''}")
            print(f"   {name:50s} " + "  ".join(out))
    print("   (x = cost / offline hindsight optimum that KNOWS n; * = rejected early; WRONG = wrong answer)")
    # worst case online vs today (online-achievable optimum when n unknown = today)
    print(" -- online doubling worst ratio vs TODAY, sweeping attempt depth L, B=65536, n=1MiB, byte absent:")
    w = (0, None)
    for L in sorted({16, 17, 31, 32, 33, 64, 65, 100, 1000, 4096, 4097, 20000, 65535, 65537, 1 << 17, 1 << 20}):
        c, ok, rej = stream_cost("online doubling", r, 1 << 20, 65536, None, L, False)
        x = c / (r.F + r.a * L)
        w = max(w, (x, L))
    print(f"    worst x{w[0]:.3f} at L={w[1]}")
    print()

if __name__ == "__main__":
    calibrate()
    sensitivity()
    for r in (INSTR_EMAIL, INSTR_ISO, CYC_EMAIL, CYC_ISO):
        sweep(r, r.name)
    texts()
    findall_scenarios()
    streaming()
