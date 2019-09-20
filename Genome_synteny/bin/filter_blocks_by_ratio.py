#!/usr/bin/env python3

import sys

# Import palettable
try:
    from palettable.tableau import GreenOrange_12
except ImportError:
    print("We need palettable, sorry...\ninstall: pip install palettable")
    sys.exit(1)

try:
    import palettable.cartocolors.qualitative
except ImportError:
    print("We need palettable, sorry...\ninstall: pip install palettable")
    sys.exit(1)

scafcut = 1000
blockcut = 500
rate = 0

if len(sys.argv) < 4:
    print("Usage: python3 {} <scaf.lens> <block.record.txt> <filtered.link.txt>".format(sys.argv[0]))
    exit()
outfile = sys.argv[3]

def getLen(length_file):
    lens = {}
    with open(length_file, 'r') as fh:
        for i in fh:
            tmp = i.strip().split()
            lens[tmp[0]] = int(tmp[1])
    return lens


def main():
    synteny = {}
    good_scaf = []
    records = []
    lens = getLen(sys.argv[1])
    out = open(outfile, 'w')
    with open(sys.argv[2], 'r') as fh:
        for b in fh:
            tmp = b.strip().split()
            records.append(tmp)
            if lens[tmp[0]] >= scafcut and lens[tmp[3]] >= scafcut:
                block_len = int(tmp[2]) - int(tmp[1]) + 1
                if block_len < blockcut:
                    continue
                if tmp[0] in synteny.keys():
                    synteny[tmp[0]] += block_len
                else:
                    synteny[tmp[0]] = block_len

    for k in synteny.keys():
        if synteny[k] >= lens[k] * rate:
            good_scaf.append(k)

    for t in records:
        if t[0] in good_scaf:
            out.write(" ".join(t) + "\n")

    out.close()


if __name__ == '__main__':
    main()
