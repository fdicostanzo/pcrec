0000000000002100 <rx_search>:
    2100:	xor    %eax,%eax
    2102:	cmp    %rsi,%rdx
    2105:	ja     21ee <rx_search+0xee>
    210b:	mov    %rdx,%r8
    210e:	jae    216f <rx_search+0x6f>
    2110:	movzbl (%rdi,%rdx,1),%r8d
    2115:	add    $0x9f,%r8b
    2119:	cmp    $0x19,%r8b
    211d:	ja     21da <rx_search+0xda>
    2123:	lea    0x1(%rdx),%r8
    2127:	cmp    %rsi,%r8
    212a:	jae    216f <rx_search+0x6f>
    212c:	movzbl (%rdi,%r8,1),%r9d
    2131:	add    $0x9f,%r9b
    2135:	cmp    $0x1a,%r9b
    2139:	jae    2175 <rx_search+0x75>
    213b:	lea    0x2(%rdx),%r8
    213f:	cmp    %rsi,%r8
    2142:	jae    216f <rx_search+0x6f>
    2144:	movzbl (%rdi,%r8,1),%r9d
    2149:	add    $0x9f,%r9b
    214d:	cmp    $0x19,%r9b
    2151:	ja     2175 <rx_search+0x75>
    2153:	lea    0x3(%rdx),%r8
    2157:	cmp    %rsi,%r8
    215a:	jae    216f <rx_search+0x6f>
    215c:	movzbl (%rdi,%r8,1),%esi
    2161:	add    $0x9f,%sil
    2165:	cmp    $0x19,%sil
    2169:	ja     2175 <rx_search+0x75>
    216b:	lea    0x4(%rdx),%r8
    216f:	cmp    $0xffffffffffffffff,%r8
    2173:	je     21ee <rx_search+0xee>
    2175:	cmp    %rdx,%r8
    2178:	jbe    21d5 <rx_search+0xd5>
    217a:	movzbl -0x1(%rdi,%r8,1),%eax
    2180:	add    $0x9f,%al
    2182:	cmp    $0x19,%al
    2184:	ja     21d5 <rx_search+0xd5>
    2186:	lea    -0x1(%r8),%rax
    218a:	cmp    %rdx,%rax
    218d:	jbe    21d0 <rx_search+0xd0>
    218f:	movzbl -0x2(%rdi,%r8,1),%esi
    2195:	add    $0x9f,%sil
    2199:	cmp    $0x1a,%sil
    219d:	jae    21d0 <rx_search+0xd0>
    219f:	lea    -0x2(%r8),%rsi
    21a3:	cmp    %rdx,%rsi
    21a6:	jbe    21ef <rx_search+0xef>
    21a8:	movzbl -0x2(%rdi,%rax,1),%eax
    21ad:	add    $0x9f,%al
    21af:	cmp    $0x19,%al
    21b1:	ja     21ef <rx_search+0xef>
    21b3:	lea    -0x3(%r8),%rax
    21b7:	cmp    %rdx,%rax
    21ba:	jbe    21d0 <rx_search+0xd0>
    21bc:	movzbl -0x4(%rdi,%r8,1),%edx
    21c2:	add    $0x9f,%dl
    21c5:	lea    -0x4(%r8),%rsi
    21c9:	cmp    $0x1a,%dl
    21cc:	cmovb  %rsi,%rax
    21d0:	mov    %rax,%rdx
    21d3:	jmp    21dd <rx_search+0xdd>
    21d5:	mov    %r8,%rdx
    21d8:	jmp    21dd <rx_search+0xdd>
    21da:	mov    %rdx,%r8
    21dd:	mov    $0x1,%eax
    21e2:	test   %rcx,%rcx
    21e5:	je     21ee <rx_search+0xee>
    21e7:	mov    %rdx,(%rcx)
    21ea:	mov    %r8,0x8(%rcx)
    21ee:	ret
    21ef:	mov    %rsi,%rdx
    21f2:	jmp    21dd <rx_search+0xdd>
    21f4:	data16 data16 cs nopw 0x0(%rax,%rax,1)

