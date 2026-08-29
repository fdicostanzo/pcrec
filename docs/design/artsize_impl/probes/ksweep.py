#!/usr/bin/env python3
"""[ART-SIZE] STEP 2 — the K curve the census (§9) did not take.

For each subject pattern, emit at K in {1,2,3,4,6,8,12,16,32} and record
comment-excluded bytes, node-label count and emit time. This is the curve a
K-descent rule needs; the census took only the K=1 and K=default endpoints.
"""
import sys, json, time
sys.path.insert(0, "/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3")
from measure import emit, scan

KS = [1, 2, 3, 4, 6, 8, 12, 16, 32]

SUBJECTS = [
    # (label, pattern)   -- rung coverage stated in the note
    ("nested-N8",     "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}"),
    ("nested-N6",     "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,6}(){2,3}){1,2}){2,3}"),
    ("nested-N4",     "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,4}(){2,3}){1,2}){2,3}"),
    ("nested-N2",     "((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,2}(){2,3}){1,2}){2,3}"),
    ("alt4000-exact", "((a)|ab){4000}c"),
    ("alt4000-open",  "((a)|ab){0,4000}c"),
    ("altbc4000",     "((a)|bc){0,4000}d"),
    ("alt2047",       "((a)|ab){0,2047}c"),
    ("a10_20x10_50",  "(a{10,20}){10,50}"),
    ("a1_20x1_50",    "(a{1,20}){1,50}"),
    ("x_ab24_x012",   "(x(?:ab){2,4}){0,12}c"),
    ("cls8_8",        "(1{0,30}?[^]abc][^abc]){8,8}0+|a"),
    ("ab300",         "(ab){300}"),
    ("simple",        "a(b|c)+d"),
    ("isots",         r"\d{4}-\d{2}-\d{2}"),
]


def main():
    out = open(sys.argv[1], "w")
    out.write("label\tK\tbytes\tlabels\tgotos\ttables\ttable_entries\temit_s\terr\tpattern\n")
    for label, pat in SUBJECTS:
        for K in KS:
            text, err, secs = emit(pat, extra=["--unroll=%d" % K], timeout=300)
            if err:
                out.write("%s\t%d\t\t\t\t\t%.3f\t%s\t%s\n" % (label, K, secs, err, pat))
            else:
                r = scan(text)
                out.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%.3f\t\t%s\n" % (
                    label, K, r["bytes"], r["labels"], r["gotos"], r["tables"],
                    r["table_entries"], secs, pat))
            out.flush()
            print("%s K=%d done %.1fs" % (label, K, secs), flush=True)
    out.close()


if __name__ == "__main__":
    main()
