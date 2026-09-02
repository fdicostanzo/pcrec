00000000000021c0 <rx_search>:
    21c0:	endbr64
    21c4:	xor    %eax,%eax
    21c6:	cmp    %rdx,%rsi
    21c9:	jb     21e8 <rx_search+0x28>
    21cb:	cmp    %rsi,%rdx
    21ce:	jae    21e8 <rx_search+0x28>
    21d0:	cmpb   $0x3a,(%rdi,%rdx,1)
    21d4:	je     21f0 <rx_search+0x30>
    21d6:	add    $0x1,%rdx
    21da:	cmp    %rdx,%rsi
    21dd:	jne    21d0 <rx_search+0x10>
    21df:	xor    %eax,%eax
    21e1:	ret
    21e2:	nopw   0x0(%rax,%rax,1)
    21e8:	ret
    21e9:	nopl   0x0(%rax)
    21f0:	test   %rcx,%rcx
    21f3:	je     2200 <rx_search+0x40>
    21f5:	mov    %rdx,(%rcx)
    21f8:	add    $0x1,%rdx
    21fc:	mov    %rdx,0x8(%rcx)
    2200:	mov    $0x1,%eax
    2205:	ret
    2206:	cs nopw 0x0(%rax,%rax,1)

