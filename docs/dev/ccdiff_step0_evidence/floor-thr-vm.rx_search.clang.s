0000000000002100 <rx_search>:
    2100:	xor    %eax,%eax
    2102:	cmp    %rsi,%rdx
    2105:	jbe    2110 <rx_search+0x10>
    2107:	ret
    2108:	nopl   0x0(%rax,%rax,1)
    2110:	cmp    %rsi,%rdx
    2113:	jae    211b <rx_search+0x1b>
    2115:	cmpb   $0x3a,(%rdi,%rdx,1)
    2119:	je     2125 <rx_search+0x25>
    211b:	cmp    %rdx,%rsi
    211e:	je     2107 <rx_search+0x7>
    2120:	inc    %rdx
    2123:	jmp    2110 <rx_search+0x10>
    2125:	mov    $0x1,%eax
    212a:	test   %rcx,%rcx
    212d:	je     2107 <rx_search+0x7>
    212f:	mov    %rdx,(%rcx)
    2132:	inc    %rdx
    2135:	mov    %rdx,0x8(%rcx)
    2139:	ret
    213a:	nopw   0x0(%rax,%rax,1)

