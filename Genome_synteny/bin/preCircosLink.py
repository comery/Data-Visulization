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


def Fileter_records(records, lens, args):
    synteny = {}
    good_scaf = []
    filtered_records = []

    for r in records:
        (querry_scaf, q_start, q_end, ref_scaf, r_start, r_end) = r
        if lens[querry_scaf] >= args.minL and lens[ref_scaf] >= args.minL:
            block_len = int(q_end) - int(q_start) + 1
            #if block_len < args.minB:
            #    continue
            if querry_scaf in synteny.keys():
                synteny[querry_scaf] += block_len
            else:
                synteny[querry_scaf] = block_len

    for k in synteny.keys():
        if synteny[k] >= lens[k] * args.rate:
            good_scaf.append(k)

    for t in records:
        block_len = int(t[2]) - int(t[1]) + 1
        if t[0] in good_scaf:
            filtered_records.append(t)

    return filtered_records


def main(args):
    records = []
    marker = 0
    marked = {}
    lens = getLen(args.scaf_len)
    colors = give_color()
    kary = open("karyotype.txt", 'w')
    link = open("link.txt", 'w')
    with open(args.link, 'r') as fh:
        for b in fh:
            tmp = b.strip().split()
            records.append(tmp)

    # filter link record with short length
    filtered_records = Fileter_records(records, lens, args)

    for tmp in filtered_records:

        if marker > 150:

            print(
                "Sorry, It just can handle more than 150 chrs because " +\
                "too many chrs will make a mass!, however, you can change" +\
                "this code for suit\n"
                )
            exit(0)
        # init
        if len(marked) == 0:
            marker = 1
            color1 = ",".join(str(v) for v in colors[marker - 1])
            kary.write("chr - hs{} {} 0 {} {}\n".format(marker,
                                                      tmp[0],
                                                      lens[tmp[0]],
                                                      color1))
            marked[tmp[0]] = marker
            marker += 1
            color2 = ",".join(str(v) for v in colors[marker - 1])
            kary.write("chr - hs{} {} 0 {} {}\n".format(marker,
                                                      tmp[3],
                                                      lens[tmp[3]],
                                                      color2))
            marked[tmp[3]] = marker
            id1 = "hs" + str(marked[tmp[0]])
            id2 = "hs" + str(marked[tmp[3]])
            link.write("{} {} {} {} {} {}\n".format(id1,
                                                       tmp[1],
                                                       tmp[2],
                                                       id2,
                                                       tmp[4],
                                                       tmp[5]))
        else:
            for i in [tmp[0], tmp[3]]:
                if i not in marked.keys():
                    marker += 1
                    marked[i] = marker
                    color = ",".join(str(v) for v in colors[marker - 1])
                    kary.write("chr - hs{} {} 0 {} {}\n".format(marker,
                                                               i,
                                                               lens[i],
                                                               color))

            id1 = "hs" + str(marked[tmp[0]])
            id2 = "hs" + str(marked[tmp[3]])
            link.write("{} {} {} {} {} {}\n".format(id1,
                                                       tmp[1],
                                                       tmp[2],
                                                       id2,
                                                       tmp[4],
                                                       tmp[5]))
    kary.close()
    link.close()


if __name__ == '__main__':
    description = """

    deal synteny block file and generate color profile for circos,
    imput file should be six-column table, querry_scaf, q_start,
    q_end, ref_scaf, r_start, r_end, also you need give a table 
    containing scaffold's length.

    yangchentao at genomics.cn, BGI.
    """
    parser = argparse.ArgumentParser(description="Create Krona plots from basta output files",
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--link", type=str, required=True,
                        help="BASTA annotation file(s) separated by comma")
    parser.add_argument("--scaf_len", type=str, required=True,
                        help="all scaffold length, including querry and ref")
    parser.add_argument("--minL", type=int, required=False,
                        help="min scaffold lenth in link record, default=1000000",
                        default=1000000)
    parser.add_argument("--minB", type=int, required=False,
                        help="min block length of synteny, default=100000",
                       default=100000)
    parser.add_argument("--rate", type=float, required=False,
                        help="remove these scafoold which synteny block is shorter than scaf_len * rate",
                       default=0.5)
    args =  parser.parse_args()
    main(args)
