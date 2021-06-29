#!/usr/bin/env python3

import sys

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

usage = "Usage: python3 {} <number> <l|m>".format(sys.argv[0])
note = """
l means all colors in one line with , separated, whereas m means in multi-line
"""
if len(sys.argv) < 3:
    print(usage)
    print(note)
    exit()
elif sys.argv[2] != 'l' or sys.argv[2] != 'm':
    print(usage)
    print(note)

def give_color(n):
    """ colors theme
    "colors theme is designed by palettable. see more:http://colorbrewer2.org"
    """
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
    return colors[:n]

def rgb2hex(tuble):
    r, g, b = int(tuble[0]), int(tuble[1]), int(tuble[2])
    print("{},{},{}".format(r,g,b))
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

if __name__ == '__main__':
    if int(sys.argv[1]) > 150:
        print("too many colors")
        exit()
    else:
        colors = give_color(int(sys.argv[1]))
        out = []
        for i in colors:
            out.append(rgb2hex(i))
        if sys.argv[2] == 'l':
            print(",".join(out))
        else:
            print("\n".join(out))
