import sed3
import numpy as np
import matplotlib.pyplot as plt


img = (np.random.random([100,100,3]) * 100).astype(np.uint8)

img[20:60, 20:60, 0] +=60

plt.imshow(img)
plt.show()

ed = sed3.sed3(img)
ed.show()

seeds = ed.seeds

plt.imshow(seeds)
plt.show()

print("Left click intensities", img[seeds[:,:,0]==1] )
print("Right click intensities", img[seeds[:,:,0]==3] )
print(img[seeds==1])




