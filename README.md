py3DSeedEditor
==============

3D viewer and seed editor



Example
=======

    import sed3
    import numpy as np

    img = np.zeros([20,20,30])
    img[3:6, 2:7, :11:25] = 1
    img[9:16, 3:8, :8:14] = 2

    ed = sed3.sed3(img)
    ed.show()
    selected_seeds = ed.seeds



Install notes 
=============

    sudo apt-get install python-matplotlib
    
    pip install sed3
