#-------------------------------------------------------------------------------
# Updated:     2017-02-08
#
# Name:        get_mgmt_plan_attributes_json.py
#
# Purpose:     Geoprocessing service to get all attributes for a management_plan
#              polygon that are needed in the PFMWM from related records in PFMM.
#
# Author:      Jeff Reinhart
#
# Created:     2017-02-08
#-------------------------------------------------------------------------------

import arcpy
import module_connection_properties, module_pfmm_get

def getMgmtPlanAttributesJSON(maGlobalId):
    # Connection properties
    connectionProperties = module_connection_properties.clsConnectionProperties()
    db = connectionProperties.database
    fd = connectionProperties.featureDataset
    tbPref = connectionProperties.tablePrefix

    # Output variable
    returnString = ''

    # Get management_plan object
    mpObj = module_pfmm_get.cls_management_plan(maGlobalId)

    # Get related ownership_block object
    obObj = module_pfmm_get.cls_ownership_block(mpObj.ownership_block_guid)

    # Build output string as JSON
    returnString = obObj.globalid

    # Return
    return returnString

def main():
    # Environment
    arcpy.env.overwriteOutput = True

    # Inputs
    maGlobalId = arcpy.GetParameterAsText(0)

    # Run
    outputText = ''
    if maGlobalId == 'none':
        # Allowing option entry on tool to prevent a default value from being set.
        outputText = 'error: no global id provided'
    else:
        outputText = getMgmtPlanAttributesJSON(maGlobalId)

    # Set output
    arcpy.SetParameterAsText(1, outputText)

if __name__ == '__main__':
    main()
