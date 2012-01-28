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

UDP_IP="127.0.0.1"
UDP_PORT=5005

capSetMsg = test_pb2.captureSettings()

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
		    if s == sock:
			    data = s.recv(4096)
			    if data:
				    dataInQueue = 1
				    capSetMsg.ParseFromString(data)
                                    period = capSetMsg.colorFilter.beatPeriod

