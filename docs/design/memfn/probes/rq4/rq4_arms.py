"""docs/design/memfn/probes/rq4/rq4_arms.py -- the arm sets and the pair
definitions rq4.py (the runner) and rq4_table.py (the renderer) both read
(lane s21prep). One module so the two cannot disagree on an arm's flags, a
pair's sign or an identity column's name.

An ARM is (name, pcrec flags). A PAIR (x, y, short, verdict column) is a
comparison delta = x - y; the table renders it when both arms were run. The
null population of a pair is every cell whose x and y artifacts are
byte-identical (meta.tsv column `id_col(x, y)`).

ARM SETS (`rq4.py --armset NAME`; `--arm NAME=FLAGS` repeated builds a custom
set instead):
  slot20   DEFAULT, KBDENY, OFF -- slot20's three arms, unchanged (the table of
           that run re-renders byte-identically)
  slot21   DEFAULT, NOPAD, FULL, KBDENY, OFF -- R-14's five arms (below)
  slot21x  slot21 plus FULLKB -- the exact analogue of slot20's KBDENY on R-13's
           verify, so FULL-FULLKB reproduces slot20's D-K comparison text for
           text (6 arms, 6/5 of slot21's timing wall)

slot21's arms (all at -fmemfn-simd unless OFF; deny syntax is a comma list):
  DEFAULT  the R-14 build: trimmed verify (r14b) + padded word (r14p) + KA and KB
  NOPAD    --memfn=no-vrun-pad                     = trim only
  FULL     --memfn=no-vrun-pad,no-vrun-trim        = R-13's whole-run verify
  KBDENY   --memfn=no-vrun-kb                      = KA alone, trim + pad ON
  FULLKB   --memfn=no-vrun-pad,no-vrun-trim,no-vrun-kb = slot20's KBDENY (slot21x)
  OFF      -fno-memfn-simd                         = the scalar layer
"""

SIMD = "-fmemfn-simd"
ARMSETS = {
    "slot20": [("DEFAULT", [SIMD]),
               ("KBDENY", [SIMD, "--memfn=no-vrun-kb"]),
               ("OFF", ["-fno-memfn-simd"])],
    "slot21": [("DEFAULT", [SIMD]),
               ("NOPAD", [SIMD, "--memfn=no-vrun-pad"]),
               ("FULL", [SIMD, "--memfn=no-vrun-pad,no-vrun-trim"]),
               ("KBDENY", [SIMD, "--memfn=no-vrun-kb"]),
               ("OFF", ["-fno-memfn-simd"])],
}
ARMSETS["slot21x"] = ARMSETS["slot21"][:4] + [
    ("FULLKB", [SIMD, "--memfn=no-vrun-pad,no-vrun-trim,no-vrun-kb"])] + ARMSETS["slot21"][4:]

# (x, y, short name, verdict column header); delta = x - y, + = x costs.
# D-K and ON-OFF keep slot20's names and headers so a slot20 run re-renders
# byte-identically.
PAIRS = [("DEFAULT", "FULL", "D-F", "R-14 verify vs R-13 verify"),
         ("NOPAD", "FULL", "N-F", "trim vs R-13 verify"),
         ("DEFAULT", "NOPAD", "D-N", "pad vs trim"),
         ("DEFAULT", "KBDENY", "D-K", "KB verdict"),
         ("FULL", "KBDENY", "F-K", "R-13 verify vs KA-alone R-14"),
         ("FULL", "FULLKB", "F-FK", "slot20 KB question"),
         ("DEFAULT", "OFF", "ON-OFF", "SIMD verdict")]

# slot20's meta.tsv names for its three pairs (any other pair is id_<x>_<y>)
LEGACY_ID = {("DEFAULT", "KBDENY"): "id_DK", ("DEFAULT", "OFF"): "id_DO", ("KBDENY", "OFF"): "id_KO"}


def id_col(x, y):
    return LEGACY_ID.get((x, y)) or LEGACY_ID.get((y, x)) or "id_%s_%s" % (x, y)


def all_pairs(names):
    """every unordered pair of the run's arms, in arm order (meta.tsv columns)"""
    return [(x, y) for i, x in enumerate(names) for y in names[i + 1:]]


def parse_arm(spec):
    name, _, flags = spec.partition("=")
    if not name or not name.isalnum():
        raise ValueError("--arm wants NAME=FLAGS with an alphanumeric NAME: %r" % spec)
    return name, flags.split()
