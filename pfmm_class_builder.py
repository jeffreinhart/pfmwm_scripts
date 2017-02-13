'''Builds class for table. A few fixes still needed:
- delete featureDataset if table
    - replace class name
    - add globalIdExists or recordExists in searchCursor'''

import arcpy

##dataset = r'P:\FOR\FORIST\PFM\dev10_2\dnrgdrs-prod1-pg-dc-pfmm.sde\pfmm_dev.pfmm.party_contacts'
##dataset = r'P:\FOR\FORIST\PFM\dev10_2\dnrgdrs-prod1-pg-dc-pfmm.sde\pfmm_dev.pfmm.spatial\pfmm_dev.pfmm.management_plans'
##dataset = r'P:\FOR\FORIST\PFM\dev10_2\dnrgdrs-prod1-pg-dc-pfmm.sde\pfmm_dev.pfmm.spatial\pfmm_dev.pfmm.ownership_blocks'
##dataset = r'P:\FOR\FORIST\PFM\dev10_2\dnrgdrs-prod1-pg-dc-pfmm.sde\pfmm_dev.pfmm.spatial\pfmm_dev.pfmm.ownership_parcels'
dataset = r'P:\FOR\FORIST\PFM\dev10_2\dnrgdrs-prod1-pg-dc-pfmm.sde\pfmm_dev.pfmm.party_cont_own_prcl'

skipList = ['objectid', 'shape', 'st_area(shape)', 'st_length(shape)']

fieldList = arcpy.ListFields(dataset)

datasetDesc = arcpy.Describe(dataset)

isTable = False
if datasetDesc.dataType == 'Table':
    isTable = True

datasetShortName = datasetDesc.baseName[14:]

datasetFormalName = ' '.join(datasetShortName.split("_")).title()

# start class
classScript = ''
if isTable:
    classScript += "class cls_{0}:\n".format(datasetShortName)
else:
    classScript += "class cls_{0}:\n".format(datasetShortName[:-1])
classScript += "    '''PFM {0} record.'''\n".format(datasetFormalName)
classScript += "    def __init__(self, globalId = '', guid = ''):\n"
classScript += "        self.globalIdExists = False\n"
if isTable:
    classScript += "        self.path = os.path.join(db, tbPref+'{0}')\n".format(datasetShortName)
else:
    classScript += "        self.path = os.path.join(db, fd, tbPref+'{0}')\n".format(datasetShortName)
classScript += "        self.where = \"globalid = '\"+globalId+\"'\"\n"
classScript += "        self.fieldList = [\n"

# build self.fieldList
for field in fieldList:
    if field.baseName not in skipList:
        classScript += "            '{0}',\n".format(field.baseName)

# add shape
if isTable:
    # drop the last comma and add a line return
    classScript = classScript[:-2]
    classScript += "\n"
else:
    # add shape
    classScript += "            'SHAPE@'\n"

# close braces on the field list
classScript +=  "             ]\n"


# build each property
for field in fieldList:
    if field.baseName not in skipList:
        if field.baseName[-4:] == "date":
            classScript += "        self.{0} = datetime.datetime(1900,1,1,0,0,0)\n".format(field.baseName)
        elif field.baseName == "globalid":
            classScript += "        self.{0} = ''\n".format(field.baseName)
        elif field.type in ["Double", "SmallInteger"]:
            classScript += "        self.{0} = 0\n".format(field.baseName)
        else:
            classScript += "        self.{0} = ''\n".format(field.baseName)

if isTable:
    pass
else:
    classScript += "        self.shape = None\n"

classScript += "        with arcpy.da.SearchCursor(self.path, self.fieldList, self.where) as scur:\n"
classScript += "            for srow in scur:\n"
classScript += "                self.globalIdExists = True\n"

# build each property
index = 0
for field in fieldList:
    if field.baseName not in skipList:
        classScript += "                self.{0} = module_pfmm_helpers.passNull(srow[{1}], self.{0})\n".format(field.baseName, str(index))
        index += 1

if isTable:
    pass
else:
    classScript += "                self.shape = srow[{0}]".format(str(index))

print classScript


