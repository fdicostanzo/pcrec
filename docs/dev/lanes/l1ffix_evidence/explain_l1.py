#!/usr/bin/env python3
"""span_arms L1's compare, the DISAGREEMENTS EXPLAINED (lane l1feat): every
row compare_l1.py lists as OBSERVED-ONLY or UTF8-ONLY is put in one class by
a MECHANICAL test, never by reading it; a row no class's test accepts is
UNEXPLAINED (a STOP). The classes, each with its test:

  leaf-dead   the empty-class leaf (span_arms §14.4 L1, D-9; "the census lists
              them apart", §14.3): listed `dead`, with no lookaround of any
              spelling in the text, and still `dead` under
              `--harness=restore=look` (build/pcrec-harness), so the never bit
              is not the item's.
  spelling    a positive lookaround spelled `(?*`, `(*pla:`, `(*plb:`,
              `(*positive_lookahead:` etc. (the census population reads `(?=`
              and `(?<=` only, census_l1.py `has_pos_look`): rewritten to
              `(?=` / `(?<=` (`(*napla:` and `(?*` are the non-atomic forms;
              the walk reads a body's bytes, which atomicity does not move),
              the feature lists the SAME byte facts for the rewrite, and the
              model, run on the rewrite, predicts the observed byte movers.
  rep-copy    a guard meets a variable repeat's first or last COPY (span arms
              R1's split `X^m . gap`: the head is the first copy, the tail the
              last); the model reads a variable repeat as a WALL
              (census_l1.py `flatten`). Test: with the repeat's copies taken
              away (`--harness=restore=rep`, its old best-only form) the item
              moves nothing: the byte facts equal those under
              `--harness=restore=rep+look`.
  utf8-only   no byte fact moves; the utf8 compile moved. The model reads
              byte only. Test: the byte facts are equal (by construction of
              the class) and the utf8 `req_whole_run` why is `dead`, the
              utf8 run otherwise unchanged.

REVISED by lane l1ffix (review r55 H): every row kind compare_l1.py writes is
read (DIFFER, MODEL-ONLY and the route rows PIN-* / LANDMARK-* too, never only
the two above); a row whose subject lists `dead` where BASE did not has its
DEAD CLAIM TESTED before any class may take it (r55: `leaf-dead` never checked
the dead was true):

  dead-machine  the subject's own `never_matches` (the compiled machines,
                facts_listing §4.1.2¶12, a source independent of the run walk)
                names the pattern;
  dead-sampled  otherwise libpcre2 (P2PROBE, tests/lib/p2probe.c) answers
                NOMATCH on every subject of a deterministic sample over the
                pattern's own bytes and the walk's run (SAMPLES strings); a
                single match is DEAD-REFUTED, a STOP. Evidence, not a proof:
                the class name says so.

`rep-copy` takes a row only where a VALUE moved (r55: it was vacuous on a
dead-only row, `(?x) (?=a) x`), and compares value AND dead-ness under the
two restores. Two classes for the route rows:

  pin-substretch PIN-GAIN: BASE pinned nothing; the subject pins a stretch
                 strictly inside the run's maximal exact stretch (tuning
                 §2.30¶4, r55 B: the longest walk-proved sub-stretch), and
                 under `--harness=restore=look` the subject's pin is BASE's
                 or the same sub-stretch (the gain is the rule's, read on a
                 run L1 did not narrow, or L1's own).
  look-item      any other row (DIFFER, PIN-*, LANDMARK-*, OBSERVED-ONLY):
                 under `--harness=restore=look` the subject's byte facts
                 (WATCH and the route facts, value and dead-ness) are BASE's,
                 so the movement is L1's item and nothing else; the row's
                 kind and its model disagreement stay listed beside the class.

Three classes for the model disagreements (DIFFER, MODEL-ONLY), each tested:

  dead-both      DIFFER: model and build both list the pattern `dead` (no
                 match exists, the dead claim tested above); the run VALUE
                 of a dead pattern is the walk's own, advisory, and differs
                 by the order the guards meet (D27 F5, span_arms §10 U-assoc).
  offset-looser  DIFFER: the observed set equals the model's and every byte
                 whose `req_set_maxoff` differs has a LARGER (looser, sound)
                 observed offset: a member keeps the offset it first joined
                 at (r55 EMITTED-1, ruled PLAN).
  d27-limit      MODEL-ONLY: the pattern is a D27 witness the author judged
                 FAIL and tests/lookaround/d27_l1/l1d27_limits.tsv names its
                 stated limit (checked by `make test-lookaround`).
  route-row      OBSERVED-ONLY whose moved byte facts are route facts only
                 (`run_pin`, `req_landmark_maxoff`): its own PIN-*/LANDMARK-*
                 row, which must be present, carries the verdict.
Any other MODEL-ONLY row is UNEXPLAINED (the model predicts a move the build
does not make).

usage: explain_l1.py COMPARE_TXT BASE_PCREC WORK_PCREC WORK_HARNESS OUT_FILE [P2PROBE]
rc 0 when every row is explained.
"""
import importlib.util
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("compare_l1", os.path.join(HERE, "compare_l1.py"))
CMP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CMP)
C = CMP.C

LOOKAROUND = re.compile(rb"\(\?(<?[=!]|\*|<\*)|\(\*(n?a?p?l[ab]|positive_look|negative_look|non_atomic_positive_look)")
SAMPLES = 400
ROWS = [(k, re.compile(r"\s+(%s) (\S+) (.*?) %s" % (k, tail))) for k, tail in (
    ("OBSERVED-ONLY", "observed="), ("UTF8-ONLY", "utf8-facts="), ("DIFFER", "observed="),
    ("MODEL-ONLY", "model="),
    ("PIN-LOST|PIN-GAIN|PIN-MOVED", r"run_pin base \["),
    ("LANDMARK-LOST|LANDMARK-LOOSER|LANDMARK-GAIN|LANDMARK-TIGHTER", r"req_landmark_maxoff base \["))]
D27 = os.path.join(HERE, "../../../../tests/lookaround/d27_l1")


def d27_limited():
    """the D27 listing's FAIL patterns that name a declared limit."""
    import csv
    lim = {}
    for line in open(os.path.join(D27, "l1d27_limits.tsv")):
        if line.strip() and not line.startswith("#"):
            rid, keys = line.rstrip("\n").split("\t")
            lim[rid] = keys
    out = {}
    for r in csv.DictReader(open(os.path.join(D27, "l1d27_listing.tsv")), delimiter="\t"):
        if r["verdict"] == "FAIL" and r["id"] in lim:
            out[r["pattern"].encode("utf-8", "surrogateescape")] = r["id"] + ":" + lim[r["id"]]
    return out


MAXOFF_ONLY = re.compile(r".*model=\S+ req_set_maxoff observed \[([^\]]*)\] model \[([^\]]*)\]\s*$")


def offset_looser(raw, w):
    """the DIFFER row's only value disagreement is req_set_maxoff, over the
    same members, and every differing offset is LARGER as observed."""
    m = MAXOFF_ONLY.match(raw)
    if not m:
        return False
    om, mm = maxoffs(m.group(1)), maxoffs(m.group(2))
    if set(om) != set(mm) or maxoffs(w[("byte", "req_set_maxoff")][0]) != om:
        return False
    diff = [k for k in om if om[k] != mm[k]]
    return bool(diff) and all(int(om[k]) > int(mm[k]) for k in diff)


def maxoffs(v):
    return dict(x.split(":") for x in v.split(",") if ":" in x) if v not in ("", "none") else {}
REWRITE = [(rb"(*non_atomic_positive_lookahead:", b"(?="), (rb"(*non_atomic_positive_lookbehind:", b"(?<="),
           (rb"(*positive_lookahead:", b"(?="), (rb"(*positive_lookbehind:", b"(?<="),
           (rb"(*napla:", b"(?="), (rb"(*naplb:", b"(?<="), (rb"(*pla:", b"(?="), (rb"(*plb:", b"(?<="),
           (rb"(?<*", b"(?<="), (rb"(?*", b"(?=")]


def byte_facts(pcrec, pat, extra=()):
    try:
        r = subprocess.run([pcrec, "--features", "all"] + list(extra) + ["--emit-facts=byte,utf8", "--pattern", pat],
                           capture_output=True, timeout=C.TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode:
        return None
    out = {}; sec = None
    for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section "):
            sec = line.split()[1]; continue
        if line.startswith("#") or sec != "facts":
            continue
        x = line.split("\t")
        if x[1] in CMP.WATCH or x[1] in CMP.ROUTE or x[1] == "never_matches":
            out[(x[0], x[1])] = (x[6], x[7])
    return out


def vals(f, enc="byte"):
    return {k[1]: v[0] for k, v in f.items() if k[0] == enc and k[1] in CMP.WATCH}


def state(f, enc="byte"):
    """value and dead-ness of the walk facts AND the route facts (a `harness:`
    token is not a state: it only says a restore ran)."""
    return {k[1]: (v[0], v[1] == "dead") for k, v in f.items()
            if k[0] == enc and k[1] != "never_matches"}


def is_dead(f, enc):
    return f.get((enc, "req_whole_run"), ("", ""))[1] == "dead"


def run_bytes(v):
    """the exact bytes of a listed run value (`6162`, `61[62,63]`, `/mask`)."""
    v = v.split("/")[0]
    out = b""
    for m in re.finditer(r"\[([^\]]*)\]|([0-9a-f]{2})", v):
        if m.group(2):
            out += bytes([int(m.group(2), 16)])
        else:
            first = m.group(1).split(",")[0].split("-")[0]
            out += bytes([int(first, 16)]) if re.fullmatch(r"[0-9a-f]{2}", first) else b""
    return out


def dead_check(p2, pat, enc, w):
    """r55 H: the dead claim tested. -> ("dead-machine"|"dead-sampled", "")
    or ("DEAD-REFUTED", subject)."""
    nm = w.get((enc, "never_matches"), ("no", ""))[0]
    if nm not in ("no", ""):
        return "dead-machine", nm
    if not p2:
        return "DEAD-UNTESTED", "no P2PROBE given"
    alpha = sorted(set(c for c in pat if 0x20 < c < 0x7f and chr(c) not in "()[]{}?*+|^$\\.") |
                   set(run_bytes(w.get((enc, "req_whole_run"), ("", ""))[0]))) or [0x61]
    rng = random.Random(pat)
    run = run_bytes(w.get((enc, "req_whole_run"), ("", ""))[0])
    lit = bytes(c for c in pat if 0x20 < c < 0x7f and chr(c) not in "()[]{}?*+|^$\\.=<!:")
    subs = [run, lit, b"x" + run + b"x", lit + lit]
    n = max(8, 2 * len(run) + 6)
    while len(subs) < SAMPLES:
        subs.append(bytes(rng.choice(alpha) for _ in range(rng.randint(0, n))))
    r = subprocess.run([p2, "u" if enc == "utf8" else "", pat.hex()] + ["0:" + x.hex() for x in subs],
                       capture_output=True, text=True, timeout=120)
    lines = r.stdout.splitlines()
    if not lines or not lines[0].startswith("OK"):
        return "DEAD-UNTESTED", "libpcre2: " + (lines[0] if lines else "no output")
    for x, l in zip(subs, lines[1:]):
        if l.startswith("M"):
            return "DEAD-REFUTED", C.esc(x)
    return "dead-sampled", "%d subjects" % len(subs)


def pin_parts(v):
    """`o:at+len` -> (at, len); a bare offset (whole-run pin) -> None."""
    m = re.fullmatch(r"(\d+):(\d+)\+(\d+)", v or "")
    return (int(m.group(2)), int(m.group(3))) if m else None


def exact_stretch(run, at):
    """the maximal stretch of one-member positions of the run value containing at."""
    v = run.split("/")[0]
    pos = [m.group(0) for m in re.finditer(r"\[[^\]]*\]|[0-9a-f]{2}", v)]
    one = [not p.startswith("[") or ("," not in p and "-" not in p) for p in pos]
    if at >= len(one) or not one[at]:
        return 0
    a = b = at
    while a > 0 and one[a - 1]:
        a -= 1
    while b + 1 < len(one) and one[b + 1]:
        b += 1
    return b - a + 1


def main():
    a = sys.argv[1:]
    cmp_txt, base, work, harn, out = a[:5]
    p2 = a[5] if len(a) > 5 else None
    rows = []
    for l in open(cmp_txt, encoding="utf-8", errors="surrogateescape"):
        for _, rx in ROWS:
            m = rx.match(l)
            if m:
                pat = m.group(3).encode("latin-1", "surrogateescape").decode("unicode_escape").encode("latin-1")
                rows.append((m.group(1), m.group(2), pat, l.strip()))
                break
    routed = {pat for kind, _, pat, _ in rows if kind.startswith(("PIN-", "LANDMARK-"))}
    cls = {}; lines = []; bad = 0
    for kind, src, pat, raw in rows:
        b, w = byte_facts(base, pat), byte_facts(work, pat)
        verdict = None
        deadnote = ""
        if b is not None and w is not None:
            for enc in ("byte", "utf8"):
                if is_dead(w, enc) and not is_dead(b, enc):
                    dv, why = dead_check(p2, pat, enc, w)
                    deadnote += " [%s %s: %s]" % (enc, dv, why)
                    if dv.isupper() or dv.startswith("DEAD"):
                        verdict = "UNEXPLAINED (%s %s %s)" % (enc, dv, why)
        if verdict is not None:
            pass
        elif b is None or w is None:
            verdict = "UNEXPLAINED (a build refused)"
        elif kind == "OBSERVED-ONLY" and pat in routed and \
                set(re.search(r"byte-facts=(\S*)", raw).group(1).split(",")) <= set(CMP.ROUTE):
            verdict = "route-row"
        elif kind == "MODEL-ONLY":
            lim = d27_limited().get(pat)
            verdict = ("d27-limit " + lim) if lim else \
                "UNEXPLAINED (model-only: the model predicts a move the build does not make)"
        elif kind == "DIFFER" and "model=" in raw and "dead" in raw.split("model=")[1].split()[0].split(",") \
                and is_dead(w, "byte"):
            verdict = "dead-both"
        elif kind == "DIFFER" and offset_looser(raw, w):
            verdict = "offset-looser"
        elif kind == "PIN-GAIN" and b.get(("byte", "run_pin"), ("none",))[0] == "none":
            pw = w[("byte", "run_pin")][0]; pp = pin_parts(pw)
            h = byte_facts(harn, pat, ["--harness=restore=look"])
            if pp and pp[1] < exact_stretch(w[("byte", "req_whole_run")][0], pp[0]) and h is not None and \
               h.get(("byte", "run_pin"), ("",))[0] in ("none", pw):
                verdict = "pin-substretch"
        elif kind == "UTF8-ONLY":
            bu, wu = vals(b, "utf8"), vals(w, "utf8")
            if vals(b) == vals(w) and w[("utf8", "req_whole_run")][1] == "dead" and bu == wu:
                verdict = "utf8-only"
        else:
            dead = w[("byte", "req_whole_run")][1] == "dead" and b[("byte", "req_whole_run")][1] != "dead"
            if dead and not LOOKAROUND.search(pat):
                h = byte_facts(harn, pat, ["--harness=restore=look"])
                if h and h[("byte", "req_whole_run")][1] == "dead":
                    verdict = "leaf-dead"
            if verdict is None and any(o in pat for o, _ in REWRITE):
                q = pat
                for o, n in REWRITE:
                    q = q.replace(o, n)
                wq = byte_facts(work, q)
                if wq is not None and vals(wq) == vals(w) and \
                   (wq[("byte", "req_whole_run")][1] == "dead") == dead:
                    r = C.one((base, "rewrite", q, True)) if C.has_pos_look(q) else {}
                    mv = set(r.get("moved", []))
                    ob = CMP.obs_byte_set({"work": {k: ("",) + v for k, v in w.items()},
                                           "base": {k: ("",) + v for k, v in b.items()}})
                    if mv and mv == ob:
                        verdict = "spelling"
                    elif "abstain" in r:
                        lines.append("  NOTE rewrite %s abstained: %s" % (C.esc(q), r["abstain"]))
            if verdict is None and vals(b) != vals(w):
                h = byte_facts(harn, pat, ["--harness=restore=rep"])
                hl = byte_facts(harn, pat, ["--harness=restore=rep+look"])
                if h is not None and hl is not None and state(h) == state(hl):
                    verdict = "rep-copy"
        if verdict is None and b is not None and w is not None:
            hl = byte_facts(harn, pat, ["--harness=restore=look"])
            if hl is not None and state(hl) == state(b):
                verdict = "look-item"
        if verdict is None:
            verdict = "UNEXPLAINED"
        verdict_key = verdict if not verdict.startswith("UNEXPLAINED") else "UNEXPLAINED"
        cls[verdict_key] = cls.get(verdict_key, 0) + 1
        if verdict.startswith("UNEXPLAINED"):
            bad += 1
        lines.append("  %-14s %-16s %s %s%s" % (verdict, kind, src, C.esc(pat), deadnote))
    head = ["rows read: %d" % len(rows)] + ["  %s: %d" % kv for kv in sorted(cls.items())]
    lines = head + lines + ["== explain COMPLETE: %d unexplained" % bad]
    open(out, "w").write("\n".join(lines) + "\n")
    print("\n".join(head)); print(lines[-1])
    for l in lines:
        if "UNEXPLAINED" in l or "NOTE" in l:
            print(l)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
