"""[REVW.4] item 5: the `--` guard's own acceptance proof. Every option
spelling the CLI knows, in four positions relative to `--`, before vs after."""
import subprocess, sys, hashlib, re, os
REF, NEW, MAINC = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(MAINC).read()
# every literal the parser compares against, plus every axis spelling
flags = sorted(set(re.findall(r'strcmp\(a,\s*"([^"]+)"\)', src)) |
               set(re.findall(r'strncmp\(a,\s*"([^"]+)",', src)) |
               set(re.findall(r'"(-f(?:no-)?[a-z-]+)"', open('src/core/axes.def').read())))
shapes = [
    lambda f: ["--", f],
    lambda f: [f, "--", "a"],
    lambda f: ["--", f, "b"],
    lambda f: ["--count-groups", "--", f],
]
def run(b, args):
    try:
        r = subprocess.run([b] + args, capture_output=True, timeout=30)
        return (r.returncode, hashlib.sha256(r.stdout).hexdigest()[:12],
                r.stderr.decode("utf-8", "replace").strip())
    except subprocess.TimeoutExpired:
        return ("T", "", "")
n = same = diff = 0
diffs = []
for f in flags:
    for sh in shapes:
        args = sh(f)
        a, b = run(REF, args), run(NEW, args)
        n += 1
        if a == b: same += 1
        else:
            diff += 1
            if len(diffs) < 10: diffs.append((args, a, b))
print(f"flag spellings found in the parser + axes.def: {len(flags)}")
print(f"invocations: {n}  identical: {same}  DIFFERING: {diff}")
for d in diffs: print("DIFF", d)
sys.exit(1 if diff else 0)
