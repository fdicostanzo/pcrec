#!/usr/bin/env python3
"""[PF-KNOW] (D140) — THE DYNAMIC SHARE: how many of the VM's executed
tests lie on the prefilter-proven leading/trailing segments.

Method: compile the pattern with the tree's own pcrec, build the artifact
with `--coverage` against a find-all driver, run it once over the subject,
and read gcov's per-line execution counts.  Lines are classified by
position in the emitted program region (`goto rx_L0;` .. `rx_accept:`):
  lead   from `rx_L0:` up to the FIRST choice-point line (an RX_PUSH, a
         span-loop cursor, a counter/revdet loop, an island switch, or a
         lookaround/backref/call marker) — the leading deterministic segment
  trail  from the LAST choice-point line's block end to `rx_accept:` — the
         trailing deterministic segment (only counted when the program has
         a choice point; on a det_all program lead == everything)
  mid    everything else
A "test" is an executed `if (`/`while (`/`switch (` line.  Reported:
executed tests per class, plus the driver's match count and the number of
search calls, so the per-attempt cost can be read off too.

Environment: PCREC CC GCOV OUT
Usage: dyn.py <id> <pattern-file-or-literal:...> <subject> [findall|first]
Writes OUT/<id>.json and prints one TSV row.  gcov counts are not timing;
no clock is read.
"""
import os, sys, re, json, subprocess, shutil

E = os.environ
PCREC, CC, GCOV, OUT = E["PCREC"], E.get("CC", "gcc-16"), E.get("GCOV", "gcov-16"), E["OUT"]

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.h"
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc(n > 0 ? n : 1); fread(buf, 1, n, f); fclose(f);
    int find_all = argc < 3 || strcmp(argv[2], "first") == 0 ? (argc < 3 ? 1 : 0) : 1;
    ptrdiff_t caps[RX_NCAPS][2]; memset(caps, 0, sizeof caps);
    long count = 0, calls = 0; size_t pos = 0;
    for (;;) {
        int r = rx_search(buf, (size_t)n, pos, caps); calls++;
        if (r <= 0) { if (r < 0) fprintf(stderr, "rx_search gave up: %d\n", r); break; }
        count++;
        size_t e = (size_t)caps[0][1];
        pos = (e > pos) ? e : pos + 1;
        if (!find_all || pos > (size_t)n) break;
    }
    printf("count=%ld calls=%ld\n", count, calls);
    return 0;
}
'''

CHOICE_RE = re.compile(r"RX_PUSH\(|_span_cursor = scan_position|switch \(|RX_CHARGE_WORK|_rv\d+_cursor|"
                       r"counter|RX_LOOK|lookpos|RX_BREF|RX_CALL|goto \*|_isl")
TEST_RE = re.compile(r"^\s*(if|while|for|switch) \(|^\s*\} while|&& |\|\| ")

def main():
    ident, patarg, subject = sys.argv[1], sys.argv[2], sys.argv[3]
    mode = sys.argv[4] if len(sys.argv) > 4 else "findall"
    pat = patarg[len("literal:"):].encode("latin-1") if patarg.startswith("literal:") else open(patarg, "rb").read().rstrip(b"\n")
    work = os.path.join(OUT, "work_" + re.sub(r"[^A-Za-z0-9_.-]", "_", ident))
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    gen = os.path.join(work, "gen.c")
    r = subprocess.run([PCREC, "--features", "all", "-p", "rx", "-o", gen, "--pattern", pat], capture_output=True, timeout=120)
    if r.returncode != 0:
        print("%s\trefused\t%s" % (ident, r.stderr.decode("latin-1").strip()[:100])); return
    open(os.path.join(work, "driver.c"), "w").write(DRIVER)
    r = subprocess.run([CC, "-O1", "--coverage", "-fno-inline", "-I" + work, "-o", os.path.join(work, "run"),
                        gen, os.path.join(work, "driver.c")], capture_output=True, cwd=work, timeout=600)
    if r.returncode != 0:
        print("%s\tcc-failed\t%s" % (ident, r.stderr.decode("latin-1").strip()[:200])); return
    r = subprocess.run([os.path.join(work, "run"), subject, mode], capture_output=True, cwd=work, timeout=600)
    drv = r.stdout.decode().strip()
    m = re.search(r"count=(\d+) calls=(\d+)", drv)
    count, calls = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    subprocess.run([GCOV, "-i", "run-gen.gcda"], capture_output=True, cwd=work, timeout=120)
    # gcov -i writes <name>.gcov.json.gz (gcc >= 9) or a text intermediate
    counts = {}
    import glob
    jz = glob.glob(os.path.join(work, "*gen*.gcov.json.gz"))
    jsz = jz[0] if jz else ""
    txt = os.path.join(work, "gen.c.gcov")
    if jsz and os.path.exists(jsz):
        import gzip
        j = json.load(gzip.open(jsz))
        for f in j["files"]:
            if not f["file"].endswith("gen.c"): continue
            for ln in f["lines"]:
                counts[ln["line_number"]] = counts.get(ln["line_number"], 0) + ln["count"]
    elif os.path.exists(txt):
        for ln in open(txt):
            if ln.startswith("lcount:"):
                _t, no, c = ln.strip().split(",")[0].split(":")[1], ln.strip().split(",")[0].split(":")[1], ln.strip().split(",")[1]
                counts[int(no)] = counts.get(int(no), 0) + int(c)
    else:
        print("%s\tno-gcov" % ident); return
    src = open(gen, encoding="latin-1").read().split("\n")
    # locate the program region of rx_match_anchored
    l0 = next(i for i, s in enumerate(src) if s.strip() == "goto rx_L0;") + 1
    acc = next(i for i, s in enumerate(src) if s.startswith("rx_accept:"))
    region = list(range(l0, acc))
    choice_lines = [i for i in region if CHOICE_RE.search(src[i]) and not src[i].strip().startswith(("/*", "*"))]
    first_c = choice_lines[0] if choice_lines else acc
    last_c = choice_lines[-1] if choice_lines else l0
    # the trailing segment starts at the first LABEL after the last choice line
    trail_start = acc
    for i in range(last_c + 1, acc):
        if re.match(r"^rx_L\d+:", src[i]): trail_start = i; break
    if not choice_lines: trail_start = acc
    tot = {"lead": 0, "mid": 0, "trail": 0}
    lines = {"lead": 0, "mid": 0, "trail": 0}
    for i in region:
        s = src[i]
        if not TEST_RE.search(s) or s.strip().startswith(("/*", "*")): continue
        c = counts.get(i + 1, 0)
        k = "lead" if i < first_c else "trail" if i >= trail_start else "mid"
        tot[k] += c; lines[k] += 1
    # the entry and search-loop attempts: count executions of the `goto rx_L0;` line
    attempts = counts.get(l0, 0)
    rec = dict(id=ident, pattern=pat.decode("latin-1"), subject=os.path.basename(subject), mode=mode,
               matches=count, calls=calls, attempts=attempts, tests=tot, test_lines=lines,
               first_choice_line=first_c + 1 if choice_lines else None, program_lines=len(region))
    json.dump(rec, open(os.path.join(OUT, re.sub(r"[^A-Za-z0-9_.-]", "_", ident) + ".json"), "w"), indent=1)
    allt = sum(tot.values()) or 1
    print("%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%.1f%%\t%.1f%%" % (ident, mode, count, calls, attempts, tot["lead"], tot["mid"], tot["trail"],
          100.0 * tot["lead"] / allt, 100.0 * (tot["lead"] + tot["trail"]) / allt))

if __name__ == "__main__":
    main()
