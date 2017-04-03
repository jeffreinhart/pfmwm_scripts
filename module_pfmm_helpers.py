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
from calendar import isleap

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

def addYears(d, years):
    # copied from stack overflow
    new_year = d.year + years
    try:
        return d.replace(year=new_year)
    except ValueError:
        if (d.month == 2 and d.day == 29 and # leap day
            isleap(d.year) and not isleap(new_year)):
            return d.replace(year=new_year, day=28)
        raise