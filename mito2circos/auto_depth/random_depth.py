import random
import sys
with open(sys.argv[1], 'r') as fh:
    for i in fh:
        tmp = i.strip().split()
        dep = random.randint(10, 200)
        print("{0}\t{1}\t{2}\t{3}".format(tmp[0], tmp[1], tmp[2], dep))
