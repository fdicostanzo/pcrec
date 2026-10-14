#!/usr/bin/env python3
"""rwquest check: compile + count each question's pattern with python `re`.

Run:  python3 -I check.py [--corpus DIR] [--sample-mib 4] [--full-cap-mib 64] [--jobs 6] [--only L01,C02]

Reads questions.src (next to this script), writes questions.tsv.
The corpus files are only READ (bytes), never executed or imported.

Semantics per mode (applied to the FIRST file listed, on two inputs: a
head sample of --sample-mib, cut at a line boundary for text classes, and the
whole file when it is <= --full-cap-mib):
  find-all / count : number of non-overlapping matches (re.finditer)
  first            : 1 if re.search finds a match, else 0
  line             : number of '\\n'-separated lines in which re.search succeeds
observed_frequency buckets matches per MiB of the whole file (sample if the
file was too big): none=0, rare<10, some<500, many<10000, everywhere>=10000
(thresholds are this lane's own, arbitrary). For `first` mode: hit / no-hit.
Flags: i=IGNORECASE m=MULTILINE s=DOTALL utf=decode as UTF-8 and use a str
pattern (otherwise bytes), ucp=Unicode \\w\\d\\s\\b (str patterns without ucp get
re.ASCII, as PCRE2 without UCP would).
\\p{..} etc. are not expressible in python re: the status is "py-unsupported"
and, when the question carries a hand-written py_equiv pattern, the counts come
from that equivalent (status "py-unsupported (equiv)").
"""
import os, re, sys, time, signal, warnings, argparse
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
warnings.simplefilter("ignore")


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def load_src(path):
    qs = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        f = ln.split(" ||| ")
        if len(f) not in (8, 9):
            raise SystemExit("bad line (%d fields): %s" % (len(f), ln[:80]))
        qs.append(dict(id=f[0], cls=f[1], files=f[2], intent=f[3],
                       flags=f[4], mode=f[5], guess=f[6], pattern=f[7],
                       equiv=f[8] if len(f) == 9 else ""))
    return qs


def read_input(path, cls, sample_bytes, full_cap):
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        head = fh.read(sample_bytes)
        full = None
        if size <= full_cap:
            fh.seek(0)
            full = fh.read()
    if cls != "binary" and len(head) == sample_bytes and size > sample_bytes:
        cut = head.rfind(b"\n")
        if cut > 0:
            head = head[:cut + 1]
    return head, full, size


def compile_pat(pat, flags, utf):
    fl = 0
    if "i" in flags: fl |= re.I
    if "m" in flags: fl |= re.M
    if "s" in flags: fl |= re.S
    if utf:
        if "ucp" not in flags: fl |= re.A
        return re.compile(pat, fl)
    return re.compile(pat.encode("utf-8"), fl)


FIRST_OFF = {}


def count(rx, data, mode, utf):
    if mode == "first":
        m = rx.search(data)
        FIRST_OFF["v"] = m.start() if m else -1
        return 1 if m else 0
    if mode == "line":
        sep = "\n" if utf else b"\n"
        return sum(1 for l in data.split(sep) if rx.search(l))
    return sum(1 for _ in rx.finditer(data))


def run_one(args):
    q, corpus, sample_mib, full_cap_mib, tmo = args
    flags = set(x for x in q["flags"].split(",") if x and x != "-")
    utf = "utf" in flags
    first = q["files"].split(";")[0]
    path = os.path.join(corpus, first)
    res = dict(q)
    res.update(status="", n_sample="", n_full="", sample_bytes="", file_bytes="",
               density="", seconds="", first_off="", density_full="", observed="")
    t0 = time.time()
    try:
        head, full, size = read_input(path, q["cls"], int(sample_mib * 1048576),
                                      int(full_cap_mib * 1048576))
    except OSError as e:
        res["status"] = "no-file: %s" % e
        return res
    res["sample_bytes"] = len(head)
    res["file_bytes"] = size
    status, rx = "ok", None
    try:
        rx = compile_pat(q["pattern"], flags, utf)
    except re.error as e:
        status = "py-unsupported (%s)" % str(e)[:60]
        if q["equiv"]:
            try:
                rx = compile_pat(q["equiv"], flags, utf)
                status += " (equiv)"
            except re.error as e2:
                status += " equiv-also-failed (%s)" % str(e2)[:40]
    res["status"] = status
    if rx is None:
        return res
    signal.signal(signal.SIGALRM, _alarm)
    mode = q["mode"]

    def go(raw):
        data = raw.decode("utf-8", "replace") if utf else raw
        signal.alarm(tmo)
        try:
            return count(rx, data, mode, utf)
        finally:
            signal.alarm(0)

    try:
        res["n_sample"] = go(head)
    except Timeout:
        res["n_sample"] = "timeout"
        res["status"] += " py-timeout(sample)"
    if mode == "first" and isinstance(res["n_sample"], int):
        res["first_off"] = FIRST_OFF.get("v", "")
    if full is not None:
        try:
            res["n_full"] = go(full)
        except Timeout:
            res["n_full"] = "timeout"
            res["status"] += " py-timeout(full)"
    else:
        res["n_full"] = "skipped(>%dMiB)" % full_cap_mib
    if isinstance(res["n_sample"], int) and mode != "first" and len(head):
        res["density"] = "%.2f" % (res["n_sample"] / (len(head) / 1048576))
    nf = res["n_full"] if isinstance(res["n_full"], int) else None
    if nf is not None and mode != "first":
        res["density_full"] = "%.2f" % (nf / (size / 1048576))
    d = None
    if mode != "first":
        if res["density_full"] != "":
            d = float(res["density_full"])
        elif res["density"] != "":
            d = float(res["density"])
    if mode == "first":
        res["observed"] = "hit" if (res["n_full"] == 1 or res["n_sample"] == 1) else "no-hit"
    elif d is not None:
        res["observed"] = ("none" if d == 0 else "rare" if d < 10 else "some" if d < 500
                           else "many" if d < 10000 else "everywhere")
    res["seconds"] = "%.1f" % (time.time() - t0)
    return res


COLS = ["id", "cls", "files", "intent", "pattern", "flags", "mode", "guess",
        "status", "n_sample", "n_full", "sample_bytes", "file_bytes", "density",
        "density_full", "observed", "first_off", "equiv", "seconds"]
HDR = ["id", "class", "files", "intent", "pattern", "flags", "mode",
       "guess_frequency", "py_status", "py_count_sample", "py_count_full",
       "sample_bytes", "file_bytes", "py_matches_per_MiB_sample",
       "py_matches_per_MiB_full", "observed_frequency", "first_match_offset_sample",
       "py_equiv_pattern", "check_seconds"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="/home/pcrec/projects/pcrec/worktrees/.corpus")
    ap.add_argument("--src", default=os.path.join(HERE, "questions.src"))
    ap.add_argument("--out", default=os.path.join(HERE, "questions.tsv"))
    ap.add_argument("--sample-mib", type=float, default=4)
    ap.add_argument("--full-cap-mib", type=float, default=64)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    qs = load_src(a.src)
    if a.only:
        keep = set(a.only.split(","))
        qs = [q for q in qs if q["id"] in keep]
    jobs = [(q, a.corpus, a.sample_mib, a.full_cap_mib, a.timeout) for q in qs]
    with Pool(a.jobs, maxtasksperchild=1) as p:
        out = list(p.imap(run_one, jobs))
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\t".join(HDR) + "\n")
        for r in out:
            row = []
            for c in COLS:
                v = str(r[c]).replace("\t", "\\t").replace("\n", "\\n")
                row.append(v)
            fh.write("\t".join(row) + "\n")
    bad = [r for r in out if not r["status"].startswith("ok")]
    print("questions: %d  ok: %d  other: %d" % (len(out), len(out) - len(bad), len(bad)))
    for r in bad:
        print("  %s %s" % (r["id"], r["status"]))


if __name__ == "__main__":
    main()
