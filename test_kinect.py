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
from rx_config import *
from freenect import sync_get_depth as get_depth, sync_get_video as get_video
# TBD figure out what's in opencv.cv vs. cv and are they compatible?
# from cv import ShowImage as CV_ShowImage 
import numpy as np

# Select a camera to capture from
##capture = cvCreateCameraCapture( 0 )

# Grab an initial frame to get the video size
##frame = cvQueryFrame(capture)
global depth, rgb
(depth,_), (rgb,_) = get_depth(), get_video()

rgbFrameSize = cvGetSize(rgb)
depthSize = cvGetSize(depth)
print 'rgbSize = %d %d' % (rgbFrameSize.width, rgbFrameSize.height)
print 'depthSize = %d %d' % (depthSize.width, depthSize.height)


# Allocate processing chain image buffers the same size as
# the video frame
rgbFrame        = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 3 )
hsvImage        = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 3 )
smooth          = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 3 )
inRange         = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 1 )
canny           = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 1 )
canny2          = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 1 )
rgbFrameAndinRange = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_8U, 3 )
depth1           = cvCreateImage( rgbFrameSize, cv.IPL_DEPTH_16U, 1 )

# allocate memory for contours
storContours = cv.cvCreateMemStorage(0);
storContours2 = cv.cvCreateMemStorage(0);

period = 0
i = 0
now = 0
before = 0
deltaTime = 0
beat=0

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
        
        # Build a two panel color image
        #d3 = np.dstack((depth,depth,depth)).astype(np.uint8)
        #da = np.hstack((d3,rgbFrame))
        
        # Simple Downsample
        #cvShowImage('both',adaptors.NumPy2Ipl(np.array(da[::2,::2,::-1])))

        #depth0 = depth.astype(np.uint16)
        #depth1 = adaptors.NumPy2Ipl(depth)
        depth1 = depth

        x = 0
        y = 0
        rawDisparity = cv.cvGet2D( depth1, y, x )[0]
        distance1a = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.3937
        distance2a = (100.0 / (-0.00307*rawDisparity+3.33))*0.3937

        x = 320
        y = 0
        rawDisparity = cv.cvGet2D( depth1, y, x )[0]
        distance1b = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.3937
        distance2b = (100.0 / (-0.00307*rawDisparity+3.33))*0.3937

        x = 631
        y = 0
        rawDisparity = cv.cvGet2D( depth1, y, x )[0]
        distance1c = (12.36 * math.tan(rawDisparity / 2842.5 + 1.1863))*0.3937
        distance2c = (100.0 / (-0.00307*rawDisparity+3.33))*0.3937
        rgbFrame = adaptors.NumPy2Ipl(rgb)
        print "c=%d r=%d depth=%d in=%f in=%f in=%f" % ( x, y, rawDisparity, distance1a, distance1b, distance1c
 ) 

        #cvCvtColor(rgbFrame,rgbFrame,CV_RGB2BGR)

        if beat==0:
            now = time()
            if before > 0 :
            	deltaTime = now - before
            before = now	
            
            # convert frame from Blue.Green.Red to Hue.Saturation.Value
            # image "rgbFrame" -> image "hsvImage"
            cvCvtColor(rgbFrame,hsvImage,CV_BGR2HSV)
        
            # gaussian smooth the Hue.Saturation.Value image
            # image "hsvImage" -> image "smooth"
            smoothSize=9
            cvSmooth(hsvImage,smooth,CV_GAUSSIAN,smoothSize,smoothSize)
        
        
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
            cvInRangeS(smooth,minHSV,maxHSV,inRange)
        
            # make a debug image whose pixels are 
            # frame when minHSV < threshold < maxHSV
            # and (0,0,0) "Black" elsewhere
            # images "rgbFrame" AND "inRange" -> image "rgbFrameAndinRange"
            cvZero(rgbFrameAndinRange)
            cvCopy(rgbFrame,rgbFrameAndinRange,inRange)
        
            # run Canny edge detection on inRange
            # image "inRange" -> image "canny"
            cvCanny(inRange,canny,getConfig().findPoly.cannyThreshold1,
                    getConfig().findPoly.cannyThreshold2,
                    getConfig().findPoly.cannyAperature)
        
            # copy canny to canny2 because cvFindContours will overwrite canny2
            # image "canny" -> image "canny2"
            cvCopy(canny,canny2)
        
            # Find all contours in the canny edged detected image
            # image "canny2" -> list of contours: "cont"
            nb_contours, contourList = cv.cvFindContours (canny2,
                                                   storContours,
                                                   cv.sizeof_CvContour,
                                                   cv.CV_RETR_LIST,
                                                   cv.CV_CHAIN_APPROX_SIMPLE,
                                                   cv.cvPoint (0,0))
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
                            cv.cvDrawContours(rgbFrame, poly, CV_RGB(0,255,0), CV_RGB(0,255,255), 1, 4, 8)
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
                            
        
            # display the captured frame, rgbFrameAndThresh, and canny images for debug
            cvShowImage('window-capture',rgbFrame)
            cvShowImage('thresh',rgbFrameAndinRange)
            cvShowImage('canny',canny)
            cvShowImage('depth',depth1)

            #print 'i=%d delta_time=%f sat<%d %d<val' % ( i, deltaTime, 
            #                                             getConfig().colorFilter.maxSat, 
            #                                             getConfig().colorFilter.minVal )
    # wait 1 milliseconds for a key press
    k = cvWaitKey (1)
