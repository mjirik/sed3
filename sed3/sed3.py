#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append("./src/")
# import pdb
# pdb.set_trace();

import scipy.io

import logging
logger = logging.getLogger(__name__)


import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.widgets import Slider, Button


class sed3:

    """ Viewer and seed editor for 2D and 3D data.

    sed3(img, ...)

    img: 2D or 3D grayscale data
    voxelsizemm: size of voxel, default is [1, 1, 1]
    initslice: 0
    colorbar: True/False, default is True
    cmap: colormap
    zaxis: axis with slice numbers


    ed = sed3(img)
    ed.show()
    selected_seeds = ed.seeds

    """
    # if data.shape != segmentation.shape:
    # raise Exception('Input size error','Shape if input data and segmentation
    # must be same')

    def __init__(
        self, img, voxelsizemm=[1, 1, 1], initslice=0, colorbar=True,
        cmap=matplotlib.cm.Greys_r, seeds=None, contour=None, zaxis=0,
        mouse_button_map={1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8},
        windowW=[], windowC=[], show=False
    ):
        self.fig = plt.figure()

        if len(img.shape) == 2:
            imgtmp = img
            img = np.zeros([1, imgtmp.shape[0], imgtmp.shape[1]])
            # self.imgshape.append(1)
            img[-1, :, :] = imgtmp

            zaxis = 0
            # pdb.set_trace();

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
        if seeds is None:
            self.seeds = np.zeros(self.imgshape, np.int8)
        else:
            self.seeds = seeds
        if not (windowW and windowC):
            self.imgmax = np.max(img)
            self.imgmin = np.min(img)
        else:
            self.imgmax = windowC + (windowW / 2)
            self.imgmin = windowC - (windowW / 2)

        """ Mapping mouse button to class number. Default is normal order"""
        self.button_map = mouse_button_map

        self.contour = contour

        self.press = None
        self.press2 = None

# language
        self.texts = {'btn_delete': 'Delete', 'btn_close': 'Close'}

        # iself.fig.subplots_adjust(left=0.25, bottom=0.25)
        self.ax = self.fig.add_axes([0.2, 0.3, 0.7, 0.6])

        self.draw_slice()

        if self.colorbar:
            self.fig.colorbar(self.imsh)

        # user interface look

        axcolor = 'lightgoldenrodyellow'
        ax_actual_slice = self.fig.add_axes(
            [0.2, 0.2, 0.6, 0.03], axisbg=axcolor)
        self.actual_slice_slider = Slider(ax_actual_slice, 'Slice', 0,
                                          self.imgshape[2], valinit=initslice)

        # conenction to wheel events
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.actual_slice_slider.on_changed(self.sliceslider_update)
# draw
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

# delete seeds
        self.ax_delete_seeds = self.fig.add_axes([0.2, 0.1, 0.1, 0.075])
        self.btn_delete = Button(
            self.ax_delete_seeds, self.texts['btn_delete'])
        self.btn_delete.on_clicked(self.callback_delete)

# close button
        self.ax_delete_seeds = self.fig.add_axes([0.7, 0.1, 0.1, 0.075])
        self.btn_delete = Button(self.ax_delete_seeds, self.texts['btn_close'])
        self.btn_delete.on_clicked(self.callback_close)

        self.draw_slice()
        if show:
            self.show()

    def _rotate_start(self, data, zaxis):
        if data is not None:
            if zaxis == 0:
                data = np.transpose(data, (1, 2, 0))
            elif zaxis == 2:
                pass
            else:
                print "problem with zaxis in _rotate_start()"

        return data

    def _rotate_end(self, data, zaxis):
        if data is not None:
            if self.rotated_back is False:
                if zaxis == 0:
                    data = np.transpose(data, (2, 0, 1))
                elif zaxis == 2:
                    pass
                else:
                    print "problem with zaxis in _rotate_start()"

            else:
                print "There is a danger in calling show() twice"

        return data

    def update_slice(self):
        # TODO tohle je tu kvuli contour, neumim ji odstranit jinak
        self.ax.cla()

        self.draw_slice()

    def draw_slice(self):
        sliceimg = self.img[:, :, int(self.actual_slice)]
        self.imsh = self.ax.imshow(sliceimg, self.cmap, vmin=self.imgmin,
                                   vmax=self.imgmax, interpolation='nearest')
        # plt.hold(True)
        # pdb.set_trace();
        self.ax.imshow(self.prepare_overlay(
            self.seeds[:, :, int(self.actual_slice)]
        ), interpolation='nearest', vmin=self.imgmin, vmax=self.imgmax)

        # vykreslení okraje
        # X,Y = np.meshgrid(self.imgshape[0], self.imgshape[1])

        if self.contour is not None:
            try:
                # exception catch problem with none object in image
                # ctr =
                self.ax.contour(
                    self.contour[:, :, int(self.actual_slice)], 1,
                    linewidths=2)
            except:
                pass

        # print ctr
        # import pdb; pdb.set_trace()

        self.fig.canvas.draw()
        # self.ax.cla()
        # del(ctr)

        # pdb.set_trace();
        # plt.hold(False)

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
        plt.show()
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
        # print self.actual_slice

# malování -------------------
    def on_press(self, event):
        'on but-ton press we will see if the mouse is over us and store data'
        if event.inaxes != self.ax:
            return
        # contains, attrd = self.rect.contains(event)
        # if not contains: return
        # print 'event contains', self.rect.xy
        # x0, y0 = self.rect.xy
        self.press = [event.xdata], [event.ydata], event.button
        # self.press1 = True

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None:
            return

        if event.inaxes != self.ax:
            return
        # print event.inaxes

        x0, y0, btn = self.press
        x0.append(event.xdata)
        y0.append(event.ydata)

    def on_release(self, event):
        'on release we reset the press data'
        if self.press is None:
            return
        # print self.press
        x0, y0, btn = self.press
        if btn == 1:
            color = 'r'
        elif btn == 2:
            color = 'b'

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


# self.rect.figure.canvas.draw()

    # return data

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

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.tests:
        # hack for use argparse and unittest in one module
        sys.argv[1:] = []
        unittest.main()

    if args.example3d:
        data = generate_data()
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

    pyed = sed3(data)
    output = pyed.show()

    scipy.io.savemat(args.outputfile, {'data': output})
    pyed.get_seed_val(1)
