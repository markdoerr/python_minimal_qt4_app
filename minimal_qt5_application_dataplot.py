#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#_____________________________________________________________________________
#
# PROJECT: LARA
# CLASS: 
# FILENAME: dataplot.py
#
# CATEGORY:
#
# AUTHOR: mark doerr
# EMAIL: mark@ismeralda.org
#
# VERSION: 0.0.1
#
# CREATION_DATE: 20180210
# LASTMODIFICATION_DATE: 20180210
#
# BRIEF_DESCRIPTION: Minimal application for data plotting
# DETAILED_DESCRIPTION: 
#   - argument parsing
#   - QApplication
#   - QMainwindow with menues, toolbar and statusbar
#   - Central Tab widget with random number plot
#   - CSV loading and plot
# ____________________________________________________________________________
#
#   Copyright:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
#   INCLUDING THE WARRANTIES OF DESIGN, MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE.
#
#   For further Information see COPYING file that comes with this distribution.
#_______________________________________________________________________________

__version__ = "v0.0.1"

import sys, os, csv
import pkgutil
import argparse
import logging

import math
import random

import numpy as np

import minimal_qt5_application_dataplot_rc

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#~ from matplotlib.backends.backend_qt5agg import NavigationToolbar2QTAgg as NavigationToolbar

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, \
                            QFileDialog, QTabWidget, QPushButton, QLabel, QAction, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, QFileInfo, pyqtSignal, pyqtSlot


class DP_CentralTabWidget(QTabWidget):
    """ Container for all process and process info widgets
    """
    def __init__(self, parent):
        super(DP_CentralTabWidget, self).__init__(parent=None)
        
        self.parent = parent
        self.setTabsClosable(True)
        self.setAcceptDrops(True)
        
        self.tab1 = PlotCanvas(self)
        self.tab1.plotSinus()
        
        self.tab2 = PlotCanvas(self)
        self.tab2.plotRandomNumbers()
        
        self.tab3 = PlotCanvas(self)
        
        # sample data
        x_data = [1,2,3,4]
        y_data = [3,5,8,8]
        
        self.tab3.plotXY(x_data, y_data)

        # Add some sample tabs
        self.addTab(self.tab1,"Sin Plot")
        self.addTab(self.tab2,"Random Number Plot")
        self.addTab(self.tab3,"XY")
        
    # this is required for the CentralTabWidget to accept drags and drops
    def dragEnterEvent(self, event): 
        if event.mimeData().hasFormat('application/dp-dnditemdata'):
            if event.source() == self:  # dragging inside the CentralTabWidget
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()
        super(DP_CentralTabWidget, self).dragEnterEvent(event)

    def dropEvent(self, event): 
        if event.mimeData().hasFormat('application/dp-dnditemdata'):
            # triggering new_action to generate a new tab if no tabs present...
            if self.count() == 0:
                self.parent.new_act.trigger()
                event.acceptProposedAction() # changed from event.accept()
            else:
                logging.info("central tab widget: new data existis ")
        else : 
            event.ignore()
            
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
 
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
 
    def plotSinus(self):
        t = np.arange(0.0, 1.0, 0.01)
        
        #~ fig = self.figure(1)
        
        ax1 = self.fig.add_subplot(211)
        ax1.plot(t, np.sin(2*np.pi*t))
        ax1.grid(True)
        ax1.set_ylim((-2, 2))
        ax1.set_ylabel('1 Hz')
        ax1.set_title('Some sine waves')
        
        for label in ax1.get_xticklabels():
            label.set_color('r')
        
        ax2 = self.fig.add_subplot(212)
        ax2.plot(t, np.sin(2*2*np.pi*t))
        ax2.grid(True)
        ax2.set_ylim((-2, 2))
        l = ax2.set_xlabel('time  / s')
        l.set_color('g')
        l.set_fontsize('large')
        
        self.show()
 
    def plotRandomNumbers(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('Random number plot')
        self.draw()
        
    def plotXY(self, x_data=[1.0], y_data=[1.0], plot_title=""):
        ax = self.figure.add_subplot(111)
        ax.plot(x_data, y_data, 'g-')
        ax.set_title(plot_title)
        self.draw()
        
    def plotXY_np(self, xy_data=None, plot_title=""):
        ax = self.figure.add_subplot(111)
        ax.plot(xy_data, 'b-')
        ax.set_title(plot_title)
        self.draw()

class DP_MainWindow(QMainWindow):
    """Generating the main application window
    """
    editCutSig = pyqtSignal()
    unselctAllSig = pyqtSignal()
        
    def __init__(self):
        super(DP_MainWindow, self).__init__(parent=None)
        
        self.setWindowTitle("Data plot " +  __version__ )
        
        self.dp_default_working_dir = os.getcwd()
        
        self.createActions()
        self.createMenus()
        self.createToolbars()
        self.createStatusbar()
        
        self.central_tw = DP_CentralTabWidget(self) 
        self.setCentralWidget(self.central_tw)

        self.showMaximized()
        
    def createActions(self):
        self.exit_act = QAction(QIcon(':/linux/quit'),"E&xit", self, shortcut="Ctrl+X",
                                      statusTip="Quit datplot", triggered=self.close)                
        self.new_act = QAction(QIcon(':/linux/new'),"&New CSV file", self, shortcut="Ctrl+N",
                                     statusTip="New CSV file for saving data to", triggered=lambda new_csv_filename="": self.new_data_action(new_csv_filename="" ) )
        self.open_act = QAction(QIcon(':/linux/open'),"&Open", self, shortcut="Ctrl+O",
                                      statusTip="Open CSV file", triggered=self.openDataAction)
        
        self.copy_act = QAction(QIcon(':/linux/copy'),"&Copy", self, shortcut="Ctrl+c",
                                      statusTip="copy item", triggered=self.default_action)
        self.cut_act = QAction(QIcon(':/linux/cut'),"&Cut", self, shortcut="Ctrl+x",
                                     statusTip="cut item", triggered=self.editCutAction)
        self.paste_act = QAction(QIcon(':/linux/paste'),"&Paste", self, shortcut="Ctrl+v",
                                       statusTip="paste item", triggered=self.default_action)
                                       
        self.zoom_in_act = QAction(QIcon(':/linux/zoom_out'),"zoom &in", self, shortcut="Ctrl++",
                                         statusTip="zoom in", triggered=self.zoom_in_action)
        self.zoom_out_act = QAction(QIcon(':/linux/zoom_in'),"zoom &out", self, shortcut="Ctrl+-",
                                          statusTip="zoom in", triggered=self.zoom_out_action)

        self.about_act = QAction("A&bout", self, shortcut="F1",
                                       triggered=self.about_action)
    def default_action(self,mode):
        logging.debug("default action")
        return()
        
    def openDataAction(self):
        url1 = QUrl("file://")
        url2 = QUrl("file:///home")
        urls = [url1,url2]
        new_filname_dia = QFileDialog()
        #~ new_filname_dia.setSidebarUrls(urls);
    
        new_filename_default = self.dp_default_working_dir
        csv_filename,csv_extension  = new_filname_dia.getOpenFileName(self, 'Select a csv file to be opened...',new_filename_default,'CSV files (*.csv)')
        
        logging.debug(csv_filename)
        
        # now generating a new data
        if csv_filename == "" :
            logging.debug("creating new file %s" % csv_filename)
            
        else :
            logging.debug("opening %s" % csv_filename)
            curr_FI = QFileInfo(csv_filename)
            self.dp_default_working_dir = curr_FI.absolutePath()
            
            self.loadCSVFile(csv_filename)
            
    def loadCSVFile(self, csv_filename):
        curr_FI = QFileInfo(csv_filename)
        csv_basename = curr_FI.fileName()
        
        with open(csv_filename, 'rb' ) as csv_file:
            x_dat, y_dat = np.loadtxt(csv_file, delimiter=",", skiprows=1, unpack=True)
        
        # now generating new plot and adding tab
        plot_canv = PlotCanvas(self)
        plot_canv.plotXY(x_dat,y_dat, plot_title=csv_basename)
        
        self.central_tw.addTab(plot_canv , csv_basename)
        
                
    def new_data_action(self, new_csv_filename="" ):  
        if new_csv_filename == "" :
            url1 = QtCore.QUrl("file://")       # def. location 1
            url2 = QtCore.QUrl("file:///home")  # def. location 2
            urls = [url1,url2]
            new_filname_dia = QFileDialog()
            #~ new_filname_dia.setSidebarUrls(urls);
        
            new_filename_default = self.dp_default_working_dir + "/%s_%s.csv" %( QtCore.QDateTime.currentDateTime().toString("yyMMdd_hhmmss"),"process")
            new_csv_filename = new_filname_dia.getSaveFileName(self, 'Select New empty data file to be used for saving data...',new_filename_default,'CSV files (*.csv)')
        
        # now generating a new data
        if new_csv_filename != "" :
            curr_FI = QtCore.QFileInfo(new_csv_filename)
            logging.info("try to replace by weak list if performance is too slow or memory intensive")
            
            logging.debug("creating new file %s" % new_csv_filename)
            self.dp_default_working_dir = curr_FI.absolutePath()
                                           
    def editCutAction(self):
        self.editCutSig.emit()
        
    def zoom_in_action(self):
        #~ curr_view = self.central_tw.currentWidget()        
        #~ if(curr_view) :
            #~ curr_view.zoomIn()
        pass
        
    def zoom_out_action(self):
        #~ curr_view = self.central_tw.currentWidget()
        #~ if(curr_view) :
            #~ curr_view.zoomOut()
        pass

    def about_action(self):
        QMessageBox.about(self, "About data plot","<b>Data plot %s</b> is a very simple data plotting framework." % __version__)
        
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        #~ self.fileMenu.addAction(self.new_act)
        self.fileMenu.addAction(self.open_act)
        self.fileMenu.addAction(self.exit_act)
        
        self.itemMenu = self.menuBar().addMenu("&Item")
        self.itemMenu.addAction(self.cut_act)
        self.itemMenu.addSeparator()
        # property could be added

        self.itemMenu = self.menuBar().addMenu("&View")
        self.itemMenu.addAction(self.zoom_in_act)
        self.itemMenu.addAction(self.zoom_out_act)
        
        self.aboutMenu = self.menuBar().addMenu("&Help")
        self.aboutMenu.addAction(self.about_act)
    
    def createToolbars(self):
        self.file_tb = self.addToolBar("File")
        self.file_tb.addAction(self.exit_act)
        #~ self.file_tb.addAction(self.new_act)
        self.file_tb.addAction(self.open_act)
                
        #~ self.edit_tb = self.addToolBar("Edit")
 
        #~ self.edit_tb.addAction(self.copy_act)
        #~ self.edit_tb.addAction(self.cut_act)
        #~ self.edit_tb.addAction(self.paste_act)
        #~ self.edit_tb.addSeparator()
        
        self.zoom_tb = self.addToolBar("Zoom")
        #~ zoom_slider = QSlider(QtCore.Qt.Horizontal)
        #~ zoom_slider.setRange(5, 200)
        #~ zoom_slider.setValue(100)
        #~ self.zoom_tb.addWidget(zoom_slider)
        self.zoom_tb.addAction(self.zoom_in_act)
        self.zoom_tb.addAction(self.zoom_out_act)
        
    def createStatusbar(self):
        self.status_text = QLabel("Please select a CSV to load")
        self.statusBar().addWidget(self.status_text, 1)

class DP_QApplication(QApplication):
    """Data plot global Qt-Application"""
    def __init__(self, args):
        super(DP_QApplication, self).__init__(args)
        
        server_mode = False
        if server_mode == False :
            self.mw = DP_MainWindow()
        else :
            logging.info("running in server mode")
        
            self.lara_default_working_dir = os.getcwd()
        
            logging.debug("server ended")            
        self.exec_()    

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s| %(module)s.%(funcName)s:%(message)s', level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(description="simple data plot framework")

    # just some examples for command line parsing
    parser.add_argument('-s','--server', action='store_true', help='run dataplot in server mode')
    parser.add_argument('-v','--version', action='version', version='%(prog)s ' + __version__)
        
    parsed_args = parser.parse_args()
    
    if (parsed_args.server) :
        logging.info("runnig data plot in server mode now ... (just a dummy)")
                
    if (not (parsed_args.server) ):
        logging.info("runnig data plot in GUI mode")
        DP_QApplication(sys.argv)
