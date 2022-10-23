#!/usr/bin/env python3

import sys
import argparse
from icecream import ic

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

def get_coveraged_length(bed_list):
    # merge bed to generate non-overlap blocks
    mapped_length = 0
    sort_bed_list = sorted(bed_list)

    low_est = sort_bed_list[0][0]
    high_est = sort_bed_list[0][1]

    for index, block in enumerate(sort_bed_list):
        low, high = block
        if high_est >= low:
            if high_est < high:
                high_est = high
        else:
            mapped_length += (high_est - low_est + 1)
            low_est, high_est = sort_bed_list[index]
    mapped_length += (high_est - low_est + 1)
    return mapped_length


def Add_records(dict, k, v):
    if k in dict.keys():
        dict[k].append(v)
    else:
        dict[k] = [v,]

def main(args):
    colors = give_color() # a container of all avaliable colors
    synteny = {}
    query_coverage = {}
    scaf_length = {}

    with open(args.paf, 'r') as fh:
        # input file is in paf format
        for b in fh:
            tmp = b.strip().split()
            ref_start = int(tmp[7])
            ref_end = int(tmp[8])
            qry_start = int(tmp[2])
            qry_end = int(tmp[3])
            ref_alen  = abs(ref_end - ref_start)
            qry_aln   = abs(qry_end - qry_start)
            identity  = int(tmp[9]) / int(tmp[10])
            ref_length = int(tmp[6])
            qry_length = int(tmp[1])
            ref_id = tmp[5]
            qry_id = tmp[0]
            scaf_length[ref_id] = ref_length
            scaf_length[qry_id] = qry_length
            # make all positive strand
            if qry_start > qry_end:
                qry_end, qry_start = qry_start, qry_end
            # calculate query's coverage before filtering
            if qry_id not in query_coverage:
                query_coverage[qry_id] = [[qry_start, qry_end],]
            else:
                query_coverage[qry_id].append([qry_start, qry_end])

            if args.filter:
                # round 1, filtering by scaffold length and identity, and work out query coverage
                if ref_length < args.minL or qry_length < args.minL:
                    continue
                elif ref_alen < args.minB or qry_aln < args.minB:
                    continue
                elif identity < args.identity:
                    continue
            record = [ref_id, ref_start, ref_end, qry_id, qry_start, qry_end]
            Add_records(synteny, ref_id, record)

    if args.filter:
        query_remove = []
        # round 2, filtering by query coverage
        for q in query_coverage:
            coveraged_length = get_coveraged_length(query_coverage[q])
            if coveraged_length / scaf_length[q] < args.rate:
                query_remove.append(q)
        # then remove coords of removed querys
        for r in synteny.keys():
            fixed_records = synteny[r]
            new_records = []
            for coord in fixed_records:
                if coord[3] not in query_remove:
                    new_records.append(coord)
            synteny[r] = new_records

    # default order is sorted by scaffold length;
    # if you specify a certain list, it will draw as you wish
    if args.order:
        unknow_order = []
        order_you_wish = []
        with open(args.order, 'r') as fh:
            for i in fh:
                order_you_wish.append(i.strip())
        for s in synteny.keys():
            if s not in order_you_wish:
                unknow_order.append(s)
        final_order = order_you_wish + unknow_order
    else:
        final_order = sorted(synteny.keys(), key=lambda k:scaf_length[k], reverse=True)

    kary_que = []
    kary_ref = final_order
    for x in kary_ref:
        for i in synteny[x]:
            if i[3] not in kary_que:
                kary_que.append(i[3])
    # keep all scaffolds in list all_kary
    #ic(kary_que)
    new_que = kary_que[::-1]
    #if len(new_que) > 1:
     #   first_one_que = new_que.pop(0)
      #  new_que.append(first_one_que)
    all_kary = kary_ref + new_que
    if len(all_kary) > 150:
        print(f"you have {len(all_kary)} scaffolds")
        print("Given you have more 150 scaffolds, which is over the color limitation, " +\
              "so some scaffolds don't have unique color in circos plot!")
    elif len(all_kary) > 250:
        print(f"Sorry, You have asked to draw {len(all_kary)} ideograms, but the maximum is currently set at [250]")
        exit()

    karyotype_id = {}
    with open("karyotype.txt", 'w') as ka:
        color_profile = {}
        for i in range(len(all_kary)):
            id = i + 1
            color_index =  id % 150
            karyotype_id[all_kary[i]] = id
            color = ",".join(str(v) for v in colors[color_index])
            color_profile["hs"+str(id)] = color
            ka.write("chr - hs{} {} 0 {} {}\n".format(id, all_kary[i], scaf_length[all_kary[i]], color))

    with open("link.txt", 'w') as lk:
        for i in kary_ref:
            for link in synteny[i]:
                lk.write("hs{} {} {} hs{} {} {} color={}\n".format(karyotype_id[link[0]],
                                                                   link[1], link[2],
                                                                   karyotype_id[link[3]],
                                                                   link[4], link[5],
                                                                   color_profile["hs"+str(karyotype_id[link[3]])])) # link color is defined by que

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
    parser.add_argument("-paf", type=str, required=True, metavar='<File>',
                        help="alignment result (paf format) generated by unimap")
    parser.add_argument("-order", type=str, required=False, metavar='<File>',
                       help="guide order of karyotype to show in circos")
    parser.add_argument("-filter", action="store_true",
                       help="filter records or not?")
    parser.add_argument("-minL", type=int, required=False, metavar='<INT>',
                        help="min scaffold length in link record, default=1000",
                        default=1000)
    parser.add_argument("-minB", type=int, required=False, metavar='<INT>',
                        help="min length of synteny block, default=500",
                       default=500)
    parser.add_argument("-id", type=float, required=False, metavar='<FLOAT>', dest="identity",
                       help="min identiy of synteny block, default=95", default=0.90)
    parser.add_argument("-rate", type=float, required=False, metavar='<FLOAT>',
                        help="remove these query which coverage is shorter than scaf_len * rate, default=0.1",
                       default=0.1)
    args =  parser.parse_args()
    main(args)
