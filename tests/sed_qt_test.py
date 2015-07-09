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
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import sys

# class Window(QtGui.QDialog):
#     def __init__(self, parent=None):
#         super(Window, self).__init__(parent)
#         self.figure = plt.figure
class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        # self.setWindowIcon(QtGui.QIcon('web.png'))
        btn1 = QtGui.QPushButton("Button 1", self)
        btn1.clicked.connect(self.buttonClicked) 
        self.show()

    def buttonClicked(self):
        print "button"
        import sed3
        import numpy as np

        img = np.zeros([10, 10, 15])
        img[6:9, 2:7, 1:5] = 1
        img[7:9, 3:9, 8:14] = 2

        ed = sed3.sed3(img)
        ed.show()
        print "konec sed3"
        pass

class TemplateTest(unittest.TestCase):

    @attr('interactive')
    @attr('actual')

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
        # print ed.seeds
        app = QtGui.QApplication(sys.argv)

        main = Example()
        sys.exit(app.exec_())


        pass

if __name__ == "__main__":
    unittest.main()
