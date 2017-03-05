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

import arcpy, json
from collections import OrderedDict
import module_connection_properties, module_pfmm_get, module_pfmm_helpers

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

    # Get party_contact.planwriter
    pcPwObj = module_pfmm_get.cls_party_contact(mpObj.party_contact_guid)

    # Get related ownership_block object
    obObj = module_pfmm_get.cls_ownership_block(mpObj.ownership_block_guid)

    # Get ownership parcels
    obChildTbls = module_pfmm_get.relatedRecordGlobalIds('ownership_blocks', obObj.globalid)
    opGids = obChildTbls[tbPref+'ownership_parcels']

    # Get party_cont_own_prcl
    pcopGids = []
    for opGid in opGids:
        opObj = module_pfmm_get.cls_ownership_parcel(opGid)
        opChildTbls = module_pfmm_get.relatedRecordGlobalIds('ownership_parcels', opObj.globalid)
        pcopGids += opChildTbls[tbPref+'party_cont_own_prcl']

    # Get party_contact.landcontact
    pcLoGid = module_pfmm_get.lastPcopPcGid(pcopGids)
    pcLoObj = module_pfmm_get.cls_party_contact(pcLoGid)

    # Build list for html
    attrDict = dict()
    attrDict["html"] = [
        {
            "type": "hidden",
            "name": "party_contacts.globalid.landcontact",
            "value": pcLoObj.globalid
        },
        {
            "type": "hidden",
            "name": "party_contacts.globalid.planwriter",
            "value": pcPwObj.globalid
        },
        {
            "type": "hidden",
            "name": "managment_plans.globalid",
            "value": mpObj.globalid
        },
        {
            "caption": "Land Contact First Name",
            "type": "text",
            "name": "party_contacts.person_first_name.landcontact",
            "value": pcLoObj.person_first_name
        },
        {
            "caption": "Land Contact Last Name",
            "type": "text",
            "name": "party_contacts.person_last_name.landcontact",
            "value": pcLoObj.person_last_name
        },
        {
            "caption": "Land Contact Partner First Name",
            "type": "text",
            "name": "party_contacts.spouse_name.landcontact",
            "value": pcLoObj.spouse_name
        },
        {
            "caption": "Land Contact Business Name",
            "type": "text",
            "name": "party_contacts.business_name.landcontact",
            "value": pcLoObj.business_name
        },
        {
            "caption": "Land Contact Street Address",
            "type": "text",
            "name": "party_contacts.address_line_1.landcontact",
            "value": pcLoObj.address_line_1
        },
        {
            "caption": "Land Contact City",
            "type": "text",
            "name": "party_contacts.city.landcontact",
            "value": pcLoObj.city
        },
        {
            "caption": "Land Contact State",
            "type": "text",
            "name": "party_contacts.state_provice_short_name_code.landcontact",
            "value": pcLoObj.state_provice_short_name_code
        },
        {
            "caption": "Land Contact Zip",
            "type": "text",
            "name": "party_contacts.postal_code.landcontact",
            "value": pcLoObj.postal_code
        },
        {
            "caption": "Land Contact Do Not Mail",
            "type": "text",
            "name": "party_contacts.do_not_mail.landcontact",
            "value": pcLoObj.do_not_mail
        },
        {
            "caption": "Land Contact Phone 1",
            "type": "text",
            "name": "party_contacts.phone_line_1.landcontact",
            "value": pcLoObj.phone_line_1
        },
        {
            "caption": "Plan Writer First Name",
            "type": "text",
            "name": "party_contacts.person_first_name.planwriter",
            "value": pcPwObj.person_first_name
        },
        {
            "caption": "Plan Writer Last Name",
            "type": "text",
            "name": "party_contacts.person_last_name.planwriter",
            "value": pcPwObj.person_last_name
        },
        {
            "caption": "Plan Writer Type",
            "type": "text",
            "name": "party_contacts.business_type.planwriter",
            "value": pcPwObj.business_type
        },
        {
            "caption": "Plan Date",
            "type": "text",
            "name": "management_plans.plan_date",
            "datepicker": {
                "minDate": "01/01/1900"
            },
            "value": module_pfmm_helpers.dateToMDYYYY(mpObj.plan_date)
        },
        {
            "caption": "Plan Status",
            "type": "text",
            "name": "management_plans.status",
            "value": mpObj.status
        },
        {
            "caption": "Grant Funding",
            "type": "text",
            "name": "management_plans.grant_id",
            "value": mpObj.grant_id
        },
        {
            "caption": "Plan Acres",
            "type": "number",
            "name": "management_plans.acres_plan",
            "value": mpObj.acres_plan
        },
        {
            "caption": "Registation Number",
            "type": "text",
            "name": "management_plans.reg_num",
            "value": mpObj.reg_num
        },
        {
            "caption": "Registration Date",
            "type": "text",
            "name": "management_plans.registered_date",
            "datepicker": {
                "minDate": "01/01/1900"
            },
            "value": module_pfmm_helpers.dateToMDYYYY(mpObj.registered_date)
        }
    ]

    # Dictionary to JSON string (have to do this instead of just str() because of ' and ")
    jsonString = json.dumps(attrDict)

    # Return
    return jsonString

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
