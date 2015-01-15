sed3
====

3D viewer and seed editor

[![PyPI version](https://badge.fury.io/py/sed3.svg)](http://badge.fury.io/py/sed3)

Example
=======

    import sed3
    import numpy as np

    img = np.zeros([10, 10, 15])
    img[6:9, 2:7, 1:5] = 1
    img[7:9, 3:9, 8:14] = 2

    ed = sed3.sed3(img)
    ed.show()
    print ed.seeds



Install notes 
=============

    sudo apt-get install python-matplotlib
    
    pip install sed3
