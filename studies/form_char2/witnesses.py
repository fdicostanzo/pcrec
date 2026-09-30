# [FORM-CHAR2] timing witnesses: name -> (pattern, engine flag, match-subject, note)
import os
BENCH = os.environ.get("BENCH_DIR", os.path.expanduser("~/pcrec-bench/bench"))
def rx(p):
    try: return open(os.path.join(BENCH, p)).read().rstrip("\n")
    except OSError: return None   # --reuse builds on a box without pcrec-bench
L = "abcdefghijklmnopqrstuvwxyz"
W = {
 "ci256":   (rx("altwide/patterns/ci-256.rx"), "--engine=vm", b"YoSlWsSiYyBw", "the bench's one witness; 26 fold classes, 1842 sites"),
 "waf744":  (rx("capability/patterns/wild-waf-crs-942360-concat-sqli.rx"), "--engine=vm", b"SeLeCt  GrOuP_CoNcAt(", "744 sites, one fold constant up to 98x"),
 "waf186":  (rx("capability/patterns/wild-waf-crs-942140-dbnames.rx"), "--engine=vm", b"DaTaBaSe(", "186 sites, fold constant up to 24x"),
 "slack":   (rx("capability/patterns/wild-secrets-slack-webhook-url.rx"), "", b"HTTPS://hooks.slack.com/services/T12345678/B12345678/abcdefghijklmnopqrstuvwx", "default-route VM, real customer"),
 "union":   ("(?i)union.*?select.*?from", "--engine=vm", b"UNION ALL SELECT a FROM t", "15 sites"),
 "kwalt":   ("(?i)\\b(?:select|insert|update|delete|create|drop|alter|truncate)\\b", "--engine=vm", b"SeLeCt", "caseless keyword alternation, ~40 sites"),
 "hdr":     ("(?i)content-security-policy:", "--engine=vm", b"Content-Security-Policy:", "one long caseless literal, 22 fold sites"),
 "lit16":   ("(?i)abcdefghijklmnop", "--engine=vm", b"AbCdEfGhIjKlMnOp", "16 distinct fold classes (atom-table row fires)"),
 "hotloop": ("(?i)e+q", "--engine=vm", b"eEeEeEeEeEeEeEeEq", "ONE fold class in a hot loop (subject: runs of 64 e/E)"),
 "hotchain":("(?i)eeeeeeeeeeeeeeeeeeeeeeeeeeq", "--engine=vm", b"eEeEeEeEeEeEeEeEeEeEeEeEeEq", "ONE fold constant repeated 26x in a chain"),
}
