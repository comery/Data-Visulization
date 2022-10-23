#!/usr/bin/env python3

import sys
import argparse
from typing import final

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


def getLen(length_file):
    lens = {}
    with open(length_file, 'r') as fh:
        for i in fh:
            tmp = i.strip().split()
            lens[tmp[0]] = int(tmp[1])
    return lens

def give_color():
    """ colors theme  """""
    colors = []
    #print(
    #        "colors theme is designed by palettable." +\
    #        " \nsee more:http://colorbrewer2.org\n"
    #)
    # total color number = 150
    colors = palettable.cartocolors.qualitative.Antique_10.colors
    colors += palettable.cartocolors.qualitative.Bold_10.colors
    colors += palettable.cartocolors.qualitative.Pastel_10.colors
    colors += palettable.cartocolors.qualitative.Prism_10.colors
    colors += palettable.cartocolors.qualitative.Safe_10.colors
    colors += palettable.cartocolors.qualitative.Vivid_10.colors
    colors += palettable.cartocolors.diverging.ArmyRose_7.colors
    colors += palettable.cartocolors.diverging.Earth_7.colors
    colors += palettable.cartocolors.diverging.Fall_7.colors
    colors += palettable.cartocolors.diverging.Geyser_7.colors
    colors += palettable.cartocolors.diverging.TealRose_7.colors
    colors += palettable.cartocolors.diverging.Temps_7.colors
    colors += palettable.cartocolors.diverging.Tropic_7.colors
    colors += palettable.cartocolors.diverging.Geyser_7.colors
    colors += palettable.tableau.BlueRed_12.colors
    colors += palettable.tableau.ColorBlind_10.colors
    colors += palettable.tableau.PurpleGray_12.colors
    return colors

def Add_records(dict, k, v):
    if k in dict.keys():
        dict[k].append(v)
    else:
        dict[k] = [v,]

def deal_coords(coords, block_length, identity_cutoff):
    records = {}
    scaflens = {}

    with open(coords, 'r') as fh:
        for b in fh:
            tmp = b.strip().split("\t")
            ref_start = int(tmp[0])
            ref_end   = int(tmp[1])
            ref_alen  = int(tmp[4])
            qry_aln   = int(tmp[5])
            identity  = float(tmp[6])
            ref_length = int(tmp[7])
            ref_id = tmp[-2]
            # filter low quality blocks by length and identity
            if args.filter:
                if ref_alen < block_length and qry_aln < block_length:
                    continue
                elif identity < identity_cutoff:
                    continue
            scaflens[ref_id] = ref_length
            if ref_id not in records:
                records[ref_id] = [(ref_start, ref_end),]
            else:
                records[ref_id].append((ref_start, ref_end))

    return scaflens, records

def main(args):
    colors = give_color() # a container of all avaliable colors
    scaflens, uniq_alignment = deal_coords(args.coords, args.uniq_minB, args.uniq_identity)
    null, multi_alignment = deal_coords(args.mcoords, args.multi_minB, args.uniq_identity)
    final_order = sorted(uniq_alignment.keys(), key=lambda k:scaflens[k], reverse=True)

    if len(final_order) > 150:
        print("you have {} scaffolds".format(len(final_order)))
        print(
                "Sorry, It just can handle less than 150 chrs because " +\
                "too many chrs will make a mass!, however, you can change" +\
                "this code for your need\n"
                )
        exit(0)
    with open("karyotype.txt", 'w') as ka:
        color_profile = {}
        for i in range(len(final_order)):
            id = i + 1
            color = ",".join(str(v) for v in colors[i])
            color_profile["hs"+str(id)] = color
            ka.write("chr - hs{} {} 0 {} {}\n".format(id, final_order[i], scaflens[final_order[i]], color))

    with open("uniq.highlight.txt", 'w') as uh:
        for i,scaf in enumerate(final_order):
            chr_order = i + 1
            for block in uniq_alignment[scaf]:
                uh.write("hs{} {} {}\n".format(chr_order, block[0], block[1]))

    with open("multi.highlight.txt", 'w') as mh:
        for i,scaf in enumerate(final_order):
            chr_order = i + 1
            for block in multi_alignment[scaf]:
                mh.write("hs{} {} {}\n".format(chr_order, block[0], block[1]))

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
    parser.add_argument("-1c", "--coords", type=str, required=True, metavar='<File>',
                        help="uniq coords generated by nucmer and dnadiff, named by xx.1coords")
    parser.add_argument("-mc", "--mcoords", type=str, required=True, metavar='<File>',
                        help="multi coords generated by nucmer and dnadiff, named by xx.mcoords")
    parser.add_argument("-filter", action="store_true", help="filter records or not?")
    parser.add_argument("-uB", type=int, required=False, metavar='<INT>', dest='uniq_minB',
                        help="min length of synteny block in 1coords, default=1000",
                        default=500)
    parser.add_argument("-mB", type=int, required=False, metavar='<INT>', dest='multi_minB',
                        help="min length of synteny block in mcoords, default=500", default=500)
    parser.add_argument("-uid", type=float, required=False, metavar='<FLOAT>', dest='uniq_identity',
                        help="remove these scafoold which identity of synteny block is less than [float] in 1coords",
                       default=0.95)
    parser.add_argument("-mid", type=float, required=False, metavar='<FLOAT>', dest='multi_identity',
                        help="remove these scafoold which identity of synteny block is less than [float] in mcoords",
                       default=0.90)
    args =  parser.parse_args()
    main(args)
