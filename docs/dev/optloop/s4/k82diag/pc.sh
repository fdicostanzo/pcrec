for f in subj/short/*.bin; do id=$(basename $f .bin); n=$(wc -c < $f | tr -d ' ')
 g=$(art/union-caps/cnt/run c $f 1 2>&1 >/dev/null | tail -1)
 calls=$(sed -E 's/.*gate_calls=([0-9]+).*/\1/' <<<"$g"); pass=$(sed -E 's/.*gate_pass=([0-9]+).*/\1/' <<<"$g"); mc=$(sed -E 's/.*memchr_calls=([0-9]+).*/\1/' <<<"$g"); cmp=$(sed -E 's/.*cmp=([0-9]+).*/\1/' <<<"$g")
 u=$(python3 -c "import sys;b=open('$f','rb').read().lower();print(b.count(b'u'),b.count(b'c'),int(b'select' in b),int(b'union' in b))")
 declare -A M=(); for i in 1 2 3; do for a in deny new; do v=$(art/union-caps/$a/run c $f 5 | sed -n 's/.*median=\([0-9.]*\).*/\1/p'); M[$a]="${M[$a]:-} $v"; done; done
 b=$(tr ' ' '\n' <<<"${M[deny]}" | grep . | sort -g | sed -n 2p); nw=$(tr ' ' '\n' <<<"${M[new]}" | grep . | sort -g | sed -n 2p); unset M
 awk -v id=$id -v n=$n -v b=$b -v nw=$nw -v c=$calls -v p=$pass -v mc=$mc -v cmp=$cmp -v u="$u" 'BEGIN{printf "%-26s n=%5d base=%7.2f new=%7.2f d=%+7.2f pass=%.2f memchr/call=%.1f cmp/call=%.1f u,c,sel,uni=%s\n", id,n,b,nw,nw-b,p/c,mc/c,cmp/c,u}'
done
