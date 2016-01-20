[![Build Status](https://travis-ci.org/mjirik/sed3.svg?branch=master)](https://travis-ci.org/mjirik/sed3)
[![Coverage Status](https://coveralls.io/repos/mjirik/sed3/badge.svg)](https://coveralls.io/r/mjirik/sed3)
[![PyPI version](https://badge.fury.io/py/sed3.svg)](http://badge.fury.io/py/sed3)

sed3
====

3D viewer and seed editor

Example 1 - get seeds
=======

    import sed3
    import numpy as np

    img = np.random.random([10, 12, 15])
    img[6:9, 2:7, 1:5] += 2
    img[7:9, 3:9, 8:14] += 3

    ed = sed3.sed3(img)
    ed.show()
    print ed.seeds

![sed_screenshot](http://147.228.240.61/queetech/www/sed3_screenshot.png)


Example 2 - static figure
=======

    import sed3
    import numpy as np

    img = np.random.random([10, 12, 15])
    img[6:9, 2:7, 1:5] += 2
    img[7:9, 3:9, 8:14] += 3

    sed3.show_slices(img)

![sed_screenshot](http://147.228.240.61/queetech/www/sed3_screenshot3.png)

Example 3 - more options
=======

    import sed3
    import numpy as np

    img = np.random.random([10, 12, 15])
    img[6:9, 2:7, 1:5] += 2
    img[7:9, 3:9, 8:14] += 3


    seeds = np.zeros(img.shape)
    seeds[6:8, 4, 3:10] = 1
    seeds[6:8, 6:11, 9:11] = 2
    ed = sed3.sed3(img, seeds=seeds)

    contour = np.zeros(img.shape)
    contour[6:8, 3:10, 2:10] = 1
    contour[6:8, 5:8, 4:7] = 2
    ed = sed3.sed3(img, seeds=seeds, contour=contour, windowW=3.5, windowC=1.5)

    seeds = ed.show()

![sed_screenshot](http://147.228.240.61/queetech/www/sed3_screenshot2.png)

Example 4 - PyQt version
=======

    import sed3qt
    import numpy as np

    from PyQt4.QtGui import QApplication

    img = np.random.random([10, 12, 15])
    img[6:9, 2:7, 1:5] += 2
    img[7:9, 3:9, 8:14] += 3


    app = QApplication([])
    ed = sed3.sed3qt(img)
    ed.exec_()
    print ed.seeds

Install notes 
=============

    sudo apt-get install python-matplotlib
    
    pip install sed3
