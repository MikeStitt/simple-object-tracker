#!/usr/bin/python
#
#  Find 4 sided polygons from a kinect
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
import sys
import math
from opencv.cv import *
from opencv import adaptors
from opencv.highgui import *
from time import time
from freenect import sync_get_depth as get_depth, sync_get_video as get_video, init
import numpy as np

from rx_config import *
from timing_stats import *

#initialize the camera
ctx = init()

# Grab an initial frame to get the video size
global depth, rgb
(depth,_), (rgb,_) = get_depth(), get_video()

rgbFrameSize = cvGetSize(rgb)
depthSize = cvGetSize(depth)
dwnFrameSize = cvSize(rgbFrameSize.width / 2, rgbFrameSize.height / 2)
dwnDepthSize = cvSize(depthSize.width / 2, depthSize.height / 2)

print 'rgbSize = %d %d' % (rgbFrameSize.width, rgbFrameSize.height)
print 'depthSize = %d %d' % (depthSize.width, depthSize.height)


# Allocate processing chain image buffers the same size as
# the video frame
rgbFrame        = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 3 )
depthFrame      = cvCreateImage( depthSize,    cv.IPL_DEPTH_16U, 3 )
dwnDepthFrame   = cvCreateImage( dwnDepthSize,    cv.IPL_DEPTH_16U, 1 )#tbd 3 or 1?
dwnFrame        = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_8U, 3 )
hsvImage        = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_8U, 3 )
smooth          = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_8U, 3 )
inRange         = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_8U, 1 )
canny           = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_8U, 1 )
canny2          = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_8U, 1 )
rgbFrameAndinRange = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_8U, 3 )
#depth1           = cvCreateImage( dwnFrameSize, cv.IPL_DEPTH_16U, 1 )

# allocate memory for contours
storContours = cv.cvCreateMemStorage(0);
storContours2 = cv.cvCreateMemStorage(0);

period = 0
i = 0
now = 0
before = 0
deltaTime = 0
beat=0

frameToFrame = timing( 'frame to frame', 15)
beatToBeat = timing( 'beat to beat', 15)
convertColorTime = timing( 'convert color', 15 )
pyrDwnTime = timing( 'pyrDown', 15 )
smoothTime= timing( 'smooth', 15 )
inRangeTime = timing( 'in range', 15 )
copy1Time= timing( 'copy1', 15 )
cannyTime = timing( 'canny', 15 )
copy2Time = timing( 'copy2', 15 )
findContoursTime = timing( 'find contours', 15 )
procContoursTime = timing( 'process contours', 15 )
showImageTime = timing( 'show image', 15 )
frameProcTime = timing( 'frameProcTime', 15 )

while True:
    # process beat frame out of "period" beats
    i = i + 1
    readConfig()
    period = getConfig().colorFilter.beatPeriod
    beat=beat+1
    if beat >= period:
        beat=0

    if period>0:
        # grab a video frame
        # video device -> image "rgbFrame"
        # Get a fresh frame
        (depth,_), (rgb,_) = get_depth(), get_video()
        
        frameToFrame.measureDeltaTime(frameToFrame)

        # Build a two panel color image
        #d3 = np.dstack((depth,depth,depth)).astype(np.uint8)
        #da = np.hstack((d3,rgbFrame))
        
        # Simple Downsample
        #cvShowImage('both',adaptors.NumPy2Ipl(np.array(da[::2,::2,::-1])))

        #depth0 = depth.astype(np.uint16)
        #depth1 = adaptors.NumPy2Ipl(depth)
        #depth1 = depth

        if 0:
            x = 0
            y = 0
            rawDisparity = cv.cvGet2D( depth, y, x )[0]
            distance1a = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.3937
            distance2a = (100.0 / (-0.00307*rawDisparity+3.33))*0.3937

            x = 320
            y = 0
            rawDisparity = cv.cvGet2D( depth, y, x )[0]
            distance1b = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.3937
            distance2b = (100.0 / (-0.00307*rawDisparity+3.33))*0.3937

            x = 631
            y = 0
            rawDisparity = cv.cvGet2D( depth, y, x )[0]
            distance1c = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.3937
            distance2c = (100.0 / (-0.00307*rawDisparity+3.33))*0.3937
            print "c=%d r=%d depth=%d in=%f in=%f in=%f" % ( x, y, rawDisparity, distance1a, distance1b, distance1c ) 

        if beat==0:
            beatToBeat.measureDeltaTime(beatToBeat)
            
            # convert frame from Blue.Green.Red to Hue.Saturation.Value
            # image "rgbFrame" -> image "hsvImage"

            rgbFrame = adaptors.NumPy2Ipl(rgb)
            #depthFrame = adaptors.NumPy2Ipl(depth)

            cvPyrDown(rgbFrame,dwnFrame)
            cvPyrDown(depth,dwnDepthFrame)
            pyrDwnTime.measureDeltaTime(beatToBeat)

            cvCvtColor(dwnFrame,hsvImage,CV_BGR2HSV)
            convertColorTime.measureDeltaTime(pyrDwnTime)

            # gaussian smooth the Hue.Saturation.Value image
            # image "hsvImage" -> image "smooth"
            #smoothSize=9
            #cvSmooth(hsvImage,smooth,CV_GAUSSIAN,smoothSize,smoothSize)
            #smoothTime.measureDeltaTime(convertColorTime)
        
        
            # find the target in the range:  minHSV < target < maxHSV
            # image "smooth" -> image "inRange"
            minHSV = cvScalar( getConfig().colorFilter.minHue-1, 
                               getConfig().colorFilter.minSat-1, 
                               getConfig().colorFilter.minVal-1, 
                               0 )
            maxHSV = cvScalar( getConfig().colorFilter.maxHue+1, 
                               getConfig().colorFilter.maxSat+1,
                               getConfig().colorFilter.maxVal+1, 
                               0 )
            print '%d<%d  %d<%d %d<%d' % ( getConfig().colorFilter.minHue, getConfig().colorFilter.maxHue, getConfig().colorFilter.minSat, getConfig().colorFilter.maxSat, getConfig().colorFilter.minVal, getConfig().colorFilter.maxVal )
            cvInRangeS(hsvImage,minHSV,maxHSV,inRange)
            inRangeTime.measureDeltaTime(convertColorTime)
        
            # make a debug image whose pixels are 
            # frame when minHSV < threshold < maxHSV
            # and (0,0,0) "Black" elsewhere
            # images "rgbFrame" AND "inRange" -> image "rgbFrameAndinRange"
            cvZero(rgbFrameAndinRange)
            cvCopy(dwnFrame,rgbFrameAndinRange,inRange)
            copy1Time.measureDeltaTime(inRangeTime)
        
            # run Canny edge detection on inRange
            # image "inRange" -> image "canny"
            print "t1=%d t2=%d a=%d" % (getConfig().findPoly.cannyThreshold1, getConfig().findPoly.cannyThreshold2, getConfig().findPoly.cannyAperature )
            cvCanny(inRange,canny,getConfig().findPoly.cannyThreshold1,
                    getConfig().findPoly.cannyThreshold2,
                    getConfig().findPoly.cannyAperature)
            cannyTime.measureDeltaTime(copy1Time)
        
            # copy canny to canny2 because cvFindContours will overwrite canny2
            # image "canny" -> image "canny2"
            cvCopy(canny,canny2)
            copy2Time.measureDeltaTime(cannyTime)
        
            # Find all contours in the canny edged detected image
            # image "canny2" -> list of contours: "cont"
            nb_contours, contourList = cv.cvFindContours (canny2,
                                                   storContours,
                                                   cv.sizeof_CvContour,
                                                   cv.CV_RETR_LIST,
                                                   cv.CV_CHAIN_APPROX_SIMPLE,
                                                   cv.cvPoint (0,0))

            findContoursTime.measureDeltaTime(copy2Time)
            # if we found a list of contours
            if contourList:
                # look at each contour
                # countourList(n) -> contour
                for contour in contourList.hrange():
                    # keep contours greater than the minimum perimeter
                    perimiter = cvContourPerimeter(contour)
                    if perimiter > getConfig().findPoly.minPerimeter :
                        # approximate the contours into polygons 
                        poly = cvApproxPoly( contour, sizeof_CvContour, storContours2,
                                             CV_POLY_APPROX_DP,
                                             perimiter*(getConfig().findPoly.deviationRatio/1000.0), 0 );   
                        # good polygons should have 4 vertices after approximation                        
                        # relatively large area (to filter out noisy contours)                              
                        # and be convex.                                                                    
                        # Note: absolute value of an area is used because                                   
                        # area may be positive or negative - in accordance with the                         
                        # contour orientation                                                             
                        if ( poly.total==4 
                        and abs(cvContourArea(poly)) > getConfig().findPoly.minArea 
                        and cvCheckContourConvexity(poly) ):
                            # draw the good polygons on the frame
                            cv.cvDrawContours(dwnFrame, poly, CV_RGB(0,255,0), CV_RGB(0,255,255), 1, 4, 8)
                            # is polyOnImage ?
                            polyOnImage = True
                            for i in range(4):
                                if ( (poly[i].x <0) or (poly[i].x >= depthSize.width)):
                                    polyOnImage = False
                                if ( (poly[i].y) <0 or (poly[i].y >= depthSize.height)):
                                    polyOnImage = False
                            if 0:
                                #if polyOnImage:
                                for i in range(4):
                                    print 'i=%d x=%d y=%d' % ( i, poly[i].x, poly[i].y )
                                    rawDisparity = cv.cvGet2D( depth1, poly[i].y, poly[i].x )[0]
                                    distance1 = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.3937
                                    distance2 = (100.0 / (-0.00307*rawDisparity+3.33))*0.3937
                                    print "corner=%d c=%d r=%d depth=%d cm=%f cm=%f" % ( i, poly[i].x, poly[i].y, rawDisparity, distance1, distance2 )         

            procContoursTime.measureDeltaTime(findContoursTime)
            # display the captured frame, rgbFrameAndThresh, and canny images for debug
            cvShowImage('window-capture',dwnFrame)
            cvShowImage('thresh',rgbFrameAndinRange)
            cvShowImage('canny',canny)
            cvShowImage('depth',dwnDepthFrame)
            showImageTime.measureDeltaTime(procContoursTime)

            #print 'i=%d' % ( i )
            x = 160
            y = 120
            rawDisparity = cv.cvGet2D( dwnDepthFrame, y, x )[0]
            distance1b = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.39
            print "col=%d row=%d %f in" % (x, y, distance1b)

            frameProcTime.measureDeltaTime(frameToFrame)


    # wait 1 milliseconds for a key press
    k = cvWaitKey(1)
    if k > -1 :
        printStats()
        quit()
