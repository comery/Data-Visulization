#!/usr/bin/env python3
import sys

if len(sys.argv) < 3:
    print("python3 {} <querry scaf length> <ref length> " +\
          "<link>".format(sys.argv[0]))
    exit()

def getLen(length_file):
    lens = 0
    with open(length_file, 'r') as fh:
        for i in fh:
            tmp = i.strip().split()
            lens += int(tmp[1])
    return lens


def main():
    querry_block = 0
    ref_block = 0
    querry_total = getLen(sys.argv[1])
    ref_total = getLen(sys.argv[2])

    with open(sys.argv[3], 'r') as fh:
        for b in fh:
            tmp = b.strip().split()
            qb = int(tmp[2]) - int(tmp[1]) + 1
            rb = int(tmp[5]) - int(tmp[4]) + 1
            querry_block += qb
            ref_block += rb
    print("target genome total length:\t{}".format(querry_total))
    print("target genome syntenic block length:\t{}".format(querry_block))
    print("target genome syntenic block ratio:\t{:.3f}".format(querry_block/querry_total))
    print("reference genome total length:\t{}".format(ref_total))
    print("reference genome syntenic block length:\t{}".format(ref_block))
    print("reference genome syntenic block ratio:\t{:.3f}".format(ref_block/ref_total))


if __name__ == '__main__':
    main()
