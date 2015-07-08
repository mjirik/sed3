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

class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.figure = plt.figure

class TemplateTest(unittest.TestCase):

    @attr('interactive')
    @attr('actual')

    def test_qt(self):
        from PyQt4 import QtGui

        pass

if __name__ == "__main__":
    unittest.main()
