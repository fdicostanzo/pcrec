#!/usr/bin/perl
# sr_perl.pl -- the [DD-14.D27] corpus's SECOND-ORACLE runner (D71 item 5).
#
# Reads a TSV job file: id \t pattern-as-hex \t startpos \t subject-as-hex.
# Everything is hex-encoded so a pattern or a subject full of regex
# metacharacters, quotes, spaces or control bytes survives the trip without
# any shell or field-separator escaping at all -- the brief's "subject read
# from a file" advice, taken one step further because the PATTERNS in this
# corpus are as hostile to a shell as the subjects are.
#
# Prints, per job: id \t ERR \t message
#                | id \t nomatch
#                | id \t match \t s0,e0 s1,e1 ...   (from @- and @+, so an
#                                                    unset group is -1,-1)
#
# @-/@+ rather than $& per the brief: unset groups and byte offsets then
# report the same way PCRE2's ovector does.
use strict;
use warnings;

open(my $fh, '<', $ARGV[0]) or die "open: $!";
while (my $line = <$fh>) {
    chomp $line;
    next unless length $line;
    my ($id, $pathex, $start, $subjhex) = split(/\t/, $line, 4);
    my $pat  = pack("H*", $pathex);
    my $subj = pack("H*", $subjhex);

    my $re;
    {
        local $SIG{__WARN__} = sub { };
        $re = eval { qr/$pat/ };
    }
    if (!defined $re) {
        my $e = $@ // "unknown";
        $e =~ s/\s+/ /g;
        $e =~ s/^\s+|\s+$//g;
        print "$id\tERRC\t$e\n";
        next;
    }

    my ($matched, @starts, @ends);
    {
        local $SIG{__WARN__} = sub { };
        $matched = eval {
            pos($subj) = $start;
            if ($subj =~ /$re/g) {
                @starts = @-;
                @ends   = @+;
                1;
            } else {
                0;
            }
        };
    }
    if (!defined $matched) {
        my $e = $@ // "unknown";
        $e =~ s/\s+/ /g;
        $e =~ s/^\s+|\s+$//g;
        print "$id\tERRM\t$e\n";
        next;
    }
    if (!$matched) { print "$id\tnomatch\n"; next; }

    my @pairs;
    for my $i (0 .. $#starts) {
        my $s = defined $starts[$i] ? $starts[$i] : -1;
        my $e = defined $ends[$i]   ? $ends[$i]   : -1;
        push @pairs, "$s,$e";
    }
    print "$id\tmatch\t" . join(" ", @pairs) . "\n";
}
