0000000000002100 <rx_search>:
    2100:	cmp    %rsi,%rdx
    2103:	jbe    2108 <rx_search+0x8>
    2105:	xor    %eax,%eax
    2107:	ret
    2108:	mov    $0x3b9aca00,%r8d
    210e:	jmp    2118 <rx_search+0x18>
    2110:	cmp    %rsi,%rdx
    2113:	mov    %r9,%rdx
    2116:	je     2105 <rx_search+0x5>
    2118:	lea    0x1(%rdx),%r9
    211c:	mov    %rdx,%r10
    211f:	cmp    %rsi,%r9
    2122:	jbe    2150 <rx_search+0x50>
    2124:	mov    %r10,%r11
    2127:	sub    %rdx,%r11
    212a:	test   %r11,%r11
    212d:	jle    2134 <rx_search+0x34>
    212f:	sub    %r11,%r8
    2132:	js     2187 <rx_search+0x87>
    2134:	cmp    %rdx,%r10
    2137:	jle    2110 <rx_search+0x10>
    2139:	lea    0x6(%r11),%rax
    213d:	cmp    $0x5,%rax
    2141:	jb     218d <rx_search+0x8d>
    2143:	test   %r11,%r11
    2146:	js     2110 <rx_search+0x10>
    2148:	jmp    2191 <rx_search+0x91>
    214a:	nopw   0x0(%rax,%rax,1)
    2150:	mov    %rdx,%r10
    2153:	xor    %eax,%eax
    2155:	data16 cs nopw 0x0(%rax,%rax,1)
    2160:	movzbl (%rdi,%r10,1),%r11d
    2165:	add    $0xd0,%r11b
    2169:	cmp    $0xa,%r11b
    216d:	jae    2124 <rx_search+0x24>
    216f:	lea    0x2(%r10),%r11
    2173:	inc    %r10
    2176:	cmp    %rsi,%r11
    2179:	ja     2124 <rx_search+0x24>
    217b:	cmp    $0xe,%rax
    217f:	lea    0x1(%rax),%rax
    2183:	jbe    2160 <rx_search+0x60>
    2185:	jmp    2124 <rx_search+0x24>
    2187:	mov    $0xfffffffc,%eax
    218c:	ret
    218d:	add    $0xfffffffa,%eax
    2190:	ret
    2191:	mov    $0x1,%eax
    2196:	test   %rcx,%rcx
    2199:	je     2190 <rx_search+0x90>
    219b:	mov    %rdx,(%rcx)
    219e:	mov    %r10,0x8(%rcx)
    21a2:	ret
    21a3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)

