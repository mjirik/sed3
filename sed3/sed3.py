#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys


import scipy.io
import math
import copy
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.widgets import Slider, Button
import traceback

import logging
logger = logging.getLogger(__name__)

# import pdb
# pdb.set_trace();

try:
    from PyQt4 import QtGui, QtCore
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    try:
        from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    except:
        from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
except:
    logger.exception('PyQt4 not detected')
    print('PyQt4 not detected')

# compatibility between python 2 and 3
if sys.version_info[0] >= 3:
    xrange = range


class sed3:
    """ Viewer and seed editor for 2D and 3D data.

    sed3(img, ...)

    img: 2D or 3D grayscale data
    voxelsizemm: size of voxel, default is [1, 1, 1]
    initslice: 0
    colorbar: True/False, default is True
    cmap: colormap
    zaxis: axis with slice numbers
    show: (True/False) automatic call show() function
    sed3_on_close: callback function on close



    ed = sed3(img)
    ed.show()
    selected_seeds = ed.seeds

    """
    # if data.shape != segmentation.shape:
    # raise Exception('Input size error','Shape if input data and segmentation
    # must be same')

    def __init__(
            self, img, voxelsize=[1, 1, 1], initslice=0, colorbar=True,
            cmap=matplotlib.cm.Greys_r, seeds=None, contour=None, zaxis=0,
            mouse_button_map={1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8},
            windowW=None, windowC=None, show=False, sed3_on_close=None, figure=None,
            show_axis=False, flipV=False, flipH=False
    ):
        """

        :param img:
        :param voxelsize: size of voxel
        :param initslice:
        :param colorbar:
        :param cmap:
        :param seeds: define seeds
        :param contour: contour
        :param zaxis:
        :param mouse_button_map:
        :param windowW: window width
        :param windowC: window center
        :param show:
        :param sed3_on_close:
        :param figure:
        :param show_axis:
        :param flipH: horizontal flip
        :param flipV: vertical flip

        :return:
        """

        self.sed3_on_close = sed3_on_close
        self.show_fcn = plt.show
        if figure is None:
            self.fig = plt.figure()
        else:
            self.fig = figure
        img = _import_data(img, axis=0, slice_step=1)

        if len(img.shape) == 2:
            imgtmp = img
            img = np.zeros([1, imgtmp.shape[0], imgtmp.shape[1]])
            # self.imgshape.append(1)
            img[-1, :, :] = imgtmp

            zaxis = 0
            # pdb.set_trace();
        self.voxelsize = voxelsize
        self.actual_voxelsize = copy.copy(voxelsize)

        # Rotate data in depndecy on zaxispyplot
        img = self._rotate_start(img, zaxis)
        seeds = self._rotate_start(seeds, zaxis)
        contour = self._rotate_start(contour, zaxis)

        self.rotated_back = False
        self.zaxis = zaxis

        # self.ax = self.fig.add_subplot(111)
        self.imgshape = list(img.shape)
        self.img = img
        self.actual_slice = initslice
        self.colorbar = colorbar
        self.cmap = cmap
        self.show_axis = show_axis
        self.flipH = flipH
        self.flipV = flipV
        if seeds is None:
            self.seeds = np.zeros(self.imgshape, np.int8)
        else:
            self.seeds = seeds
        self.set_window(windowC, windowW)

        """ Mapping mouse button to class number. Default is normal order"""
        self.button_map = mouse_button_map

        self.contour = contour

        self.press = None
        self.press2 = None

        # language
        self.texts = {'btn_delete': 'Delete', 'btn_close': 'Close',
                      'btn_view0': "v0", 'btn_view1': "v1", 'btn_view2': "v2"}

        # iself.fig.subplots_adjust(left=0.25, bottom=0.25)
        if self.show_axis:
            self.ax = self.fig.add_axes([0.20, 0.25, 0.70, 0.70])
        else:
            self.ax = self.fig.add_axes([0.1, 0.20, 0.8, 0.75])

        self.ax_colorbar = self.fig.add_axes([0.9, 0.30, 0.02, 0.6])
        self.draw_slice()

        if self.colorbar:
            # self.colorbar_obj = self.fig.colorbar(self.imsh)
            self.colorbar_obj = plt.colorbar(self.imsh, cax=self.ax_colorbar)
            try:
                self.colorbar_obj.on_mappable_changed(self.imsh)
            except:
                traceback.print_exc()
                logger.warning("with old matplotlib version does not work colorbar redraw")

        # user interface look

        axcolor = 'lightgoldenrodyellow'
        self.ax_actual_slice = self.fig.add_axes(
            [0.15, 0.15, 0.7, 0.03], axisbg=axcolor)
        self.actual_slice_slider = Slider(self.ax_actual_slice, 'Slice', 0,
                                          self.imgshape[2] - 1,
                                          valinit=initslice)

        immax = np.max(self.img)
        immin = np.min(self.img)
        # axcolor_front = 'darkslategray'
        ax_window_c = self.fig.add_axes(
            [0.5, 0.05, 0.2, 0.02], axisbg=axcolor)
        self.window_c_slider = Slider(ax_window_c, 'Center',
                                          immin,
                                          immax,
                                          valinit=float(self.windowC))
        ax_window_w = self.fig.add_axes(
            [0.5, 0.10, 0.2, 0.02], axisbg=axcolor)
        self.window_w_slider = Slider(ax_window_w, 'Width',
                                      0,
                                      (immax - immin) * 2,
                                      valinit=float(self.windowW))
        # conenction to wheel events
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.actual_slice_slider.on_changed(self.sliceslider_update)
        self.window_c_slider.on_changed(self._on_window_c_change)
        self.window_w_slider.on_changed(self._on_window_w_change)
        # draw
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        # delete seeds
        self.ax_delete_seeds = self.fig.add_axes([0.05, 0.05, 0.1, 0.075])
        self.btn_delete = Button(
            self.ax_delete_seeds, self.texts['btn_delete'])
        self.btn_delete.on_clicked(self.callback_delete)

        # close button
        self.ax_delete_seeds = self.fig.add_axes([0.85, 0.05, 0.1, 0.075])
        self.btn_delete = Button(self.ax_delete_seeds, self.texts['btn_close'])
        self.btn_delete.on_clicked(self.callback_close)

        # im shape
        # self.ax_shape = self.fig.add_axes([0.85, 0.05, 0.1, 0.075])
        self.fig.text(0.20, 0.10, 'shape')
        sh = self.img.shape
        self.fig.text(0.20, 0.05, "%ix%ix%i" % (sh[0], sh[1], sh[2]))
        self.draw_slice()


        # view0
        self.ax_v0= self.fig.add_axes([0.05, 0.80, 0.08, 0.075])
        self.btn_v0 = Button(
            self.ax_v0, self.texts['btn_view0'])
        self.btn_v0.on_clicked(self._callback_v0)

        # view1
        self.ax_v1= self.fig.add_axes([0.05, 0.70, 0.08, 0.075])
        self.btn_v1 = Button(
            self.ax_v1, self.texts['btn_view1'])
        self.btn_v1.on_clicked(self._callback_v1)

        # view2
        self.ax_v2= self.fig.add_axes([0.05, 0.60, 0.08, 0.075])
        self.btn_v2 = Button(
            self.ax_v2, self.texts['btn_view2'])
        self.btn_v2.on_clicked(self._callback_v2)
        if show:
            self.show()

    def _callback_v0(self, event):
        self.rotate_to_zaxis(0)

    def _callback_v1(self, event):
        self.rotate_to_zaxis(1)

    def _callback_v2(self, event):
        self.rotate_to_zaxis(2)

    def set_window(self, windowC, windowW):
        """
        Sets visualization window
        :param windowC: window center
        :param windowW: window width
        :return:
        """
        if not (windowW and windowC):
            windowW = np.max(self.img) - np.min(self.img)
            windowC = (np.max(self.img) + np.min(self.img)) / 2.0

        self.imgmax = windowC + (windowW / 2)
        self.imgmin = windowC - (windowW / 2)
        self.windowC = windowC
        self.windowW = windowW

            # self.imgmax = np.max(self.img)
            # self.imgmin = np.min(self.img)
            # self.windowC = windowC
            # self.windowW = windowW
        # else:
        #     self.imgmax = windowC + (windowW / 2)
        #     self.imgmin = windowC - (windowW / 2)
        #     self.windowC = windowC
        #     self.windowW = windowW

    def _on_window_w_change(self, windowW):
        self.set_window(self.windowC, windowW)
        if self.colorbar:
            try:
                self.colorbar_obj.on_mappable_changed(self.imsh)
            except:
                traceback.print_exc()
                logger.warning("with old matplotlib version does not work colorbar redraw")

        self.update_slice()

    def _on_window_c_change(self, windowC):
        self.set_window(windowC, self.windowW)
        if self.colorbar:
            try:
                self.colorbar_obj.on_mappable_changed(self.imsh)
            except:
                traceback.print_exc()
                logger.warning("with old matplotlib version does not work colorbar redraw")

        self.update_slice()

    def rotate_to_zaxis(self, new_zaxis):
        """
        rotate image to selected axis
        :param new_zaxis:
        :return:
        """

        img = self._rotate_end(self.img, self.zaxis)
        seeds = self._rotate_end(self.seeds, self.zaxis)
        contour = self._rotate_end(self.contour, self.zaxis)

        # Rotate data in depndecy on zaxispyplot
        self.img = self._rotate_start(img, new_zaxis)
        self.seeds = self._rotate_start(seeds, new_zaxis)
        self.contour = self._rotate_start(contour, new_zaxis)
        self.zaxis = new_zaxis
        # import ipdb
        # ipdb.set_trace()
        # self.actual_slice_slider.valmax = self.img.shape[2] - 1
        self.actual_slice = 0
        self.rotated_back = False

        # update slicer
        self.fig.delaxes(self.ax_actual_slice)
        self.ax_actual_slice.cla()
        del(self.actual_slice_slider)
        self.fig.add_axes(self.ax_actual_slice)
        self.actual_slice_slider = Slider(self.ax_actual_slice, 'Slice', 0,
                                          self.img.shape[2] - 1,
                                          valinit=0)
        self.actual_slice_slider.on_changed(self.sliceslider_update)
        self.update_slice()

    def _rotate_start(self, data, zaxis):
        if data is not None:
            if zaxis == 0:
                tr =(1, 2, 0)
                data = np.transpose(data, tr)
                vs = self.actual_voxelsize
                if self.actual_voxelsize is not None:
                    self.actual_voxelsize = [vs[tr[0]], vs[tr[1]], vs[tr[2]]]
            elif zaxis == 1:
                tr = (2, 0, 1)
                data = np.transpose(data, tr)
                vs = self.actual_voxelsize
                if self.actual_voxelsize is not None:
                    self.actual_voxelsize = [vs[tr[0]], vs[tr[1]], vs[tr[2]]]
            elif zaxis == 2:
                # data = np.transpose(data, (0, 1, 2))
                pass
            else:
                print("problem with zaxis in _rotate_start()")
                logger.warning("problem with zaxis in _rotate_start()")

        return data

    def _rotate_end(self, data, zaxis):
        if data is not None:
            if self.rotated_back is False:
                if zaxis == 0:
                    tr = (2, 0, 1)
                    data = np.transpose(data, tr)
                    vs = self.actual_voxelsize
                    if self.actual_voxelsize is not None:
                        self.actual_voxelsize = [vs[tr[0]], vs[tr[1]], vs[tr[2]]]
                elif zaxis == 1:
                    tr = (1, 2, 0)
                    data = np.transpose(data, tr)
                    vs = self.actual_voxelsize
                    if self.actual_voxelsize is not None:
                        self.actual_voxelsize = [vs[tr[0]], vs[tr[1]], vs[tr[2]]]
                elif zaxis == 2:
                    pass
                else:
                    print("problem with zaxis in _rotate_start()")
                    logger.warning("problem with zaxis in _rotate_start()")

            else:
                print("There is a danger in calling show() twice")
                logger.warning("There is a danger in calling show() twice")

        return data

    def update_slice(self):
        # TODO tohle je tu kvuli contour, neumim ji odstranit jinak
        self.ax.cla()

        self.draw_slice()

    def __flip(self, sliceimg):
        """
        Flip if asked in self.flipV or self.flipH
        :param sliceimg: one image slice
        :return: flipp
        """
        if self.flipH:
            sliceimg = sliceimg[:, -1:0:-1]

        if self.flipV:
            sliceimg = sliceimg [-1:0:-1,:]

        return sliceimg

    def draw_slice(self):
        sliceimg = self.img[:, :, int(self.actual_slice)]
        sliceimg = self.__flip(sliceimg)
        self.imsh = self.ax.imshow(sliceimg, self.cmap, vmin=self.imgmin,
                                   vmax=self.imgmax, interpolation='nearest')
        # plt.hold(True)
        # pdb.set_trace();
        sliceseeds = self.seeds[:, :, int(self.actual_slice)]
        sliceseeds = self.__flip(sliceseeds)
        self.ax.imshow(self.prepare_overlay(
            sliceseeds
        ), interpolation='nearest', vmin=self.imgmin, vmax=self.imgmax)

        # vykreslení okraje
        # X,Y = np.meshgrid(self.imgshape[0], self.imgshape[1])

        if self.contour is not None:
            try:
                # exception catch problem with none object in image
                # ctr =
                slicecontour = self.contour[:, :, int(self.actual_slice)]
                slicecontour = self.__flip(slicecontour)
                self.ax.contour(
                    slicecontour, 1,
                    levels=[0.5, 1.5, 2.5],
                    linewidths=2)
            except:
                pass

        # self.ax.set_axis_off()
        # self.ax.set_axis_below(False)
        self._ticklabels()

        # print(ctr)
        # import pdb; pdb.set_trace()

        self.fig.canvas.draw()
        # self.ax.cla()
        # del(ctr)

        # pdb.set_trace();
        # plt.hold(False)
    def _ticklabels(self):
        if self.show_axis and self.actual_voxelsize is not None:
            # pass

            xmax = self.img.shape[0]
            ymax = self.img.shape[1]
            xmaxmm = xmax * self.actual_voxelsize[0]
            ymaxmm = ymax * self.actual_voxelsize[1]
            xmm = 10.0**np.floor(np.log10(xmaxmm))
            ymm = 10.0**np.floor(np.log10(ymaxmm))
            x = xmm * 1.0 / self.actual_voxelsize[0]
            y = ymm * 1.0 / self.actual_voxelsize[1]

            self.ax.set_xticks([0, x])
            self.ax.set_xticklabels([0, xmm])
            self.ax.set_yticks([0, y])
            self.ax.set_yticklabels([0, ymm])
            # self.ax.set_yticklabels([13,12])

        else:
            self.ax.set_xticklabels([])
            self.ax.set_yticklabels([])


    def next_slice(self):
        self.actual_slice = self.actual_slice + 1
        if self.actual_slice >= self.imgshape[2]:
            self.actual_slice = 0

    def prev_slice(self):
        self.actual_slice = self.actual_slice - 1
        if self.actual_slice < 0:
            self.actual_slice = self.imgshape[2] - 1

    def sliceslider_update(self, val):
        # zaokrouhlení
        # self.actual_slice_slider.set_val(round(self.actual_slice_slider.val))
        self.actual_slice = round(val)
        self.update_slice()

    def prepare_overlay(self, seeds):
        sh = list(seeds.shape)
        if len(sh) == 2:
            sh.append(4)
        else:
            sh[2] = 4
        # assert sh[2] == 1, 'wrong overlay shape'
        # sh[2] = 4
        overlay = np.zeros(sh)

        overlay[:, :, 0] = (seeds == 1)
        overlay[:, :, 1] = (seeds == 2)
        overlay[:, :, 2] = (seeds == 3)

        overlay[:, :, 3] = (seeds > 0)

        return overlay

    def show(self):
        """ Function run viewer window.
        """
        self.show_fcn()
        # plt.show()\

        return self.prepare_output_data()

    def prepare_output_data(self):
        if self.rotated_back is False:
            # Rotate data in depndecy on zaxis
            self.img = self._rotate_end(self.img, self.zaxis)
            self.seeds = self._rotate_end(self.seeds, self.zaxis)
            self.contour = self._rotate_end(self.contour, self.zaxis)
            self.rotated_back = True
        return self.seeds

    def on_scroll(self, event):
        ''' mouse wheel is used for setting slider value'''
        if event.button == 'up':
            self.next_slice()
        if event.button == 'down':
            self.prev_slice()
        self.actual_slice_slider.set_val(self.actual_slice)
        # tim, ze dojde ke zmene slideru je show_slce volan z nej
        # self.show_slice()
        # print(self.actual_slice)

    # malování -------------------
    def on_press(self, event):
        'on but-ton press we will see if the mouse is over us and store data'
        if event.inaxes != self.ax:
            return
        # contains, attrd = self.rect.contains(event)
        # if not contains: return
        # print('event contains', self.rect.xy)
        # x0, y0 = self.rect.xy
        self.press = [event.xdata], [event.ydata], event.button
        # self.press1 = True

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None:
            return

        if event.inaxes != self.ax:
            return
        # print(event.inaxes)

        x0, y0, btn = self.press
        x0.append(event.xdata)
        y0.append(event.ydata)

    def on_release(self, event):
        'on release we reset the press data'
        if self.press is None:
            return
        # print(self.press)
        x0, y0, btn = self.press
        if btn == 1:
            color = 'r'
        elif btn == 2:
            color = 'b'  # noqa

        # plt.axes(self.ax)
        # plt.plot(x0, y0)
        # button Mapping
        btn = self.button_map[btn]

        self.set_seeds(y0, x0, self.actual_slice, btn)
        # self.fig.canvas.draw()
        # pdb.set_trace();
        self.press = None
        self.update_slice()

    def callback_delete(self, event):
        self.seeds[:, :, int(self.actual_slice)] = 0
        self.update_slice()

    def callback_close(self, event):
        matplotlib.pyplot.clf()
        matplotlib.pyplot.close()
        if self.sed3_on_close is not None:
            self.sed3_on_close(self)

    def set_seeds(self, px, py, pz, value=1, voxelsizemm=[1, 1, 1],
                  cursorsizemm=[1, 1, 1]):
        assert len(px) == len(
            py), 'px and py describes a point, their size must be same'

        for i, item in enumerate(px):
            self.seeds[int(item), int(py[i]), int(pz)] = value

        # @todo

    def get_seed_sub(self, label):
        """ Return list of all seeds with specific label
        """
        sx, sy, sz = np.nonzero(self.seeds == label)

        return sx, sy, sz

    def get_seed_val(self, label):
        """ Return data values for specific seed label"""
        return self.img[self.seeds == label]


def show_slices(data3d, contour=None, seeds=None, axis=0, slice_step=None,
                shape=None, show=True,
                flipH=False, flipV=False,
                first_slice_offset=0,
                first_slice_offset_to_see_seed_with_label=None
                ):
    """
    Show slices as tiled image

    :param data3d: Input data
    :param contour: Data for contouring
    :param seeds: Seed data
    :param axis: Axis for sliceing
    :param slice_step: Show each "slice_step"-th slice, can be float
    :param shape: set shape of output tiled image. slice_step is estimated if it is not set explicitly
    :param first_slice_offset: set offset of first slice
    :param first_slice_offset_to_see_seed_with_label: find offset to see slice with seed with defined label
    """

    # odhad slice_step, neni li zadan
    # slice_step estimation
    # TODO make precise estimation (use np.linspace to indexing?)
    if slice_step is None:
        if shape is None:
            slice_step = 1
        else:
            slice_step = ((data3d.shape[axis] - first_slice_offset ) / float(np.prod(shape)))



    if first_slice_offset_to_see_seed_with_label is not None:
        if seeds is not None:
            inds = np.nonzero(seeds==first_slice_offset_to_see_seed_with_label)
            # print(inds)
            # take first one with defined seed
            # ind = inds[axis][0]
            # take most used index
            ind = np.median(inds[axis])
            first_slice_offset = ind % slice_step


    data3d = _import_data(data3d, axis=axis, slice_step=slice_step, first_slice_offset=first_slice_offset)
    contour = _import_data(contour, axis=axis, slice_step=slice_step, first_slice_offset=first_slice_offset)
    seeds = _import_data(seeds, axis=axis, slice_step=slice_step, first_slice_offset=first_slice_offset)

    number_of_slices = data3d.shape[axis]
    # square image
    #     nn = int(math.ceil(number_of_slices ** 0.5))

    #     sh = [nn, nn]

    # 4:3 image
    meta_shape = shape
    if meta_shape is None:
        na = int(math.ceil(number_of_slices * 16.0 / 9.0) ** 0.5)
        nb = int(math.ceil(float(number_of_slices) / na))
        meta_shape = [nb, na]

    dsh = __get_slice(data3d, 0, axis).shape
    slimsh = [int(dsh[0] * meta_shape[0]), int(dsh[1] * meta_shape[1])]
    slim = np.zeros(slimsh, dtype=data3d.dtype)
    slco = None
    slse = None
    if seeds is not None:
        slse = np.zeros(slimsh, dtype=seeds.dtype)
    if contour is not None:
        slco = np.zeros(slimsh, dtype=contour.dtype)
    #         slse =
    #     f, axarr = plt.subplots(sh[0], sh[1])

    for i in range(0, number_of_slices):
        cont = None
        seeds2d = None
        im2d = __get_slice(data3d, i, axis, flipH=flipH, flipV=flipV)
        if contour is not None:
            cont = __get_slice(contour, i, axis, flipH=flipH, flipV=flipV)
            slco = __put_slice_in_slim(slco, cont, meta_shape, i)
        if seeds is not None:
            seeds2d = __get_slice(seeds, i, axis, flipH=flipH, flipV=flipV)
            slse = __put_slice_in_slim(slse, seeds2d, meta_shape, i)
        #         plt.axis('off')
        #         plt.subplot(sh[0], sh[1], i+1)
        #         plt.subplots_adjust(wspace=0, hspace=0)

        slim = __put_slice_in_slim(slim, im2d, meta_shape, i)
    #         show_slice(im2d, cont, seeds2d)
    show_slice(slim, slco, slse)
    if show:
        plt.show()


# a, b = np.unravel_index(i, sh)

#     pass


def __get_slice(data, slice_number, axis=0, flipH=False, flipV=False):
    """

    :param data:
    :param slice_number:
    :param axis:
    :param flipV: vertical flip
    :param flipH: horizontal flip
    :return:
    """
    if axis == 0:
        data2d =  data[slice_number, :, :]
    elif axis == 1:
        data2d = data[:, slice_number, :]
    elif axis == 2:
        data2d = data[:, :, slice_number]
    else:
        logger.error("axis number error")
        print("axis number error")
        return None

    if flipV:
        if data2d is not None:
            data2d = data2d[-1:0:-1,:]
    if flipH:
        if data2d is not None:
            data2d = data2d[:, -1:0:-1]
    return data2d


def __put_slice_in_slim(slim, dataim, sh, i):
    """
    put one small slice as a tile in a big image
    """
    a, b = np.unravel_index(int(i), sh)

    st0 = int(dataim.shape[0] * a)
    st1 = int(dataim.shape[1] * b)
    sp0 = int(st0 + dataim.shape[0])
    sp1 = int(st1 + dataim.shape[1])

    slim[
    st0:sp0,
    st1:sp1
    ] = dataim

    return slim


# def show():
#     plt.show()
# \
#
# def close():
#     plt.close()

def sigmoid(x, x0, k):
     y = 1 / (1 + np.exp(-k*(x-x0)))
     return y

def show_slice(data2d, contour2d=None, seeds2d=None):
    """

    :param data2d:
    :param contour2d:
    :param seeds2d:
    :return:
    """

    import copy as cp
    # Show results

    colormap = cp.copy(plt.cm.get_cmap('brg'))
    colormap._init()
    colormap._lut[:1:, 3] = 0

    plt.imshow(data2d, cmap='gray', interpolation='none')
    if contour2d is not None:
        plt.contour(contour2d, levels=[0.5, 1.5, 2.5])
    if seeds2d is not None:
        # Show results
        colormap = copy.copy(plt.cm.get_cmap('Paired'))
        # colormap = copy.copy(plt.cm.get_cmap('gist_rainbow'))
        colormap._init()

        colormap._lut[0, 3] = 0

        tmp0 = copy.copy(colormap._lut[:,0])
        tmp1 = copy.copy(colormap._lut[:,1])
        tmp2 = copy.copy(colormap._lut[:,2])

        colormap._lut[:, 0] = sigmoid(tmp0, 0.5, 5)
        colormap._lut[:, 1] = sigmoid(tmp1, 0.5, 5)
        colormap._lut[:, 2] = 0# sigmoid(tmp2, 0.5, 5)
        # seed 4
        colormap._lut[140:220:, 1] = 0.7# sigmoid(tmp2, 0.5, 5)
        colormap._lut[140:220:, 0] = 0.2# sigmoid(tmp2, 0.5, 5)
        # seed 2
        colormap._lut[40:120:, 1] = 1.# sigmoid(tmp2, 0.5, 5)
        colormap._lut[40:120:, 0] = 0.1# sigmoid(tmp2, 0.5, 5)


        # seed 2
        colormap._lut[120:150:, 0] = 1.# sigmoid(tmp2, 0.5, 5)
        colormap._lut[120:150:, 1] = 0.1# sigmoid(tmp2, 0.5, 5)

        # my colors

        # colormap._lut[1,:] = [.0,.1,.0,1]
        # colormap._lut[2,:] = [.1,.1,.0,1]
        # colormap._lut[3,:] = [.1,.1,.1,1]
        # colormap._lut[4,:] = [.3,.3,.3,1]

        plt.imshow(seeds2d, cmap=colormap, interpolation='none')


def __select_slices(data, axis, slice_step, first_slice_offset=0):
    if data is None:
        return None

    inds = np.floor(np.arange(first_slice_offset, data.shape[axis], slice_step)).astype(np.int)
    # import ipdb
    # ipdb.set_trace()
    # logger.warning("select slices")

    if axis == 0:
        # data = data[first_slice_offset::slice_step, :, :]
        data = data[inds, :, :]
    if axis == 1:
        # data = data[:, first_slice_offset::slice_step, :]
        data = data[:, inds, :]
    if axis == 2:
        # data = data[:, :, first_slice_offset::slice_step]
        data = data[:, :, inds]
    return data


def _import_data(data, axis, slice_step, first_slice_offset=0):
    """
    import ndarray or SimpleITK data
    """
    try:
        import SimpleITK as sitk
        if type(data) is sitk.SimpleITK.Image:
            data = sitk.GetArrayFromImage(data)
    except:
        pass

    data = __select_slices(data, axis, slice_step, first_slice_offset=first_slice_offset)
    return data


# self.rect.figure.canvas.draw()

# return data
try:
    from PyQt4 import QtGui, QtCore
    class sed3qt(QtGui.QDialog):
        def __init__(self, *pars, **params):
            # def __init__(self,parent=None):
            parent = None

            QtGui.QDialog.__init__(self, parent)
            # super(Window, self).__init__(parent)
            # self.setupUi(self)
            self.figure = plt.figure()
            self.canvas = FigureCanvas(self.figure)
            self.toolbar = NavigationToolbar(self.canvas, self)

            # set the layout
            layout = QtGui.QVBoxLayout()
            layout.addWidget(self.toolbar)
            layout.addWidget(self.canvas)
            # layout.addWidget(self.button)
            self.setLayout(layout)

            # def set_params(self, *pars, **params):
            # import sed3.sed3

            params["figure"] = self.figure
            self.sed = sed3(*pars, **params)
            self.sed.sed3_on_close = self.callback_close
            # ed.show()
            self.output = None

        def callback_close(self, sed):
            self.output = sed
            sed.prepare_output_data()
            self.seeds = sed.seeds
            self.close()

        def show(self):
            return self.sed.show_fcn()

        def get_values(self):
            return self.sed

    class sed3qtWidget(QtGui.QWidget):
        def __init__(self, *pars, **params):
            # def __init__(self,parent=None):
            parent = None

            # QtGui.QWidget.__init__(self, parent)
            super(sed3qtWidget, self).__init__(parent)
            # self.setupUi(self)
            self.figure = plt.figure()
            self.canvas = FigureCanvas(self.figure)
            # self.toolbar = NavigationToolbar(self.canvas, self)

            # set the layout
            layout = QtGui.QVBoxLayout()
            # layout.addWidget(self.toolbar)
            layout.addWidget(self.canvas)
            # layout.addWidget(self.button)
            self.setLayout(layout)

            # def set_params(self, *pars, **params):
            # import sed3.sed3

            params["figure"] = self.figure
            self.sed = sed3(*pars, **params)
            self.sed.sed3_on_close = self.callback_close
            # ed.show()
            self.output = None

        def callback_close(self, sed):
            self.output = sed
            sed.prepare_output_data()
            self.seeds = sed.seeds
            self.close()

        def show(self):
            super(sed3qtWidget, self).show()
            return self.sed.show_fcn()

        def get_values(self):
            return self.sed
except:
    pass

# --------------------------tests-----------------------------
class Tests(unittest.TestCase):
    def test_t(self):
        pass

    def setUp(self):
        """ Nastavení společných proměnných pro testy  """
        datashape = [120, 85, 30]
        self.datashape = datashape
        self.rnddata = np.random.rand(datashape[0], datashape[1], datashape[2])
        self.segmcube = np.zeros(datashape)
        self.segmcube[30:70, 40:60, 5:15] = 1

        self.ed = sed3(self.rnddata)
        # ed.show()
        # selected_seeds = ed.seeds

    def test_same_size_input_and_output(self):
        """Funkce testuje stejnost vstupních a výstupních dat"""
        # outputdata = vesselSegmentation(self.rnddata,self.segmcube)
        self.assertEqual(self.ed.seeds.shape, self.rnddata.shape)

    def test_set_seeds(self):
        ''' Testuje uložení do seedů '''
        val = 7
        self.ed.set_seeds([10, 12, 13], [13, 13, 15], 3, value=val)
        self.assertEqual(self.ed.seeds[10, 13, 3], val)

    def test_prepare_overlay(self):
        ''' Testuje vytvoření rgba obrázku z labelů'''
        overlay = self.ed.prepare_overlay(self.segmcube[:, :, 6])
        onePixel = overlay[30, 40]
        self.assertTrue(all(onePixel == [1, 0, 0, 1]))

    def test_get_seed_sub(self):
        """ Testuje, jestli funkce pro vracení dat funguje správně,
        je to zkoušeno na konkrétních hodnotách
        """
        val = 7
        self.ed.set_seeds([10, 12, 13], [13, 13, 15], 3, value=val)
        seedsx, seedsy, seedsz = self.ed.get_seed_sub(val)

        found = [False, False, False]
        for i in range(len(seedsx)):
            if (seedsx[i] == 10) & (seedsy[i] == 13) & (seedsz[i] == 3):
                found[0] = True
            if (seedsx[i] == 12) & (seedsy[i] == 13) & (seedsz[i] == 3):
                found[1] = True
            if (seedsx[i] == 13) & (seedsy[i] == 15) & (seedsz[i] == 3):
                found[2] = True

        logger.debug(found)

        self.assertTrue(all(found))

    def test_get_seed_val(self):
        """ Testuje, jestli jsou správně vraceny hodnoty pro označené pixely
        je to zkoušeno na konkrétních hodnotách
        """
        label = 7
        self.ed.set_seeds([11], [14], 4, value=label)
        seedsx, seedsy, seedsz = self.ed.get_seed_sub(label)

        val = self.ed.get_seed_val(label)
        expected_val = self.ed.img[11, 14, 4]

        logger.debug(val)
        logger.debug(expected_val)

        self.assertIn(expected_val, val)


def generate_data(shp=[16, 20, 24]):
    """ Generating data """

    x = np.ones(shp)
    # inserting box
    x[4:-4, 6:-2, 1:-6] = -1
    x_noisy = x + np.random.normal(0, 0.6, size=x.shape)
    return x_noisy


# --------------------------main------------------------------
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    # při vývoji si necháme vypisovat všechny hlášky
    # logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    #   output configureation
    # logging.basicConfig(format='%(asctime)s %(message)s')
    logging.basicConfig(format='%(message)s')

    formatter = logging.Formatter(
        "%(levelname)-5s [%(module)s:%(funcName)s:%(lineno)d] %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    # input parser
    parser = argparse.ArgumentParser(
        description='Segment vessels from liver. Try call sed3 -f lena')
    parser.add_argument(
        '-f', '--filename',
        # default = '../jatra/main/step.mat',
        default='lena',
        help='*.mat file with variables "data", "segmentation" and "threshod"')
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='run in debug mode')
    parser.add_argument(
        '-e3', '--example3d', action='store_true',
        help='run with 3D example data')
    parser.add_argument(
        '-t', '--tests', action='store_true',
        help='run unittest')
    parser.add_argument(
        '-o', '--outputfile', type=str,
        default='output.mat', help='output file name')
    args = parser.parse_args()

    voxelsize = None

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.tests:
        # hack for use argparse and unittest in one module
        sys.argv[1:] = []
        unittest.main()

    if args.example3d:
        data = generate_data([16, 20, 24])
        voxelsize = [0.1, 1.2, 2.5]
    elif args.filename == 'lena':
        from scipy import misc

        data = misc.lena()
    else:
        #   load all
        mat = scipy.io.loadmat(args.filename)
        logger.debug(mat.keys())

        # load specific variable
        dataraw = scipy.io.loadmat(args.filename, variable_names=['data'])
        data = dataraw['data']

        # logger.debug(matthreshold['threshold'][0][0])

        # zastavení chodu programu pro potřeby debugu,
        # ovládá se klávesou's','c',...
        # zakomentovat
        # pdb.set_trace();

        # zde by byl prostor pro ruční (interaktivní) zvolení prahu z
        # klávesnice
        # tě ebo jinak

    pyed = sed3(data, voxelsize=voxelsize)
    output = pyed.show()

    scipy.io.savemat(args.outputfile, {'data': output})
    pyed.get_seed_val(1)


def index_to_coords(index, shape):
    '''convert index to coordinates given the shape'''
    coords = []
    for i in xrange(1, len(shape)):
        divisor = int(np.product(shape[i:]))
        value = index // divisor
        coords.append(value)
        index -= value * divisor
    coords.append(index)
    return tuple(coords)


sh = np.asarray([3, 4])


def slices(img, shape=[3, 4]):
    """
    create tiled image with multiple slices
    :param img:
    :param shape:
    :return:
    """
    sh = np.asarray(shape)
    i_max = np.prod(sh)
    allimg = np.zeros(img.shape[-2:] * sh)

    for i in range(0, i_max):
        # i = 0
        islice = round((img.shape[0] / float(i_max)) * i)
        #         print(islice)
        imgi = img[islice, :, :]
        coords = index_to_coords(i, sh)
        aic = np.asarray(img.shape[-2:]) * coords

        allimg[aic[0]:aic[0] + imgi.shape[-2], aic[1]:aic[1] + imgi.shape[-1]] = imgi

    #     plt.imshow(imgi)
    #     print(imgi.shape)
    #     print(img.shape)
    return allimg


# sz = img.shape
# np.zeros()
def sed2(img, contour=None, shape=[3, 4]):
    """
    plot tiled image of multiple slices

    :param img:
    :param contour:
    :param shape:
    :return:
    """
    """
    :param img:
    :param contour:
    :param shape:
    :return:
    """

    plt.imshow(slices(img, shape), cmap='gray')
    if contour is not None:
        plt.contour(slices(contour, shape))
