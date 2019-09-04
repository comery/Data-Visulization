#!/usr/bin/env python3
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python3 {} <synteny.cook.1k.sort.txt>\n".format(sys.argv[0]))
    exit()

records = {}

with open(sys.argv[1], 'r') as fh:
    for i in fh:
        tmp = i.strip().split()
        ref = tmp[3]
        if ref not in records.keys():
            records[ref] = [tmp,]
        else:
            records[ref].append(tmp)
if not os.path.exists("linkbyChrs"):
    os.mkdir("linkbyChrs")


for k in sorted(records.keys()):
    outdir = "linkbyChrs/" + k
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    with open(outdir + "/" + k + ".txt", 'w') as out:
        for i in records[k]:
            out.write(" ".join(i))
            out.write("\n")
