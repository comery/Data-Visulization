import seaborn as sns
import numpy as np
from numpy.random import randn
import matplotlib as mpl
import matplotlib.pyplot as plt

data = []
with open("test1.dep", 'r') as fh:
    for i in fh:
        data.append(int(i.strip()))
        #if len(data) > 200000:
        #    break

#data = randn(100)
sns.kdeplot(data, shade=True)
#plt.hist(data, 1000)
pal = sns.blend_palette([sns.desaturate("royalblue", 0), "royalblue"], 5)
#bws = [1, 5, 10, 15]

#for bw, c in zip(bws, pal):
    #sns.kdeplot(data, bw=bw, color=c, lw=1.8, label=bw)

#sns.kdeplot(dist1, shade=True, color=c2, ax=ax2)

plt.legend(title="varians depth value")
sns.rugplot(data, color="#CF3512")
plt.show()
