#-------------------------------------------------------------------------------
# Updated:     2017-02-10
#
# Name:        module_pfmm_helpers.py
# Purpose:     Helper functions for PFMWM scripts.
#
# Author:      Jeff Reinhart
#
# Created:     2017-02-10
#-------------------------------------------------------------------------------

import arcpy, os, sys, datetime, module_pfmm_get

def passNull(fieldValue, propertyValue):
    if fieldValue != None:
        return fieldValue
    else:
        return propertyValue

def dateToMDYYYY(dateIn):
    if dateIn == datetime.datetime(1900,1,1,0,0,0) or dateIn is None:
        dateStr = ''
    else:
        dateStr = "{dt.month}/{dt.day}/{dt.year}".format(dt = dateIn)
    return dateStr