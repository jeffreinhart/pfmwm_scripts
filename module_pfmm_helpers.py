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