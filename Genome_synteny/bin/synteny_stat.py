#!/usr/bin/env python3
import sys
import numpy as np

if len(sys.argv) < 3:
    print("python3 {} <querry scaf length> <ref length> " +\
          "<link>".format(sys.argv[0]))
    exit()

def getLen(length_file):
    lens = 0
    lensdict = {}
    with open(length_file, 'r') as fh:
        for i in fh:
            tmp = i.strip().split()
            lensdict[tmp[0]] = int(tmp[1])
            lens += int(tmp[1])
    return lens, lensdict



def add2dict(dict, k, v):
    if k in dict.keys():
        dict[k].append(v)
    else:
        dict[k] = [v,]


def main():
    querry_block = 0
    ref_block = 0
    querry_total, querry_lens = getLen(sys.argv[1])
    ref_total, ref_lens = getLen(sys.argv[2])
    records1 = {}
    records2 = {}

    with open(sys.argv[3], 'r') as fh:
        for b in fh:
            tmp = b.strip().split()
            add2dict(records1, tmp[0], (int(tmp[1]), int(tmp[2])))
            add2dict(records2, tmp[3], (int(tmp[4]), int(tmp[5])))
    unmapped1 = 0
    scaffold_len1 = 0
    for k in records1.keys():
        # make a list, length is scaffold length, value is 0
        tmp = np.zeros(querry_lens[k])
        for v in records1[k]:
            (s, e) = v
            for i in range(s-1, e):
                tmp[i] = 1
        gap1 = [ x for x in tmp if x==0 ]
        unmapped1 += len(gap1)
        scaffold_len1 += querry_lens[k]
    unmapped2 = 0
    scaffold_len2 = 0
    for k in records2.keys():
        # make a list, length is scaffold length, value is 0
        tmp = np.zeros(ref_lens[k])
        for v in records2[k]:
            (s, e) = v
            for i in range(s-1, e):
                tmp[i] = 1
        gap2 = [ x for x in tmp if x==0 ]
        unmapped2 += len(gap2)
        scaffold_len2 += ref_lens[k]


    print("target genome total scaffold length:\t{}".format(querry_total))
    print("target genome mapped scaffold length:\t{}".format(scaffold_len1))
    print("target genome unmapped length:\t{}".format(unmapped1))
    print("target genome syntenic block ratio:\t{:.3f}".format((scaffold_len1-unmapped1)/scaffold_len1))
    print("reference genome total length:\t{}".format(ref_total))
    print("reference genome total length:\t{}".format(scaffold_len2))
    print("reference genome syntenic block length:\t{}".format(unmapped2))
    print("reference genome syntenic block ratio:\t{:.3f}".format((scaffold_len2-unmapped2)/scaffold_len2))


if __name__ == '__main__':
    main()
