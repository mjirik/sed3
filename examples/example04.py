import sed3
import numpy as np

from PyQt5.QtWidgets import QApplication

img = np.random.random([10, 12, 15])
img[6:9, 2:7, 1:5] += 2
img[7:9, 3:9, 8:14] += 3


app = QApplication([])
ed = sed3.sed3qt(img)
ed.exec_()
print(ed.seeds)
