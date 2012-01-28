#!/usr/bin/python
#
#  Find 4 sided polygons from a camera
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
Import sys
from opencv.cv import *
from opencv.highgui import *
from time import time
from rx_config import *

# Select a camera to capture from
capture = cvCreateCameraCapture( 0 )

# Grab an initial frame to get the video size
frame = cvQueryFrame(capture)
frameSize = cvGetSize(frame)

# Allocate processing chain image buffers the same size as
# the video frame
hsvImage        = cvCreateImage( frameSize, cv.IPL_DEPTH_8U, 3 )
smooth          = cvCreateImage( frameSize, cv.IPL_DEPTH_8U, 3 )
inRange         = cvCreateImage( frameSize, cv.IPL_DEPTH_8U, 1 )
canny           = cvCreateImage( frameSize, cv.IPL_DEPTH_8U, 1 )
canny2          = cvCreateImage( frameSize, cv.IPL_DEPTH_8U, 1 )
frameAndinRange = cvCreateImage( frameSize, cv.IPL_DEPTH_8U, 3 )

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
        # video device -> image "frame"
        frame = cvQueryFrame (capture)

        if beat==0: 
            now = time()
            if before > 0 :
            	deltaTime = now - before
            before = now	
            
            # convert frame from Blue.Green.Red to Hue.Saturation.Value
            # image "frame" -> image "hsvImage"
            cvCvtColor(frame,hsvImage,CV_BGR2HSV)
        
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
            # images "frame" AND "inRange" -> image "frameAndinRange"
            cvZero(frameAndinRange)
            cvCopy(frame,frameAndinRange,inRange)
        
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
                            cv.cvDrawContours(frame, poly, CV_RGB(0,255,0), CV_RGB(0,255,255), 1, 4, 8)
        
            # display the captured frame, frameAndThresh, and canny images for debug
            cvShowImage('window-capture',frame)
            cvShowImage('thresh',frameAndinRange)
            cvShowImage('canny',canny)
        
            print 'i=%d delta_time=%f sat<%d %d<val' % ( i, deltaTime, 
                                                         getConfig().colorFilter.maxSat, 
                                                         getConfig().colorFilter.minVal )
        # wait 1 milliseconds for a key press
        k = cvWaitKey (1)
