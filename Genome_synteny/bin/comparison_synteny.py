#!/usr/bin/env python3

import sys
import argparse

def getLen(length_file):
    lens = {}
    with open(length_file, 'r') as fh:
        for i in fh:
            tmp = i.strip().split()
            lens[tmp[0]] = int(tmp[1])
    return lens

def Add_records(dict, k, v):
    if k in dict.keys():
        dict[k].append(v)
    else:
        dict[k] = [v,]

def main(args):
    lens = getLen(args.scaf_len)

    with open(args.link, 'r') as fh:
        scaf_block = {}
        recordsByquerry = {}
        recordsByref = {}
        for b in fh:
            tmp = b.strip().split()

            [querry_scaf, q_start, q_end, ref_scaf, r_start, r_end] = tmp
            len_q = int(q_end) - int(q_start) + 1
            len_r = int(r_end) - int(r_start) + 1
            if querry_scaf in scaf_block.keys():
                scaf_block[querry_scaf] += len_q
            else:
                scaf_block[querry_scaf] = len_q
            if ref_scaf in scaf_block.keys():
                scaf_block[ref_scaf] += len_r
            else:
                scaf_block[ref_scaf] = len_r

            Add_records(recordsByquerry, querry_scaf, ref_scaf)
            Add_records(recordsByref, ref_scaf, querry_scaf)

    with open("synteny.stat", 'w') as fh:
        fh.write("scaffold\tmapped_scaffold_number\tmapped_ratio\tscaffold_length\tspecies\n")
        for k in recordsByquerry.keys():
            num_map = len(list(set(recordsByquerry[k])))
            fh.write("{}\t{}\t{:.3f}\t{}\tspotted_hyena\n".format(k, num_map,
                                                                  scaf_block[k]/lens[k],
                                                                 lens[k]))
        for k in recordsByref.keys():
            num_map = len(list(set(recordsByref[k])))
            fh.write("{}\t{}\t{:.3f}\t{}\tstriped_hyena\n".format(k, num_map,
                                                                  scaf_block[k]/lens[k],
                                                                 lens[k]))

if __name__ == '__main__':
    des = """

    deal synteny block file and generate color profile for circos,
    imput file should be six-column table, querry_scaf, q_start,
    q_end, ref_scaf, r_start, r_end, also you need give a table 
    containing scaffold's length.

    yangchentao at genomics.cn, BGI.
    """
    parser = argparse.ArgumentParser(description=des,
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--link", type=str, required=True, metavar='<STR>',
                        help="BASTA annotation file(s) separated by comma")
    parser.add_argument("--scaf_len", type=str, required=True, metavar='<STR>',
                        help="all scaffold length, including querry and ref")
    args =  parser.parse_args()
    main(args)
