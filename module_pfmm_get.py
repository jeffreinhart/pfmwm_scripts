#-------------------------------------------------------------------------------
# Updated:     2017-02-10
#
# Name:        module_pfmm_get.py
# Purpose:     Functions and classes for getting records from PFMM tables.
#              Record classes are cls_table_name (less the s).
#
# Author:      Jeff Reinhart
#
# Created:     2017-02-10
#-------------------------------------------------------------------------------

import arcpy, os, sys, datetime
import module_connection_properties, module_pfmm_helpers

connectionProperties = module_connection_properties.clsConnectionProperties()
db = connectionProperties.database
fd = connectionProperties.featureDataset
tbPref = connectionProperties.tablePrefix

def relatedRecordGlobalIds(tableName, globalId):
    '''Returns dictionary of tables with key as table name and value as list of
    related globalid values.'''
    # tables
    county_coun = os.path.join(db, tbPref+'county_coun')
    contact_events = os.path.join(db, tbPref+'contact_events')
    party_cont_own_prcl = os.path.join(db, tbPref+'party_cont_own_prcl')
    party_cont_own_blks = os.path.join(db, tbPref+'party_cont_own_blks')
    pls_sections_extents = os.path.join(db, tbPref+'pls_sections_extents')
    party_contacts = os.path.join(db, tbPref+'party_contacts')
    # feature datasets
    ownership_parcels = os.path.join(db, fd, tbPref+'ownership_parcels')
    ownership_blocks = os.path.join(db, fd, tbPref+'ownership_blocks')
    management_plans = os.path.join(db, fd, tbPref+'management_plans')
    project_practices = os.path.join(db, fd, tbPref+'project_practices')
    project_areas = os.path.join(db, fd, tbPref+'project_areas')
    # parent immediate child dictionary as key = parent, value =
    # either table_name or [table_name, field_name] for multiple foreign keys
    picDict = {
        'project_areas': [
            project_practices
            ],
        'ownership_blocks': [
            ownership_parcels,
            party_cont_own_blks,
            contact_events,
            management_plans,
            project_areas
            ],
        'ownership_parcels': [
            party_cont_own_prcl
            ],
        'party_contacts': [
            party_cont_own_prcl,
            party_cont_own_blks,
            [contact_events, 'party_contact_1_guid'],
            [contact_events, 'party_contact_2_guid'],
            [contact_events, 'party_contact_3_guid'],
            [project_areas, 'party_contact_applicant_guid'],
            [project_areas, 'party_contact_writer_guid'],
            [project_areas, 'party_contact_entered_guid'],
            [project_areas, 'party_contact_approver_guid'],
            [project_areas, 'party_contact_certifier_guid']
            ]
        }
    # get list of globalids for each child table
    childTablesDict = {}
    for childTable in picDict[tableName]:
        gidList = []
        if isinstance(childTable, (list)):
            tablePath = childTable[0]
            fieldName = childTable[1]
            where = "{0} = '{1}'".format(fieldName, globalId)
            with arcpy.da.SearchCursor(tablePath, ['globalid'], where) as scur:
                for srow in scur:
                    gidList.append(srow[0])
            childTableName = arcpy.Describe(tablePath).baseName
            # add to dictionary as table_name.foreign_key_field for dictionary key
            childTablesDict["{0}.{1}".format(childTableName, fieldName)] = gidList
        else:
            where = "{0}_guid = '{1}'".format(tableName[:-1], globalId)
            with arcpy.da.SearchCursor(childTable, ['globalid'], where) as scur:
                for srow in scur:
                    gidList.append(srow[0])
            childTableName = arcpy.Describe(childTable).baseName
            childTablesDict[childTableName] = gidList
    return childTablesDict

def lastPcopPcGid(pcopGids):
    lastDate = datetime.datetime(1900, 1, 1, 0, 0)
    partyContactGlobalId = ''
    for pcopGid in pcopGids:
        pcopObj = cls_party_cont_own_prcl(pcopGid)
        if pcopObj.purchase_date >= lastDate:
            partyContactGlobalId = pcopObj.party_contact_guid
            lastDate = pcopObj.purchase_date
    return partyContactGlobalId

class cls_party_contact:
    '''Party Contacts record.'''
    def __init__(self, globalId):
        self.globalIdExists = False
        self.path = os.path.join(db, tbPref+'party_contacts')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'person_first_name',
            'person_middle_name',
            'person_last_name',
            'preferred_name',
            'person_name_prefix',
            'person_name_suffix',
            'business_name',
            'business_type',
            'business_unit',
            'business_title',
            'business_role',
            'address_attention_line',
            'address_line_1',
            'address_line_2',
            'city',
            'state_provice_short_name_code',
            'country_short_name_code',
            'postal_code',
            'fire_number',
            'po_box',
            'rural_route_nbr',
            'phone_line_1',
            'phone_type_1',
            'phone_line_2',
            'phone_type_2',
            'phone_line_3',
            'phone_type_3',
            'email_address_1',
            'email_type_1',
            'email_address_2',
            'email_type_2',
            'sys_username',
            'plan_writer_id',
            'spouse_name',
            'plchldr',
            'comments',
            'orig_id',
            'plan_writer_certified',
            'do_not_mail',
            'email_address_1_unsubscribe',
            'email_address_2_unsubscribe',
            'vendor_number',
             ]
        self.globalid = ''
        self.person_first_name = ''
        self.person_middle_name = ''
        self.person_last_name = ''
        self.preferred_name = ''
        self.person_name_prefix = ''
        self.person_name_suffix = ''
        self.business_name = ''
        self.business_type = ''
        self.business_unit = ''
        self.business_title = ''
        self.business_role = ''
        self.address_attention_line = ''
        self.address_line_1 = ''
        self.address_line_2 = ''
        self.city = ''
        self.state_provice_short_name_code = ''
        self.country_short_name_code = ''
        self.postal_code = ''
        self.fire_number = ''
        self.po_box = ''
        self.rural_route_nbr = ''
        self.phone_line_1 = ''
        self.phone_type_1 = ''
        self.phone_line_2 = ''
        self.phone_type_2 = ''
        self.phone_line_3 = ''
        self.phone_type_3 = ''
        self.email_address_1 = ''
        self.email_type_1 = ''
        self.email_address_2 = ''
        self.email_type_2 = ''
        self.sys_username = ''
        self.plan_writer_id = ''
        self.spouse_name = ''
        self.plchldr = ''
        self.comments = ''
        self.orig_id = ''
        self.plan_writer_certified = ''
        self.do_not_mail = ''
        self.email_address_1_unsubscribe = ''
        self.email_address_2_unsubscribe = ''
        self.vendor_number = ''
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.person_first_name = module_pfmm_helpers.passNull(srow[1], self.person_first_name)
                self.person_middle_name = module_pfmm_helpers.passNull(srow[2], self.person_middle_name)
                self.person_last_name = module_pfmm_helpers.passNull(srow[3], self.person_last_name)
                self.preferred_name = module_pfmm_helpers.passNull(srow[4], self.preferred_name)
                self.person_name_prefix = module_pfmm_helpers.passNull(srow[5], self.person_name_prefix)
                self.person_name_suffix = module_pfmm_helpers.passNull(srow[6], self.person_name_suffix)
                self.business_name = module_pfmm_helpers.passNull(srow[7], self.business_name)
                self.business_type = module_pfmm_helpers.passNull(srow[8], self.business_type)
                self.business_unit = module_pfmm_helpers.passNull(srow[9], self.business_unit)
                self.business_title = module_pfmm_helpers.passNull(srow[10], self.business_title)
                self.business_role = module_pfmm_helpers.passNull(srow[11], self.business_role)
                self.address_attention_line = module_pfmm_helpers.passNull(srow[12], self.address_attention_line)
                self.address_line_1 = module_pfmm_helpers.passNull(srow[13], self.address_line_1)
                self.address_line_2 = module_pfmm_helpers.passNull(srow[14], self.address_line_2)
                self.city = module_pfmm_helpers.passNull(srow[15], self.city)
                self.state_provice_short_name_code = module_pfmm_helpers.passNull(srow[16], self.state_provice_short_name_code)
                self.country_short_name_code = module_pfmm_helpers.passNull(srow[17], self.country_short_name_code)
                self.postal_code = module_pfmm_helpers.passNull(srow[18], self.postal_code)
                self.fire_number = module_pfmm_helpers.passNull(srow[19], self.fire_number)
                self.po_box = module_pfmm_helpers.passNull(srow[20], self.po_box)
                self.rural_route_nbr = module_pfmm_helpers.passNull(srow[21], self.rural_route_nbr)
                self.phone_line_1 = module_pfmm_helpers.passNull(srow[22], self.phone_line_1)
                self.phone_type_1 = module_pfmm_helpers.passNull(srow[23], self.phone_type_1)
                self.phone_line_2 = module_pfmm_helpers.passNull(srow[24], self.phone_line_2)
                self.phone_type_2 = module_pfmm_helpers.passNull(srow[25], self.phone_type_2)
                self.phone_line_3 = module_pfmm_helpers.passNull(srow[26], self.phone_line_3)
                self.phone_type_3 = module_pfmm_helpers.passNull(srow[27], self.phone_type_3)
                self.email_address_1 = module_pfmm_helpers.passNull(srow[28], self.email_address_1)
                self.email_type_1 = module_pfmm_helpers.passNull(srow[29], self.email_type_1)
                self.email_address_2 = module_pfmm_helpers.passNull(srow[30], self.email_address_2)
                self.email_type_2 = module_pfmm_helpers.passNull(srow[31], self.email_type_2)
                self.sys_username = module_pfmm_helpers.passNull(srow[32], self.sys_username)
                self.plan_writer_id = module_pfmm_helpers.passNull(srow[33], self.plan_writer_id)
                self.spouse_name = module_pfmm_helpers.passNull(srow[34], self.spouse_name)
                self.plchldr = module_pfmm_helpers.passNull(srow[35], self.plchldr)
                self.comments = module_pfmm_helpers.passNull(srow[36], self.comments)
                self.orig_id = module_pfmm_helpers.passNull(srow[37], self.orig_id)
                self.plan_writer_certified = module_pfmm_helpers.passNull(srow[38], self.plan_writer_certified)
                self.do_not_mail = module_pfmm_helpers.passNull(srow[39], self.do_not_mail)
                self.email_address_1_unsubscribe = module_pfmm_helpers.passNull(srow[40], self.email_address_1_unsubscribe)
                self.email_address_2_unsubscribe = module_pfmm_helpers.passNull(srow[41], self.email_address_2_unsubscribe)
                self.vendor_number = module_pfmm_helpers.passNull(srow[42], self.vendor_number)

class cls_management_plan:
    '''PFM Management Plans record.'''
    def __init__(self, globalId):
        self.globalIdExists = False
        self.path = os.path.join(db, fd, tbPref+'management_plans')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'ownership_block_guid',
            'status',
            'plan_type',
            'plan_date',
            'acres_plan',
            'acres_gis',
            'tree_farm_status',
            'conservation_easement',
            'request_date',
            'assigned_date',
            'registered_date',
            'incentives_date',
            'completion_date',
            'priority',
            'donation',
            'comments',
            'orig_id',
            'completion_status',
            'party_contact_guid',
            'ecs_subsection_guid',
            'cultural_heritage',
            'grant_id',
            'planname',
            'planid',
            'fedfy',
            'reg_fee',
            'cust_num',
            'invc_num',
            'invc_date',
            'reg_num',
            'ran',
            'registering',
            'party_contact_2_guid',
            'party_contact_3_guid',
            'approved_date',
            'dnr_plan_writing_fee',
            'cost_share_to_be_paid',
            'po_number',
            'reconciled_date',
            'cs_invoice_number',
            'SHAPE@'
             ]
        self.globalid = ''
        self.ownership_block_guid = ''
        self.status = ''
        self.plan_type = ''
        self.plan_date = datetime.datetime(1900,1,1,0,0,0)
        self.acres_plan = 0
        self.acres_gis = 0
        self.tree_farm_status = ''
        self.conservation_easement = ''
        self.request_date = datetime.datetime(1900,1,1,0,0,0)
        self.assigned_date = datetime.datetime(1900,1,1,0,0,0)
        self.registered_date = datetime.datetime(1900,1,1,0,0,0)
        self.incentives_date = datetime.datetime(1900,1,1,0,0,0)
        self.completion_date = datetime.datetime(1900,1,1,0,0,0)
        self.priority = 0
        self.donation = ''
        self.comments = ''
        self.orig_id = ''
        self.completion_status = ''
        self.party_contact_guid = ''
        self.ecs_subsection_guid = ''
        self.cultural_heritage = ''
        self.grant_id = ''
        self.planname = ''
        self.planid = ''
        self.fedfy = ''
        self.reg_fee = 0
        self.cust_num = ''
        self.invc_num = ''
        self.invc_date = datetime.datetime(1900,1,1,0,0,0)
        self.reg_num = ''
        self.ran = ''
        self.registering = ''
        self.party_contact_2_guid = ''
        self.party_contact_3_guid = ''
        self.approved_date = datetime.datetime(1900,1,1,0,0,0)
        self.dnr_plan_writing_fee = 0
        self.cost_share_to_be_paid = 0
        self.po_number = ''
        self.reconciled_date = datetime.datetime(1900,1,1,0,0,0)
        self.cs_invoice_number = ''
        self.shape = None
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.ownership_block_guid = module_pfmm_helpers.passNull(srow[1], self.ownership_block_guid)
                self.status = module_pfmm_helpers.passNull(srow[2], self.status)
                self.plan_type = module_pfmm_helpers.passNull(srow[3], self.plan_type)
                self.plan_date = module_pfmm_helpers.passNull(srow[4], self.plan_date)
                self.acres_plan = module_pfmm_helpers.passNull(srow[5], self.acres_plan)
                self.acres_gis = module_pfmm_helpers.passNull(srow[6], self.acres_gis)
                self.tree_farm_status = module_pfmm_helpers.passNull(srow[7], self.tree_farm_status)
                self.conservation_easement = module_pfmm_helpers.passNull(srow[8], self.conservation_easement)
                self.request_date = module_pfmm_helpers.passNull(srow[9], self.request_date)
                self.assigned_date = module_pfmm_helpers.passNull(srow[10], self.assigned_date)
                self.registered_date = module_pfmm_helpers.passNull(srow[11], self.registered_date)
                self.incentives_date = module_pfmm_helpers.passNull(srow[12], self.incentives_date)
                self.completion_date = module_pfmm_helpers.passNull(srow[13], self.completion_date)
                self.priority = module_pfmm_helpers.passNull(srow[14], self.priority)
                self.donation = module_pfmm_helpers.passNull(srow[15], self.donation)
                self.comments = module_pfmm_helpers.passNull(srow[16], self.comments)
                self.orig_id = module_pfmm_helpers.passNull(srow[17], self.orig_id)
                self.completion_status = module_pfmm_helpers.passNull(srow[18], self.completion_status)
                self.party_contact_guid = module_pfmm_helpers.passNull(srow[19], self.party_contact_guid)
                self.ecs_subsection_guid = module_pfmm_helpers.passNull(srow[20], self.ecs_subsection_guid)
                self.cultural_heritage = module_pfmm_helpers.passNull(srow[21], self.cultural_heritage)
                self.grant_id = module_pfmm_helpers.passNull(srow[22], self.grant_id)
                self.planname = module_pfmm_helpers.passNull(srow[23], self.planname)
                self.planid = module_pfmm_helpers.passNull(srow[24], self.planid)
                self.fedfy = module_pfmm_helpers.passNull(srow[25], self.fedfy)
                self.reg_fee = module_pfmm_helpers.passNull(srow[26], self.reg_fee)
                self.cust_num = module_pfmm_helpers.passNull(srow[27], self.cust_num)
                self.invc_num = module_pfmm_helpers.passNull(srow[28], self.invc_num)
                self.invc_date = module_pfmm_helpers.passNull(srow[29], self.invc_date)
                self.reg_num = module_pfmm_helpers.passNull(srow[30], self.reg_num)
                self.ran = module_pfmm_helpers.passNull(srow[31], self.ran)
                self.registering = module_pfmm_helpers.passNull(srow[32], self.registering)
                self.party_contact_2_guid = module_pfmm_helpers.passNull(srow[33], self.party_contact_2_guid)
                self.party_contact_3_guid = module_pfmm_helpers.passNull(srow[34], self.party_contact_3_guid)
                self.approved_date = module_pfmm_helpers.passNull(srow[35], self.approved_date)
                self.dnr_plan_writing_fee = module_pfmm_helpers.passNull(srow[36], self.dnr_plan_writing_fee)
                self.cost_share_to_be_paid = module_pfmm_helpers.passNull(srow[37], self.cost_share_to_be_paid)
                self.po_number = module_pfmm_helpers.passNull(srow[38], self.po_number)
                self.reconciled_date = module_pfmm_helpers.passNull(srow[39], self.reconciled_date)
                self.cs_invoice_number = module_pfmm_helpers.passNull(srow[40], self.cs_invoice_number)
                self.shape = srow[41]

class cls_ownership_block:
    '''PFM Ownership Blocks record.'''
    def __init__(self, globalId):
        self.globalIdExists = False
        self.path = os.path.join(db, fd, tbPref+'ownership_blocks')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'coun',
            'acres_deed',
            'acres_gis',
            'town',
            'range',
            'sect',
            'fort',
            'legal_desc',
            'orig_id',
            'rdir',
            'SHAPE@'
             ]
        self.globalid = ''
        self.coun = 0
        self.acres_deed = 0
        self.acres_gis = 0
        self.town = 0
        self.range = 0
        self.sect = 0
        self.fort = 0
        self.legal_desc = ''
        self.orig_id = ''
        self.rdir = ''
        self.shape = None
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.coun = module_pfmm_helpers.passNull(srow[1], self.coun)
                self.acres_deed = module_pfmm_helpers.passNull(srow[2], self.acres_deed)
                self.acres_gis = module_pfmm_helpers.passNull(srow[3], self.acres_gis)
                self.town = module_pfmm_helpers.passNull(srow[4], self.town)
                self.range = module_pfmm_helpers.passNull(srow[5], self.range)
                self.sect = module_pfmm_helpers.passNull(srow[6], self.sect)
                self.fort = module_pfmm_helpers.passNull(srow[7], self.fort)
                self.legal_desc = module_pfmm_helpers.passNull(srow[8], self.legal_desc)
                self.orig_id = module_pfmm_helpers.passNull(srow[9], self.orig_id)
                self.rdir = module_pfmm_helpers.passNull(srow[10], self.rdir)
                self.shape = srow[11]

class cls_ownership_parcel:
    '''PFM Ownership Parcels record.'''
    def __init__(self, globalId):
        self.globalIdExists = False
        self.path = os.path.join(db, fd, tbPref+'ownership_parcels')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'coun',
            'acres_deed',
            'acres_gis',
            'pin',
            'legal_desc',
            'orig_id',
            'ownership_block_guid',
            'SHAPE@'
             ]
        self.globalid = ''
        self.coun = 0
        self.acres_deed = 0
        self.acres_gis = 0
        self.pin = ''
        self.legal_desc = ''
        self.orig_id = ''
        self.ownership_block_guid = ''
        self.shape = None
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.coun = module_pfmm_helpers.passNull(srow[1], self.coun)
                self.acres_deed = module_pfmm_helpers.passNull(srow[2], self.acres_deed)
                self.acres_gis = module_pfmm_helpers.passNull(srow[3], self.acres_gis)
                self.pin = module_pfmm_helpers.passNull(srow[4], self.pin)
                self.legal_desc = module_pfmm_helpers.passNull(srow[5], self.legal_desc)
                self.orig_id = module_pfmm_helpers.passNull(srow[6], self.orig_id)
                self.ownership_block_guid = module_pfmm_helpers.passNull(srow[7], self.ownership_block_guid)
                self.shape = srow[8]

class cls_party_cont_own_prcl:
    '''PFM Party Cont Own Prcl record.'''
    def __init__(self, globalId):
        self.globalIdExists = False
        self.path = os.path.join(db, tbPref+'party_cont_own_prcl')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'party_contact_guid',
            'ownership_parcel_guid',
            'purchase_date',
            'sale_date',
            'current_owner',
            'ownership_block_contct_type',
            'comments'
             ]
        self.globalid = ''
        self.party_contact_guid = ''
        self.ownership_parcel_guid = ''
        self.purchase_date = datetime.datetime(1900,1,1,0,0,0)
        self.sale_date = datetime.datetime(1900,1,1,0,0,0)
        self.current_owner = 0
        self.ownership_block_contct_type = ''
        self.comments = ''
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.party_contact_guid = module_pfmm_helpers.passNull(srow[1], self.party_contact_guid)
                self.ownership_parcel_guid = module_pfmm_helpers.passNull(srow[2], self.ownership_parcel_guid)
                self.purchase_date = module_pfmm_helpers.passNull(srow[3], self.purchase_date)
                self.sale_date = module_pfmm_helpers.passNull(srow[4], self.sale_date)
                self.current_owner = module_pfmm_helpers.passNull(srow[5], self.current_owner)
                self.ownership_block_contct_type = module_pfmm_helpers.passNull(srow[6], self.ownership_block_contct_type)
                self.comments = module_pfmm_helpers.passNull(srow[7], self.comments)

class cls_county_coun:
    '''PFM County Coun record.'''
    def __init__(self, coun = ''):
        self.recordExists = False
        self.path = os.path.join(db, tbPref+'county_coun')
        self.where = "coun = "+str(coun)
        self.fieldList = [
            'coun',
            'cty_name'
             ]
        self.coun = 0
        self.cty_name = ''
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.recordExists = True
                self.coun = srow[0]
                self.cty_name = srow[1]

class cls_party_cont_own_blks:
    '''PFM Party Cont Own Blks record.'''
    def __init__(self, globalId = '', guid = ''):
        self.globalIdExists = False
        self.path = os.path.join(db, tbPref+'party_cont_own_blks')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'party_contact_guid',
            'ownership_block_guid',
            'ownership_block_contact_type'
             ]
        self.globalid = ''
        self.party_contact_guid = ''
        self.ownership_block_guid = ''
        self.ownership_block_contact_type = ''
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.party_contact_guid = module_pfmm_helpers.passNull(srow[1], self.party_contact_guid)
                self.ownership_block_guid = module_pfmm_helpers.passNull(srow[2], self.ownership_block_guid)
                self.ownership_block_contact_type = module_pfmm_helpers.passNull(srow[3], self.ownership_block_contact_type)

class cls_contact_events:
    '''PFM Contact Events record.'''
    def __init__(self, globalId = '', guid = ''):
        self.globalIdExists = False
        self.path = os.path.join(db, tbPref+'contact_events')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'party_contact_1_guid',
            'party_contact_2_guid',
            'ownership_block_guid',
            'management_plan_guid',
            'subject',
            'contact_event_type',
            'summary',
            'notes',
            'contact_date',
            'party_contact_3_guid'
             ]
        self.globalid = ''
        self.party_contact_1_guid = ''
        self.party_contact_2_guid = ''
        self.ownership_block_guid = ''
        self.management_plan_guid = ''
        self.subject = ''
        self.contact_event_type = ''
        self.summary = ''
        self.notes = ''
        self.contact_date = datetime.datetime(1900,1,1,0,0,0)
        self.party_contact_3_guid = ''
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.party_contact_1_guid = module_pfmm_helpers.passNull(srow[1], self.party_contact_1_guid)
                self.party_contact_2_guid = module_pfmm_helpers.passNull(srow[2], self.party_contact_2_guid)
                self.ownership_block_guid = module_pfmm_helpers.passNull(srow[3], self.ownership_block_guid)
                self.management_plan_guid = module_pfmm_helpers.passNull(srow[4], self.management_plan_guid)
                self.subject = module_pfmm_helpers.passNull(srow[5], self.subject)
                self.contact_event_type = module_pfmm_helpers.passNull(srow[6], self.contact_event_type)
                self.summary = module_pfmm_helpers.passNull(srow[7], self.summary)
                self.notes = module_pfmm_helpers.passNull(srow[8], self.notes)
                self.contact_date = module_pfmm_helpers.passNull(srow[9], self.contact_date)
                self.party_contact_3_guid = module_pfmm_helpers.passNull(srow[10], self.party_contact_3_guid)

class cls_project_area:
    '''PFM Project Areas record.'''
    def __init__(self, globalId = '', guid = ''):
        self.globalIdExists = False
        self.path = os.path.join(db, fd, tbPref+'project_areas')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'party_contact_applicant_guid',
            'acres_gis',
            'assigned_date',
            'party_contact_writer_guid',
            'project_plan_delivered_date',
            'anticipated_project_start_date',
            'anticipated_project_end_date',
            'completion_date',
            'canceled_date',
            'reason_for_canceling',
            'comments',
            'entered_date',
            'party_contact_entered_guid',
            'request_approved_date',
            'party_contact_approver_guid',
            'total_cost_share_approved',
            'da_signed_date',
            'po_number',
            'po_encumbered_date',
            'completion_deadline_date',
            'practices_certified_date',
            'party_contact_certifier_guid',
            'total_cost_share_to_be_paid',
            'reconciled_date',
            'ownership_block_guid',
            'pa_cultural_heritage',
            'invoice_number',
            'SHAPE@'
             ]
        self.globalid = ''
        self.party_contact_applicant_guid = ''
        self.acres_gis = 0
        self.assigned_date = datetime.datetime(1900,1,1,0,0,0)
        self.party_contact_writer_guid = ''
        self.project_plan_delivered_date = datetime.datetime(1900,1,1,0,0,0)
        self.anticipated_project_start_date = datetime.datetime(1900,1,1,0,0,0)
        self.anticipated_project_end_date = datetime.datetime(1900,1,1,0,0,0)
        self.completion_date = datetime.datetime(1900,1,1,0,0,0)
        self.canceled_date = datetime.datetime(1900,1,1,0,0,0)
        self.reason_for_canceling = ''
        self.comments = ''
        self.entered_date = datetime.datetime(1900,1,1,0,0,0)
        self.party_contact_entered_guid = ''
        self.request_approved_date = datetime.datetime(1900,1,1,0,0,0)
        self.party_contact_approver_guid = ''
        self.total_cost_share_approved = 0
        self.da_signed_date = datetime.datetime(1900,1,1,0,0,0)
        self.po_number = ''
        self.po_encumbered_date = datetime.datetime(1900,1,1,0,0,0)
        self.completion_deadline_date = datetime.datetime(1900,1,1,0,0,0)
        self.practices_certified_date = datetime.datetime(1900,1,1,0,0,0)
        self.party_contact_certifier_guid = ''
        self.total_cost_share_to_be_paid = 0
        self.reconciled_date = datetime.datetime(1900,1,1,0,0,0)
        self.ownership_block_guid = ''
        self.pa_cultural_heritage = ''
        self.invoice_number = ''
        self.shape = None
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.party_contact_applicant_guid = module_pfmm_helpers.passNull(srow[1], self.party_contact_applicant_guid)
                self.acres_gis = module_pfmm_helpers.passNull(srow[2], self.acres_gis)
                self.assigned_date = module_pfmm_helpers.passNull(srow[3], self.assigned_date)
                self.party_contact_writer_guid = module_pfmm_helpers.passNull(srow[4], self.party_contact_writer_guid)
                self.project_plan_delivered_date = module_pfmm_helpers.passNull(srow[5], self.project_plan_delivered_date)
                self.anticipated_project_start_date = module_pfmm_helpers.passNull(srow[6], self.anticipated_project_start_date)
                self.anticipated_project_end_date = module_pfmm_helpers.passNull(srow[7], self.anticipated_project_end_date)
                self.completion_date = module_pfmm_helpers.passNull(srow[8], self.completion_date)
                self.canceled_date = module_pfmm_helpers.passNull(srow[9], self.canceled_date)
                self.reason_for_canceling = module_pfmm_helpers.passNull(srow[10], self.reason_for_canceling)
                self.comments = module_pfmm_helpers.passNull(srow[11], self.comments)
                self.entered_date = module_pfmm_helpers.passNull(srow[12], self.entered_date)
                self.party_contact_entered_guid = module_pfmm_helpers.passNull(srow[13], self.party_contact_entered_guid)
                self.request_approved_date = module_pfmm_helpers.passNull(srow[14], self.request_approved_date)
                self.party_contact_approver_guid = module_pfmm_helpers.passNull(srow[15], self.party_contact_approver_guid)
                self.total_cost_share_approved = module_pfmm_helpers.passNull(srow[16], self.total_cost_share_approved)
                self.da_signed_date = module_pfmm_helpers.passNull(srow[17], self.da_signed_date)
                self.po_number = module_pfmm_helpers.passNull(srow[18], self.po_number)
                self.po_encumbered_date = module_pfmm_helpers.passNull(srow[19], self.po_encumbered_date)
                self.completion_deadline_date = module_pfmm_helpers.passNull(srow[20], self.completion_deadline_date)
                self.practices_certified_date = module_pfmm_helpers.passNull(srow[21], self.practices_certified_date)
                self.party_contact_certifier_guid = module_pfmm_helpers.passNull(srow[22], self.party_contact_certifier_guid)
                self.total_cost_share_to_be_paid = module_pfmm_helpers.passNull(srow[23], self.total_cost_share_to_be_paid)
                self.reconciled_date = module_pfmm_helpers.passNull(srow[24], self.reconciled_date)
                self.ownership_block_guid = module_pfmm_helpers.passNull(srow[25], self.ownership_block_guid)
                self.pa_cultural_heritage = module_pfmm_helpers.passNull(srow[26], self.pa_cultural_heritage)
                self.invoice_number = module_pfmm_helpers.passNull(srow[27], self.invoice_number)
                self.shape = srow[28]

class cls_project_practice:
    '''PFM Project Practices record.'''
    def __init__(self, globalId = '', guid = ''):
        self.globalIdExists = False
        self.path = os.path.join(db, fd, tbPref+'project_practices')
        self.where = "globalid = '"+globalId+"'"
        self.fieldList = [
            'globalid',
            'map_label',
            'anticipated_practice_start_date',
            'practice',
            'component',
            'task',
            'subtask',
            'component_unit',
            'cost_per_unit',
            'cost_share_rate',
            'acres_gis',
            'proposed_component_amount',
            'estimated_total_cost',
            'completion_date',
            'completed_component_amount',
            'requesting_cost_share',
            'cost_shares_recommended',
            'cost_shares_earned',
            'comments',
            'project_area_guid',
            'SHAPE@'
             ]
        self.globalid = ''
        self.map_label = ''
        self.anticipated_practice_start_date = datetime.datetime(1900,1,1,0,0,0)
        self.practice = ''
        self.component = ''
        self.task = ''
        self.subtask = ''
        self.component_unit = ''
        self.cost_per_unit = 0
        self.cost_share_rate = 0
        self.acres_gis = 0
        self.proposed_component_amount = 0
        self.estimated_total_cost = 0
        self.completion_date = datetime.datetime(1900,1,1,0,0,0)
        self.completed_component_amount = 0
        self.requesting_cost_share = ''
        self.cost_shares_recommended = 0
        self.cost_shares_earned = 0
        self.comments = ''
        self.project_area_guid = ''
        self.shape = None
        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:
            for srow in scur:
                self.globalIdExists = True
                self.globalid = module_pfmm_helpers.passNull(srow[0], self.globalid)
                self.map_label = module_pfmm_helpers.passNull(srow[1], self.map_label)
                self.anticipated_practice_start_date = module_pfmm_helpers.passNull(srow[2], self.anticipated_practice_start_date)
                self.practice = module_pfmm_helpers.passNull(srow[3], self.practice)
                self.component = module_pfmm_helpers.passNull(srow[4], self.component)
                self.task = module_pfmm_helpers.passNull(srow[5], self.task)
                self.subtask = module_pfmm_helpers.passNull(srow[6], self.subtask)
                self.component_unit = module_pfmm_helpers.passNull(srow[7], self.component_unit)
                self.cost_per_unit = module_pfmm_helpers.passNull(srow[8], self.cost_per_unit)
                self.cost_share_rate = module_pfmm_helpers.passNull(srow[9], self.cost_share_rate)
                self.acres_gis = module_pfmm_helpers.passNull(srow[10], self.acres_gis)
                self.proposed_component_amount = module_pfmm_helpers.passNull(srow[11], self.proposed_component_amount)
                self.estimated_total_cost = module_pfmm_helpers.passNull(srow[12], self.estimated_total_cost)
                self.completion_date = module_pfmm_helpers.passNull(srow[13], self.completion_date)
                self.completed_component_amount = module_pfmm_helpers.passNull(srow[14], self.completed_component_amount)
                self.requesting_cost_share = module_pfmm_helpers.passNull(srow[15], self.requesting_cost_share)
                self.cost_shares_recommended = module_pfmm_helpers.passNull(srow[16], self.cost_shares_recommended)
                self.cost_shares_earned = module_pfmm_helpers.passNull(srow[17], self.cost_shares_earned)
                self.comments = module_pfmm_helpers.passNull(srow[18], self.comments)
                self.project_area_guid = module_pfmm_helpers.passNull(srow[19], self.project_area_guid)
                self.shape = srow[20]