#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 mjirik <mjirik@mjirik-Latitude-E6520>
#
# Distributed under terms of the MIT license.

"""

"""
import unittest
import numpy as np
import pytest


class TemplateTest(unittest.TestCase):
    def testSed2(self):
        import sed3
        import numpy as np

        img = np.random.randint(0, 20, [10, 10, 15])
        img[6:9, 2:7, 1:5] += 40
        img[7:9, 3:9, 8:14] += 60

        seg = np.zeros([10, 10, 15])
        seg[6:9, 2:7, 1:5] = 1
        seg[7:9, 3:9, 8:14] = 2

        ed = sed3.sed3(img, contour=seg)
        # import matplotlib.pyplot as plt
        # plt.show()

    @pytest.mark.interactive
    def test_interactive_test(self):
        import sed3
        import numpy as np

        img = np.zeros([10, 10, 15])
        img[6:9, 2:7, 1:5] = 1
        img[7:9, 3:9, 8:14] = 2

        ed = sed3.sed3(img)
        ed.show()
        print(ed.seeds)

    def test_run_without_show(self):
        import sed3
        import numpy as np

        img = np.zeros([10, 10, 15])
        img[6:9, 2:7, 1:5] = 1
        img[7:9, 3:9, 8:14] = 2

        ed = sed3.sed3(img)
        # ed.show()
        print(ed.seeds)

    def create_data(self):
        shape = [20, 21, 15]
        data = (np.random.random(shape) * 5).astype(np.uint8)
        seeds = np.zeros(shape, dtype=np.uint8)
        seeds[6:9, 2:7, 1:5] = 1
        seeds[7:9, 3:9, 8:14] = 2
        segmentation = np.zeros(shape, dtype=np.uint8)
        segmentation[6:15, 2:17, 6:18] = 1
        segmentation[10:16, 10:18, 10:19] = 2
        data += segmentation * 5
        return data, seeds, segmentation

    def test_run_with_seeds_and_contour(self):
        import sed3

        img, seeds, segmentation = self.create_data()

        wc = 15
        ww = 30

        ed = sed3.sed3(img, seeds=seeds, contour=segmentation, windowC=None, windowW=ww)
        assert ed.windowC != wc, "Should be set automatically"
        assert ed.windowW != ww, "should be set automatically"
        ed.set_window(windowW=ww, windowC=wc)

        # ed = sed3.sed3(img, seeds=seeds, contour=segmentation, windowC=wc, windowW=ww)
        assert ed.windowC == wc
        assert ed.windowW == ww

        # ed = sed3.sed3(img, seeds=seeds, contour=segmentation)
        # ed.show()
        # print(ed.seeds)

    def test_ipy_run_with_seeds_and_contour(self):
        import sed3
        from ipywidgets.embed import embed_minimal_html
        import ipywidgets

        img, seeds, segmentation = self.create_data()

        wc = 15
        ww = 30

        ed = sed3.sed3(img, seeds=seeds, contour=segmentation, windowC=None, windowW=ww)
        assert ed.windowC != wc, "Should be set automatically"
        assert ed.windowW != ww, "should be set automatically"
        ed.set_window(windowW=ww, windowC=wc)

        # ed = sed3.sed3(img, seeds=seeds, contour=segmentation, windowC=wc, windowW=ww)
        assert ed.windowC == wc
        assert ed.windowW == ww

        wg = sed3.ipy_show_slices(img, seeds=seeds, contour=segmentation)
        # wg = ipywidgets.IntSlider(value=40)
        # embed_minimal_html('export.html', views=[wg], title='Widgets export')
        # ed.show()
        # print(ed.seeds)

    @pytest.mark.interactive
    def test_first_slice_offset_interactive(self):
        """
        set offset to see seed with defined label
        :return:
        """
        import sed3

        img, seeds, segmentation = self.create_data()
        seeds[6:9, 10, 1:5] = 3
        seeds[7:9, 11, 8:14] = 4

        ed = sed3.show_slices(
            img,
            seeds=seeds,
            contour=segmentation,
            slice_step=5,
            first_slice_offset_to_see_seed_with_label=1,
        )

    def test_first_slice_offset(self):
        import sed3

        img, seeds, segmentation = self.create_data()

        sed3.show_slices(
            img,
            seeds=seeds,
            contour=segmentation,
            slice_step=5,
            first_slice_offset_to_see_seed_with_label=1,
            show=False,
        )

    def test_show_slices(self):
        import sed3

        img, seeds, segmentation = self.create_data()

        sed3.show_slices(img, seeds=seeds, contour=segmentation, show=False)
        # sed3.close()
        # sed3.sho()

    def test_show_slices_slice_number(self):
        import sed3

        img, seeds, segmentation = self.create_data()

        sed3.show_slices(
            img, seeds=seeds, contour=segmentation, show=False, slice_number=6
        )


if __name__ == "__main__":
    unittest.main()
