#!/bin/bash
# witness.sh PCREC : lane vmcons premise test + review-witness REACH probes at the base (lane/trailgc).
# Twins are one-line text deletions applying a review finding's rule AS WRITTEN; p2 is libpcre2-8 10.46 (p2.c).
# Run: S=$PCREC_TMPDIR/scratch/vmcons bash witness.sh $S/pcrec_base   (writes only under $S)
PC=$1; S=${S:?}; E=$(dirname "$0"); mkdir -p "$S/w"; gcc -O1 -o "$S/w/p2" "$E/p2.c" -lpcre2-8 || exit 1
mk() { # name flags pattern : emit with a main that prints every group
  gnutimeout 30 "$PC" -p rx --features all $2 --emit-main -o "$S/w/$1.c" --pattern "$3" || return 1
  sed 's|printf("match %td %td\\n", capture_spans\[0\]\[0\], capture_spans\[0\]\[1\]);|for (int g_ = 0; g_ < RX_NCAPS; g_++) printf("%d:%td,%td ", g_, capture_spans[g_][0], capture_spans[g_][1]); printf("\\n");|' "$S/w/$1.c" > "$S/w/$1_s.c"; }
run() { gcc -O2 -w -o "$S/w/$1" "$S/w/$1.c" && gnutimeout 10 "$S/w/$1" "$2"; }
del() { # name ERE : the twin without the lines matching ERE (inside the matcher)
  command grep -v -E "$2" "$S/w/$1_s.c" > "$S/w/$1_t.c"; }
echo "== F1 (premise): ^(?:(?:[bB]|[cC]d)(\w))+by\$ ; DEAD on the event stream deletes the revdet entry write"
P='^(?:(?:[bB]|[cC]d)(\w))+by$'; mk f1 "" "$P"; gnutimeout 30 "$PC" -p rx --features all --emit-ir --pattern "$P" > "$S/w/f1.ir"
echo "listing rows naming slot 4: $(command grep -c 'slot_values\[4\]' "$S/w/f1.ir") (the set only); C lines reading it: $(command grep -c '(size_t)slot_values\[4\]' "$S/w/f1_s.c")"
del f1 'RX_SET\(RX_SLOT_REVDET0_ENTRY'; for s in bxby bxcdzby BqBqby; do echo "$s stock: $(run f1_s $s) twin: $(run f1_t $s) pcre2: $("$S/w/p2" "$P" $s)"; done
echo "== F2: ^(b)(?1) --engine=vm -fno-splice-calls ; the caller's group-1 close writes deleted (call read missing)"
mk f2 "--engine=vm -fno-splice-calls" '^(b)(?1)'; awk '/^rx_L7:/{f=1} f&&/RX_SET\(RX_SLOT_GROUP1_(START|END)/{next} {print} /^rx_L5:/{f=0}' "$S/w/f2_s.c" > "$S/w/f2_t.c"
echo "bb stock: $(run f2_s bb) twin: $(run f2_t bb) pcre2: $("$S/w/p2" '^(b)(?1)' bb)"
echo "== F3 (reach): ^(?:(?>ab|a)c|abd) --engine=vm ; the CUT mark's value text reads run->resume_depth"
mk f3 "--engine=vm" '^(?:(?>ab|a)c|abd)'; command grep -n 'RX_SET(RX_SLOT_CUT_MARK0, (ptrdiff_t)run->resume_depth)' "$S/w/f3_s.c" | head -1
echo "== F6 (reach): left recursion gives FRAMES in stock (D as tabled answers instead)"
mk f6 "" '(?:a|(?R))+'; for s in b ab ba; do echo "$s stock: $(run f6_s $s) pcre2: $("$S/w/p2" '(?:a|(?R))+' $s)"; done
mk f6b "" '^(a|(?1)b)'; for s in x b; do echo "$s stock: $(run f6b_s $s)"; done
echo "== F7 (reach): a(?:\dx|[a-z]y)c --engine=vm is framed today with ONE disjoint push"
mk f7 "--engine=vm" 'a(?:\dx|[a-z]y)c'; command grep -E 'define RX_VM_FRAMELESS|define RX_VM_ENTRY_SHAPE' "$S/w/f7.c"; echo "push sites: $(command grep -c 'RX_PUSH(&&' "$S/w/f7.c")"
echo "== F7 (push-site under-count): [abd]x|[acd]y|[bcd]z --engine=vm ; stock push sites (D's per-class sum is 5)"
gnutimeout 30 "$PC" -p rx --features all --engine=vm --emit-ir --pattern '[abd]x|[acd]y|[bcd]z' | command grep -E '^(resume-points|islands)'
echo "== F8: callout read set is the pattern's ncap under --no-captures ; the group writes deleted"
mk f8 "--allow-code=c --no-captures" '(a)(?:(b)|c)(?C`c: return RX_CAP_SET(2) ? RX_FAIL : RX_PASS;`)d'
command grep -o 'rx_co_ctx.ncap = [0-9]*' "$S/w/f8_s.c"; del f8 '^    RX_SET\(RX_SLOT_GROUP[12]_'
for s in abd acd; do echo "$s stock: $(run f8_s $s) twin: $(run f8_t $s)"; done
echo "== F14 (reach): (?:a|ab){300}+c --engine=vm takes the counter rung ; (?:a|bc){3}+ does not"
gnutimeout 30 "$PC" -p rx --features all --engine=vm --emit-ir --pattern '(?:a|ab){300}+c' | command grep '^rungs'
gnutimeout 30 "$PC" -p rx --features all --engine=vm --emit-ir --pattern '(?:a|bc){3}+' | command grep '^rungs'
