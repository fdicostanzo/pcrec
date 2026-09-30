set -e
cd "$(mktemp -d /tmp/k73probe.XXXX)"
cat > pr2.c
gcc -O0 -o pr2 pr2.c -lpcre2-8
echo "libpcre2: $(pkg-config --modversion libpcre2-8 2>/dev/null || echo ?)"
S=('\x80' '\x80\x80' '\x80a' '\x80\xc3\xa9' '\x80\x80b' '\xff' '\xe3\x80' 'b')
for p in '' '\B' 'x*' '(?=)' '^' '$' '\b' '\G' '\G|b' '(?m)^a|\B' 'a|'; do echo "## pattern [$p]"; ./pr2 "$p" "${S[@]}"; done
echo "#### PCRE2_ANCHORED at start 0"
for p in '' 'x*' '\B'; do echo "## pattern [$p] anchored"; ./pr2 -A "$p" "${S[@]}"; done
cd /; rm -rf "$OLDPWD"
