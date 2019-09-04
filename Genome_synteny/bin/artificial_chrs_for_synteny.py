#!/usr/bin/env python3
import sys
import os
import re

if len(sys.argv) < 6:
    print("Usage: python3 {} <querry scaffold length> <ref chrs length>" +\
          " <synteny block> <min scaffold length> <min block length>\n".format(sys.argv[0]))
    exit()

def getLen(length_file, minL):
    lens = {}
    with open(length_file, 'r') as fh:
        for i in fh:
            #tmp = i.strip().split("\t")
            tmp = re.split('\t|\s',i.strip())
            length = int(tmp[1])
            if length >= minL:
                lens[tmp[0]] = int(length)
    return lens

def connect_scaf(lens):
    new_location = {}
    current = 1
    for q in sorted(lens.keys(), key=lambda k:lens[k], reverse=True):
        if current == 1:
            new_location[q] = (1, lens[q])
            current = lens[q]
        else:
            new_location[q] = (current, current + lens[q])
            current = current + lens[q]
    return (current, new_location)

def check_scaf(scaf, dict):
    if scaf not in dict.keys():
        #print("Error: can not find {} in your file".format(scaf))
        return False
    else:
        return True

def main():
    minL = int(sys.argv[4])
    minB = int(sys.argv[5])
    q_lens = getLen(sys.argv[1], minL)
    r_lens = getLen(sys.argv[2], minL)
    (total_q, q_new_location) = connect_scaf(q_lens)
    (total_r, r_new_location) = connect_scaf(r_lens)

    link = open("link.txt", 'w')
    with open(sys.argv[3], 'r') as fh:
        for i in fh:
            tmp = i.strip().split()
            block_q = int(tmp[2]) - int(tmp[1]) + 1
            block_r = int(tmp[5]) - int(tmp[4]) + 1
            if block_q < minB and block_r < minB:
                continue
            if check_scaf(tmp[0], q_lens) and check_scaf(tmp[3], r_lens):
                q_start_new = q_new_location[tmp[0]][0] + int(tmp[1])
                q_end_new = q_new_location[tmp[0]][1] + int(tmp[2])
                r_start_new = r_new_location[tmp[3]][0] + int(tmp[4])
                r_end_new = r_new_location[tmp[3]][1] + int(tmp[5])
                link.write("hs1 {} {} hs2 {} {}\n".format(q_start_new, q_end_new,
                                                   r_start_new, r_end_new))
    with open("karyotype.txt", 'w') as out:
        out.write("chr - hs1 querry 0 {} 133,92,117\n".format(total_q))
        out.write("chr - hs2 ref 0 {} 217,175,107".format(total_r))

if __name__ == "__main__":
    main()
