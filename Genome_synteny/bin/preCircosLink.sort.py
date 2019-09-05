#!/usr/bin/env python3

import sys
import argparse

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
    print(
            "colors theme is designed by palettable." +\
            " \nsee more:http://colorbrewer2.org\n"
    )

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

def main(args):
    records = []
    lens = getLen(args.scaf_len)
    colors = give_color()

    with open(args.link, 'r') as fh:
        for b in fh:
            tmp = b.strip().split()
            records.append(tmp)

    # filter link record with short length
    scaf_block = {}

    good_rate_scaf = []
    filtered_records = []
    # filter by scaffold and block length
    for r in records:
        (querry_scaf, q_start, q_end, ref_scaf, r_start, r_end) = r
        block_len = int(q_end) - int(q_start) + 1
        if querry_scaf in scaf_block.keys():
            scaf_block[querry_scaf] += block_len
        else:
            scaf_block[querry_scaf] = block_len
    # filter scaffold by block ratio
    for k in scaf_block.keys():
        if scaf_block[k] >= lens[k] * args.rate:
            good_rate_scaf.append(k)
    # filter records by block length

    synteny = {}
    for item in records:
        block_len = int(item[2]) - int(item[1]) + 1
        if item[0] not in good_rate_scaf:
            continue
        if lens[item[0]] < args.minL or lens[item[3]] < args.minL:
            continue
        if block_len < args.minB:
            continue
        Add_records(synteny, item[3], item)

    kary_ref = []
    kary_que = []

    for x in sorted(synteny.keys(), key=lambda k:lens[k], reverse=True):
        kary_ref.append(x)
        for i in synteny[x]:
            (querry_scaf, q_start, q_end, ref_scaf, r_start, r_end) = i
            if querry_scaf not in kary_que:
                kary_que.insert(0, querry_scaf)
    all_kary = kary_ref + kary_que
    if len(all_kary) > 150:
        print(
                "Sorry, It just can handle less than 150 chrs because " +\
                "too many chrs will make a mass!, however, you can change" +\
                "this code for suit\n"
                )
        exit(0)
    order_kary = {}
    with open("karyotype.txt", 'w') as ka:
        for i in range(len(all_kary)):
            id = i + 1
            order_kary[all_kary[i]] = id
            color = ",".join(str(v) for v in colors[i])
            ka.write("chr - hs{} {} 0 {} {}\n".format(id, all_kary[i], lens[all_kary[i]], color))

    with open("link.txt", 'w') as lk:
        for i in kary_ref:
            for link in synteny[i]:
                lk.write("hs{} {} {} hs{} {} {}\n".format(order_kary[link[0]], link[1], link[2], order_kary[i], link[4], link[5]))

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
    parser.add_argument("--minL", type=int, required=False, metavar='<INT>',
                        help="min scaffold lenth in link record, default=1000000",
                        default=1000000)
    parser.add_argument("--minB", type=int, required=False, metavar='<iNT>',
                        help="min block length of synteny, default=100000",
                       default=10000)
    parser.add_argument("--rate", type=float, required=False,
                        metavar='<FLOAT>',
                        help="remove these scafoold which synteny block is shorter than scaf_len * rate",
                       default=0.5)
    args =  parser.parse_args()
    main(args)
