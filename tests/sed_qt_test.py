#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 mjirik <mjirik@hp-mjirik>
#
# Distributed under terms of the MIT license.

"""

"""
import unittest
from nose.plugins.attrib import attr
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import sys
import random

import os
import numpy as np
# plt.ion()
# my_site = os.path.join(os.environ['HOME'] , "projects/sed3/")
# sys.path.insert(0, my_site)
# class Window(QtGui.QDialog):
#     def __init__(self, parent=None):
#         super(Window, self).__init__(parent)
#         self.figure = plt.figure





class FailingExample(QtGui.QWidget):
    """
    sed3 by měl zastavit po řádku ed.show()
    bohužel však nezastaví. Tento kód replikuje tuto chybu
    """

    def __init__(self):
        super(FailingExample, self).__init__()
        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        # self.setWindowIcon(QtGui.QIcon('web.png'))
        btn1 = QtGui.QPushButton("Button 1", self)
        btn1.clicked.connect(self.buttonClicked)
        self.show()

    def buttonClicked(self):
        print("button")
        import sed3
        import sed3.sed3
        import numpy as np

        img = np.zeros([10, 10, 15])
        img[6:9, 2:7, 1:5] = 1
        img[7:9, 3:9, 8:14] = 2

        ed = sed3.sed3qt(img)
        # ed.set_params(img)

        if ed.exec_():
            print("konec edu")
            vals = ed.o
            print(vals.seeds)


        print(np.nonzero(ed.seeds))
        # ed = sed3.sed3(img)
        # ed.sed3_on_close = self.callback_close
        # ed.show()

        print("konec sed3")
        # QtCore.pyqtRemoveInputHook()
        # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT

    def callback_close(self, sss):
        print("callback222")
        print(np.nonzero(sss.seeds))

# def callback_close(sss):
#     print("callback")
#     print(sss.seeds)

class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.initUI2()

    def initUI2(self, parent=None):
        super(Example, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        # self.btn1 = QtGui.QPushButton("Button 1", self)
        # self.btn1.clicked.connect(self.buttonClicked)
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)
 # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def initUI(self):

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        # self.setWindowIcon(QtGui.QIcon('web.png'))
        self.show()

    def buttonClicked(self):
        print("button")
        import sed3
        import numpy as np

        img = np.zeros([10, 10, 15])
        img[6:9, 2:7, 1:5] = 1
        img[7:9, 3:9, 8:14] = 2

        ed = sed3.sed3(img)
        ed.show()
        print("konec sed3")

    def plot(self):
        ''' plot some random stuff '''
        # random data
        data = [random.random() for i in range(10)]

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()

class TemplateTest(unittest.TestCase):

    @attr('interactive')
    def test_qt(self):
        # import sed3
        # import numpy as np
        #
        # img = np.zeros([10, 10, 15])
        # img[6:9, 2:7, 1:5] = 1
        # img[7:9, 3:9, 8:14] = 2
        #
        # ed = sed3.sed3(img)
        # ed.show()
        # print(ed.seeds)
        app = QtGui.QApplication(sys.argv)

        main = Example()
        main.show()
        sys.exit(app.exec_())

    @attr('interactive')
    @attr('actual')
    def test_sed3_qt(self):
        # import sed3
        # import numpy as np
        #
        # img = np.zeros([10, 10, 15])
        # img[6:9, 2:7, 1:5] = 1
        # img[7:9, 3:9, 8:14] = 2
        #
        # ed = sed3.sed3(img)
        # ed.show()
        # print(ed.seeds)
        app = QtGui.QApplication(sys.argv)

        main = FailingExample()
        sys.exit(app.exec_())


        pass

    def test_sed3qtWidget(self):
        app = QtGui.QApplication(sys.argv)
        print("button")
        import sed3
        import sed3.sed3qt
        import numpy as np

        sz = [10, 20, 15]
        img = np.zeros(sz)
        img[6:9, 2:7, 1:5] = 1
        img[7:9, 3:9, 8:14] = 2

        ed = sed3.sed3qtWidget(img)
        # ed.show()
        ed.close()
        # app.exec_()
        # self.assertEquals(ed.seeds, sz)
        # self.assertEqual(np.sum(ed.seeds), 0)


if __name__ == "__main__":
    unittest.main()
