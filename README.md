[![Build Status](https://travis-ci.org/mjirik/sed3.svg?branch=master)](https://travis-ci.org/mjirik/sed3)
[![Coverage Status](https://coveralls.io/repos/mjirik/sed3/badge.svg)](https://coveralls.io/r/mjirik/sed3)
[![PyPI version](https://badge.fury.io/py/sed3.svg)](http://badge.fury.io/py/sed3)

sed3
====

3D viewer and seed editor

Example 1
=======

    import sed3
    import numpy as np

    img = np.zeros([10, 10, 15])
    img[6:9, 2:7, 1:5] = 1
    img[7:9, 3:9, 8:14] = 2

    ed = sed3.sed3(img)
    ed.show()
    print ed.seeds


Example 2
=======

    import sed3
    import numpy as np

    img = np.zeros([10, 10, 15])
    img[6:9, 2:7, 1:5] = 1
    img[7:9, 3:9, 8:14] = 2

    sed3.show_slices(img)

Install notes 
=============

    sudo apt-get install python-matplotlib
    
    pip install sed3
