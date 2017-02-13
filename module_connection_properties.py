#-------------------------------------------------------------------------------
# Updated:     2017-02-08
#
# Name:        module_connection_properties.py
# Purpose:     Class for connection properties.
#
# Author:      Jeff Reinhart
#
# Created:     2017-02-08
#-------------------------------------------------------------------------------

class clsConnectionProperties:
    '''Connection properties for PFMWM.'''

    def __init__(self):
        # Set connection properties
        self.database = r'P:\FOR\FORIST\PFM\prod10_2\dnrgdrs-prod1-pg-dc-pfmm.sde'
        self.featureDataset = 'pfmm.pfmm.spatial'
        self.tablePrefix = 'pfmm.pfmm.'