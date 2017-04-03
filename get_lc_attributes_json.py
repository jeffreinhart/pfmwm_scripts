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

def getLcAttributesJSON(lcGid):
    # Connection properties
    connectionProperties = module_connection_properties.clsConnectionProperties()
    db = connectionProperties.database
    fd = connectionProperties.featureDataset
    tbPref = connectionProperties.tablePrefix

    # Dictionary to pass to JSON output
    attrDict = dict()

    # Get party_contact.landcontact
    pcLoObj = module_pfmm_get.cls_party_contact(lcGid)

    # Build list for html for record attributes
    attrDict["html"] = [
        {
            "type": "hidden",
            "name": "party_contacts.globalid.landcontact",
            "value": pcLoObj.globalid
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
        }
    ]

    # Get stewardship plan info through owner block
    attrDict["mpDgv"] = []
    pcLoChildTables = module_pfmm_get.relatedRecordGlobalIds('party_contacts', lcGid)
    pcobGidList = pcLoChildTables[tbPref+'party_cont_own_blks']
    obGidList = []
    for pcobGid in pcobGidList:
        pcobObj = module_pfmm_get.cls_party_cont_own_blks(pcobGid)
        obGidList.append(pcobObj.ownership_block_guid)
    for obGid in obGidList:
        # start temporary dict
        tempMpDict = dict()
        isOwner = "No" # assume not owner until confirmed
        countyList = []
        # get ownership_block and child tables
        obObj = module_pfmm_get.cls_ownership_block(obGid)
        obChildTables = module_pfmm_get.relatedRecordGlobalIds('ownership_blocks', obGid)
        # get ownership parcels
        opGidList = obChildTables[tbPref+'ownership_parcels']
        for opGid in opGidList:
            # get ownership_parcel and child tables
            opObj = module_pfmm_get.cls_ownership_parcel(opGid)
            opChildTables = module_pfmm_get.relatedRecordGlobalIds('ownership_parcels', opGid)
            # append county to list
            counObj = module_pfmm_get.cls_county_coun(opObj.coun)
            countyList.append(counObj.cty_name)
            # check if owner is same
            pcopGidList = opChildTables[tbPref+'party_cont_own_prcl']
            pcOnwerGid = module_pfmm_get.lastPcopPcGid(pcopGidList)
            if pcOnwerGid == lcGid:
                isOwner = "Yes"
        # county list to string
        tempMpDict["counties"] = ", ".join(sorted(set(countyList)))
        # get management plans
        mpGidList = obChildTables[tbPref+'management_plans']
        for mpGid in mpGidList:
            mpObj = module_pfmm_get.cls_management_plan(mpGid)
            tempMpDict["management_plans.globalid"] = mpGid
            tempMpDict["management_plans.plan_date"] = module_pfmm_helpers.dateToMDYYYY(mpObj.plan_date)
            tempMpDict["management_plans.acres_plan"] = mpObj.acres_plan
            expirationDate = module_pfmm_helpers.addYears(mpObj.plan_date, 10)
            tempMpDict["expiration_date"] = module_pfmm_helpers.dateToMDYYYY(expirationDate)
            # get plan writer
            pcPwObj = module_pfmm_get.cls_party_contact(mpObj.party_contact_guid)
            tempMpDict["plan_writer"] = "{0} {1} - {2}".format(
                pcPwObj.person_first_name,
                pcPwObj.person_last_name,
                pcPwObj.business_name)
            # trs from owner block
            tempMpDict["pls_section"] = "T{0}N-R{1}{2}-S{3}".format(
                obObj.town,
                obObj.range,
                obObj.rdir,
                obObj.sect)
            # get registration status
            if mpObj.registered_date != datetime.datetime(1900,1,1,0,0,0):
                tempMpDict["registered"] = "Yes"
            else:
                tempMpDict["registered"] = "No"
            # add if is owner
            tempMpDict["is_owner"] = isOwner
        # add dict to attrDict
        attrDict["mpDgv"].append(tempMpDict)

    # Get contact_events
    attrDict["ceDgv"] = []
    contactEventGidList = pcLoChildTables[tbPref+'contact_events.party_contact_1_guid']
    for contactEventGid in contactEventGidList:
        # start temporary dict
        tempCeDict = dict()
        # get object
        contactEventObj = module_pfmm_get.cls_contact_events(contactEventGid)
        # add values to temp dict
        tempCeDict["contact_events.globalid"] = contactEventGid
        tempCeDict["contact_events.contact_date"] = module_pfmm_helpers.dateToMDYYYY(contactEventObj.contact_date)
        tempCeDict["contact_events.subject"] = contactEventObj.subject
        tempCeDict["contact_events.contact_event_type"] = contactEventObj.contact_event_type
        tempCeDict["contact_events.summary"] = contactEventObj.summary
        tempCeDict["contact_events.notes"] = contactEventObj.notes
        # get DNR party contact and add
        pcDnrObj = module_pfmm_get.cls_party_contact(contactEventObj.party_contact_2_guid)
        tempCeDict["dnr_staff"] = "{0} {1}".format(
            pcDnrObj.person_first_name,
            pcDnrObj.person_last_name)
        # get Partner Forester party contact and add
        pcPfObj = module_pfmm_get.cls_party_contact(contactEventObj.party_contact_3_guid)
        tempCeDict["partner_forester"] = "{0} {1}".format(
            pcPfObj.person_first_name,
            pcPfObj.person_last_name)
        attrDict["ceDgv"].append(tempCeDict)

    # Get project_areas
    attrDict["paDgv"] = []
    paGidList = pcLoChildTables[tbPref+'project_areas.party_contact_applicant_guid']
    for paGid in paGidList:
        # start temporary dict
        tempPaDict = dict()
        # get objects
        paObj = module_pfmm_get.cls_project_area(paGid)
        paChildTables = module_pfmm_get.relatedRecordGlobalIds('project_areas', paGid)
        # add values to temp dict
        tempPaDict["project_areas.globalid"] = paGid
        tempPaDict["project_areas.anticipated_project_start_date"] = module_pfmm_helpers.dateToMDYYYY(paObj.anticipated_project_start_date)
        tempPaDict["project_areas.total_cost_share_approved"] = "{0:.2f}".format(paObj.total_cost_share_approved)
        tempPaDict["project_areas.practices_certified_date"] = module_pfmm_helpers.dateToMDYYYY(paObj.practices_certified_date)
        # get plan writer and add
        pcWriterObj = module_pfmm_get.cls_party_contact(paObj.party_contact_writer_guid)
        tempPaDict["writer"] = "{0} {1}".format(
            pcWriterObj.person_first_name,
            pcWriterObj.person_last_name)
        # get approver and add
        pcApproverObj = module_pfmm_get.cls_party_contact(paObj.party_contact_approver_guid)
        tempPaDict["approver"] = "{0} {1}".format(
            pcApproverObj.person_first_name,
            pcApproverObj.person_last_name)
        # get string list of project practices
        ppList = []
        ppGidList = paChildTables[tbPref+'project_practices']
        for ppGid in ppGidList:
            ppObj = module_pfmm_get.cls_project_practice(ppGid)
            ppList.append(ppObj.practice)
        tempPaDict["practices"] = ", ".join(sorted(set(ppList)))
        # append temp dict to out attrDict
        attrDict["paDgv"].append(tempPaDict)

    # Dictionary to JSON string (have to do this instead of just str() because of ' and ")
    jsonString = json.dumps(attrDict)

    # Return
    return jsonString

def main():
    # Environment
    arcpy.env.overwriteOutput = True

    # Inputs
    lcGid = arcpy.GetParameterAsText(0)

    # Run
    outputText = ''
    if lcGid == 'none':
        # Allowing option entry on tool to prevent a default value from being set.
        outputText = 'error: no global id provided'
    else:
        outputText = getLcAttributesJSON(lcGid)

    # Set output
    arcpy.SetParameterAsText(1, outputText)

if __name__ == '__main__':
    main()
