import numpy as np
import matplotlib.pyplot as plt

forward = []
reverse = []
sams = []
maxval = 0
sum = []
with open("samples.assignment.sorted.log",'r') as fh:
    all = fh.readlines()
    for a in all:
        a = a.strip()
        b = a.split()
        c = np.log10(int(b[1]))
        d = np.log10(int(b[3]))
        forward.append(c)
        reverse.append(d)
        sum.append(c+d)
        sam = b[0][-3:]
        print(sam)
        sams.append(sam)
        if c +d  > maxval:
            maxval = c + d

step = int(maxval/1)
print(maxval,step)


N = len(forward)
ind = np.arange(N)    # the x locations for the groups
width = 0.15       # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, forward, width )
p2 = plt.bar(ind, reverse, width,
             bottom=forward)

plt.ylabel('Scores')
plt.title('Scores by group and gender')
plt.xticks(ind, sams)
plt.yticks(np.arange(0, maxval, step))
plt.legend((p1[0], p2[0]), ('forward', 'reverse'))

plt.show()
