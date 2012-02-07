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
import socket
import select
import test_pb2

#UDP_IP="127.0.0.1"
UDP_IP="0.0.0.0"
UDP_PORT=5005

capSetMsg = test_pb2.captureSettings()

def setOptions(f,v):
 if f==0:
    capSetMsg.colorFilter.minHue = v
 elif f==1:
    capSetMsg.colorFilter.maxHue = v
 elif f==2:  
    capSetMsg.colorFilter.minSat = v
 elif f==3:  
    capSetMsg.colorFilter.maxSat = v
 elif f==4:  
    capSetMsg.colorFilter.minVal = v
 elif f==5:  
    capSetMsg.colorFilter.maxVal = v
 elif f==7:  
     capSetMsg.findPoly.cannyThreshold1 = v
 elif f==8:  
     capSetMsg.findPoly.cannyThreshold2 = v
 elif f==9:  
     capSetMsg.findPoly.cannyAperature = v
 elif f==10: 
     capSetMsg.findPoly.minPerimeter = v
 elif f==11: 
     capSetMsg.findPoly.minArea = v
 elif f==12: 
     capSetMsg.findPoly.deviationRatio = v
 elif f==13:  
     capSetMsg.colorFilter.beatPeriod = v
     period = capSetMsg.colorFilter.beatPeriod
 elif f==14: 
     capSetMsg.videoOut = v  


sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
sock.bind( (UDP_IP,UDP_PORT) )
input = [sock]

def getConfig():
    return capSetMsg

def readConfig():
    dataInQueue = 1
    while dataInQueue:
	    dataInQueue = 0
	    inputready,outputready,exceptready = select.select(input,[],[],0.00001)
	    for s in inputready:		    
                    print 's'
		    if s == sock:
                            print 'select returned sock'
			    data = s.recv(4096)
			    if data:
                                dataInQueue = 1
                                print 'data=%s=' % ( data )
                                fields = data.strip().split ('>', 2 )
                                print fields
                                for i in fields:
                                    print 'i=%s=' % ( i )
                                f = int( fields[0] )
                                v = int( fields[1] )
                                print 'f=%d v=%d' % ( f, v )
                                setOptions( f, v )

