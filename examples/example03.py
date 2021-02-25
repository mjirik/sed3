import sed3
import numpy as np

img = np.random.random([10, 12, 15])
img[6:9, 2:7, 1:5] += 2
img[7:9, 3:9, 8:14] += 3


seeds = np.zeros(img.shape)
seeds[6:8, 4, 3:10] = 1
seeds[6:8, 6:11, 9:11] = 2

contour = np.zeros(img.shape)
contour[6:8, 3:10, 2:10] = 1
contour[6:8, 5:8, 4:7] = 2
ed = sed3.sed3(img, seeds=seeds, contour=contour, windowW=3.5, windowC=1.5)

seeds = ed.show()
