#!/usr/bin/env python3
"""bottom_model.py STREAMS.txt [CONTROL] -- checks the design's ILL-FORMED CONTEXT
MODEL against libpcre2's UCP|MATCH_INVALID_UTF answers (ucp_points.py's
STREAM rows).  The model (ucp_design.md s3.5): the character ENDING at a
position is found by pcrec's repaired back_step (walk back over
continuation bytes; the lead byte must be well-formed and DECLARE exactly
the run walked, utf8_design.md s5.2.1), the character STARTING there by
the stage-4 decoder (enc_utf8.c: truncated/overlong/surrogate/>10FFFF/
stray continuation are ill-formed); an ill-formed side, like a missing
side, is NOT a word character.  Scored only where the model is asked:
positions a pcrec thread can occupy (a character-start byte or the end,
the [K50] N_CSTART gate) and where libpcre2 returned a definite answer
(not '?', its MIU re-positioning).  Local python unicodedata supplies
word-ness; every character in the alphabet predates Unicode 6."""
import sys, unicodedata, ast
def dec(b, i):
    c = b[i]
    if c < 0x80: return c, 1
    for lo, hi, n, mn in ((0xC2, 0xDF, 2, 0x80), (0xE0, 0xEF, 3, 0x800), (0xF0, 0xF4, 4, 0x10000)):
        if lo <= c <= hi:
            if i + n > len(b): return None
            cp = c & (0x7F >> n)
            for k in range(1, n):
                if b[i+k] & 0xC0 != 0x80: return None
                cp = cp << 6 | (b[i+k] & 0x3F)
            if cp < mn or 0xD800 <= cp <= 0xDFFF or cp > 0x10FFFF: return None
            return cp, n
    return None
def back(b, p):
    if p == 0: return None
    q = p - 1
    while q > 0 and b[q] & 0xC0 == 0x80: q -= 1
    r = dec(b, q)
    # failing-direction control `unrepaired-back-step`: utf8_design.md
    # s5.2's first body, which never checked the lead DECLARES the run
    if CONTROL == "unrepaired-back-step" and b[q] & 0xC0 != 0x80:
        r2 = dec(b + b"\x80\x80\x80", q)
        return r2[0] if r2 else None
    return r[0] if r and q + r[1] == p else None
CONTROL = sys.argv[2] if __name__ == "__main__" and len(sys.argv) > 2 else ""
def word(cp):
    # failing-direction control `bottom-is-word`: an ill-formed side reads as
    # a WORD character -- the model must then DISAGREE somewhere
    if cp is None: return CONTROL == "bottom-is-word"
    cat = unicodedata.category(chr(cp))
    return cat[0] in "LN" or cat in ("Mn", "Pc")
def fwd(b, p):
    if p >= len(b): return None
    r = dec(b, p); return r[0] if r else None
PRED = {"\\\\b": lambda pv, nx: word(pv) != word(nx), "\\\\B": lambda pv, nx: word(pv) == word(nx),
        "(?<=\\\\w)": lambda pv, nx: word(pv), "(?!\\\\w)": lambda pv, nx: not word(nx)}
def main():
    ok = bad = skipped = 0
    import re
    TOK = re.compile(r"b'(?:[^'\\]|\\.)*'")
    for line in open(sys.argv[1]):
        if not line.startswith("STREAM") or "UTF|UCP|MIU" not in line: continue
        pat, subj, marks = [ast.literal_eval(t) for t in TOK.findall(line)]
        pred = PRED[pat.decode().replace("\\", "\\\\")]
        # walk the mark string back onto positions
        pos, i, ans = 0, 0, {}
        while i < len(marks):
            ch = marks[i:i+1]
            if ch in (b"|", b"?"): ans[pos] = ch; i += 1; continue
            if ch == b"<": j = marks.index(b">", i); ans[pos] = b"E"; i = j + 1; continue
            pos += 1; i += 1
        for p in range(len(subj) + 1):
            a = ans.get(p, b"")
            if a in (b"?", b"E") or (p < len(subj) and subj[p] & 0xC0 == 0x80): skipped += 1; continue
            m = pred(back(subj, p), fwd(subj, p))
            if m == (a == b"|"): ok += 1
            else: bad += 1; print("DISAGREE", pat, subj, "pos", p, "pcre2", a or b".", "model", m)
    print("#model%s vs 10.46 UCP|MIU: agree" % ((" [control " + CONTROL + "]") if CONTROL else "") + " %d, disagree %d, not asked %d" % (ok, bad, skipped))

if __name__ == "__main__":
    main()
