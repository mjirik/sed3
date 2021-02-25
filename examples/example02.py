import sed3
import numpy as np

img = np.random.random([10, 12, 15])
img[6:9, 2:7, 1:5] += 2
img[7:9, 3:9, 8:14] += 3

sed3.show_slices(img)