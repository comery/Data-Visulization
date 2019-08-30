import numpy as np
id = 1
grid = np.arange(1, 97).reshape((8, 12))
grid = numpy.zeros((2,3))
while id < 97:
    ori = int((id-1) / 8)
    vel = (id-1) % 8 ;
    grid[vel][ori] = id
    id += 1

for a in grid:
    b = list(a)
    print(b)
    print(",".join(b))
