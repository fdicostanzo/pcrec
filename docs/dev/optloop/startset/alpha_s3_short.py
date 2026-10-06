#!/usr/bin/env python3
# [START-SET] stage 3 alpha, K90 comparison probe (lane alphas3): does the DFA
# hat show K90's offset-0 / short-call shape? alpha_s3.sh times throughput only
# (its PERCALLS list is empty: the CTX cells' short-call subjects are owed to
# the bench, by the pcrec-bench-dev rule never reverse-engineered here). This
# probe is SYNTHETIC and SCRATCH TIER: five of alpha_s3.sh's own cells' artifacts
# (art/<cell>/{base,new,deny}/run, built by `alpha_s3.sh build`) are called ONCE
# per timed call (driver mode `c`, one rx_search at offset 0) on hand-written
# short subjects of four shapes: `hit0` (the match starts at offset 0), `late`
# (the match after a 40-byte filler with no start byte), `missT` (start bytes
# present, no match) and `missN` (no start byte at all). Absolute ns/call
# against the deny/base floor, alpha_s3.sh's protocol (taskset, load gate,
# LAUNCHES launches round-robin, median of per-launch medians).
import os, re, statistics, subprocess, sys, time

S2A = os.environ.get("S2A", "/tmp/s3alpha_startset")
CPU = os.environ.get("CPU", "2")
LAUNCHES = int(os.environ.get("LAUNCHES", "5"))
PASSES = int(os.environ.get("PASSES", "5"))
os.chdir(S2A)
FILL = b"the quick brown dog jumps over a lazy cat today"  # no A/E/F/C/t-f-n start byte except lowercase t,f(?)
X40 = b"x" * 40
SUBJ = {
    "aws": {
        "hit0": b"AKIAIOSFODNN7EXAMPLE and more text follows here\n",
        "late": X40 + b" AKIAIOSFODNN7EXAMPLE and more\n",
        "missT": b"All Around Again, Apples And Almonds Are Awesome, Ahoy\n",
        "missN": X40 + b" no such thing in this line at all\n",
    },
    "json-constant": {
        "hit0": b"true and false and null values in json\n",
        "late": X40 + b" null value\n",
        "missT": b"tfn tfn another notrue nulll falsey truth\n",
        "missN": X40 + b" zzz yyy zzz yyy zzz\n",
    },
    "level-context": {
        "hit0": b"ERROR connection timeout reached\n",
        "late": X40 + b" ERROR connection timeout reached\n",
        "missT": b"Eeeee Ccc Fff ERRORS fatally critical timeouts denied\n",
        "missN": X40 + b" nothing to see here at all\n",
    },
    "grok": {
        "hit0": b'"quoted text" and more text here\n',
        "late": X40 + b' "quoted text" and more\n',
        "missT": b'a lone " quote and a lone \' and ` tick and nothing else\n',
        "missN": X40 + b" no quote characters here at all\n",
    },
    "ctx-lazy-64": {
        "hit0": b"fail: disk quota exceeded here\n",
        "late": X40 + b" fail: disk quota exceeded\n",
        "missT": b"failure aborted panicky fail abort panic xx\n",
        "missN": X40 + b" nothing to see here at all\n",
    },
}


def load1():
    return float(open("/proc/loadavg").read().split()[0])


def run(cell, arm, f):
    r = subprocess.run(["taskset", "-c", CPU, "art/%s/%s/run" % (cell, arm), "c", f, str(PASSES)],
                       capture_output=True, text=True, timeout=300).stdout
    m = re.search(r"median=([0-9.]+)", r)
    res = re.search(r"result=(-?\d+)", r)
    return (float(m.group(1)) if m else float("nan")), (res.group(1) if res else "?")


def main():
    os.makedirs("short", exist_ok=True)
    print("# alpha_s3_short %s %s load1=%.2f CPU=%s LAUNCHES=%d PASSES=%d" % (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), os.uname().nodename, load1(), CPU, LAUNCHES, PASSES))
    print("cell\tshape\tresult(base/new/deny)\tbase\tnew\tdeny\tnew-base\tfloor\tverdict")
    for cell, shapes in SUBJ.items():
        for shape, data in shapes.items():
            f = "short/%s_%s.bin" % (cell, shape)
            open(f, "wb").write(data)
            while load1() >= 0.5:
                time.sleep(20)
            M = {a: [] for a in ("base", "new", "deny")}
            R = {}
            for _ in range(LAUNCHES):
                for a in M:
                    v, res = run(cell, a, f)
                    M[a].append(v)
                    R[a] = res
            med = {a: statistics.median_low(v) for a, v in M.items()}
            fl = abs(med["deny"] - med["base"])
            d = med["new"] - med["base"]
            v = "NULL" if abs(d) <= fl else ("WIN" if d < 0 else "REGRESSION")
            print("%s\t%s\t%s/%s/%s\t%.3f\t%.3f\t%.3f\t%+.3f\t%.3f\t%s" % (
                cell, shape, R["base"], R["new"], R["deny"], med["base"], med["new"], med["deny"], d, fl, v))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
