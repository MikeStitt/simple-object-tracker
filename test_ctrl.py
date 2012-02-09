#!/usr/bin/python
#
# Copyright (C) 2012 Mike Stitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
from PyQt4 import *
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import test_ui
import test_pb2
import socket
 
UDP_IP="127.0.0.1"
#UDP_IP="192.168.1.100"
UDP_PORT=5005
 
class sendCtrl(QObject):

    def __init__(self):
	    QObject.__init__(self)
	    self.capSetMsg = test_pb2.captureSettings()
	    self.capSetMsg.magicTest = 123456

	    self.sock = socket.socket( socket.AF_INET, # Internet
                        socket.SOCK_DGRAM ) # UDP
	    
    def send(self):
#	    self.sock.sendto( self.capSetMsg.SerializeToString(), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '0' + '>' +str(self.capSetMsg.colorFilter.minHue), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '1' + '>' +str(self.capSetMsg.colorFilter.maxHue), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '2' + '>' +str(self.capSetMsg.colorFilter.minSat), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '3' + '>' +str(self.capSetMsg.colorFilter.maxSat), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '4' + '>' +str(self.capSetMsg.colorFilter.minVal), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '5' + '>' +str(self.capSetMsg.colorFilter.maxVal), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '7' + '>' +str(self.capSetMsg.findPoly.cannyThreshold1), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '8' + '>' +str(self.capSetMsg.findPoly.cannyThreshold2), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '9' + '>' +str(self.capSetMsg.findPoly.cannyAperature), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '10' + '>' +str(self.capSetMsg.findPoly.minPerimeter), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '11' + '>' +str(self.capSetMsg.findPoly.minArea), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '12' + '>' +str(self.capSetMsg.findPoly.deviationRatio), (UDP_IP, UDP_PORT) )
        self.sock.sendto( '14' + '>' +str(self.capSetMsg.videoOut), (UDP_IP, UDP_PORT) )

        self.sock.sendto( '13' + '>' +str(self.capSetMsg.colorFilter.beatPeriod), (UDP_IP, UDP_PORT) )

    def newMinHue(self,x):
	    self.capSetMsg.colorFilter.minHue = x
	    self.send()

    def newMaxHue(self,x):
	    self.capSetMsg.colorFilter.maxHue = x
	    self.send()
	    
    def newMinSat(self,x):
	    self.capSetMsg.colorFilter.minSat = x
	    self.send()

    def newMaxSat(self,x):
	    self.capSetMsg.colorFilter.maxSat = x
	    self.send()

    def newMinVal(self,x):
	    self.capSetMsg.colorFilter.minVal = x
	    self.send()

    def newMaxVal(self,x):
	    self.capSetMsg.colorFilter.maxVal = x
	    self.send()

    def newBeatPeriod(self,x):
	    self.capSetMsg.colorFilter.beatPeriod = x
	    self.send()

    def newCannyThreshold1(self,x):
	    self.capSetMsg.findPoly.cannyThreshold1 = x
	    self.send()

    def newCannyThreshold2(self,x):
	    self.capSetMsg.findPoly.cannyThreshold2 = x
	    self.send()

    def newCannyAperature(self,x):
	    self.capSetMsg.findPoly.cannyAperature = x
	    self.send()

    def newMinPerimeter(self,x):
	    self.capSetMsg.findPoly.minPerimeter = x
	    self.send()

    def newMinArea(self,x):
	    self.capSetMsg.findPoly.minArea = x
	    self.send()

    def newDeviationRatio(self,x):
	    self.capSetMsg.findPoly.deviationRatio = x
	    self.send()

if __name__ == "__main__":
		app = QApplication(sys.argv)

		sendMsg = sendCtrl()
	        sendMsg.capSetMsg.colorFilter.minHue = 0
	        sendMsg.capSetMsg.colorFilter.maxHue = 0
	        sendMsg.capSetMsg.colorFilter.minSat = 0
	        sendMsg.capSetMsg.colorFilter.maxSat = 0
	        sendMsg.capSetMsg.colorFilter.minVal = 0
	        sendMsg.capSetMsg.colorFilter.maxVal = 0
	        sendMsg.capSetMsg.colorFilter.beatPeriod = 0
	        sendMsg.capSetMsg.findPoly.cannyThreshold1 = 0
	        sendMsg.capSetMsg.findPoly.cannyThreshold2 = 0
	        sendMsg.capSetMsg.findPoly.cannyAperature = 0
	        sendMsg.capSetMsg.findPoly.minPerimeter = 0
	        sendMsg.capSetMsg.findPoly.minArea = 0
	        sendMsg.capSetMsg.findPoly.deviationRatio = 0 

		MainWindow = QMainWindow()
		ui = test_ui.Ui_MainWindow()
		ui.setupUi(MainWindow)


		ui.MinHueHorizontalSlider.connect(ui.MinHueHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMinHue)
		ui.MaxHueHorizontalSlider.connect(ui.MaxHueHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMaxHue)
		ui.MinSatHorizontalSlider.connect(ui.MinSatHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMinSat)
		ui.MaxSatHorizontalSlider.connect(ui.MaxSatHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMaxSat)
		ui.MinValHorizontalSlider.connect(ui.MinValHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMinVal)
		ui.MaxValHorizontalSlider.connect(ui.MaxValHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMaxVal)

	        ui.BeatPeriodHorizontalSlider.connect(ui.BeatPeriodHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newBeatPeriod)
	        ui.CannyThresh1HorizontalSlider.connect(ui.CannyThresh1HorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newCannyThreshold1)
	        ui.CannyThresh2HorizontalSlider.connect(ui.CannyThresh2HorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newCannyThreshold2)
	        ui.CannyAperatureHorizontalSlider.connect(ui.CannyAperatureHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newCannyAperature)
	        ui.ContourMinPerimeterHorizontalSlider.connect(ui.ContourMinPerimeterHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMinPerimeter)
	        ui.ContourMinAreaHorizontalSlider.connect(ui.ContourMinAreaHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newMinArea)
	        ui.ContourDeviationRatioHorizontalSlider.connect(ui.ContourDeviationRatioHorizontalSlider,SIGNAL("valueChanged(int)"),sendMsg.newDeviationRatio)
                # Set control initial values

		ui.MinHueHorizontalSlider.setValue(1)
		ui.MinHueHorizontalSlider.setValue(0)
		ui.MaxHueHorizontalSlider.setValue(255)

		ui.MinSatHorizontalSlider.setValue(1)
		ui.MinSatHorizontalSlider.setValue(0)
		ui.MaxSatHorizontalSlider.setValue(60)

		ui.MinValHorizontalSlider.setValue(60)
		ui.MaxValHorizontalSlider.setValue(255)

	        ui.CannyThresh1HorizontalSlider.setValue(1)
	        ui.CannyThresh2HorizontalSlider.setValue(3)
	        ui.CannyAperatureHorizontalSlider.setValue(3)
	        ui.ContourMinPerimeterHorizontalSlider.setValue(100)
	        ui.ContourMinAreaHorizontalSlider.setValue(500)
	        ui.ContourDeviationRatioHorizontalSlider.setValue(60)

	        ui.BeatPeriodHorizontalSlider.setValue(3)

		MainWindow.show()
		sys.exit(app.exec_())
