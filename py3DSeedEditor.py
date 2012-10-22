#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append("./src/")
import pdb
#  pdb.set_trace();

import scipy.io

import logging
logger = logging.getLogger(__name__)


import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.widgets import Slider, Button, RadioButtons


#Ahooooooj


class py3DSeedEditor:
    """ Volumetric vessel segmentation from liver.
    data: CT (or MRI) 3D data
    segmentation: labeled image with same size as data where label: 
    1 mean liver pixels,
    -1 interesting tissuse (bones)
    0 othrewise
    """
#   Funkce pracuje z počátku na principu jednoduchého prahování. Nalezne se 
#   největší souvislý objekt nad stanoveným prahem, Průběžně bude segmentace 
#   zpřesňována. Bude nutné hledat cévy, které se spojují mimo játra, ale 
#   ignorovat žebra. 
#   Proměnné threshold, dataFiltering a nObj se postupně pokusíme eliminovat a 
#   navrhnout je automaticky. 
#   threshold: ručně určený práh
#   dataFiltering: označuje, jestli budou data filtrována uvnitř funkce, nebo 
#   již vstupují filtovaná. False znamená, že vstupují filtrovaná.
#   nObj: označuje kolik největších objektů budeme hledat
    #if data.shape != segmentation.shape:
    #    raise Exception('Input size error','Shape if input data and segmentation must be same')

    def __init__(self, img, voxelsizemm=[1,1,1], startslice = 0 , colorbar = True,
            cmap = matplotlib.cm.Greys_r):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        if len(img.shape) == 2:
            imgtmp = img
            img = np.zeros([imgtmp.shape[0], imgtmp.shape[1], 1])
            #self.imgshape.append(1)
            img[:,:,-1] = imgtmp
            pdb.set_trace();
        self.imgshape = list(img.shape)
        self.img = img
        self.actual_slice = startslice
        self.colorbar = colorbar
        self.cmap = cmap 

        self.fig.subplots_adjust(left=0.25, bottom=0.25)


        self.show_slice()

        if self.colorbar:
            self.fig.colorbar(self.imsh)

        # user interface look

        axcolor = 'lightgoldenrodyellow'
        ax_actual_slice = self.fig.add_axes([0.2, 0.2, 0.5, 0.03], axisbg=axcolor)
        self.actual_slice_slider = Slider(ax_actual_slice, 'Slice', 0, 
                self.imgshape[2], valinit=startslice)
        
        # conenction to wheel events
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.actual_slice_slider.on_changed(self.sliceslider_update)

        self.show_slice()


    def show_slice(self):
        sliceimg = self.img[:,:,self.actual_slice]
        self.imsh = self.ax.imshow(sliceimg, self.cmap)
        self.fig.canvas.draw()
    def next_slice(self):
        self.actual_slice = self.actual_slice + 1
        if self.actual_slice >= self.imgshape[2]:
            self.actual_slice = 0

    def sliceslider_update(self, val):
# zaokrouhlení
        #self.actual_slice_slider.set_val(round(self.actual_slice_slider.val))
        self.actual_slice = round(val)
        self.show_slice()


    def prev_slice(self):
        self.actual_slice = self.actual_slice - 1
        if self.actual_slice < 0:
            self.actual_slice = self.imgshape[2] - 1

    def show(self):
        plt.show()
        return 6

    def on_scroll(self, event):
        if event.button == 'up':
            self.next_slice()
        if event.button == 'down':
            self.prev_slice()
        self.show_slice()
        self.actual_slice_slider.set_val (self.actual_slice)
        #print self.actual_slice

        #pdb.set_trace();


    #return data 

# --------------------------tests-----------------------------
class Tests(unittest.TestCase):
    def test_t(self):
        pass
    def setUp(self):
        """ Nastavení společných proměnných pro testy  """
        datashape = [220,115,30]
        self.datashape = datashape
        self.rnddata = np.random.rand(datashape[0], datashape[1], datashape[2])
        self.segmcube = np.zeros(datashape)
        self.segmcube[130:190, 40:90,5:15] = 1

    def test_same_size_input_and_output(self):
        """Funkce testuje stejnost vstupních a výstupních dat"""
        outputdata = vesselSegmentation(self.rnddata,self.segmcube)
        self.assertEqual(outputdata.shape, self.rnddata.shape)


#
#    def test_different_data_and_segmentation_size(self):
#        """ Funkce ověřuje vyhození výjimky při různém velikosti vstpních
#        dat a segmentace """
#        pdb.set_trace();
#        self.assertRaises(Exception, vesselSegmentation, (self.rnddata, self.segmcube[2:,:,:]) )
#
        
        
# --------------------------main------------------------------
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
# při vývoji si necháme vypisovat všechny hlášky
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
#   output configureation
    #logging.basicConfig(format='%(asctime)s %(message)s')
    logging.basicConfig(format='%(message)s')

    formatter = logging.Formatter("%(levelname)-5s [%(module)s:%(funcName)s:%(lineno)d] %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)

    logger.addHandler(ch)


    # input parser
    parser = argparse.ArgumentParser(description='Segment vessels from liver')
    parser.add_argument('-f','--filename',  
            default = '../jatra/main/step.mat',
            help='*.mat file with variables "data", "segmentation" and "threshod"')
    parser.add_argument('-d', '--debug', action='store_true',
            help='run in debug mode')
    parser.add_argument('-t', '--tests', action='store_true', 
            help='run unittest')
    parser.add_argument('-o', '--outputfile', type=str,
        default='output.mat',help='output file name')
    args = parser.parse_args()


    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.tests:
        # hack for use argparse and unittest in one module
        sys.argv[1:]=[]
        unittest.main()

    if args.filename == 'lena':
        from scipy import misc
        data = misc.lena()
    else:
    #   load all 
        mat = scipy.io.loadmat(args.filename)
        logger.debug( mat.keys())

        # load specific variable
        dataraw = scipy.io.loadmat(args.filename, variable_names=['data'])
        data = dataraw['data']

        #logger.debug(matthreshold['threshold'][0][0])


        # zastavení chodu programu pro potřeby debugu, 
        # ovládá se klávesou's','c',... 
        # zakomentovat
        #pdb.set_trace();

        # zde by byl prostor pro ruční (interaktivní) zvolení prahu z klávesnice 
        #tě ebo jinak

    pyed = py3DSeedEditor(data)
    output = pyed.show()

    scipy.io.savemat(args.outputfile,{'vesselSegm':output})

