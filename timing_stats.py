#!/usr/bin/python
#
#  timing stats
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
#
# Import Libraries
#
from time import time

timingObjectList = []

class timing:
    def __init__(self,nameStr,filterSteps):
        self.name = nameStr
        self.filter = filterSteps
        self.min = float("inf")
        self.max = float("-inf")
        self.movingAvg = 0.0
        self.lastTime = 0.0
        timingObjectList.append( self )

    def measureDeltaTime(self, old ):
        now = time()
        if old.lastTime > 0.0:
            deltaTime = now - old.lastTime
            if deltaTime < self.min:
                self.min = deltaTime
            if deltaTime > self.max:
                self.max = deltaTime
            self.movingAvg = ( self.movingAvg * (self.filter-1) + deltaTime ) / self.filter
        self.lastTime = now

    def printStats(self):
        print '%s min=%f < avg=%f < max=%f' % ( self.name, self.min, self.movingAvg, self.max )

def printStats():
    for i in timingObjectList:
        i.printStats()
