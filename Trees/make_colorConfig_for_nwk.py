import sys
from Bio import Phylo
import palettable.cartocolors.qualitative
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


if len(sys.argv) < 3:
    print("Usage: python3 {} tree.nwk tag(label|range|...)".format(sys.argv[0]))
    exit()


""" colors theme """
colors = []
colors = palettable.cartocolors.qualitative.Antique_10.colors
colors += palettable.cartocolors.qualitative.Bold_10.colors
colors += palettable.cartocolors.qualitative.Pastel_10.colors
colors += palettable.cartocolors.qualitative.Prism_10.colors
colors += palettable.cartocolors.qualitative.Safe_10.colors
colors += palettable.cartocolors.qualitative.Vivid_10.colors

def rgb2hex(a):
    r, g , b = a
    if type(r) == int and type(g) == int and type(b) == int:
        hex_c = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        return hex_c
    else:
        print("type error, must be int")
        exit()


colored = {}
x = 0
tag = sys.argv[2]
with open(tag + ".color.config.txt", 'w') as out:
    #with open("dataset_styles_template.txt" ,'r') as fh:
    #    for i in fh:
    #        out.write(i)
    tree = Phylo.read(sys.argv[1], 'newick')
    for leaf in tree.get_terminals():
        leaf = str(leaf)
        tmp = leaf.split("_")
        if len(tmp) == 3:
            family = tmp[2]
        else:
            print("{} is ignored".format(leaf))
            continue
        if family in colored.keys():
            out.write("{},{},clade,{},1,normal\n".format(leaf, tag, colored[family]))
        else:
            colored[family] = rgb2hex(colors[x])
            x += 1
            if x > 49:
                print("too many families in this tree")
                exit()
            out.write("{},{},clade,{},1,normal\n".format(leaf, tag, colored[family]))

families = []
lenged_colors = []
for f in colored.keys():
    families.append(f)
    lenged_colors.append(colored[f])

print("LEGEND_COLORS,", ",".join(lenged_colors))
print("LEGEND_LABELS,", ",".join(families))


